"""Actual stock WaveShaper Pre/Mix/Post in current normal two-ZL chain.

Only three measured raw controls vary; the actual canonical fine32 curve,
other11 native states, Diva281, three incoming notes and both ZLs are fixed.
The uploaded original is the only target. No v83/Finish transfer objective.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,tarfile,threading,traceback
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=Path('/tmp/divalead-original-target-native-WScontrols-20261025-01');ROOT.mkdir(exist_ok=False)
STATE=N/'ORIGINAL_TARGET_NATIVE_WS_CONTROLS_STUDY.json';prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert prior['accepted_full_public_kit']=='ZL26';seed=prior['native_base'];bundle=seed['native_saved_state_bundle'];base=Path(bundle['directory']);ws=next(row for row in bundle['manifest']if row['node']==0);ws_state=base/ws['state'];controls=seed['waveshaper_native_controls'];assert controls==[128,128,128]
assert json.loads((N/'zl-stereo-continuation.stop').read_text())['owner']=='original-reference-tone-finite-20261025'
for name,key in [('PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(ROOT/name).write_bytes(Path(prior[key]).read_bytes())
(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal();reg=float(np.sum(np.array(seed['x'])[:28]**2))*.00000025;ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);np.testing.assert_array_equal(ref,a.REF);freq=np.fft.rfftfreq(len(ref),1/48000);masks=[(freq>=lo)&(freq<hi)for lo,hi in [(300,800),(2000,5000),(5000,10000),(10000,14000)]]
def lr(y):
 power=abs(np.fft.rfft(y,axis=0))**2;return np.array([10*np.log10(power[m,0].sum()/power[m,1].sum())for m in masks])
target=lr(ref)
def assessment(y):
 r=features.residual(y[:288000]);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));balance=lr(edit);upper=float(np.sqrt(np.mean((balance[1:]-target[1:])**2)));low=abs(float(balance[0]-target[0]))
 return dict(loss=float(r@r)+reg,assessment=features.local.last,LR_dB=balance.tolist(),stereo_preservation_passed=bool(upper<=1.5 and max(abs(balance[1:]))<=1.6 and low<=3.35))
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 return c
def configure(c,v):
 v=list(map(int,v));assert 64<=v[0]<=192 and 0<=v[1]<=128 and 0<=v[2]<=128;c.load_state(0,ws_state)
 for j,value in enumerate(v):c.set(0,j,value)
def cascade(raw,p,z):
 p.load(ROOT/'PRIMARY.bin');z.load(ROOT/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return out
clients=[];pool=queue.Queue();mutex=threading.Lock();rows=[]
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(ROOT),cases=len(rows),actual_native_hosts=[c.proc.pid for c,p,z in clients],actual_ZL_hosts=[v.child.pid for c,p,z in clients for v in [p,z]],only_three_held_notes=True,original_is_the_only_target=True,v83_Finish_not_used=True,only_native_WS_three_controls_varied=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def evaluate(case,reps=4,keep=True):
 label,v=case;v=list(map(int,v));c,p,z=pool.get()
 try:
  configure(c,v);captures=[]
  for k in range(reps):raw,_=c.render();out=cascade(raw,p,z);captures.append(assessment(out))
  row=dict(label=label,controls=v,loss=float(np.mean([r['loss']for r in captures])),realization_losses=[r['loss']for r in captures],stereo_preservation_passed=all(r['stereo_preservation_passed']for r in captures),assessment=captures[len(captures)//2])
  if keep:
   with mutex:rows.append(row);record('actual_native_WS_control_screen',latest=label,mean=row['loss'],best=min(r['loss']for r in rows))
  return row
 finally:pool.put((c,p,z))
def add(tar,name,y,members):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');b=f.getvalue();entry=tarfile.TarInfo(name);entry.size=len(b);tar.addfile(entry,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
try:
 record('starting_actual_native_WS_control_search')
 for k in range(2):
  c=native('OriginalWS-native-'+str(k));p=WinVST3('OriginalWS-primary-'+str(k));z=WinVST3('OriginalWS-post-'+str(k));clients.append((c,p,z));pool.put((c,p,z))
 baseline=evaluate(('unchanged-control',controls),8);current=baseline
 cases=[(f'pre{pre}-mix{mix}',[pre,mix,128])for pre in [112,120,124,128,132,136,144]for mix in [80,96,112,120,128]if[pre,mix,128]!=controls]
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  checked=list(executor.map(evaluate,cases));allowed=[r for r in checked if r['stereo_preservation_passed']]
  if allowed and min(allowed,key=lambda r:r['loss'])['loss']<current['loss']:current=min(allowed,key=lambda r:r['loss'])
  for sweep in range(2):
   for j,step in enumerate([2,4,2]):
    cases=[]
    for factor in [-2,-1,1,2]:
     v=list(current['controls']);v[j]+=int(factor*step/(sweep+1))
     if 64<=v[0]<=192 and 0<=v[1]<=128 and 0<=v[2]<=128:cases.append((f'fine-{sweep}-{j}-{factor}',v))
    checked=list(executor.map(evaluate,cases));allowed=[r for r in checked if r['stereo_preservation_passed']]
    if allowed and min(allowed,key=lambda r:r['loss'])['loss']<current['loss']:current=min(allowed,key=lambda r:r['loss'])
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
 unique=[];seen=set()
 for row in sorted(rows,key=lambda r:r['loss']):
  key=tuple(row['controls'])
  if row['stereo_preservation_passed']and key not in seen:unique.append(row);seen.add(key)
  if len(unique)==3:break
 finalists=[evaluate(('fresh-finalist-'+str(i),row['controls']),8,False)for i,row in enumerate(unique)];winner=min(finalists,key=lambda r:r['loss']);ready=bool(winner['controls']!=controls and baseline['loss']-winner['loss']>.0003 and winner['stereo_preservation_passed'])
 (ROOT/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(dict(winner=winner,control_mean=baseline['loss'],sufficient_screen=ready,original_is_the_only_target=True),indent=2)+'\n');summary=dict(training_cases=len(rows),baseline=baseline,winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,v83_Finish_not_used=True,only_native_WS_three_controls_varied=True,only_three_held_notes=True,not_adopted=True,reference_match_reached=False)
 if ready:
  record('fresh_six_plus_two_cold_actual_native_paired_validation',winner=winner['controls']);c0,p0,z0=clients[0];c1,p1,z1=clients[1];configure(c0,controls);configure(c1,winner['controls']);captures=[];members=[]
  with tarfile.open(ROOT/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(8):
    if rep in [6,7]:
     c0.close();c1.close();c0=native('OriginalWS-cold-control-'+str(rep));c1=native('OriginalWS-cold-candidate-'+str(rep));configure(c0,controls);configure(c1,winner['controls']);clients[0]=(c0,p0,z0);clients[1]=(c1,p1,z1)
    r0,_=c0.render();old=cascade(r0,p0,z0);d0=assessment(old);r1,_=c1.render();out=cascade(r1,p1,z1);d1=assessment(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
    for label,y in [('native-control',r0),('native-candidate',r1),('control',old),('candidate',out)]:add(tar,f'{label}-{rep}.wav',y,members)
    if rep==0:
     for label,y in [('NATIVE_CONTROL',r0),('NATIVE_CANDIDATE',r1),('CONTROL',old),('CANDIDATE',out)]:sf.write(ROOT/(label+'_00.wav'),y,48000,subtype='FLOAT')
  delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  destination=ROOT/'saved-native-bundle';new_seed=dict(seed,waveshaper_native_controls=winner['controls']);new_manifest=[]
  for row in bundle['manifest']:
   dst=destination/row['state'];dst.parent.mkdir(parents=True,exist_ok=True);c1.save_state(row['node'],dst)
   if row['node']!=0:assert dst.read_bytes()==(base/row['state']).read_bytes(),('unrelated native state changed',row['node'])
   new_manifest.append(dict(row,state_bytes=dst.stat().st_size,state_SHA256=hashlib.sha256(dst.read_bytes()).hexdigest()))
  new_seed['native_saved_state_bundle']=dict(bundle,directory=str(destination),manifest=new_manifest,settings_SHA256=native_dsp_settings_SHA256(new_seed['x'],new_seed))
  # Exact saved native state transfer on an independent canonical full chain.
  c1.set(3,1,0);expected,_=c1.render();fresh=NativeChain(seed['source_manifest']['native_input'],'OriginalWS-independent-state-replay',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
  try:
   apply_candidate(fresh,np.array(new_seed['x']),new_seed)
   for key,value in seed['chorus_overrides'].items():fresh.set(3,int(key),int(value))
   fresh.set(3,1,0);again,_=fresh.render();error=float(abs(again-expected).max());assert error<=2e-7,error
  finally:fresh.close()
  with tarfile.open(ROOT/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in members:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,only_WS_state_changed_among12=True,independent_native_zero_depth_replay_max_abs_error=error)
  (ROOT/'NATIVE_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(new_seed,indent=2)+'\n');choice=dict(prior,native_base=new_seed,loss=float(np.mean([r['candidate']['loss']for r in captures[:6]])),not_adopted_until_supported_export=True);(ROOT/'COMBINED_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(choice,indent=2)+'\n')
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_native_WS_control_study_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['baseline','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_accepted_full26',error=traceback.format_exc());raise
finally:
 for c,p,z in clients:c.close();p.close();z.close()
