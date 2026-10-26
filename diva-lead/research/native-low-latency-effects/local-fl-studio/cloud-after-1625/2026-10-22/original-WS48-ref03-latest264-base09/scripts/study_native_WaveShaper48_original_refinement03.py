"""Jointly refit all48 supported stock WaveShaper curve controls to original.

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
from fl20_curve import apply_candidate,extended_curve_bytes,native_dsp_settings_SHA256
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/tmp/divalead-original-native-WS48-20261026-01');R.mkdir(exist_ok=False);STATE=N/'ORIGINAL_NATIVE_WS48_REFINEMENT03_STUDY.json'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];base=np.array(seed['x']);bundle=seed['native_saved_state_bundle'];bundledir=Path(bundle['directory']);wsrow=next(row for row in bundle['manifest']if row['node']==0);canonical=(bundledir/wsrow['state']).read_bytes();assert struct.unpack_from('<I',canonical,30)[0]==129
origin=np.r_[base[76:78],seed['waveshaper_curve_adjustment'],seed['waveshaper_local_bump_adjustment'],seed['waveshaper_detail_bump_adjustment'],seed['waveshaper_fine_bump_adjustment']];assert len(origin)==48
step=np.r_[[.02,.02,.012,.016,.002,.003,.004,.006,.001,.0015,.002,.003,.004,.005,.006,.008],np.full(32,.001)]
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
 residual=features.residual(y[:288000]);last=features.local.last;groups=rawgroups(last['metrics']);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));v=lr(edit);return dict(loss=float(residual@residual)+reg,assessment=last,LR_dB=v.tolist(),stereo_preservation_passed=bool(np.sqrt(np.mean((v[1:]-target[1:])**2))<=1.5 and max(abs(v[1:]))<=1.6 and abs(v[0]-target[0])<=3.35)),groups
def native_case(v):
 x=base.copy();x[76:78]=v[:2];return dict(seed,x=x.tolist(),waveshaper_curve_adjustment=list(v[2:4]),waveshaper_local_bump_adjustment=list(v[4:8]),waveshaper_detail_bump_adjustment=list(v[8:16]),waveshaper_fine_bump_adjustment=list(v[16:48]))
def generated_y(v):
 s=native_case(v);b=extended_curve_bytes(np.array(s['x']),s['waveshaper_curve_adjustment'],s['waveshaper_local_bump_adjustment'],s['waveshaper_detail_bump_adjustment'],s['waveshaper_fine_bump_adjustment']);return np.array([struct.unpack_from('<d',b,34+24*k+8)[0]for k in range(129)])
Y0=np.array([struct.unpack_from('<d',canonical,34+24*k+8)[0]for k in range(129)]);G0=generated_y(origin);assert min(np.diff(Y0))>=-1e-10
def curve(v):
 y=np.clip(Y0+generated_y(v)-G0,0,1)
 if min(np.diff(y))< -1e-10:return None
 if np.array_equal(v,origin):return canonical
 b=bytearray(canonical)
 for k,value in enumerate(y):struct.pack_into('<d',b,34+24*k+8,float(value))
 return bytes(b)
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,base,seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 return c
def configure(c,v):
 b=curve(v);assert b is not None;p=c.output.parent/(c.output.stem+'-WS48-current.bin');p.write_bytes(b);c.load_state(0,p)
def cascade(raw,p,z):
 p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return out
clients=[];pool=queue.Queue();mutex=threading.Lock();rows=[]
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_native_hosts=[c.proc.pid for c,p,z in clients],actual_ZL_hosts=[c.child.pid for p,z in [(p,z)for c,p,z in clients]for c in [p,z]],original_is_the_only_target=True,v83_Finish_not_used=True,only_native_WaveShaper48_curve_controls_varied=True,other11_native_source_MIDI_ARP_ADSR_routing_and_both_ZL_unchanged=True,not_adopted=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def evaluate(case,reps=4,keep=True):
 label,v=case;v=np.array(v);c,p,z=pool.get()
 try:
  configure(c,v);captures=[];grouped=[]
  for rep in range(reps):raw,_=c.render();out=cascade(raw,p,z);d,g=assess(out);captures.append(d);grouped.append(g)
  groups={key:np.mean([g[key]for g in grouped],axis=0).tolist()for key in TONE};row=dict(label=label,curve_vector=v.tolist(),loss=float(np.mean([r['loss']for r in captures])),realization_losses=[r['loss']for r in captures],stereo_preservation_passed=all(r['stereo_preservation_passed']for r in captures),physical_feature_groups=groups,assessment=captures[len(captures)//2])
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,p,z))
def vector(row):return np.concatenate([np.array(row['physical_feature_groups'][key])*factors[key]for key in TONE])
def add(tar,name,y,members):
 stream=io.BytesIO();sf.write(stream,y,48000,format='WAV',subtype='FLOAT');b=stream.getvalue();info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
try:
 (R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(warm_pairs=10,cold_pairs=2,accept_both_first6_and_first10_gain_over_max_floor_or_3SEM=True,floor=.0005,both_cold_positive=True,all_stereo_guards_unchanged=True,full_supported_export_and_latest_context_required=True),indent=2)+'\n')
 record('starting48_control_actual_WaveShaper_refinement03')
 for k in range(2):c=native('OriginalWS48refine03-native-'+str(k));p=WinVST3('OriginalWS48refine03-primary-'+str(k));z=WinVST3('OriginalWS48refine03-post-'+str(k));clients.append((c,p,z));pool.put((c,p,z))
 baseline=evaluate(('unchanged-canonical-control',origin),12);m=baseline['assessment']['assessment']['metrics'];factors={key:float(np.sqrt((.65*TONE[key]+.35*a.WEIGHTS.get(key,0))/(SCALES[key]*max(m[key],1e-6))))for key in TONE};cases=[];endpoints={}
 for j in range(48):
  endpoints[j]={}
  for sign in [-1,1]:
   strength=1.
   while strength>=1/64:
    v=origin.copy();v[j]+=sign*step[j]*strength
    if curve(v)is not None:break
    strength*=.5
   if strength<1/64:endpoints[j][sign]=(0.,None);continue
   label=f'derivative-{j}-{sign}';endpoints[j][sign]=(strength,label);cases.append((label,v))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if k%8==0:record('actual_WaveShaper48_physical_derivative_renders',control_mean=baseline['loss'],best_mean=min(r['loss']for r in rows if r['stereo_preservation_passed']))
  bylabel={r['label']:r for r in rows};f0=vector(baseline);columns=[]
  for j in range(48):
   ap,lp=endpoints[j][1];am,lm=endpoints[j][-1];plus=vector(bylabel[lp])if lp else f0;minus=vector(bylabel[lm])if lm else f0;columns.append((plus-minus)/max(ap+am,1e-12))
  J=np.column_stack(columns);u=lsq_linear(np.r_[J,np.eye(48)*.025],np.r_[-f0,np.zeros(48)],bounds=(-1.5,1.5),tol=1e-9).x;top=np.argsort(np.linalg.norm(J,axis=0))[-16:];sparse=np.zeros(48);sparse[top]=lsq_linear(np.r_[J[:,top],np.eye(16)*.025],np.r_[-f0,np.zeros(16)],bounds=(-1.5,1.5),tol=1e-9).x
  (R/'ACTUAL_DERIVATIVE_PROPOSALS.json').write_text(json.dumps(dict(all48_direction=u.tolist(),strongest16_direction=sparse.tolist(),step=step.tolist(),physical_feature_vector_norms_verified=True,actual_native_DLL_for_every_derivative=True,original_acceptance_criterion_unchanged=True),indent=2)+'\n');proposals=[]
  for mode,direction in [('all48',u),('strong16',sparse)]:
   for fraction in [.125,.25,.5,.75,1.]:
    v=origin+step*direction*fraction
    if curve(v)is not None:proposals.append((f'joint-{mode}-{fraction}',v))
  for k,unit in enumerate(qmc.LatinHypercube(48,seed=2026102610).random(64)):
   v=origin+(unit*2-1)*step*[.25,.5,1,2][k%4]
   if curve(v)is not None:proposals.append((f'coupled-LHS-{k}',v))
  for k,row in enumerate(executor.map(evaluate,proposals)):
   if k%8==0:record('actual_joint_WaveShaper48_candidate_renders',control_mean=baseline['loss'],best_mean=min(r['loss']for r in rows if r['stereo_preservation_passed']))
 (R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));eligible=sorted([r for r in rows if r['stereo_preservation_passed']],key=lambda r:r['loss'])[:4];finalists=[evaluate(('fresh-finalist-'+str(k),row['curve_vector']),12,False)for k,row in enumerate(eligible)];winner=min(finalists,key=lambda r:r['loss']);ready=bool(winner['curve_vector']!=origin.tolist()and baseline['loss']-winner['loss']>.0003 and winner['stereo_preservation_passed']);(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(dict(winner=winner,control_mean=baseline['loss'],sufficient_screen=ready),indent=2)+'\n');summary=dict(training_cases=len(rows),baseline=baseline,winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,v83_Finish_not_used=True,only_native_WS48_curve_changed=True,only_three_held_notes=True,not_adopted=True,reference_match_reached=False,requires_latest_main_context_revalidation=True)
 if ready:
  record('first6_AND_first10_plus_two_cold_native_WaveShaper48_validation');c0,p0,z0=clients[0];c1,p1,z1=clients[1];configure(c0,origin);configure(c1,winner['curve_vector']);captures=[];members=[]
  with tarfile.open(R/'TWELVE_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in [10,11]:c0.close();c1.close();c0=native('OriginalWS48refine03-cold-control-'+str(rep));c1=native('OriginalWS48refine03-cold-candidate-'+str(rep));configure(c0,origin);configure(c1,winner['curve_vector']);clients[0]=(c0,p0,z0);clients[1]=(c1,p1,z1)
    raw0,_=c0.render();old=cascade(raw0,p0,z0);d0,g=assess(old);raw1,_=c1.render();out=cascade(raw1,p1,z1);d1,g=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
    for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
  delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));sem10=float(np.std(delta[:10],ddof=1)/np.sqrt(10));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and np.mean(delta[:10])>max(.0005,3*sem10)and min(delta[10:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures));newseed=native_case(winner['curve_vector']);newdir=R/'saved-native-bundle';manifest=[]
  for row in bundle['manifest']:
   p=newdir/row['state'];p.parent.mkdir(parents=True,exist_ok=True);c1.save_state(row['node'],p)
   if row['node']!=0:assert p.read_bytes()==(bundledir/row['state']).read_bytes(),('unrelated native state changed',row['node'])
   manifest.append(dict(row,state_bytes=p.stat().st_size,state_SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
  newseed['native_saved_state_bundle']=dict(bundle,directory=str(newdir),manifest=manifest,settings_SHA256=native_dsp_settings_SHA256(newseed['x'],newseed));c1.set(3,1,0);expected,_=c1.render();fresh=NativeChain(seed['source_manifest']['native_input'],'OriginalWS48refine03-independent-state-replay',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
  try:
   apply_candidate(fresh,np.array(newseed['x']),newseed)
   for key,value in newseed['chorus_overrides'].items():fresh.set(3,int(key),int(value))
   fresh.set(3,1,0);again,_=fresh.render();error=float(abs(again-expected).max());assert error<=2e-7,error
  finally:fresh.close()
  with tarfile.open(R/'TWELVE_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),first10_mean_improvement=float(np.mean(delta[:10])),first10_SEM=sem10,required_first10=max(.0005,3*sem10),cold2_improvements=delta[10:].tolist(),robust_improvement=robust,other11_native_states_byte_exact=True,independent_native_zero_depth_state_replay_max_abs_error=error);(R/'NATIVE_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(newseed,indent=2)+'\n');(R/'COMBINED_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(dict(prior,native_base=newseed,loss=float(np.mean([r['candidate']['loss']for r in captures[:6]])),not_adopted_until_supported_export=True),indent=2)+'\n')
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_native_WaveShaper48_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['baseline','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_main_and_accepted_kit',error=traceback.format_exc());raise
finally:
 for c,p,z in clients:c.close();p.close();z.close()
