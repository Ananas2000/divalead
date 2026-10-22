"""Finite trial of actual FL EQ2/SS cross branches, never a public 95-vector.

The additional routing is ordinary parallel FL mixer routing. All sound
processing is supplied native DLL code. Three real prefix captures are used
only for training/held-out evaluation; validation renders the whole graph.
"""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,os,queue,sys,threading,time
import numpy as np
import soundfile as sf
from scipy.optimize import minimize
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply

ROOT=W/'native-cross-MS-branches-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
N=Path('/workspace/divalead-work/native-low-latency-effects')
features=FeaturesOriginal(target);start=time.monotonic()
cross_freq=np.array([100,250,630,1600,4000,8000,16000],float)
cross_raw=np.rint(np.log(cross_freq/20)/np.log(1000)*65536).astype(int)
pool=queue.Queue();clients=[];mutex=threading.Lock();calls=0;best=float('inf');history=[]

def native_amp(value):
    return int(round(np.sign(value)*12800*np.log(1+2*abs(value))/np.log(3)))

def cross_settings(c,v):
    """95 unchanged-family fields, 14 cross EQ gains and two branch gains."""
    assert len(v)==111
    for offset,node in [(95,15),(102,16)]:
        for band in range(7):
            c.set(node,band,int(round(v[offset+band]*100)))
            c.set(node,7+band,int(cross_raw[band]));c.set(node,14+band,9830)
            c.set(node,21+band,6);c.set(node,28+band,0)
        c.set(node,35,0)
    for node,k,sign in [(17,v[109],-1),(18,v[110],1)]:
        raw=native_amp(k)
        for j,value in enumerate([0,raw,sign*raw,0,0,0]):c.set(node,j,value)
    c.gain(5,1);c.gain(6,1)

def settings(c,v,training=False,phase=0):
    if training:
        c.load_input(ROOT/f'actual-prefix-{phase}.wav');apply(c,v[:86])
        for node in [0,3,13,14]:c.bypass(node,True)
        c.gain(0,1);c.gain(1,0)
    else:
        c.load_input(INPUT);apply(c,v[:95])
        for node in [13,14]:c.bypass(node,False)
    cross_settings(c,v)

def score(y,v):
    r=features.residual(y[:len(target)])
    return float(r@r)+float(np.sum(v[:28]**2))*.00000025

def evaluate(v,save=True):
    global best,calls
    c=pool.get()
    try:
        settings(c,v,True);y,status=c.render();loss=score(y,v)
        with mutex:
            calls+=1
            if save and loss<best:
                best=loss
                row=dict(x=v.tolist(),loss=loss,calls=calls,seconds=time.monotonic()-start,
                         native_status=status,original_reference_assessment=features.local.last,
                         model_family='EXPERIMENTAL_native_cross_MS_111',source_manifest=source_manifest,
                         cross_EQ_frequencies_Hz=cross_freq.tolist(),cross_EQ_bandwidth_raw=9830,
                         only_three_held_notes=True,actual_native_DLL_audio=True,
                         training_prefix_not_a_playback_effect=True,not_supported_as_public_95_vector=True,
                         full_fresh_native_validation_pending=True,original_reference_match_reached=False)
                history.append(row);(ROOT/'best-training.json').write_text(json.dumps(row,indent=2)+'\n')
                sf.write(ROOT/'best-training-with-tail.wav',y,48000,subtype='FLOAT')
                print('CROSS_MS_BEST',loss,calls,round(time.monotonic()-start,1),flush=True)
        return loss
    finally:pool.put(c)

