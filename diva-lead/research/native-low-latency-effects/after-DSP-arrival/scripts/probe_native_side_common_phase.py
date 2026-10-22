"""Actual SIDE common-phase pair; separate experimental metadata, not public96."""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-SIDE-common-phase-screen-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];rows=[];mutex=threading.Lock();start=time.monotonic()
target_rms=float(np.sqrt(np.mean(target.astype(float)**2)))
def side_phase(c,raw):
    assert 0<=raw<=4096
    for node,value in [(15,raw),(16,-raw)]:
        for i,v in enumerate([0,12800,12800,0,0,value]):c.set(node,i,v)
def settings(c,v,raw):
    apply(c,v);side_phase(c,raw)
def score(y,v):
    r=features.residual(y[:len(target)]);return float(r@r)+float(np.sum(v[:28]**2))*.00000025
def evaluate(case,reps=3,save=True,normalize=True):
    source_raw,side_raw=case;c=pool.get()
    try:
        v=x.copy();v[94]=source_raw;settings(c,v,side_raw)
        if normalize:
            a,_=c.render();rms=float(np.sqrt(np.mean(a[:len(target)].astype(float)**2)))
            v[28:30]+=10*np.log10(target_rms/rms);settings(c,v,side_raw)
        captures=[]
        for rep in range(reps):
            y,status=c.render();captures.append(dict(loss=score(y,v),assessment=features.local.last,audio=y,status=status))
        captures.sort(key=lambda row:row['loss']);median=captures[len(captures)//2]
        row=dict(x=v.tolist(),SIDE_common_phase_raw=side_raw,loss=float(np.mean([r['loss'] for r in captures])),
            realization_losses=[r['loss'] for r in captures],realization_standard_deviation=float(np.std([r['loss'] for r in captures])),
            original_reference_assessment=median['assessment'],native_status=median['status'],source_manifest=seed['source_manifest'],
            experimental_family='actual_native_SOURCE_and_SIDE_common_phase_17_nodes',
            actual_native_DLL_audio=True,only_three_held_notes=True,not_supported_by_public95_exporter=True,
            not_automatically_accepted=True,original_reference_match_reached=False)
        with mutex:
            if save:rows.append(row)
            print('NATIVE_SIDE_PHASE',source_raw,side_raw,row['loss'],flush=True)
        return row,median['audio']
    finally:pool.put(c)
with four_native_slots(ROOT) as state:
    seed=json.loads(Path(state['best_candidate']).read_text());x=np.array(seed['x']);assert len(x)==95
    INPUT=Path(seed['source_manifest']['native_input']);(ROOT/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
    old=NativeChain(INPUT,ROOT.name+'-old',fl_graph=True,phase_pair=True)
    new=NativeChain(INPUT,ROOT.name+'-new',fl_graph=True,phase_pair=True,side_phase_pair=True)
    try:
        zero=x.copy();zero[87]=0;apply(old,zero);a,old_status=old.render();settings(new,zero,0);b,new_status=new.render()
        error=float(abs(a-b).max());assert error<=2e-7,error
        side_phase(new,2100);positive,_=new.render();delta=float(abs(positive-b).max());assert delta>1e-4
        proof=dict(zero_Chorus_depth=True,zero_extra_SIDE_phase_max_error=error,positive_SIDE_phase_delta=delta,
            actual_old15_and_new17_native_graphs=True,old_status=old_status,new_status=new_status,
            original_reference_match_reached=False)
        (ROOT/'STRUCTURAL_NATIVE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
    finally:old.close();new.close()
    try:
        for i in range(4):
            c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=True,side_phase_pair=True);clients.append(c);pool.put(c)
        control,control_audio=evaluate((int(round(x[94])),0),6,True,False)
        trials={(int(round(x[94])),r) for r in [0,1,5,20,100,320,512,800,1200,1500,1700,1800,1900,2100,2400,2800,3400,4000,4096]}
        trials|={(s,r) for s in [0,512,1200,1800,2100,2400,3400,4096] for r in [0,320,800,1500,2100,2800,4096]}
        with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,sorted(trials)))
        best=min(rows,key=lambda row:row['loss']);validated,y=evaluate((int(round(best['x'][94])),best['SIDE_common_phase_raw']),6,False)
        se=float(np.hypot(control['realization_standard_deviation'],validated['realization_standard_deviation'])/np.sqrt(6))
        robust=control['loss']-validated['loss']>max(.0005,3*se)
        validated.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
            full_fresh_native_realizations=6,full_fresh_native_validation_pending=False)
        sf.write(ROOT/'best-fresh-with-tail.wav',y,48000,subtype='FLOAT')
        (ROOT/'full-validated-candidate.json').write_text(json.dumps(validated,indent=2)+'\n')
        (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
        (ROOT/'completion.json').write_text(json.dumps(dict(actual_native_cases=len(rows),fresh_mean_loss=validated['loss'],
            seed_fresh_mean_loss=control['loss'],robust_improvement=bool(robust),seconds=time.monotonic()-start,
            new_SIDE_phase_pair=best['SIDE_common_phase_raw'],original_reference_match_reached=False),indent=2)+'\n')
        print('ACTUAL_SIDE_COMMON_PHASE_COMPLETE',validated['loss'],control['loss'],robust,flush=True)
    finally:
        for c in clients:c.close()
