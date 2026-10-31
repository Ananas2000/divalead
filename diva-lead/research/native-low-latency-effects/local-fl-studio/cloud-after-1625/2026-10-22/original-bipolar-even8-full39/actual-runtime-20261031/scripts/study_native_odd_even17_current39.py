"""Jointly refit 17 local odd/even stock WaveShaper curve controls to original.

Every derivative/candidate is real nativeDLL+two officialZL DSP. Linear feature
fits propose presets only. The unchanged complete original criterion, stereo
guards, fresh6/cold2 and exact saved-state replay gate any adoption.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,struct,tarfile,threading,traceback
import numpy as np,soundfile as sf
from scipy.optimize import lsq_linear
from scipy.stats import qmc
from native_chain import NativeChain
from fl20_curve import apply_candidate,extended_curve_bytes,native_dsp_settings_SHA256,HIGH_FORMAT
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');R=H/'WS_BIPOLAR_ODD9_EVEN8_CURRENT39';R.mkdir(exist_ok=False);STATE=N/'ORIGINAL_NATIVE_WS_ODD_EVEN17_CURRENT39_STUDY.json'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert prior['full_public_kit_directory']=='ZL-WIP39';seed=prior['native_base'];base=np.array(seed['x']);bundle=seed['native_saved_state_bundle'];bundledir=Path(bundle['directory']);wsrow=next(row for row in bundle['manifest']if row['node']==0);original_canonical=(bundledir/wsrow['state']).read_bytes();canonical=original_canonical;count=struct.unpack_from('<I',canonical,30)[0];assert count==233 and struct.unpack_from('<I',canonical,16)[0]==1
origin=np.zeros(17);step=np.r_[np.array([.001,.001,.0007,.0007,.001,.0015,.0018,.002]),np.full(9,.0006)]
for name,key in [('PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(R/name).write_bytes(Path(prior[key]).read_bytes())
(R/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n');os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment')
from fl20_objective import FeaturesOriginal,a,SCALES,TONE
features=FeaturesOriginal();reg=float(np.sum(base[:28]**2))*.00000025;ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);np.testing.assert_array_equal(ref,a.REF);freq=np.fft.rfftfreq(len(ref),1/48000);masks=[(freq>=lo)&(freq<hi)for lo,hi in [(300,800),(2000,5000),(5000,10000),(10000,14000)]]
cache=threading.local()
def capture(module,name,key):
 old=getattr(module,name)
 def wrapped(*args,**kwargs):
  result=old(*args,**kwargs);setattr(cache,key,result);return result
 setattr(module,name,wrapped)
capture(a,'powers','power');capture(a,'erbpower','erb');capture(a.wave,'features','shape');capture(a.h,'harmonic_errors','harmonic')
weights=np.maximum(a.h.HT,1e-5)**.5;weights[:,0]=0;weights/=weights.sum();factors=None
def rawgroups(metrics):
 error=10*np.log10(np.maximum(cache.power[0],1e-15)/np.maximum(a.TP,1e-15));erb=10*np.log10(np.maximum(cache.erb,1e-12)/np.maximum(a.TE,1e-12));phase=cache.shape[0];targets=[a.TS,a.TS*np.exp(1j*np.pi*(1-a.wave.ORDERS))[None]];chosen=min(targets,key=lambda target:np.sum(abs(phase-target)**2*a.TW));d=(phase-chosen)*np.sqrt(a.TW)
 groups=dict(H24=(np.array(cache.harmonic['harmonic_errors_db'])*np.sqrt(weights)).ravel(),upper_harm=error[:,4:,:2].ravel()/np.sqrt(error[:,4:,:2].size),upper_off=error[:,4:,2:].ravel()/np.sqrt(error[:,4:,2:].size),low_harm=error[:,:4,:2].ravel()/np.sqrt(error[:,:4,:2].size),ERB=(erb*np.sqrt(a.EW)).ravel(),relative_phase=np.r_[d.real.ravel(),d.imag.ravel()])
 for key,v in groups.items():assert abs(float(np.linalg.norm(v))-metrics[key])<1e-6,(key,np.linalg.norm(v),metrics[key])
 return groups
def lr(y):
 p=abs(np.fft.rfft(y,axis=0))**2;return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref)
def assess(y):
 residual=features.residual(y[:288000]);last=features.local.last;groups=rawgroups(last['metrics']);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));v=lr(edit);e=10*np.log10(np.maximum(cache.power[0],1e-15)/np.maximum(a.TP,1e-15));return dict(loss=float(residual@residual)+reg,assessment=last,LR_dB=v.tolist(),lowmid_error=abs(float(v[0]-target[0])),positive_excess_air_dB=float(np.maximum(e[:,4:6,2:],0).mean()),stereo_preservation_passed=bool(np.sqrt(np.mean((v[1:]-target[1:])**2))<=1.48 and max(abs(v[1:]))<=1.6 and abs(v[0]-target[0])<=3.25)),groups
X=np.cumsum([struct.unpack_from('<d',canonical,34+24*k)[0]for k in range(count)]);S=2*X-1;window=np.maximum(0,1-(S/.67)**2)**4
B=[S*S*window,S**4*window]
for center in[.1,.2,.3,.4,.5,.6]:B.append(S*S*np.exp(-.5*((abs(S)-center)/.055)**2)*window)
B.append(S*window)
for center in np.linspace(.08,.64,8):B.append(S*np.exp(-.5*((abs(S)-center)/.045)**2)*window)
B=np.column_stack(B);B/=np.max(abs(B),axis=0);assert B.shape[1]==17;Y0=np.array([struct.unpack_from('<d',canonical,42+24*k)[0]for k in range(count)]);assert np.min(np.diff(Y0))>=-1e-10
(R/'BIPOLAR_GUI_CONVERTED_BASE.bin').write_bytes(canonical);(R/'UNIPOLAR_CONTROL_NATIVE_STATE.bin').write_bytes(original_canonical)
def native_case(v):
 return dict(seed,not_compatible_with_standard_x95_exporter=True,waveshaper_bipolar_odd_even_research_format='canonical_parent_local_even8_odd9_research_v1',waveshaper_bipolar_odd_even_coefficients=list(map(float,v)),waveshaper_research_parent_state=str(R/'BIPOLAR_GUI_CONVERTED_BASE.bin'),waveshaper_research_parent_SHA256=hashlib.sha256(canonical).hexdigest(),parent_native_settings_SHA256=bundle['settings_SHA256'])
def curve(v):
 if v is None:return original_canonical
 y=Y0+B@np.asarray(v)
 if np.min(y)<0 or np.max(y)>1 or np.min(np.diff(y))< -1e-10:return None
 if np.array_equal(v,origin):return canonical
 data=bytearray(canonical)
 for k,value in enumerate(y):struct.pack_into('<d',data,42+24*k,float(value))
 return bytes(data)
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,base,seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 return c
def configure(c,v):
 b=curve(v);assert b is not None;p=c.output.parent/(c.output.stem+'-WS48-current.bin');p.write_bytes(b);c.load_state(0,p)
def cascade(raw,p,z,primary=None):
 p.load(primary or R/'PRIMARY.bin');z.load(R/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return trims[p.child.pid].render(out)
clients=[];trims={};pool=queue.Queue();mutex=threading.Lock();rows=[]
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_native_hosts=[c.proc.pid for c,p,z in clients],actual_ZL_hosts=[c.child.pid for p,z in [(p,z)for c,p,z in clients]for c in [p,z]],original_is_the_only_target=True,v83_Finish_not_used=True,only_native_WaveShaper_local_even8_odd9_controls_varied=True,current_comparator=prior['source_accepted_cohort'],not_compatible_with_standard_x95_exporter=True,full_base_kit='ZL-WIP39',native_trim_included=True,other11_native_source_MIDI_ARP_ADSR_routing_and_both_ZL_unchanged=True,not_adopted=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def evaluate(case,reps=4,keep=True):
 label,v=case;v=None if v is None else np.array(v);c,p,z=pool.get()
 try:
  configure(c,v);captures=[];grouped=[]
  for rep in range(reps):raw,_=c.render();out=cascade(raw,p,z);d,g=assess(out);captures.append(d);grouped.append(g)
  groups={key:np.mean([g[key]for g in grouped],axis=0).tolist()for key in TONE};row=dict(label=label,curve_vector=None if v is None else v.tolist(),loss=float(np.mean([r['loss']for r in captures])),positive_excess_air_dB=float(np.mean([r['positive_excess_air_dB']for r in captures])),lowmid_error=float(np.mean([r['lowmid_error']for r in captures])),realization_losses=[r['loss']for r in captures],stereo_preservation_passed=all(r['stereo_preservation_passed']for r in captures),physical_feature_groups=groups,assessment=captures[len(captures)//2])
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,p,z))
def vector(row):return np.concatenate([np.array(row['physical_feature_groups'][key])*factors[key]for key in TONE])
def add(tar,name,y,members):
 stream=io.BytesIO();sf.write(stream,y,48000,format='WAV',subtype='FLOAT');b=stream.getvalue();info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
try:
 (R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(parent='supported39 canonical bipolar curve',local_even_controls=8,local_odd_controls=9,main_primary_POST_trim_and_other11native_source_MIDI_unchanged=True,all_proposals_actual_native_DLL=True,physical_features_for_proposals_only=True,no_audio_averaging=True,fresh_finalist_ranking_then_new_independent12=True,first6_AND_first10_mean_gain_over_max0005_3SEM=True,bothcold_positive=True,first10_AND_bothcold_Air_nonincreasing=True,TONEfirst10_nonincreasing=True,all_upper148_abs16_lowmid325_pairedlowmid002=True,latest_BEST_context_and_explicit_supported_metadata_migration_required=True,not_compatible_with_current_supported_curve_generator=True),indent=2)+'\n')
 record('starting_actual_local_even8_plus_odd9_native_transfer_fit')
 for k in range(2):
  c=native('OddEven17-39-native-'+str(k));p=WinVST3('OddEven17-39-primary-'+str(k));z=WinVST3('OddEven17-39-post-'+str(k));clients.append((c,p,z));pool.put((c,p,z));trim=NativePostTrim(R/'trim-buffers','OddEven17-39-trim-'+str(k),cleanup_on_close=True);trim.load(prior['post_native_trim_state']);trims[p.child.pid]=trim
 baseline=evaluate(('current39-canonical-control',None),12);modelbase=evaluate(('same-canonical-parent-origin',origin),8);assert curve(origin)==original_canonical
 m=modelbase['assessment']['assessment']['metrics'];factors={key:float(np.sqrt((.65*TONE[key]+.35*a.WEIGHTS.get(key,0))/(SCALES[key]*max(m[key],1e-6))))for key in TONE};cases=[];endpoints={}
 for j in range(17):
  endpoints[j]={}
  for sign in[-1,1]:
   strength=1.
   while strength>=1/64:
    v=origin.copy();v[j]+=sign*step[j]*strength
    if curve(v)is not None:break
    strength*=.5
   if strength<1/64:endpoints[j][sign]=(0.,None);continue
   label=f'derivative-{j}-{sign}';endpoints[j][sign]=(strength,label);cases.append((label,v))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if k%8==0:record('actual_local17_physical_derivative_renders',baseline_mean=baseline['loss'])
  bylabel={r['label']:r for r in rows};f0=vector(modelbase);columns=[]
  for j in range(17):
   ap,lp=endpoints[j][1];am,lm=endpoints[j][-1];plus=vector(bylabel[lp])if lp else f0;minus=vector(bylabel[lm])if lm else f0;columns.append((plus-minus)/max(ap+am,1e-12))
  J=np.column_stack(columns);u=lsq_linear(np.r_[J,np.eye(17)*.025],np.r_[-f0,np.zeros(17)],bounds=(-1.5,1.5),tol=1e-9).x;top=np.argsort(np.linalg.norm(J,axis=0))[-9:];sparse=np.zeros(17);sparse[top]=lsq_linear(np.r_[J[:,top],np.eye(9)*.025],np.r_[-f0,np.zeros(9)],bounds=(-1.5,1.5),tol=1e-9).x;np.savez_compressed(R/'ACTUAL_LOCAL17_PHYSICAL_JACOBIAN.npz',J=J,baseline_features=f0,step=step)
  (R/'ACTUAL_DERIVATIVE_PROPOSALS.json').write_text(json.dumps(dict(all17_direction=u.tolist(),strongest9_direction=sparse.tolist(),step=step.tolist(),physical_feature_vector_norms_verified=True,original_acceptance_criterion_unchanged=True),indent=2)+'\n');proposals=[]
  for mode,direction in [('all17',u),('strong9',sparse)]:
   for fraction in[.125,.25,.5,.75,1.]:
    v=origin+step*direction*fraction
    if curve(v)is not None:proposals.append((f'joint-{mode}-{fraction}',v))
  for k,unit in enumerate(qmc.LatinHypercube(17,seed=2026103117).random(48)):
   v=origin+(unit*2-1)*step*[.25,.5,1,1.5][k%4]
   if curve(v)is not None:proposals.append((f'coupled-LHS-{k}',v))
  for k,row in enumerate(executor.map(evaluate,proposals)):
   if k%8==0:record('actual_local17_joint_curve_candidate_renders',baseline_mean=baseline['loss'],best_training_loss=min(r['loss']for r in rows))
 (R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));eligible=sorted([r for r in rows if r['stereo_preservation_passed']and r['curve_vector']is not None and r['curve_vector']!=origin.tolist()and r['positive_excess_air_dB']<=baseline['positive_excess_air_dB']],key=lambda r:r['loss'])[:4]
 finalists=[evaluate(('new-fresh-finalist-'+str(k),row['curve_vector']),12,False)for k,row in enumerate(eligible)];(R/'ALL_FRESH_FINALISTS.json').write_text(json.dumps(finalists,indent=2)+'\n');feasible=[r for r in finalists if r['stereo_preservation_passed']and r['positive_excess_air_dB']<=baseline['positive_excess_air_dB']];winner=min(feasible,key=lambda r:r['loss'])if feasible else None;ready=bool(winner and baseline['loss']-winner['loss']>.0003)
 summary=dict(training_cases=len(rows),actual_training_DSP_renders=sum(12 if r['label']=='current39-canonical-control'else 8 if r['label']=='same-canonical-parent-origin'else 4 for r in rows),baseline=baseline,winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,only_native_local17_curve_changed=True,only_three_held_notes=True,not_adopted=True,reference_match_reached=False,requires_latest_main_context_revalidation=True,requires_explicit_supported_metadata_migration=True)
 (R/'FROZEN_BEFORE_NEW_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if winner:
  (R/'SELECTED_CURVE_RESEARCH_ONLY.bin').write_bytes(curve(winner['curve_vector']));(R/'SELECTED_NATIVE_METADATA_RESEARCH_ONLY.json').write_text(json.dumps(native_case(winner['curve_vector']),indent=2)+'\n')
 if ready:
  record('new12_paired_native_control_vs_local17_candidate_validation');c0,p0,z0=clients[0];c1,p1,z1=clients[1];configure(c0,None);configure(c1,winner['curve_vector']);captures=[];members=[];archive=Path('/tmp/divalead-local17-current39-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz').symlink_to(archive)
  with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:
     c0.close();c1.close();c0=native('OddEven17-39-cold-control-'+str(rep));c1=native('OddEven17-39-cold-candidate-'+str(rep));configure(c0,None);configure(c1,winner['curve_vector']);clients[0]=(c0,p0,z0);clients[1]=(c1,p1,z1)
    raw0,_=c0.render();old=cascade(raw0,p0,z0);d0,_=assess(old);raw1,_=c1.render();out=cascade(raw1,p1,z1);d1,_=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_dB']-d0['positive_excess_air_dB']))
    for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('new12_independent_actual_native_pairs',completed_pairs=rep+1)
  delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);sem6=float(delta[:6].std(ddof=1)/np.sqrt(6));sem10=float(delta[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guards=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(delta[:6].mean()>max(.0005,3*sem6)and delta[:10].mean()>max(.0005,3*sem10)and min(delta[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and tone<=0 and guards)
  newdir=R/'saved-native-bundle';manifest=[]
  for row in bundle['manifest']:
   dst=newdir/row['state'];dst.parent.mkdir(parents=True,exist_ok=True);c1.save_state(row['node'],dst)
   if row['node']!=0:assert dst.read_bytes()==(bundledir/row['state']).read_bytes()
   manifest.append(dict(row,state_bytes=dst.stat().st_size,state_SHA256=hashlib.sha256(dst.read_bytes()).hexdigest()))
  c1.set(3,1,0);expected,_=c1.render();fresh=native('OddEven17-39-state-replay')
  try:
   fresh.load_state(0,newdir/wsrow['state']);fresh.set(3,1,0);again,_=fresh.render();error=float(abs(again-expected).max());assert error<=2e-7
  finally:fresh.close()
  with tarfile.open(archive)as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(delta[:6].mean()),first6_SEM=sem6,first10_mean_improvement=float(delta[:10].mean()),first10_SEM=sem10,cold2_improvements=delta[10:].tolist(),first10_Air_increase=float(air[:10].mean()),cold2_Air_increase=air[10:].tolist(),first10_TONE_delta=tone,all12_stereo_and_paired_lowmid=guards,robust_improvement=robust,independent_zero_depth_replay_error=error,other11_native_states_exact=True)
  (R/'RESEARCH_CANONICAL_STATE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_local17_curve_study_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in['baseline','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_accepted39',error=traceback.format_exc());raise
finally:
 for c,p,z in clients:c.close();p.close();z.close()
 for t in trims.values():t.close()