with four_native_slots(ROOT) as state:
    prior=json.loads(Path(state['best_candidate']).read_text());base=np.array(prior['x']);assert len(base)==95
    source_manifest=prior['source_manifest'];INPUT=Path(source_manifest['native_input'])
    control=np.r_[base,np.zeros(16)];seed=control.copy();seed[109:111]=[.04,.04]
    (ROOT/'seed.json').write_text(json.dumps(prior,indent=2)+'\n')
    # Structural identity: zero cross branches must reproduce the old graph.
    old=NativeChain(INPUT,ROOT.name+'-old-control',fl_graph=True,phase_pair=True)
    new=NativeChain(INPUT,ROOT.name+'-new-control',fl_graph=True,phase_pair=True,cross_ms=True)
    try:
        old_zero=base.copy();old_zero[87]=0;new_zero=control.copy();new_zero[87]=0
        apply(old,old_zero);a,status_old=old.render();settings(new,new_zero);b,status_new=new.render()
        error=float(abs(a-b).max());assert error<=2e-7,error
        positive=new_zero.copy();positive[109:111]=[.15,-.1]
        settings(new,positive);p,_=new.render();positive_delta=float(abs(p-b).max());assert positive_delta>1e-4
        proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   actual_old_and_new_native_graphs=True,zero_Chorus_depth=True,
                   zero_cross_max_error=error,nonzero_cross_positive_control_max_delta=positive_delta,
                   old_native_status=status_old,new_native_status=status_new,
                   source_audio_SHA256=hashlib.sha256(Path(source_manifest['source_audio']).read_bytes()).hexdigest(),
                   three_held_MIDI_unchanged=True,old_public_family_unchanged=True,match_reached=False)
        (ROOT/'STRUCTURAL_NATIVE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
        apply(old,base)
        for node in [4,5,6,7,8,10,11,12]:old.bypass(node,True)
        old.gain(3,1);old.gain(4,0)
        for phase in range(3):
            y,_=old.render();sf.write(ROOT/f'actual-prefix-{phase}.wav',y,48000,subtype='FLOAT')
    finally:
        old.close();new.close()
    try:
        for i in range(4):
            c=NativeChain(INPUT,f'{ROOT.name}-fit-{i}',fl_graph=True,phase_pair=True,cross_ms=True)
            clients.append(c);pool.put(c)
        initial=evaluate(control);evaluate(seed)
        active=np.r_[np.arange(28,34),np.arange(95,111)]
        scale=np.r_[[.2,.2],np.full(4,.025),np.full(14,.6),[.025,.025]]
        origin=seed.copy();lower=np.r_[[-18.,-18.],np.full(4,-1.),np.full(14,-18.),[-.6,-.6]]
        upper=np.r_[[18.,18.],np.full(4,1.),np.full(14,18.),[.6,.6]]
        lo=(lower-origin[active])/scale;hi=(upper-origin[active])/scale
        budget=int(os.environ.get('DIVALEAD_CROSS_MAXCALLS','3000'));iteration=0
        class BudgetReached(Exception):pass
        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            def vector(z):
                v=origin.copy();v[active]=origin[active]+np.asarray(z)*scale;return v
            def objective_gradient(z):
                if calls>=budget:raise BudgetReached()
                value=evaluate(vector(z));trials=[];deltas=[]
                for k in range(len(active)):
                    left=np.array(z);right=np.array(z);left[k]=max(lo[k],left[k]-.25);right[k]=min(hi[k],right[k]+.25)
                    trials.extend([vector(left),vector(right)]);deltas.append(right[k]-left[k])
                values=list(executor.map(evaluate,trials))
                gradient=np.array([(values[2*k+1]-values[2*k])/max(deltas[k],1e-12) for k in range(len(active))])
                return value,gradient
            def callback(z):
                global iteration
                iteration+=1;row=dict(iteration=iteration,calls=calls,best_training_loss=best,seconds=time.monotonic()-start)
                (ROOT/'search-state.json').write_text(json.dumps(row,indent=2)+'\n');print('CROSS_MS_ITERATION',row,flush=True)
            try:
                fit=minimize(objective_gradient,np.zeros(len(active)),jac=True,method='L-BFGS-B',bounds=list(zip(lo,hi)),callback=callback,
                             options=dict(maxiter=40,maxls=8,ftol=1e-10,gtol=1e-6))
                summary=dict(success=bool(fit.success),message=str(fit.message),iterations=int(fit.nit))
            except BudgetReached:summary=dict(success=False,message='Finite actual-DLL render budget reached',iterations=iteration)
        bestrow=json.loads((ROOT/'best-training.json').read_text());chosen=np.array(bestrow['x']);heldout=[]
        c=clients[0]
        for phase in [1,2]:
            settings(c,chosen,True,phase);y,status=c.render();heldout.append(dict(phase=phase,loss=score(y,chosen),assessment=features.local.last))
    finally:
        for c in clients:c.close()
    full=NativeChain(INPUT,ROOT.name+'-full',fl_graph=True,phase_pair=True,cross_ms=True)
    control_losses=[];captures=[]
    try:
        settings(full,control)
        for rep in range(6):
            y,status=full.render();control_losses.append(score(y,control))
        settings(full,chosen)
        for rep in range(6):
            y,status=full.render();loss=score(y,chosen);p=ROOT/f'full-fresh-realization-{rep}.wav';sf.write(p,y,48000,subtype='FLOAT')
            captures.append(dict(loss=loss,audio=str(p),assessment=features.local.last,native_status=status))
    finally:full.close()
    captures.sort(key=lambda row:row['loss']);median=captures[3]
    mean=float(np.mean([c['loss'] for c in captures]));std=float(np.std([c['loss'] for c in captures]))
    control_mean=float(np.mean(control_losses));se=float(np.hypot(np.std(control_losses),std)/np.sqrt(6))
    robust=control_mean-mean>max(.0005,3*se)
    result=dict(bestrow,loss=mean,training_loss=bestrow['loss'],realization_losses=[c['loss'] for c in captures],
                realization_standard_deviation=std,seed_fresh_mean_loss=control_mean,seed_realization_losses=control_losses,
                fresh_mean_standard_error=se,robust_improvement=robust,full_fresh_native_realizations=6,
                recorded_audio=median['audio'],recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],
                heldout_prefix_validation=heldout,full_fresh_native_validation_pending=False,optimizer=summary)
    (ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'completion.json').write_text(json.dumps(dict(initial_training_loss=initial,fresh_mean_loss=mean,
        seed_fresh_mean_loss=control_mean,robust_improvement=robust,actual_scored_renders=calls,
        seconds=time.monotonic()-start,native_effect_PDC_frames=0,match_reached=False),indent=2)+'\n')
    print('CROSS_MS_ACTUAL_NATIVE_COMPLETE',mean,control_mean,robust,flush=True)
