"""Research-only additional actual native EQ2 in each existing MID/SIDE branch.

The new graph uses the existing four mixer inserts and two additional actual EQ2 instances.
Three complete current-graph captures train16 gain controls; two are held out.
Independent full-source renders compare against the original graph, not flat EQ.
No reference audio enters a plugin and no research settings are auto-installed.
"""
from pathlib import Path
import concurrent.futures,hashlib,json,os,queue,sys,threading,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate,curve_metadata,validate_curve_candidate
B=Path('/tmp/divalead-local-1625');ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
prior=json.loads(Path(sys.argv[1]).read_text());validate_curve_candidate(prior)
assert len(prior['x'])==95
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();INPUT=Path(prior['source_manifest']['native_input']);base=np.array(prior['x'])
FREQS=np.array([52,130,320,810,2050,5200,13000],float)
RAW=np.rint(np.log(FREQS/20)/np.log(1000)*65536).astype(int)
start=time.monotonic();pool=queue.Queue();clients=[];mutex=threading.Lock();calls=0;native_renders=0;best=float('inf')
(REGULARIZER:=float(np.sum(base[:28]**2))*.00000025)
(ROOT/'seed.json').write_text(json.dumps(prior,indent=2)+'\n')
def old_settings(c):
    apply_candidate(c,base,prior)
    for i,value in prior['chorus_overrides'].items():c.set(3,int(i),int(value))
def post_settings(c,v):
    assert len(v)==16
    for node,offset,main in [(1,0,14),(2,7,15)]:
        c.bypass(node,False)
        for band in range(7):
            c.set(node,band,int(round(v[offset+band]*100)))
            c.set(node,7+band,int(RAW[band]));c.set(node,14+band,9830)
            c.set(node,21+band,6);c.set(node,28+band,0)
        c.set(node,35,int(round(v[main]*100)))
def training_settings(c,v,phase):
    c.load_input(ROOT/f'actual-WS-Chorus-prefix-{phase}.wav')
    old_settings(c)
    for node in [0,3,13,14]:c.bypass(node,True)
    c.gain(0,1);c.gain(1,0)
    post_settings(c,v)
def full_settings(c,v):old_settings(c);post_settings(c,v)
def audio_score(y):
    r=features.residual(y[:288000]);return float(r@r)+REGULARIZER
