"""Full native-DLL controls search after correcting Chorus startup context.

The original WAV is assessment-only. Every trial retains the physical FL05
Diva source and the same three held notes. This script never writes Git.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time
import numpy as np
import soundfile as sf
from scipy.stats import qmc
from native_chain import NativeChain
from apply_native_candidate import apply

ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
prior=json.loads(Path(sys.argv[1]).read_text());seed=np.array(prior['x']);assert len(seed)==95
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
def configure(c,v,extra):
    apply(c,v)
    for index,value in extra.items():c.set(3,index,value)
def evaluate(case,reps=3,save=True):
    global best
    label,v,extra=case;c=pool.get()
    try:
        v=quantize(v);configure(c,v,extra)
        for index,value in extra.items():assert c.value_hint(3,index)==value
        # Both the candidate and control are normalized using actual EQ Main.
        y,_=c.render();features.residual(y[:288000])
        gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
        v[28:30]=np.clip(v[28:30]+10*np.log10(gain),-18,18);configure(c,v,extra)
        captures=[]
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
            captures.append(dict(loss=loss,audio=y,assessment=features.local.last,native_status=status))
        values=[r['loss']for r in captures];median=sorted(captures,key=lambda r:r['loss'])[len(captures)//2]
        row=dict(label=label,x=v.tolist(),chorus_overrides={str(k):int(v)for k,v in extra.items()},
            loss=float(np.mean(values)),realization_losses=values,realization_standard_deviation=float(np.std(values)),
            original_reference_assessment=median['assessment'],recorded_render_loss=median['loss'],native_status=median['native_status'],
            source_manifest=prior['source_manifest'],model_family='FL20_corrected_context_three_held_controls',
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
coordinates=[76,77,*range(86,95),*range(30,34),29]
steps=np.array([.12,.15,.025,.06,.08,.04,.04,.04,.035,.025,120.,.025,.025,.025,.025,.6])
assert len(coordinates)==len(steps)
for i,step in zip(coordinates,steps):
    for factor in [-2.,-1.,-.5,.5,1.,2.]:
        v=seed.copy();v[i]+=factor*step;trials.append((f'coord-{i}-{factor:g}',v,dict(overrides)))
for index in [6,7,8]:
    for delta in [-256,-128,-64,64,128,256]:
        extra=dict(overrides);extra[index]=round(np.clip(extra.get(index,0)+delta,0,1024))
        if extra!=overrides:trials.append((f'LFOshape-{index}-{delta}',seed.copy(),extra))
generation=int(os.environ.get('DIVALEAD_FL20_GENERATION','1'))
lhs=qmc.LatinHypercube(d=len(coordinates)+3,seed=2026102200+generation).random(160)
for k,u in enumerate(lhs):
    v=seed.copy();radius=[.5,1.,2.,3.][k%4]
    v[coordinates]+=(u[:len(coordinates)]*2-1)*steps*radius
    extra=dict(overrides)
    if k%3==0:
        for j,index in enumerate([6,7,8]):extra[index]=round(np.clip(extra.get(index,0)+(2*u[-3+j]-1)*256,0,1024))
    trials.append((f'LHS-{generation}-{k}',v,extra))
try:
    for i in range(4):
        c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
        clients.append(c);pool.put(c)
    initial,_=evaluate(('normalized-control',seed.copy(),overrides),6)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:list(executor.map(evaluate,trials))
    # Fresh six-capture validation for four finalists, then a separate control.
    finalists=sorted(rows,key=lambda r:r['loss'])[:4];checked=[]
    for k,row in enumerate(finalists):
        extra={int(i):int(v)for i,v in row['chorus_overrides'].items()}
        got,audio=evaluate((f'fresh-finalist-{k}',np.array(row['x']),extra),6,False);checked.append((got,audio))
    control,control_audio=evaluate(('fresh-control',seed.copy(),overrides),6,False)
    chosen,chosen_audio=min(checked,key=lambda r:r[0]['loss'])
    # Final fresh batch is separate from the finalist selection batches.
    chosen,chosen_audio=evaluate(('independent-selected',np.array(chosen['x']),{int(i):int(v)for i,v in chosen['chorus_overrides'].items()}),6,False)
    se=float(np.hypot(chosen['realization_standard_deviation'],control['realization_standard_deviation'])/np.sqrt(6))
    robust=control['loss']-chosen['loss']>max(.0005,3*se)
    if not robust:chosen,chosen_audio=control,control_audio
    chosen.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
        full_fresh_native_validation_pending=False,full_fresh_native_realizations=6,reference_match_reached=False,
        recorded_audio=str(ROOT/'best-with-tail.wav'))
    sf.write(ROOT/'best-with-tail.wav',chosen_audio,48000,subtype='FLOAT')
    for name,data in [('full-validated-candidate.json',chosen),('results.json',rows),('finalists.json',[r[0]for r in checked]),
        ('paired-fresh-control.json',dict(control=control,selected=chosen,standard_error_of_difference=se,robust_improvement=bool(robust))),
        ('completion.json',dict(cases=len(rows),fresh_mean_loss=chosen['loss'],fresh_control=control['loss'],
            robust_improvement=bool(robust),seconds=time.monotonic()-start,match_reached=False))]:
        (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
    print('FL20_CONTROLS_VALIDATED',chosen['loss'],robust,flush=True)
finally:
    for c in clients:c.close()
