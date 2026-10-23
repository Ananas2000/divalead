"""Research-only eight detail bumps added to the supported native WS curve.

The exact current two-coefficient curve is retained. New bump metadata is
explicitly unsupported by the production exporter until integration and a real
saved-state/reloaded-state comparison succeed. No candidate is auto-installed.
The original reference is assessment-only; source and external MIDI stay fixed.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time,struct,hashlib
import numpy as np
import soundfile as sf
from scipy.stats import qmc
from native_note_residue import measure_native_raw
from native_chain import NativeChain
from native_fst import plugin_preset,parse
from fl20_curve import apply_candidate,extended_curve_bytes,curve_metadata,validate_curve_candidate

ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
prior=json.loads(Path(sys.argv[1]).read_text());seed=np.array(prior['x']);assert len(seed)==95
validate_curve_candidate(prior);assert prior.get('waveshaper_local_bump_adjustment')
overrides={int(k):int(v)for k,v in prior.get('chorus_overrides',{}).items()}
INPUT=Path(prior['source_manifest']['native_input']);features=FeaturesOriginal()
(ROOT/'seed.json').write_text(json.dumps(prior,indent=2)+'\n')
pool=queue.Queue();clients=[];mutex=threading.Lock();rows=[];start=time.monotonic();best=float('inf')
def quantize(v):
    v=v.copy();v[93]=round(np.clip(v[93],.001,.8)*12800)/12800
    v[94]=round(np.clip(v[94],0,4096))
    for i,scale in zip(range(86,93),[1024,5000,1024,5000,5000,5000,5000]):
        v[i]=round(np.clip(v[i],0,1)*scale)/scale
    v[30:34]=np.clip(v[30:34],-1,1);v[76:78]=np.clip(v[76:78],[-1.,-3.],[2.,1.])
    return v
CENTERS=np.array([.08,.16,.24,.32,.40,.48,.56,.64]);WIDTHS=np.full(8,.055)
u=np.linspace(0,1,129)
BASIS=(u[:,None]*(1-u[:,None])/(CENTERS*(1-CENTERS)))**2*np.exp(-.5*((u[:,None]-CENTERS)/WIDTHS)**2)
BASIS/=np.max(BASIS,axis=0)
def state_bytes(v,shape):
    data=bytearray(extended_curve_bytes(v,prior['waveshaper_curve_adjustment'],prior.get('waveshaper_local_bump_adjustment')))
    values=np.array([struct.unpack_from('<d',data,34+24*i+8)[0]for i in range(129)])
    values=np.clip(values+BASIS@np.asarray(shape),0,1)
    for i,y in enumerate(values):struct.pack_into('<d',data,34+24*i+8,float(y))
    return bytes(data)
def shape_valid(v,shape):
    data=state_bytes(v,shape);y=[struct.unpack_from('<d',data,34+24*i+8)[0]for i in range(129)]
    return bool(np.min(np.diff(y))>=-1e-10)
def configure(c,v,extra,shape):
    apply_candidate(c,v,prior)
    for index,value in extra.items():c.set(3,index,value)
    data=state_bytes(v,shape)
    path=ROOT/(c.output.stem+'-local-WS.bin');path.write_bytes(data);c.load_state(0,path)
def evaluate(case,reps=3,save=True):
    global best
    label,v,extra,shape=case;c=pool.get()
    try:
        v=quantize(v);configure(c,v,extra,shape)
        for index,value in extra.items():assert c.value_hint(3,index)==value
        # Both the candidate and control are normalized using actual EQ Main.
        y,_=c.render();features.residual(y[:288000])
        gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
        v[28:30]=np.clip(v[28:30]+10*np.log10(gain),-18,18);configure(c,v,extra,shape)
        captures=[]
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
            captures.append(dict(loss=loss,audio=y,assessment=features.local.last,native_status=status))
        values=[r['loss']for r in captures];median=sorted(captures,key=lambda r:r['loss'])[len(captures)//2]
        row=dict(curve_metadata(prior),label=label,x=v.tolist(),chorus_overrides={str(k):int(v)for k,v in extra.items()},
            loss=float(np.mean(values)),realization_losses=values,realization_standard_deviation=float(np.std(values)),
            original_reference_assessment=median['assessment'],recorded_render_loss=median['loss'],native_status=median['native_status'],
            note_residue_diagnostic=measure_native_raw(median['audio']),source_manifest=prior['source_manifest'],model_family='FL20_corrected_context_detail8_WS_curve_research',waveshaper_detail_bump_format='smooth_detail_bumps8_v1',waveshaper_detail_bump_adjustment=list(map(float,shape)),waveshaper_detail_bump_centers=CENTERS.tolist(),waveshaper_detail_bump_widths=WIDTHS.tolist(),not_compatible_with_standard_x95_exporter=True,not_automatically_adopted=True,
            host_context='Chorus_excluded_from_silent_warmup',objective_version='local_full_original_criteria_FL20_context_v1',
            actual_native_DLL_audio=True,all_requested_Chorus_overrides_read_back=True,actual_FL_validation_pending=True,
            only_three_held_notes=True,original_reference_match_reached=False,full_fresh_native_realizations=reps)
        with mutex:
            if save:
                rows.append(row)
                if row['loss']<best:
                    best=row['loss'];(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n')
                    sf.write(ROOT/'best-training-with-tail.wav',median['audio'],48000,subtype='FLOAT')
                    print('FL20_CONTROLS_BEST',label,best,len(rows),flush=True)
                (ROOT/'search-state.json').write_text(json.dumps(dict(cases=len(rows),best=best,seconds=time.monotonic()-start,
                    full_fresh_validation_pending=True,match_reached=False),indent=2)+'\n')
        return row,median['audio']
    finally:pool.put(c)

trials=[]
DETAIL_STEPS=np.array([.002,.003,.004,.006,.008,.010,.012,.015])
for k,step in enumerate(DETAIL_STEPS):
    for factor in [-2.,-1.,-.5,.5,1.,2.]:
        shape=np.zeros(8);shape[k]=factor*step
        if shape_valid(seed,shape):trials.append((f'curve-axis-{k}-{factor:g}',seed.copy(),dict(overrides),shape.tolist()))
lhs=qmc.LatinHypercube(d=8,seed=2026102244).random(256)
for k,u in enumerate(lhs):
    shape=(u*2-1)*DETAIL_STEPS*2*[.25,.5,1.,1.5][k%4]
    if shape_valid(seed,shape):trials.append((f'curve-LHS-{k}',seed.copy(),dict(overrides),shape.tolist()))
try:
    for i in range(4):
        c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
        clients.append(c);pool.put(c)
    initial,_=evaluate(('normalized-control',seed.copy(),overrides,[0.]*8),6)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:list(executor.map(evaluate,trials))
    # Refine the best actual monotone curve, with finite native coordinate passes.
    current=min(rows,key=lambda row:row['loss']);shape=np.array(current['waveshaper_detail_bump_adjustment'])
    for sweep in range(3):
        for k,step in enumerate(DETAIL_STEPS*.5**(sweep+1)):
            cases=[]
            for factor in [-2.,-1.,1.,2.]:
                changed=shape.copy();changed[k]+=step*factor
                if shape_valid(seed,changed):cases.append((f'detail-coordinate-{sweep}-{k}-{factor:g}',seed.copy(),dict(overrides),changed.tolist()))
            if cases:
                with concurrent.futures.ThreadPoolExecutor(4)as executor:got=list(executor.map(evaluate,cases))
                winner=min(got,key=lambda pair:pair[0]['loss'])[0]
                if winner['loss']<current['loss']-.00005:current=winner;shape=np.array(current['waveshaper_detail_bump_adjustment'])
    # Fresh twelve-capture validation for four finalists, then independent24+24.
    finalists=sorted(rows,key=lambda r:r['loss'])[:4];checked=[]
    for k,row in enumerate(finalists):
        extra={int(i):int(v)for i,v in row['chorus_overrides'].items()}
        got,audio=evaluate((f'fresh-finalist-{k}',np.array(row['x']),extra,row['waveshaper_detail_bump_adjustment']),12,False);checked.append((got,audio))
    control,control_audio=evaluate(('fresh-control',seed.copy(),overrides,[0.]*8),24,False)
    chosen,chosen_audio=min(checked,key=lambda r:r[0]['loss'])
    # Final fresh batch is separate from the finalist selection batches.
    chosen,chosen_audio=evaluate(('independent-selected',np.array(chosen['x']),{int(i):int(v)for i,v in chosen['chorus_overrides'].items()},chosen['waveshaper_detail_bump_adjustment']),24,False)
    se=float(np.hypot(chosen['realization_standard_deviation'],control['realization_standard_deviation'])/np.sqrt(24))
    robust=control['loss']-chosen['loss']>max(.0005,3*se)
    if not robust:chosen,chosen_audio=control,control_audio
    chosen.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
        full_fresh_native_validation_pending=False,full_fresh_native_realizations=24,reference_match_reached=False,
        recorded_audio=str(ROOT/'best-with-tail.wav'))
    sf.write(ROOT/'best-with-tail.wav',chosen_audio,48000,subtype='FLOAT')
    c=clients[0];extra={int(i):int(v)for i,v in chosen['chorus_overrides'].items()}
    configure(c,np.array(chosen['x']),extra,chosen['waveshaper_detail_bump_adjustment'])
    saved=ROOT/'Extended_WaveShaper_state.bin';c.save_state(0,saved)
    fst=ROOT/'Extended_WaveShaper_RESEARCH_ONLY.fst';fst.write_bytes(plugin_preset('Fruity WaveShaper',saved.read_bytes()))
    state=next(data for index,data in parse(fst.read_bytes())['events']if index==213);assert state==saved.read_bytes()
    c.set(3,1,0);zero_before,_=c.render();c.load_state(0,saved)
    resaved=ROOT/'Extended_WaveShaper_resaved.bin';c.save_state(0,resaved);assert resaved.read_bytes()==state
    zero_after,_=c.render();zero_error=float(np.max(np.abs(zero_after-zero_before)));assert zero_error<=2e-7,zero_error
    (ROOT/'EXTENDED_CURVE_NATIVE_STATE_PROOF.json').write_text(json.dumps(dict(native_state_byte_exact=True,
        native_FST_payload_exact=True,zero_depth_full_graph_audio_error=zero_error,
        state_SHA256=hashlib.sha256(state).hexdigest(),actual_FL_GUI_export_pending=True,
        not_yet_integrated_in_standard_x95_exporter=True,not_automatically_adopted=True),indent=2)+'\n')

    for name,data in [('full-validated-candidate.json',chosen),('results.json',rows),('finalists.json',[r[0]for r in checked]),
        ('paired-fresh-control.json',dict(control=control,selected=chosen,standard_error_of_difference=se,robust_improvement=bool(robust))),
        ('completion.json',dict(cases=len(rows),fresh_mean_loss=chosen['loss'],fresh_control=control['loss'],
            robust_improvement=bool(robust),seconds=time.monotonic()-start,match_reached=False))]:
        (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
    print('FL20_DETAIL8_WS_RESEARCH_VALIDATED',chosen['loss'],robust,flush=True)
finally:
    for c in clients:c.close()
