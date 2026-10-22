"""Actual post-EQ Fruity Soft Clipper screen, limited to ordinary FL fader gain.

No new incoming notes, sample player or custom audio processor. The extension
is kept separate from supported95 state until its fresh full-chain win is proved.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-post-softclip-screen-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];rows=[];mutex=threading.Lock();start=time.monotonic()
target_rms=float(np.sqrt(np.mean(target.astype(float)**2)))

def settings(c,vector,threshold,gain=1):
    apply(c,vector)
    if threshold is not None:
        c.bypass(9,False);c.set(9,0,threshold);c.set(9,1,160)
    c.gain(2,gain)

def evaluate(case,reps=3,save=True,normalize=True):
    label,vector,threshold=case;c=pool.get()
    try:
        gain=1.;settings(c,vector,threshold)
        if normalize:
            y,status=c.render();rms=float(np.sqrt(np.mean(y[:len(target)].astype(float)**2)));gain=target_rms/rms
            if gain>1.87:
                row=dict(case=label,eligible=False,reason='Required output gain exceeds ordinary SUM fader range used in this trial',required_gain=gain)
                with mutex:rows.append(row)
                return row,None
            c.gain(2,gain)
        captures=[]
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(vector[:28]**2))*.00000025
            captures.append(dict(loss=loss,assessment=features.local.last,audio=y,status=status))
        captures.sort(key=lambda row:row['loss']);median=captures[len(captures)//2]
        row=dict(case=label,eligible=True,x=vector.tolist(),post_clip_extension=dict(enabled=threshold is not None,
            threshold_raw=threshold,post_raw=160,SUM_fader_gain=gain,SUM_fader_dB=float(20*np.log10(gain))),
            loss=float(np.mean([r['loss'] for r in captures])),realization_losses=[r['loss'] for r in captures],
            realization_standard_deviation=float(np.std([r['loss'] for r in captures])),
            original_reference_assessment=median['assessment'],native_status=median['status'],source_manifest=seed['source_manifest'],
            only_three_held_notes=True,actual_native_DLL_audio=True,not_supported_by_current95_exporter=True,
            original_reference_match_reached=False)
        with mutex:
            if save:rows.append(row)
            (ROOT/(label+'-result.json')).write_text(json.dumps(row,indent=2)+'\n')
            print('NATIVE_POSTCLIP_CASE',label,row['loss'],gain,flush=True)
        return row,median['audio']
    finally:pool.put(c)

with four_native_slots(ROOT) as state:
    seed=json.loads(Path(state['best_candidate']).read_text());x=np.array(seed['x']);assert len(x)==95
    (ROOT/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
    INPUT=Path(seed['source_manifest']['native_input'])
    try:
        for i in range(4):
            c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=True);clients.append(c);pool.put(c)
        control,audio=evaluate(('baseline',x,None),6,True,False)
        trials=[]
        for threshold in [127,120,111,105,100,95,90,80,70,64,48]:
            for preamp in [0.,3.,6.,9.,12.]:
                v=x.copy();v[28:30]+=preamp/2
                trials.append((f'clip-{threshold}-pre-{preamp:g}dB',v,threshold))
        with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,trials))
        chosen=min((r for r in rows if r.get('eligible')),key=lambda r:r['loss'])
        extension=chosen['post_clip_extension'];validated,final_audio=evaluate(('fresh-best',np.array(chosen['x']),extension['threshold_raw']),6,False,extension['enabled'])
        # Normalize setting is solved again with actual audio; record the real used gain.
        se=float(np.hypot(control['realization_standard_deviation'],validated['realization_standard_deviation'])/np.sqrt(6))
        robust=control['loss']-validated['loss']>max(.0005,3*se) and extension['enabled']
        validated.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
            full_fresh_native_realizations=6,full_fresh_native_validation_pending=False,not_automatically_accepted=True)
        sf.write(ROOT/'fresh-best-with-tail.wav',final_audio,48000,subtype='FLOAT')
        (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
        (ROOT/'full-validated-candidate.json').write_text(json.dumps(validated,indent=2)+'\n')
        (ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),eligible_cases=sum(r.get('eligible',False) for r in rows),
            seed_mean=control['loss'],fresh_mean_loss=validated['loss'],robust_improvement=bool(robust),
            seconds=time.monotonic()-start,only_three_held_notes=True,match_reached=False),indent=2)+'\n')
        print('ACTUAL_NATIVE_POSTCLIP_COMPLETE',validated['loss'],control['loss'],robust,flush=True)
    finally:
        for c in clients:c.close()
