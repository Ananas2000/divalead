"""Actual native Chorus LFO shapes in calibrated units and corrected host context.

This is a new physical hypothesis: the earlier phase screen varied StereoShaper
and slot mix, not these LFO shape controls. Every result remains pending FL GUI.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625');ROOT=BASE/'Chorus-shapes-correct-context-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
sys.path.insert(0,'/tmp/divalead-native-effects');from native_chain import NativeChain
from apply_native_candidate import apply
prior=json.loads((BASE/'fl20-EQ76-full-01/full-validated-candidate.json').read_text());x=np.array(prior['x']);INPUT=Path(prior['source_manifest']['native_input'])
features=FeaturesOriginal();pool=queue.Queue();clients=[];rows=[];mutex=threading.Lock();start=time.monotonic()
def evaluate(case,reps=3,save=True):
    label,changes=case;c=pool.get()
    try:
        v=x.copy();apply(c,v)
        for index,value in changes.items():c.set(3,index,value)
        for index,value in changes.items():assert c.value_hint(3,index)==value
        # Match levels using real EQ Main controls for BOTH variants and control.
        y,_=c.render();features.residual(y[:288000]);gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
        v[28:30]=np.clip(v[28:30]+10*np.log10(gain),-18,18);apply(c,v)
        for index,value in changes.items():c.set(3,index,value)
        captures=[]
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
            captures.append(dict(loss=loss,assessment=features.local.last,audio=y,native_status=status))
        ordered=sorted(captures,key=lambda r:r['loss']);median=ordered[len(ordered)//2];values=[r['loss']for r in captures]
        row=dict(label=label,x=v.tolist(),chorus_overrides={str(k):value for k,value in changes.items()},loss=float(np.mean(values)),realization_losses=values,realization_standard_deviation=float(np.std(values)),original_reference_assessment=median['assessment'],native_status=median['native_status'],source_manifest=prior['source_manifest'],host_context='Chorus_excluded_from_silent_warmup',model_family='FL20_corrected_context_three_held_EQ76_Chorus_shapes',objective_version='local_full_original_criteria_FL20_context_v1',all_requested_native_values_read_back=True,level_normalization_in_actual_EQ_Main_controls=True,normalization_applied_to_control_too=True,actual_native_DLL_audio=True,actual_FL_validation_pending=True,only_three_held_notes=True,reference_match_reached=False)
        with mutex:
            if save:rows.append(row)
            print('COLD_CHORUS_SHAPES',label,row['loss'],median['assessment']['tone_score'],median['assessment']['standard_score'],flush=True)
        return row,median['audio']
    finally:pool.put(c)
trials=[(f'shapes-{a}-{b}-{c}',{6:a,7:b,8:c})for a in [0,256,512,768,1024]for b in [0,256,512,768,1024]for c in [0,256,512,768,1024]if(a,b,c)!=(0,0,0)]
for cross in [0,100]:
    for hz in [500,900,1500,2400,4000,6300,10000]:
        raw=round(5000*(69+12*np.log2(hz/440))/127);trials.append((f'cross-{cross}-Hz{hz}',{9:cross,10:raw}))
for hz in [1.6,3.2]:
    raw=round(5000*np.sqrt(hz/5));trials.append((f'equal-LFO-{hz:g}',{3:raw,4:raw,5:raw}))
try:
    for i in range(4):
        c=NativeChain(INPUT,f'cold-Chorus-shapes-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');clients.append(c);pool.put(c)
    control,_=evaluate(('normalized-baseline',{}),6)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:list(executor.map(evaluate,trials))
    best=min(rows,key=lambda r:r['loss']);selected={int(k):v for k,v in best['chorus_overrides'].items()};validated,y=evaluate(('fresh-selected',selected),6,False)
    control2,_=evaluate(('fresh-control',{}),6,False)
    se=float(np.hypot(control2['realization_standard_deviation'],validated['realization_standard_deviation'])/np.sqrt(6));robust=control2['loss']-validated['loss']>max(.0005,3*se)
    validated.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control2['loss'],fresh_mean_standard_error=se,full_fresh_native_realizations=6,full_fresh_native_validation_pending=False,heldout_actual_FL_render_pending=True,recorded_audio=str(ROOT/'selected-with-tail.wav'))
    sf.write(ROOT/'selected-with-tail.wav',y,48000,subtype='FLOAT');(ROOT/'full-validated-candidate.json').write_text(json.dumps(validated,indent=2)+'\n');(ROOT/'RESULTS.json').write_text(json.dumps(sorted(rows,key=lambda r:r['loss']),indent=2)+'\n');(ROOT/'FRESH_CONTROL.json').write_text(json.dumps(control2,indent=2)+'\n');(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),fresh_loss=validated['loss'],fresh_control_loss=control2['loss'],robust_improvement=bool(robust),seconds=time.monotonic()-start,reference_match_reached=False),indent=2)+'\n');print('COLD_CHORUS_SHAPES_VALIDATED',validated['loss'],robust,flush=True)
finally:
    for c in clients:c.close()