def evaluate(v,save=True):
    global calls,native_renders,best
    c=pool.get()
    try:
        phase_rows=[];audio=[]
        for phase in range(3):
            training_settings(c,v,phase);y,status=c.render()
            phase_rows.append(dict(phase=phase,loss=audio_score(y),assessment=features.local.last,native_status=status));audio.append(y)
        loss=float(np.mean([r['loss']for r in phase_rows]))+float(np.sum(v[:14]**2))*.00000025
        with mutex:
            calls+=1;native_renders+=3
            if save and loss<best:
                best=loss;median=sorted(range(3),key=lambda k:phase_rows[k]['loss'])[1]
                row=dict(curve_metadata(prior),x=base.tolist(),extra_MS_EQ_gains=v.tolist(),extra_MS_EQ_frequencies_Hz=FREQS.tolist(),
                    extra_MS_EQ_bandwidth_raw=9830,extra_MS_EQ_graph='existing_MID_EQs_then_extra_EQ1_and_existing_SIDE_EQs_then_extra_EQ2_before_SIDE_decode',
                    source_manifest=prior['source_manifest'],chorus_overrides=prior['chorus_overrides'],
                    training_loss=loss,loss=loss,calls=calls,actual_native_training_renders=native_renders,
                    training_phase_losses=[r['loss']for r in phase_rows],original_reference_assessment=phase_rows[median]['assessment'],
                    model_family='research_FL20_native_extra_MID_SIDE_EQ16_ensemble3',objective_version='local_full_original_criteria_FL20_context_v1',
                    training_regularizer_extra_LR_gain_squared=0.00000025,full_fresh_native_validation_pending=True,
                    not_compatible_with_standard_x95_exporter=True,not_automatically_adopted=True,
                    only_three_held_notes=True,actual_native_DLL_audio=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
                (ROOT/'best-training.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-training-with-tail.wav',audio[median],48000,subtype='FLOAT')
                print('EXTRA_MS_EQ_BEST',loss,calls,native_renders,round(time.monotonic()-start,1),flush=True)
        return loss
    finally:pool.put(c)
old=NativeChain(INPUT,ROOT.name+'-old-structural',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
new=NativeChain(INPUT,ROOT.name+'-new-structural',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_extraMS_host.exe')
try:
    old_settings(old);old.set(3,1,0);a,a_status=old.render()
    full_settings(new,np.zeros(16));new.set(3,1,0);new.bypass(1,True);new.bypass(2,True);b,b_status=new.render()
    error=float(np.max(np.abs(a-b)));assert error<=2e-7,('Extra MID/SIDE graph changed old bypass control',error)
    full_settings(new,np.zeros(16));new.set(3,1,0);flat,flat_status=new.render();flat_error=float(np.max(np.abs(flat-a)))
    positive=np.zeros(16);positive[14]=6;full_settings(new,positive);new.set(3,1,0);changed,_=new.render()
    delta=float(np.max(np.abs(changed-flat)));assert delta>1e-4
    (ROOT/'STRUCTURAL_NATIVE_PROOF.json').write_text(json.dumps(dict(
        original_source_graph_unchanged=True,post_EQ_bypassed_zero_depth_max_error=error,
        bypass_control_decoded_audio_bit_exact=bool(np.array_equal(a,b)),
        additional_EQ_active_flat_zero_depth_max_error=flat_error,flat_EQ_identity_not_assumed=True,
        positive_MID_gain_control_max_error=delta,original_status=a_status,new_bypass_status=b_status,new_flat_status=flat_status,
        all_sound_processing_actual_native_DLLs=True,existing_MID_SIDE_mixer_routes_unchanged=True,source_MIDI_unchanged=True,
        actual_FL_GUI_export_pending=True,new_graph_not_integrated_in_standard_exporter=True,match_reached=False),indent=2)+'\n')
    old_settings(old)
    for node in [4,5,6,7,8,10,11,12]:old.bypass(node,True)
    old.gain(3,1);old.gain(4,0)
    for phase in range(5):
        y,_=old.render();sf.write(ROOT/f'actual-WS-Chorus-prefix-{phase}.wav',y,48000,subtype='FLOAT')
    (ROOT/'training-prefix-manifest.json').write_text(json.dumps(dict(
        training_phases=[0,1,2],heldout_phases=[3,4],
        prefix_sha256=[hashlib.sha256((ROOT/f'actual-WS-Chorus-prefix-{i}.wav').read_bytes()).hexdigest()for i in range(5)],
        actual_native_WS_Chorus_prefixes=True,reference_analysis_only=True),indent=2)+'\n')
finally:old.close();new.close()
try:
    for i in range(4):
        c=NativeChain(ROOT/'actual-WS-Chorus-prefix-0.wav',ROOT.name+'-fit-'+str(i),fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_extraMS_host.exe')
        clients.append(c);pool.put(c)
    chosen=np.zeros(16);current=evaluate(chosen);initial=current
    directions=np.eye(16).tolist()
    for band in range(7):
        v=np.zeros(16);v[band]=1;v[7+band]=-1;directions.append(v.tolist())
    directions=np.array(directions);radii=np.r_[np.full(14,1.),[.5,.5],np.full(7,1.)]
    lower=np.r_[np.full(14,-18.),[-9.,-9.]];upper=-lower
    budget=int(os.environ.get('DIVALEAD_EXTRAMS_MAXCALLS','1800'));passes=int(os.environ.get('DIVALEAD_EXTRAMS_MAXPASSES','16'))
    rng=np.random.default_rng(2026102255)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for iteration in range(passes):
            before=current;accepted=0
            for k in rng.permutation(len(directions)):
                if calls+4>budget:break
                trials=[np.round(np.clip(chosen+factor*radii[k]*directions[k],lower,upper),2)for factor in [-2.,-1.,1.,2.]]
                values=list(executor.map(evaluate,trials));j=int(np.argmin(values))
                if values[j]<current-2e-6:chosen=trials[j];current=values[j];accepted+=1
            improvement=before-current
            progress=dict(iteration=iteration+1,calls=calls,actual_native_training_renders=native_renders,
                best_training_loss=best,accepted_moves=accepted,pass_improvement=improvement,
                seconds=time.monotonic()-start,method='Native additional MID/SIDE EQ16,3 training realizations,2 heldout',match_reached=False)
            (ROOT/'search-state.json').write_text(json.dumps(progress,indent=2)+'\n');print('EXTRA_MS_EQ_PASS',progress,flush=True)
            if calls+4>budget:break
            if improvement<.0005:radii*=.5
            if float(np.max(radii))<.025:break
    bestrow=json.loads((ROOT/'best-training.json').read_text());chosen=np.array(bestrow['extra_MS_EQ_gains']);heldout=[]
    for phase in [3,4]:
        training_settings(clients[0],chosen,phase);y,status=clients[0].render()
        heldout.append(dict(phase=phase,loss=audio_score(y),assessment=features.local.last,native_status=status))
    (ROOT/'heldout-prefix-validation.json').write_text(json.dumps(heldout,indent=2)+'\n')
finally:
    for c in clients:c.close()
def fresh(label,candidate_new,reps=12):
    c=NativeChain(INPUT,ROOT.name+'-'+label,fl_graph=True,phase_pair=True,
        engine_override='fl_native_fl20_extraMS_host.exe'if candidate_new else'fl_native_fl20_host.exe')
    captures=[]
    try:
        if candidate_new:full_settings(c,chosen)
        else:old_settings(c)
        for rep in range(reps):
            y,status=c.render();loss=audio_score(y);path=ROOT/f'{label}-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT')
            captures.append(dict(loss=loss,audio=str(path),assessment=features.local.last,native_status=status))
        if candidate_new:
            for node in [1,2]:c.save_state(node,ROOT/f'extra-MS-native-node{node}.bin')
    finally:c.close()
    vals=[r['loss']for r in captures];median=sorted(captures,key=lambda r:r['loss'])[reps//2]
    return dict(loss=float(np.mean(vals)),std=float(np.std(vals)),captures=captures,median=median)
new=fresh('independent-new',True);control=fresh('independent-original-control',False)
sem=float(np.hypot(new['std'],control['std'])/np.sqrt(12));robust=control['loss']-new['loss']>max(.0015,3*sem)
median=new['median'];result=dict(bestrow,loss=new['loss'],training_loss=bestrow['loss'],seed_fresh_mean_loss=control['loss'],
    realization_losses=[r['loss']for r in new['captures']],realization_standard_deviation=new['std'],fresh_mean_standard_error=sem,
    robust_improvement=bool(robust),full_fresh_native_validation_pending=False,full_fresh_native_realizations=12,
    recorded_audio=median['audio'],recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],
    heldout_prefix_validation=heldout,reference_match_reached=False)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(new=new,control=control,SEM=sem,robust_improvement=bool(robust)),indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(initial_training_loss=initial,final_training_loss=bestrow['loss'],
    fresh_mean_loss=new['loss'],original_graph_control_mean=control['loss'],robust_improvement=bool(robust),
    calls=calls,actual_native_training_renders=native_renders,seconds=time.monotonic()-start,
    not_integrated_in_standard_exporter=True,not_automatically_adopted=True,match_reached=False),indent=2)+'\n')
print('EXTRA_MS_EQ_ACTUAL_NATIVE_COMPLETE',new['loss'],control['loss'],robust,flush=True)
