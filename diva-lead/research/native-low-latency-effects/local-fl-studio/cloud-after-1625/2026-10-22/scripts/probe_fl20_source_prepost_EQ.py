"""Research-only real native pre-EQ -> supported WS -> post-EQ source filtering.

The current supported six-coefficient curve is retained. Extra EQ metadata is
guarded by the production exporter until integration and a real
saved-state/reloaded-state comparison succeed. No candidate is auto-installed.
The original reference is assessment-only; source and external MIDI stay fixed.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time,struct,hashlib
import numpy as np
import soundfile as sf
from scipy.stats import qmc
from native_chain import NativeChain
from native_fst import plugin_preset,parse
from fl20_curve import apply_candidate,extended_curve_bytes,curve_metadata,validate_curve_candidate

ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
prior=json.loads(Path(sys.argv[1]).read_text());seed=np.array(prior['x']);assert len(seed)==95
validate_curve_candidate(prior)
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
FREQS=np.array([60,150,400,1000,2500,6300,16000],float)
RAW=np.rint(np.log(FREQS/20)/np.log(1000)*65536).astype(int)
def shape_valid(v,shape):return bool(np.isfinite(shape).all())
def configure(c,v,extra,shape):
    apply_candidate(c,v,prior)
    for index,value in extra.items():c.set(3,index,value)
    if shape is None:return
    assert len(shape)==16
    for node,offset,main in [(1,0,14),(2,7,15)]:
        c.bypass(node,False)
        for band in range(7):
            c.set(node,band,int(round(shape[offset+band]*100)))
            c.set(node,7+band,int(RAW[band]));c.set(node,14+band,9830)
            c.set(node,21+band,6);c.set(node,28+band,0)
        c.set(node,35,int(round(shape[main]*100)))
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
            source_manifest=prior['source_manifest'],model_family='research_native_source_preEQ_WS_postEQ',source_pre_post_EQ_enabled=shape is not None,source_pre_post_EQ_gains=None if shape is None else list(map(float,shape)),source_pre_post_EQ_frequencies_Hz=FREQS.tolist(),source_pre_post_EQ_bandwidth_raw=9830,not_compatible_with_standard_x95_exporter=True,not_automatically_adopted=True,
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
for k,step in enumerate([1.]*14+[2.]):
    for factor in [-2.,-1.,-.5,.5,1.,2.]:
        shape=np.zeros(16);shape[k]=factor*step
        if shape_valid(seed,shape):trials.append((f'curve-axis-{k}-{factor:g}',seed.copy(),dict(overrides),shape.tolist()))
lhs=qmc.LatinHypercube(d=15,seed=2026102255).random(160)
for k,u in enumerate(lhs):
    shape=np.r_[(u*2-1)*np.array([2.]*14+[3.])*[.25,.5,1.,2.][k%4],0.]
    if shape_valid(seed,shape):trials.append((f'curve-LHS-{k}',seed.copy(),dict(overrides),shape.tolist()))
old=NativeChain(INPUT,ROOT.name+'-old-structural',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
new=NativeChain(INPUT,ROOT.name+'-new-structural',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_source_prepost_host.exe')
try:
    configure(old,seed,overrides,None);old.set(3,1,0);a,_=old.render()
    configure(new,seed,overrides,None);new.set(3,1,0);b,_=new.render()
    error=float(np.max(np.abs(a-b)));assert error<=2e-7,error
    configure(new,seed,overrides,np.zeros(16));new.set(3,1,0);flat,_=new.render()
    positive=np.zeros(16);positive[14]=6;configure(new,seed,overrides,positive);new.set(3,1,0);changed,_=new.render()
    delta=float(np.max(np.abs(changed-flat)));assert delta>1e-4
    (ROOT/'STRUCTURAL_NATIVE_PROOF.json').write_text(json.dumps(dict(
        bypassed_source_EQ_old_new_max_error=error,decoded_zero_depth_bypass_audio_bit_exact=bool(np.array_equal(a,b)),
        active_flat_source_EQ_max_error=float(np.max(np.abs(flat-a))),flat_EQ_not_assumed_identity=True,
        positive_pre_EQ_drive_control_max_error=delta,original_Diva_source_and_incoming_MIDI_unchanged=True,
        actual_native_EQ2_and_WS_processing=True,reference_analysis_only=True,
        same_four_mixer_routes=True,not_integrated_in_standard_exporter=True,reference_match_reached=False),indent=2)+'\n')
finally:old.close();new.close()
try:
    for i in range(4):
        c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_source_prepost_host.exe')
        clients.append(c);pool.put(c)
    initial,_=evaluate(('normalized-control',seed.copy(),overrides,None),6)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:list(executor.map(evaluate,trials))
    # Fresh twelve-capture validation for four finalists, then a separate control.
    finalists=sorted(rows,key=lambda r:r['loss'])[:4];checked=[]
    for k,row in enumerate(finalists):
        extra={int(i):int(v)for i,v in row['chorus_overrides'].items()}
        got,audio=evaluate((f'fresh-finalist-{k}',np.array(row['x']),extra,row['source_pre_post_EQ_gains']),12,False);checked.append((got,audio))
    control,control_audio=evaluate(('fresh-control',seed.copy(),overrides,None),12,False)
    chosen,chosen_audio=min(checked,key=lambda r:r[0]['loss'])
    # Final fresh batch is separate from the finalist selection batches.
    chosen,chosen_audio=evaluate(('independent-selected',np.array(chosen['x']),{int(i):int(v)for i,v in chosen['chorus_overrides'].items()},chosen['source_pre_post_EQ_gains']),12,False)
    se=float(np.hypot(chosen['realization_standard_deviation'],control['realization_standard_deviation'])/np.sqrt(12))
    robust=control['loss']-chosen['loss']>max(.0005,3*se)
    (ROOT/'independent-candidate-before-guard.json').write_text(json.dumps(chosen,indent=2)+'\n')
    if not robust:chosen,chosen_audio=control,control_audio
    chosen.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
        full_fresh_native_validation_pending=False,full_fresh_native_realizations=12,reference_match_reached=False,
        recorded_audio=str(ROOT/'best-with-tail.wav'))
    sf.write(ROOT/'best-with-tail.wav',chosen_audio,48000,subtype='FLOAT')
    c=clients[0];extra={int(i):int(v)for i,v in chosen['chorus_overrides'].items()}
    configure(c,np.array(chosen['x']),extra,chosen['source_pre_post_EQ_gains'])
    saved={};state_checks=[]
    for node,name in [(0,'Fruity WaveShaper'),(1,'Fruity Parametric EQ 2'),(2,'Fruity Parametric EQ 2')]:
        path=ROOT/f'actual-source-native-node{node}.bin';c.save_state(node,path);saved[node]=path
        data=path.read_bytes();fst=ROOT/f'RESEARCH_ONLY_source_node{node}.fst';fst.write_bytes(plugin_preset(name,data))
        assert next(d for i,d in parse(fst.read_bytes())['events']if i==213)==data
        state_checks.append(dict(node=node,SHA256=hashlib.sha256(data).hexdigest(),native_FST_payload_exact=True))
    c.set(3,1,0);zero_before,_=c.render()
    for node,path in saved.items():
        c.load_state(node,path);resaved=ROOT/f'reloaded-source-native-node{node}.bin';c.save_state(node,resaved);assert resaved.read_bytes()==path.read_bytes()
    zero_after,_=c.render();zero_error=float(np.max(np.abs(zero_after-zero_before)));assert zero_error<=2e-7,zero_error
    (ROOT/'SOURCE_PRE_POST_NATIVE_STATE_PROOF.json').write_text(json.dumps(dict(native_state_checks=state_checks,
        all_saved_states_reload_byte_exact=True,zero_depth_full_graph_audio_error=zero_error,
        active_source_EQ=chosen['source_pre_post_EQ_enabled'],same_four_mixer_routes=True,
        actual_FL_GUI_export_pending=True,not_integrated_in_standard_exporter=True,not_automatically_adopted=True),indent=2)+'\n')

    for name,data in [('full-validated-candidate.json',chosen),('results.json',rows),('finalists.json',[r[0]for r in checked]),
        ('paired-fresh-control.json',dict(control=control,selected=chosen,standard_error_of_difference=se,robust_improvement=bool(robust))),
        ('completion.json',dict(cases=len(rows),fresh_mean_loss=chosen['loss'],fresh_control=control['loss'],
            robust_improvement=bool(robust),seconds=time.monotonic()-start,match_reached=False))]:
        (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
    print('NATIVE_SOURCE_PRE_POST_RESEARCH_VALIDATED',chosen['loss'],robust,flush=True)
finally:
    for c in clients:c.close()
