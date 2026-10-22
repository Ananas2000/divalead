"""Refit native EQ against one frozen REAL Chorus realization; hold out two.

All 76 EQ gain, matrix, frequency and bandwidth coordinates are fitted jointly.
Frozen prefix files are training fixtures only. Final validation renders the
complete native WS+Chorus+EQ graph again from the actual Diva source.
No reference samples are ever passed through the effects.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time,sys,contextlib,signal
from scipy.optimize import minimize
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from fl20_objective import FeaturesOriginal
from native_features import target

prior=json.loads(Path(sys.argv[1]).read_text());x=np.array(prior['x'],dtype=float)
overrides={int(k):int(v) for k,v in prior.get('chorus_overrides',{}).items()}
source_manifest=prior.get('source_manifest');INPUT=Path(source_manifest['native_input']) if source_manifest else W/'native-frozen-source-with-tail.wav'
phase_pair=len(x)==95
engine='fl_native_fl20_host.exe';assert phase_pair
assert len(x) in [94,95]
(ROOT/'seed.json').write_text(json.dumps(dict(prior,x=x.tolist(),model_family='FL20_corrected_context_three_held_EQ76'),indent=2)+'\n')
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];mutex=threading.Lock();rows=[];best=float('inf');calls=0;start=time.monotonic()
steps=np.r_[np.full(28,.4),[.2,.2],np.full(4,.025),np.full(28,.007),np.full(14,.007),[.03,.03,.02,.1],[.012,.1]*3]
lower=np.r_[np.full(30,-18.),np.full(4,-1.),np.full(28,-.9),np.full(14,.005),[-.6,-.35,-2.,-4.],[-1.5,-4.]*3]
upper=np.r_[np.full(30,18.),np.full(4,1.),np.full(28,.9),np.full(14,.85),[.35,.5,2.,4.],[1.5,4.]*3]
indices=[i for i in range(86) if i not in [76,77]]
def apply_full(c,v):
    apply(c,v)
    for index,value in overrides.items():
        c.set(3,index,value)
        actual=c.value_hint(3,index)
        assert int(actual)==value, (index,value,actual)
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
                best=loss;row=dict(x=v.tolist(),loss=loss,calls=calls,seconds=time.monotonic()-start,model_family='FL20_corrected_context_three_held_EQ76',objective_version='local_full_original_criteria_FL20_context_v1',actual_FL_validation_pending=True,native_status=status,original_reference_assessment=features.local.last,only_three_held_notes=True,actual_native_DLL_EQ_audio=True,training_prefix_is_actual_WS_Chorus_output=True,training_prefix_not_a_deployable_playback_effect=True,full_fresh_native_validation_pending=True,strict_waveform_match=False,original_reference_match_reached=False)
                rows.append(row);(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-training-with-tail.wav',y,48000,subtype='FLOAT');print('CHORUS_EQ_REFIT_BEST',loss,calls,round(time.monotonic()-start,1),flush=True)
        return loss
    finally:pool.put(c)

with contextlib.nullcontext():
    prefix=NativeChain(INPUT,ROOT.name+'-prefix',fl_graph=True,phase_pair=phase_pair,engine_override=engine)
    try:
        apply_full(prefix,x)
        for n in [4,5,6,7,8,10,11,12]:prefix.bypass(n,True)
        prefix.gain(3,1);prefix.gain(4,0)
        for phase in range(3):
            y,status=prefix.render();sf.write(ROOT/f'actual-WS-Chorus-prefix-{phase}.wav',y,48000,subtype='FLOAT')
    finally:prefix.close()
    try:
        for i in range(4):
            c=NativeChain(ROOT/'actual-WS-Chorus-prefix-0.wav',f'{ROOT.name}-EQ-{i}',fl_graph=True,engine_override='fl_native_source_variants_host.exe');clients.append(c);pool.put(c)
        current=evaluate(x);initial=current
        active=np.arange(76);scale=steps[active].copy();origin=x.copy();budget=int(os.environ.get('DIVALEAD_LBFGS_MAXCALLS','5000'))
        lo=(lower[active]-origin[active])/scale;hi=(upper[active]-origin[active])/scale
        class BudgetReached(Exception):pass
        iteration=0
        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            def full_vector(z):
                v=origin.copy();v[active]=origin[active]+np.asarray(z)*scale;return v
            def objective_gradient(z):
                if calls>=budget:raise BudgetReached()
                value=evaluate(full_vector(z));trials=[];deltas=[]
                for k in range(len(active)):
                    left=np.array(z);right=np.array(z);left[k]=max(lo[k],left[k]-.25);right[k]=min(hi[k],right[k]+.25)
                    trials.extend([full_vector(left),full_vector(right)]);deltas.append(right[k]-left[k])
                values=list(executor.map(evaluate,trials));gradient=np.array([(values[2*k+1]-values[2*k])/max(deltas[k],1e-12) for k in range(len(active))])
                return value,gradient
            def callback(z):
                global iteration
                iteration+=1
                row=dict(iteration=iteration,calls=calls,best_training_loss=best,seconds=time.monotonic()-start,method='Actual native-DLL joint gain/frequency/bandwidth L-BFGS-B, 76 coordinates',match_reached=False)
                (ROOT/'search-state.json').write_text(json.dumps(row,indent=2)+'\n');print('NATIVE_QUASI_NEWTON',row,flush=True)
            try:
                fit=minimize(objective_gradient,np.zeros(len(active)),jac=True,method='L-BFGS-B',bounds=list(zip(lo,hi)),callback=callback,options=dict(maxiter=int(os.environ.get('DIVALEAD_LBFGS_MAXITER','40')),maxls=8,ftol=1e-10,gtol=1e-6))
                fit_summary=dict(success=bool(fit.success),message=str(fit.message),iterations=int(fit.nit),value=float(fit.fun))
            except BudgetReached:fit_summary=dict(success=False,message='Finite actual-render evaluation budget reached; keep best proved training vector',iterations=iteration)
            (ROOT/'optimizer-result.json').write_text(json.dumps(dict(fit_summary,actual_native_renders=calls,not_a_modelled_audio_fit=True),indent=2)+'\n')
        bestrow=json.loads((ROOT/'best.json').read_text());chosen=np.array(bestrow['x']);heldout=[]
        c=clients[0]
        for phase in [1,2]:
            eq_only(c,chosen,phase);y,status=c.render();r=features.residual(y[:len(target)]);heldout.append(dict(phase=phase,loss=float(r@r)+float(np.sum(chosen[:28]**2))*.00000025,assessment=features.local.last,native_status=status))
        (ROOT/'heldout-prefix-validation.json').write_text(json.dumps(heldout,indent=2)+'\n')
    finally:
        for c in clients:c.close()
full=NativeChain(INPUT,ROOT.name+'-full-fresh',fl_graph=True,phase_pair=phase_pair,engine_override=engine)
fresh=[];control=[]
try:
    apply_full(full,np.array(prior['x']))
    for rep in range(6):
        y,status=full.render();r=features.residual(y[:len(target)]);control.append(float(r@r)+float(np.sum(np.array(prior['x'])[:28]**2))*.00000025)
    apply_full(full,chosen)
    for rep in range(6):
        y,status=full.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(chosen[:28]**2))*.00000025
        path=ROOT/f'full-fresh-realization-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT');fresh.append(dict(loss=loss,assessment=features.local.last,audio=str(path),native_status=status))
finally:full.close()
fresh.sort(key=lambda v:v['loss']);median=fresh[len(fresh)//2]
control_mean=float(np.mean(control));new_mean=float(np.mean([r['loss'] for r in fresh]));uncertainty=float(np.hypot(np.std(control),np.std([r['loss'] for r in fresh]))/np.sqrt(6))
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(seed_realization_losses=control,seed_mean=control_mean,new_mean=new_mean,standard_error_of_mean_difference=uncertainty,improvement_exceeds_three_standard_errors=control_mean-new_mean>max(.0005,3*uncertainty)),indent=2)+'\n')
result=dict(bestrow,chorus_overrides={str(k):v for k,v in overrides.items()},host_context='Chorus_excluded_from_silent_warmup',training_loss=bestrow['loss'],loss=float(np.mean([r['loss'] for r in fresh])),realization_losses=[r['loss'] for r in fresh],realization_standard_deviation=float(np.std([r['loss'] for r in fresh])),original_reference_assessment=median['assessment'],recorded_audio=median['audio'],recorded_render_loss=median['loss'],full_fresh_native_validation_pending=False,full_fresh_native_realizations=6,heldout_prefix_validation=heldout,source_Diva_frozen_unchanged=not bool(source_manifest),source_manifest=source_manifest,three_incoming_held_notes=True,seed_fresh_mean_loss=control_mean,robust_improvement=control_mean-new_mean>max(.0005,3*uncertainty),fresh_mean_standard_error=uncertainty)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',sf.read(median['audio'],dtype='float32')[0],48000,subtype='FLOAT')
(ROOT/'completion.json').write_text(json.dumps(dict(initial_training_loss=initial,final_training_loss=bestrow['loss'],fresh_mean_loss=result['loss'],fresh_standard_deviation=result['realization_standard_deviation'],calls=calls,seconds=time.monotonic()-start,full_actual_native_graph_validated=True,match_reached=False),indent=2)+'\n')
print('NATIVE_CHORUS_EQ_REFIT_FULL_CHECK_COMPLETE',result['loss'],flush=True)
