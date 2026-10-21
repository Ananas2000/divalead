"""Repeated actual native Chorus trials, paired with a fresh six-capture control."""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time
import numpy as np
from scipy.stats import qmc
import soundfile as sf
from native_chain import NativeChain,W
from apply_native_candidate import apply
ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
prior=json.loads(Path(sys.argv[1]).read_text());seed=np.array(prior['x'],dtype=float);assert len(seed) in [94,95]
source_manifest=prior.get('source_manifest');INPUT=Path(source_manifest['native_input']) if source_manifest else W/'native-frozen-source-with-tail.wav'
phase_pair=len(seed)==95;engine='fl_native_common_phase_host.exe' if phase_pair else 'fl_native_chorus_verified_host.exe'
(ROOT/'seed.json').write_text(json.dumps(prior,indent=2)+'\n')
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];mutex=threading.Lock();rows=[];best=float('inf');calls=0;start=time.monotonic()
target_rms=float(np.sqrt(np.mean(target.astype(float)**2)))
def quantize(v):
    v=v.copy();v[93]=round(v[93]*12800)/12800
    if len(v)==95:v[94]=int(round(np.clip(v[94],0,4096)))
    for i,scale in zip(range(86,93),[1024,5000,1024,5000,5000,5000,5000]):v[i]=round(v[i]*scale)/scale
    return v
def evaluate(v,reps=3,normalize=True,save=True):
    global best,calls
    c=pool.get()
    try:
        fitted=quantize(v);apply(c,fitted)
        if normalize:
            raw,_=c.render();rms=float(np.sqrt(np.mean(raw[:len(target)].astype(float)**2)))
            fitted[28:30]=np.clip(fitted[28:30]+10*np.log10(target_rms/rms),-18,18);apply(c,fitted)
        captures=[]
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(fitted[:28]**2))*.00000025
            captures.append(dict(loss=loss,assessment=features.local.last,audio=y,status=status))
        values=[v['loss'] for v in captures];mean=float(np.mean(values));std=float(np.std(values));median=sorted(captures,key=lambda q:q['loss'])[len(captures)//2]
        row=dict(x=fitted.tolist(),loss=mean,realization_losses=values,realization_standard_deviation=std,recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],native_status=median['status'],peak=float(abs(median['audio']).max()),native_DLL_audio=True,only_three_held_notes=True,model_family='actual_native_Chorus_controls_plus_EQ',strict_waveform_match=False,original_reference_match_reached=False,full_fresh_native_realizations=reps,free_running_LFO_not_sample_exact=True,source_Diva_frozen_unchanged=not bool(source_manifest),source_manifest=source_manifest)
        with mutex:
            calls+=reps;rows.append(row)
            if save and mean<best:
                best=mean;(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',median['audio'],48000,subtype='FLOAT');print('CHORUS_CONTROLS_BEST',mean,std,calls,flush=True)
            (ROOT/'search-state.json').write_text(json.dumps(dict(calls=calls,cases=len(rows),loss=best,seconds=time.monotonic()-start),indent=2)+'\n')
        return row,median['audio']
    finally:pool.put(c)
trials=[]
# Native scales: time and depth linear; rate squared; cutoff in MIDI-note units.
for i,step in [(76,.2),(77,.4),(86,.05),(87,.12),(88,.125),(89,.08),(90,.08),(91,.08),(92,.08),(93,.025)]:
    for sign in [-1,1]:
        z=seed.copy();z[i]+=sign*step
        z[76:78]=np.clip(z[76:78],[-3.,-6.],[6.,12.]);z[86:93]=np.clip(z[86:93],0,1);z[93]=np.clip(z[93],.001,.45);trials.append(z)
for c3 in [0,.35,1.,2.,4.,6.]:
    for c5 in [0,.5,2.,4.,8.,12.]:
        z=seed.copy();z[76:78]=[c3,c5];trials.append(z)
for i in [79,81,83,85]:
    for value in [-4.,-2.,-.5,-.2,-.05,-.01,-.002,-.001,.001,.002,.01,.05,.2,.5,2.,4.]:
        z=seed.copy();z[i]=value;trials.append(z)
if phase_pair:
    for raw in [0,1,5,20,100,320,512,800,1200,1500,1700,1800,1900,2100,2400,2800,3400,4000]:
        z=seed.copy();z[94]=raw;trials.append(z)
lhs=qmc.LatinHypercube(d=8,seed=830000+int(os.environ.get('DIVALEAD_CHORUS_GENERATION','1'))).random(96)
for k,v in enumerate(lhs):
    z=seed.copy();z[86]=(2+16*v[0]-.05)/29.95;z[87]=(.5+4.5*v[1])/5;z[88]=v[2]
    rates=.2+4.7*v[3:6];z[89:92]=np.sqrt(rates/5)
    cutoff=500*(14000/500)**v[6];z[92]=(69+12*np.log2(cutoff/440))/127
    z[93]=.008*(.4/.008)**v[7]
    if k%2==0:
        # Local perturbations keep half the candidates near the proven family.
        z[86:93]=np.clip(.7*seed[86:93]+.3*z[86:93],0,1)
        z[93]=np.clip(.7*seed[93]+.3*z[93],.001,.45)
    trials.append(z)
try:
    for i in range(4):
        c=NativeChain(INPUT,f'{ROOT.name}-{i}',fl_graph=True,phase_pair=phase_pair,engine_override=engine);clients.append(c);pool.put(c)
    control,control_audio=evaluate(seed,6,False)
    with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,trials))
    candidate=np.array(json.loads((ROOT/'best.json').read_text())['x'])
    validated,audio=evaluate(candidate,6,False,False)
    uncertainty=float(np.hypot(control['realization_standard_deviation'],validated['realization_standard_deviation'])/np.sqrt(6))
    robust=control['loss']-validated['loss']>max(.0005,3*uncertainty)
    if not robust:validated,audio=control,control_audio
    validated.update(robust_improvement=robust,seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=uncertainty,full_fresh_native_validation_pending=False,full_fresh_native_realizations=6)
    (ROOT/'full-validated-candidate.json').write_text(json.dumps(validated,indent=2)+'\n');sf.write(ROOT/'best-validated-with-tail.wav',audio,48000,subtype='FLOAT')
    (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),scored_actual_renders=calls,seconds=time.monotonic()-start,initial_control_mean=control['loss'],fresh_mean_loss=validated['loss'],robust_improvement=robust,match_reached=False),indent=2)+'\n')
    print('ACTUAL_CHORUS_CONTROLS_VALIDATED',validated['loss'],robust,flush=True)
finally:
    for c in clients:c.close()
