"""Screen stronger stock WaveShaper curves using actual native DLL audio.

The current accepted polynomial sits on both old positive bounds. This tests
whether those bounds concealed a cleaner harmonic fit. Every curve remains a
real Fruity WaveShaper state in the existing supported95 graph.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time,sys
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
fine='--fine' in sys.argv
ROOT=W/('native-expanded-WaveShaper-fine-screen-01' if fine else 'native-expanded-WaveShaper-screen-01');ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];rows=[];mutex=threading.Lock();start=time.monotonic()
target_rms=float(np.sqrt(np.mean(target.astype(float)**2)))

def evaluate(case,reps=3,save=True):
    c3,c5=case;c=pool.get()
    try:
        v=x.copy();v[76:78]=[c3,c5];apply(c,v)
        raw,_=c.render();rms=float(np.sqrt(np.mean(raw[:len(target)].astype(float)**2)))
        v[28:30]=np.clip(v[28:30]+10*np.log10(target_rms/rms),-18,18);apply(c,v)
        captures=[]
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
            captures.append(dict(loss=loss,assessment=features.local.last,audio=y,status=status))
        captures.sort(key=lambda row:row['loss']);median=captures[len(captures)//2]
        row=dict(x=v.tolist(),loss=float(np.mean([r['loss'] for r in captures])),
            realization_losses=[r['loss'] for r in captures],realization_standard_deviation=float(np.std([r['loss'] for r in captures])),
            original_reference_assessment=median['assessment'],native_status=median['status'],source_manifest=seed['source_manifest'],
            actual_native_DLL_audio=True,only_three_held_notes=True,normalization_by_actual_native_EQ_main_controls=True,
            normalization_applied_to_control_too=True,not_automatically_accepted=True,original_reference_match_reached=False)
        with mutex:
            if save:rows.append(row)
            print('NATIVE_EXPANDED_SHAPER',c3,c5,row['loss'],flush=True)
        return row,median['audio']
    finally:pool.put(c)

with four_native_slots(ROOT) as state:
    seed=json.loads(Path(state['best_candidate']).read_text());x=np.array(seed['x']);assert len(x)==95
    INPUT=Path(seed['source_manifest']['native_input']);(ROOT/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
    try:
        for i in range(4):
            c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=True);clients.append(c);pool.put(c)
        control,control_audio=evaluate(tuple(x[76:78]),6)
        trials=({(float(c3),float(c5)) for c3 in [.4,.55,.7,.85,1.,1.2] for c5 in [-2.,-1.5,-1.,-.75,-.5,-.25,0.,.25]}
            if fine else {(float(c3),float(c5)) for c3 in [-.6,0.,.35,.75,1.5,3.,6.,12.] for c5 in [-.35,0.,.5,2.,6.,12.]})
        if fine:trials.add((.75,-.35))
        with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,sorted(trials)))
        best=min(rows,key=lambda row:row['loss']);validated,y=evaluate(tuple(best['x'][76:78]),6,False)
        # Re-capture the control after the grid, with the same level procedure.
        control2,control_audio=evaluate(tuple(x[76:78]),6,False)
        se=float(np.hypot(control2['realization_standard_deviation'],validated['realization_standard_deviation'])/np.sqrt(6))
        robust=control2['loss']-validated['loss']>max(.0005,3*se)
        validated.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control2['loss'],fresh_mean_standard_error=se,
            full_fresh_native_realizations=6,full_fresh_native_validation_pending=False,recorded_audio=str(ROOT/'best-fresh-with-tail.wav'))
        sf.write(ROOT/'best-fresh-with-tail.wav',y,48000,subtype='FLOAT');sf.write(ROOT/'control-fresh-with-tail.wav',control_audio,48000,subtype='FLOAT')
        (ROOT/'full-validated-candidate.json').write_text(json.dumps(validated,indent=2)+'\n')
        (ROOT/'results.json').write_text(json.dumps(sorted(rows,key=lambda r:r['loss']),indent=2)+'\n')
        (ROOT/'fresh-control.json').write_text(json.dumps(control2,indent=2)+'\n')
        (ROOT/'completion.json').write_text(json.dumps(dict(actual_native_cases=len(rows),fresh_mean_loss=validated['loss'],
            seed_fresh_mean_loss=control2['loss'],robust_improvement=bool(robust),seconds=time.monotonic()-start,
            c3=validated['x'][76],c5=validated['x'][77],normalization_applied_to_control_too=True,
            original_reference_match_reached=False),indent=2)+'\n')
        print('ACTUAL_EXPANDED_WAVESHAPER_COMPLETE',validated['loss'],control2['loss'],robust,flush=True)
    finally:
        for c in clients:c.close()
