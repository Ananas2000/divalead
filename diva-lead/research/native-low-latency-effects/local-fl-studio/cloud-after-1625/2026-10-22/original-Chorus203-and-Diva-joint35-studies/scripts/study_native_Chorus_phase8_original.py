"""Actual native Chorus7 + source phase1 against the original, normal FX only.

The canonical fine32 WaveShaper, EQ, matrix, wet routing, Diva281 and both ZL
states remain fixed. Any screen win requires fresh6/cold2 and saved-state replay.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,tarfile,threading,traceback
import numpy as np,soundfile as sf
from scipy.stats import qmc
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=Path('/tmp/divalead-original-Chorus-phase8-20261025-01');ROOT.mkdir(exist_ok=False);STATE=N/'ORIGINAL_NATIVE_CHORUS_PHASE8_STUDY.json'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];base=np.array(seed['x']);bundle=seed['native_saved_state_bundle'];bundle_root=Path(bundle['directory']);origin=np.r_[base[86:93],base[94]];scales=np.array([1024,5000,1024,5000,5000,5000,5000,1]);hi=np.r_[np.ones(7),4096.];steps=np.array([.012,.015,.015,.02,.02,.02,.015,24.])
for name,key in [('PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(ROOT/name).write_bytes(Path(prior[key]).read_bytes())
(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal();reg=float(np.sum(base[:28]**2))*.00000025;ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);np.testing.assert_array_equal(ref,a.REF);freq=np.fft.rfftfreq(len(ref),1/48000);masks=[(freq>=lo)&(freq<hi)for lo,hi in [(300,800),(2000,5000),(5000,10000),(10000,14000)]]
def lr(y):
 p=abs(np.fft.rfft(y,axis=0))**2;return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref)
def assess(y):
 r=features.residual(y[:288000]);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));balance=lr(edit);upper=float(np.sqrt(np.mean((balance[1:]-target[1:])**2)));low=abs(float(balance[0]-target[0]));return dict(loss=float(r@r)+reg,assessment=features.local.last,LR_dB=balance.tolist(),stereo_preservation_passed=bool(upper<=1.5 and max(abs(balance[1:]))<=1.6 and low<=3.35))
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,base,seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 return c
def quant(v):return np.round(np.clip(v,0,hi)*scales)/scales
def configure(c,v):
 v=quant(v)
 for node in [3,13,14]:c.load_state(node,bundle_root/next(row['state']for row in bundle['manifest']if row['node']==node))
 for j,index in enumerate([0,1,2,3,4,5,10]):c.set(3,index,int(round(v[j]*scales[j])))
 c.set(13,5,int(round(v[7])));c.set(14,5,-int(round(v[7])))
def cascade(raw,p,z):
 p.load(ROOT/'PRIMARY.bin');z.load(ROOT/'POST.bin');middle,_=p.render(raw);out,_=z.render(middle);assert p.latency()+z.latency()==0;return out
clients=[];pool=queue.Queue();mutex=threading.Lock();rows=[]
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(ROOT),cases=len(rows),actual_native_hosts=[c.proc.pid for c,p,z in clients],actual_ZL_hosts=[v.child.pid for c,p,z in clients for v in [p,z]],only_native_Chorus7_and_source_phase1_varied=True,source_MIDI_ARP_ADSR_wet_routing_WSfine32_and_both_ZL_unchanged=True,original_is_the_only_target=True,v83_Finish_not_used=True,reference_match_reached=False,not_adopted=True,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def evaluate(case,reps=4,keep=True):
 label,v=case;v=quant(v);c,p,z=pool.get()
 try:
  configure(c,v);captures=[]
  for k in range(reps):raw,_=c.render();out=cascade(raw,p,z);captures.append(assess(out))
  median=int(np.argsort([r['loss']for r in captures])[len(captures)//2]);row=dict(label=label,vector=v.tolist(),loss=float(np.mean([r['loss']for r in captures])),realization_losses=[r['loss']for r in captures],stereo_preservation_passed=all(r['stereo_preservation_passed']for r in captures),assessment=captures[median])
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,p,z))
def add(tar,name,y,members):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');b=f.getvalue();i=tarfile.TarInfo(name);i.size=len(b);tar.addfile(i,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
try:
 record('starting_actual_native_Chorus_source_phase_screen')
 for k in range(2):
  c=native('OriginalChorus8-native-'+str(k));p=WinVST3('OriginalChorus8-primary-'+str(k));z=WinVST3('OriginalChorus8-post-'+str(k));clients.append((c,p,z));pool.put((c,p,z))
 baseline=evaluate(('unchanged-control',origin),12);current=baseline;cases=[]
 for k,u in enumerate(qmc.LatinHypercube(8,seed=2026102541).random(96)):cases.append((f'coupled-{k}',origin+(u*2-1)*steps*[.5,1,2,4][k%4]))
 for value in [0,512,1024,1536,1792,2048,2304,2560,3072,4096]:v=origin.copy();v[7]=value;cases.append((f'source-phase-{value}',v))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if row['stereo_preservation_passed']and row['loss']<current['loss']:current=row
   if k%8==0:record('actual_native_Chorus_phase_joint_screen',control_mean=baseline['loss'],best_mean=current['loss'],best_vector=current['vector'])
  for sweep in range(3):
   for j in range(8):
    cases=[]
    for factor in [-2,-1,1,2]:v=np.array(current['vector']);v[j]+=factor*steps[j]*(.55**sweep);cases.append((f'axis-{sweep}-{j}-{factor}',v))
    checked=list(executor.map(evaluate,cases));valid=[r for r in checked if r['stereo_preservation_passed']]
    if valid and min(valid,key=lambda r:r['loss'])['loss']<current['loss']:current=min(valid,key=lambda r:r['loss'])
    record('actual_native_Chorus_phase_coordinate_fit',sweep=sweep,coordinate=j,control_mean=baseline['loss'],best_mean=current['loss'])
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));unique=[];seen=set()
 for row in sorted(rows,key=lambda r:r['loss']):
  key=tuple(row['vector'])
  if row['stereo_preservation_passed']and key not in seen:unique.append(row);seen.add(key)
  if len(unique)==3:break
 finalists=[evaluate(('fresh-finalist-'+str(i),row['vector']),12,False)for i,row in enumerate(unique)];winner=min(finalists,key=lambda r:r['loss']);ready=bool(winner['vector']!=origin.tolist()and baseline['loss']-winner['loss']>.0003 and winner['stereo_preservation_passed'])
 (ROOT/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(dict(winner=winner,control_mean=baseline['loss'],sufficient_screen=ready,original_is_the_only_target=True),indent=2)+'\n')
 summary=dict(training_cases=len(rows),baseline=baseline,winner=winner,sufficient_screen=ready,robust_improvement=False,only_native_Chorus7_source_phase1_changed=True,original_is_the_only_target=True,v83_Finish_not_used=True,only_three_held_notes=True,requires_latest_main_context_revalidation=True,not_adopted=True,reference_match_reached=False)
 if ready:
  record('fresh_six_plus_two_cold_native_Chorus_phase_pairs',selected=winner['vector']);c0,p0,z0=clients[0];c1,p1,z1=clients[1];configure(c0,origin);configure(c1,winner['vector']);captures=[];members=[]
  with tarfile.open(ROOT/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(8):
    if rep in [6,7]:
     c0.close();c1.close();c0=native('OriginalChorus8-cold-control-'+str(rep));c1=native('OriginalChorus8-cold-candidate-'+str(rep));configure(c0,origin);configure(c1,winner['vector']);clients[0]=(c0,p0,z0);clients[1]=(c1,p1,z1)
    r0,_=c0.render();old=cascade(r0,p0,z0);d0=assess(old);r1,_=c1.render();out=cascade(r1,p1,z1);d1=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
    for label,y in [('native-control',r0),('native-candidate',r1),('control',old),('candidate',out)]:add(tar,f'{label}-{rep}.wav',y,members)
    if rep==0:
     for label,y in [('NATIVE_CONTROL',r0),('NATIVE_CANDIDATE',r1),('CONTROL',old),('CANDIDATE',out)]:sf.write(ROOT/(label+'_00.wav'),y,48000,subtype='FLOAT')
  delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures));new_x=base.copy();new_x[86:93]=winner['vector'][:7];new_x[94]=winner['vector'][7];new_seed=dict(seed,x=new_x.tolist());destination=ROOT/'saved-native-bundle';new_manifest=[]
  for row in bundle['manifest']:
   p=destination/row['state'];p.parent.mkdir(parents=True,exist_ok=True);c1.save_state(row['node'],p)
   if row['node']not in [3,13,14]:assert p.read_bytes()==(bundle_root/row['state']).read_bytes(),('unrelated native state changed',row['node'])
   new_manifest.append(dict(row,state_bytes=p.stat().st_size,state_SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
  new_seed['native_saved_state_bundle']=dict(bundle,directory=str(destination),manifest=new_manifest,settings_SHA256=native_dsp_settings_SHA256(new_seed['x'],new_seed))
  c1.set(3,1,0);expected,_=c1.render();fresh=NativeChain(seed['source_manifest']['native_input'],'OriginalChorus8-independent-state-replay',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
  try:
   apply_candidate(fresh,new_x,new_seed)
   for key,value in new_seed['chorus_overrides'].items():fresh.set(3,int(key),int(value))
   fresh.set(3,1,0);again,_=fresh.render();error=float(abs(again-expected).max());assert error<=2e-7,error
  finally:fresh.close()
  with tarfile.open(ROOT/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in members:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,unrelated_native_states_byte_exact=True,independent_native_zero_depth_replay_max_abs_error=error)
  (ROOT/'NATIVE_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(new_seed,indent=2)+'\n');choice=dict(prior,native_base=new_seed,loss=float(np.mean([r['candidate']['loss']for r in captures[:6]])),not_adopted_until_supported_export=True);(ROOT/'COMBINED_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(choice,indent=2)+'\n')
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_native_Chorus_phase_screen_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['baseline','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_accepted_kit_and_main',error=traceback.format_exc());raise
finally:
 for c,p,z in clients:c.close();p.close();z.close()
