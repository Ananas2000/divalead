"""Research capacity: two common native EQ2s AFTER Chorus/common phase.

Uses the existing spare EQ nodes1/2 in a separately compiled graph. A bypassed-EQ
control must reproduce the supported15-node graph. Metadata source_post_EQ
is NOT understood by the ordinary x95 exporter. No candidate is auto-deployed.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time
import numpy as np
import soundfile as sf
from scipy.optimize import minimize
from native_chain import NativeChain
from apply_native_candidate import apply,FREQS
ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
prior=json.loads(Path(sys.argv[1]).read_text());x=np.array(prior['x']);assert len(x)==95
overrides={int(k):int(v)for k,v in prior.get('chorus_overrides',{}).items()}
assert not prior.get('source_post_EQ'),'Separate integration is required before stacking extensions'
INPUT=Path(prior['source_manifest']['native_input']);features=FeaturesOriginal();pool=queue.Queue();clients=[]
start=time.monotonic();mutex=threading.Lock();best=float('inf');calls=0
engine='fl_native_fl20_postEQ_host.exe'
initial=np.r_[np.zeros(14),np.zeros(14),np.full(14,.15)]
steps=np.r_[np.full(14,.4),np.full(14,.02),np.full(14,.015)]
lower=np.r_[np.full(14,-12.),np.full(14,-.9),np.full(14,.008)]
upper=np.r_[np.full(14,12.),np.full(14,.9),np.full(14,.6)]
def base(c):
    apply(c,x)
    for i,v in overrides.items():c.set(3,i,v)
def extra(c,z):
    for n,off in [(1,0),(2,7)]:
        c.bypass(n,False)
        f=FREQS[off:off+7]*2**z[14+off:14+off+7]
        raw=np.rint(np.log(np.clip(f,20,20000)/20)/np.log(1000)*65536).astype(int)
        for b in range(7):
            c.set(n,b,round(z[off+b]*100));c.set(n,7+b,int(raw[b]))
            c.set(n,14+b,round(z[28+off+b]*65536));c.set(n,21+b,6);c.set(n,28+b,0)
        c.set(n,35,0)
def configured(c,z,phase=None):
    base(c)
    if z is not None:extra(c,z)
    if phase is not None:
        c.load_input(ROOT/f'actual-prefix-{phase}.wav');c.bypass(0,True);c.bypass(3,True)
        c.bypass(13,True);c.bypass(14,True);c.gain(0,1);c.gain(1,0)
def assess(y):
    r=features.residual(y[:288000]);return float(r@r)+float(np.sum(x[:28]**2))*.00000025
def evaluate(z):
    global best,calls
    c=pool.get()
    try:
        configured(c,z,0);y,status=c.render();loss=assess(y)
        with mutex:
            calls+=1
            if loss<best:
                best=loss;row=dict(source_post_EQ=z.tolist(),training_loss=loss,calls=calls,
                    assessment=features.local.last,native_status=status,actual_FL_validation_pending=True,match_reached=False)
                (ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n')
                print('COMMON_POST_EQ_BEST',loss,calls,flush=True)
        return loss
    finally:pool.put(c)

# True neutral control is BYPASS. EQ2 may have a non-identity flat response.
control_audio=[];flat_audio=[]
for executable in ['fl_native_fl20_host.exe',engine]:
    c=NativeChain(INPUT,ROOT.name+'-control-'+executable,fl_graph=True,phase_pair=True,engine_override=executable)
    try:
        base(c);c.set(3,1,0);y,status=c.render();control_audio.append(y)
        extra(c,initial);flat,_=c.render();flat_audio.append(flat)
        if executable==engine:
            z=initial.copy();z[3]=3.;extra(c,z);positive,_=c.render()
    finally:c.close()
error=float(abs(control_audio[0]-control_audio[1]).max());assert error<=2e-7,error
# Old placement before zero-depth Chorus vs new placement after it: native
# common linear EQ response must commute within floating-point tolerance.
flat_delta=(flat_audio[0]-flat_audio[1]).astype(float)
flat_placement_error=float(abs(flat_delta).max());flat_placement_rms=float(np.sqrt(np.mean(flat_delta**2)))
# Independently observed baseline block-size variation bounds, measured before
# this extension. The exact bypass check above is still required separately.
block_proof=json.loads((Path('/tmp/divalead-local-1625')/'FL20_NATIVE_06_WIP/verification/NATIVE_LATENCY_AND_BLOCKS.json').read_text())
known_peak=max(r['max_error_from_block128']for r in block_proof['block_size_cases'])
known_rms=max(r['null_RMS']for r in block_proof['block_size_cases'])
assert flat_placement_error<=2*known_peak and flat_placement_rms<=2*known_rms,(flat_placement_error,flat_placement_rms)
for k,(neutral,flat)in enumerate(zip(control_audio,flat_audio)):
    sf.write(ROOT/f'graph-bypass-control-{k}.wav',neutral,48000,subtype='FLOAT')
    sf.write(ROOT/f'graph-flat-control-{k}.wav',flat,48000,subtype='FLOAT')
flat_change=float(abs(flat_audio[1]-control_audio[1]).max())
positive_error=float(abs(positive-flat_audio[1]).max());assert positive_error>1e-4
(ROOT/'GRAPH_CONTROL_PROOF.json').write_text(json.dumps(dict(bypass_extra_EQ_max_abs_error=error,
    flat_EQ_old_new_placement_max_abs_error=flat_placement_error,flat_EQ_old_new_placement_RMS_error=flat_placement_rms,
    flat_comparison_tolerance_source='Twice independently measured native baseline block-size variation; no exact commutation claim',
    known_baseline_block_peak=known_peak,known_baseline_block_RMS=known_rms,
    actual_native_EQ2_flat_response_is_not_identity=True,flat_EQ_vs_bypass_max_abs_difference=flat_change,
    nonzero_gain_extra_EQ_max_abs_difference=positive_error,actual_native_DLL_controls=True,
    ordinary_graph_preserved=True,no_hidden_time_or_gain_correction=True,
    new_family_is_research_only=True,actual_FL_validation_pending=True),indent=2)+'\n')

prefix=NativeChain(INPUT,ROOT.name+'-prefix',fl_graph=True,phase_pair=True,engine_override=engine)
try:
    base(prefix)
    for n in [1,2,4,5,6,7,8,10,11,12]:prefix.bypass(n,True)
    prefix.gain(3,1);prefix.gain(4,0)
    for phase in range(3):
        y,_=prefix.render();sf.write(ROOT/f'actual-prefix-{phase}.wav',y,48000,subtype='FLOAT')
finally:prefix.close()
try:
    for i in range(4):
        c=NativeChain(ROOT/'actual-prefix-0.wav',f'{ROOT.name}-EQ-{i}',fl_graph=True,phase_pair=True,engine_override=engine)
        clients.append(c);pool.put(c)
    origin=initial.copy();iterations=0
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        def f(z):
            value=evaluate(origin+np.array(z)*steps);trials=[]
            for k in range(len(z)):
                l=np.array(z);r=np.array(z);l[k]-=.25;r[k]+=.25
                trials.extend([np.clip(origin+l*steps,lower,upper),np.clip(origin+r*steps,lower,upper)])
            values=list(executor.map(evaluate,trials))
            # Fixed factor preserves the objective/optimum, but makes the first step
            # exceed actual native .01dB quantization instead of rounding to zero.
            return 1000*value,1000*np.array([(values[2*k+1]-values[2*k])/.5 for k in range(len(z))])
        def callback(z):
            global iterations
            iterations+=1
            (ROOT/'search-state.json').write_text(json.dumps(dict(iteration=iterations,calls=calls,best_training_loss=best,
                seconds=time.monotonic()-start,full_fresh_validation_pending=True,reference_match_reached=False),indent=2)+'\n')
        fit=minimize(f,np.zeros(42),jac=True,method='L-BFGS-B',bounds=list(zip((lower-origin)/steps,(upper-origin)/steps)),
            callback=callback,options=dict(maxiter=int(os.environ.get('DIVALEAD_POST_EQ_MAXITER','28')),maxls=6,ftol=1e-9,gtol=1e-6))
    (ROOT/'optimizer-result.json').write_text(json.dumps(dict(success=bool(fit.success),message=str(fit.message),
        actual_native_EQ_evaluations=calls,iterations=int(fit.nit)),indent=2)+'\n')
    chosen=np.array(json.loads((ROOT/'best.json').read_text())['source_post_EQ']);heldout=[]
    for phase in [1,2]:
        configured(clients[0],chosen,phase);y,_=clients[0].render();heldout.append(dict(phase=phase,loss=assess(y),assessment=features.local.last))
finally:
    for c in clients:c.close()

fresh=[];control=[];c=NativeChain(INPUT,ROOT.name+'-full-validation',fl_graph=True,phase_pair=True,engine_override=engine)
try:
    for kind,z,out in [('control',None,control),('selected',chosen,fresh)]:
        configured(c,z)
        for rep in range(6):
            y,status=c.render();loss=assess(y);path=ROOT/f'{kind}-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT')
            out.append(dict(loss=loss,audio=str(path),assessment=features.local.last,native_status=status))
finally:c.close()
seed_mean=float(np.mean([r['loss']for r in control]));mean=float(np.mean([r['loss']for r in fresh]));std=float(np.std([r['loss']for r in fresh]))
se=float(np.hypot(np.std([r['loss']for r in control]),std)/np.sqrt(6));robust=seed_mean-mean>max(.0005,3*se)
selected=sorted(fresh,key=lambda r:r['loss'])[3]
result=dict(prior,source_post_EQ=chosen.tolist(),source_post_EQ_nodes=[1,2],
    model_family='FL20_corrected_context_common_post_EQ_research',requires_extended_graph_and_exporter=True,
    actual_FL_validation_pending=True,loss=mean,realization_losses=[r['loss']for r in fresh],realization_standard_deviation=std,
    recorded_render_loss=selected['loss'],original_reference_assessment=selected['assessment'],recorded_audio=selected['audio'],
    seed_fresh_mean_loss=seed_mean,fresh_mean_standard_error=se,robust_improvement=bool(robust),
    heldout_prefix_validation=heldout,full_fresh_native_realizations=6,full_fresh_native_validation_pending=False,
    original_reference_match_reached=False,reference_match_reached=False)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(seed_mean=seed_mean,new_mean=mean,SEM=se,robust_improvement=bool(robust),
    control=control,selected=fresh),indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(actual_native_EQ_evaluations=calls,seconds=time.monotonic()-start,
    loss=mean,seed_mean=seed_mean,robust_improvement=bool(robust),not_yet_exportable_by_x95_tools=True,match_reached=False),indent=2)+'\n')
sf.write(ROOT/'best-with-tail.wav',sf.read(selected['audio'],dtype='float32')[0],48000,subtype='FLOAT')
print('FL20_COMMON_POST_EQ_VALIDATED',mean,robust,flush=True)
