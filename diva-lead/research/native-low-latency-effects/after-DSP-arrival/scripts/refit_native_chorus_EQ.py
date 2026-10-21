"""Refit native EQ against one frozen REAL Chorus realization; hold out two.

Frozen prefix files are training fixtures only. Final validation renders the
complete native WS+Chorus+EQ graph again from the actual Diva source.
No reference samples are ever passed through the effects.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(W/'chorus-EQ-refit-isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target

ROOT=W/'native-chorus-EQ-refit';ROOT.mkdir(exist_ok=False)
prior=json.loads((W/'native-lowwet-chorus-grid/best.json').read_text())
x=np.r_[prior['x'],[prior['chorus_raw_parameters'][str(p)]/scale for p,scale in [(0,1024),(1,5000),(2,1024),(3,5000),(4,5000),(5,5000),(10,5000)]],prior['chorus']['mix']]
assert len(x)==94
(ROOT/'seed.json').write_text(json.dumps(dict(prior,x=x.tolist(),model_family='native_Chorus_8percent_plus_EQ'),indent=2)+'\n')
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];mutex=threading.Lock();rows=[];best=float('inf');calls=0;start=time.monotonic()
steps=np.r_[np.full(28,.4),[.2,.2],np.full(4,.025),np.full(28,.007),np.full(14,.007),[.03,.03,.02,.1],[.012,.1]*3]
lower=np.r_[np.full(30,-18.),np.full(4,-1.),np.full(28,-.9),np.full(14,.005),[-.6,-.35,-2.,-4.],[-1.5,-4.]*3]
upper=np.r_[np.full(30,18.),np.full(4,1.),np.full(28,.9),np.full(14,.85),[.35,.5,2.,4.],[1.5,4.]*3]
indices=[i for i in range(86) if i not in [76,77]]
def eq_only(c,v,phase=0):
    c.load_input(ROOT/f'actual-WS-Chorus-prefix-{phase}.wav');apply(c,v[:86])
    c.bypass(0,True);c.bypass(3,True);c.gain(0,1);c.gain(1,0)
def evaluate(v,save=True):
    global best,calls
    c=pool.get()
    try:
        eq_only(c,v);y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
        with mutex:
            calls+=1
            if save and loss<best:
                best=loss;row=dict(x=v.tolist(),loss=loss,calls=calls,seconds=time.monotonic()-start,model_family='native_Chorus_small_mix_plus_EQ',native_status=status,original_reference_assessment=features.local.last,only_three_held_notes=True,actual_native_DLL_EQ_audio=True,training_prefix_is_actual_WS_Chorus_output=True,training_prefix_not_a_deployable_playback_effect=True,full_fresh_native_validation_pending=True,strict_waveform_match=False,original_reference_match_reached=False)
                rows.append(row);(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-training-with-tail.wav',y,48000,subtype='FLOAT');print('CHORUS_EQ_REFIT_BEST',loss,calls,round(time.monotonic()-start,1),flush=True)
        return loss
    finally:pool.put(c)

with four_native_slots(ROOT):
    prefix=NativeChain(W/'native-frozen-source-with-tail.wav','chorus-EQ-prefix-generator',fl_graph=True)
    try:
        apply(prefix,x)
        for n in [4,5,6,7,8,10,11,12]:prefix.bypass(n,True)
        prefix.gain(3,1);prefix.gain(4,0)
        for phase in range(3):
            y,status=prefix.render();sf.write(ROOT/f'actual-WS-Chorus-prefix-{phase}.wav',y,48000,subtype='FLOAT')
    finally:prefix.close()
    try:
        for i in range(4):
            c=NativeChain(ROOT/'actual-WS-Chorus-prefix-0.wav',f'chorus-EQ-refit-{i}',fl_graph=True,engine_override='fl_native_source_variants_host.exe');clients.append(c);pool.put(c)
        current=evaluate(x);initial=current
        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            for sweep in range(8):
                trials=[];which=[]
                for i in indices:
                    for sign in [-1,1]:
                        z=x.copy();z[i]=np.clip(z[i]+sign*steps[i],lower[i],upper[i]);trials.append(z);which.append(i)
                losses=list(executor.map(evaluate,trials));good=[int(j) for j in np.argsort(losses) if losses[j]<current-1e-7]
                if good:
                    z=x.copy();used=set()
                    for j in good[:16]:
                        i=which[j]
                        if i not in used:z[i]=trials[j][i];used.add(i)
                    joint=evaluate(z);j=good[0]
                    if joint<losses[j]:x=z;current=joint
                    else:x=trials[j];current=losses[j]
                else:steps*=.6
                (ROOT/'search-state.json').write_text(json.dumps(dict(sweep=sweep,loss=current,calls=calls,seconds=time.monotonic()-start),indent=2)+'\n');print('REFIT_SWEEP',sweep,current,flush=True)
        bestrow=json.loads((ROOT/'best.json').read_text());chosen=np.array(bestrow['x']);heldout=[]
        c=clients[0]
        for phase in [1,2]:
            eq_only(c,chosen,phase);y,status=c.render();r=features.residual(y[:len(target)]);heldout.append(dict(phase=phase,loss=float(r@r)+float(np.sum(chosen[:28]**2))*.00000025,assessment=features.local.last,native_status=status))
        (ROOT/'heldout-prefix-validation.json').write_text(json.dumps(heldout,indent=2)+'\n')
    finally:
        for c in clients:c.close()
full=NativeChain(W/'native-frozen-source-with-tail.wav','chorus-EQ-full-fresh-check',fl_graph=True)
fresh=[]
try:
    apply(full,chosen)
    for rep in range(6):
        y,status=full.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(chosen[:28]**2))*.00000025
        path=ROOT/f'full-fresh-realization-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT');fresh.append(dict(loss=loss,assessment=features.local.last,audio=str(path),native_status=status))
finally:full.close()
fresh.sort(key=lambda v:v['loss']);median=fresh[len(fresh)//2]
result=dict(bestrow,training_loss=bestrow['loss'],loss=float(np.mean([r['loss'] for r in fresh])),realization_losses=[r['loss'] for r in fresh],realization_standard_deviation=float(np.std([r['loss'] for r in fresh])),original_reference_assessment=median['assessment'],recorded_audio=median['audio'],recorded_render_loss=median['loss'],full_fresh_native_validation_pending=False,full_fresh_native_realizations=6,heldout_prefix_validation=heldout,source_Diva_frozen_unchanged=True,three_incoming_held_notes=True)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',sf.read(median['audio'],dtype='float32')[0],48000,subtype='FLOAT')
(ROOT/'completion.json').write_text(json.dumps(dict(initial_training_loss=initial,final_training_loss=bestrow['loss'],fresh_mean_loss=result['loss'],fresh_standard_deviation=result['realization_standard_deviation'],calls=calls,seconds=time.monotonic()-start,full_actual_native_graph_validated=True,match_reached=False),indent=2)+'\n')
print('NATIVE_CHORUS_EQ_REFIT_FULL_CHECK_COMPLETE',result['loss'],flush=True)
