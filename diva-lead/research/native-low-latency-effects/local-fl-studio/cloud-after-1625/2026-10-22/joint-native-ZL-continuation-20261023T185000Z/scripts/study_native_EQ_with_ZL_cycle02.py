"""Refit actual native EQ76 in the CURRENT real ZL context.
Training uses actual WS/Chorus/phase prefix captures, never reference samples.
Fresh whole native+ZL renders, heldouts and state replay gate any adoption.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,struct,tarfile,threading,time,traceback
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply
from fl20_curve import apply_candidate
from win_vst3 import D,WinVST3
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-native-EQ76-after-ZL13-02';ROOT.mkdir(exist_ok=False)
OWNER='native-and-ZL-finite-refit-20261023';PAUSE=N/'fl20-corrected-search.pause';STATE=N/'ZL_NATIVE_EQ76_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
f=FeaturesOriginal();prior=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];origin=np.array(seed['x']);INPUT=seed['source_manifest']['native_input']
component=ROOT/'UNCHANGED_ZL_COMPONENT.bin';component.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
clients=[];fullclients=[];pool=queue.Queue();rows=[];mutex=threading.Lock();started=time.monotonic()
def read(p):return json.loads(Path(p).read_text())
def identity(pid):
 try:
  p=Path(f'/proc/{pid}');s=(p/'stat').read_text().split()
  if s[2]=='Z':return None
  return dict(PID=pid,starttime=s[21],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
 except FileNotFoundError:return None
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,root=str(ROOT),actual_native_hosts=[identity(c.proc.pid)for c,z in clients],actual_VST3_hosts=[identity(z.child.pid)for c,z in clients],calls=len(rows),only_three_held_notes=True,source_and_ZL_component_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def full(tag,v=origin):
 c=NativeChain(INPUT,tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,v,seed)
 for k,val in seed['chorus_overrides'].items():c.set(3,int(k),int(val))
 return c
def eq(c,v,phase=0):
 c.load_input(ROOT/f'prefix-{phase}.wav');apply(c,v[:86]);c.bypass(0,True);c.bypass(3,True);c.gain(0,1);c.gain(1,0)
def quant(v):
 v=np.array(v,float).copy();v[:30]=np.round(np.clip(v[:30],-18,18)*100)/100;v[30:34]=np.round(np.clip(v[30:34],-1,1)*12800)/12800
 v[34:62]=np.clip(v[34:62],-.9,.9);v[62:76]=np.round(np.clip(v[62:76],.005,.85)*65536)/65536
 return v
def score(y,v):
 a=f.residual(y[:288000]);return float(a@a)+float(np.sum(v[:28]**2))*.00000025

def evaluate(case,phase=0,save=True):
 label,v=case;v=quant(v);c,z=pool.get()
 try:
  eq(c,v,phase);raw,status=c.render();out,zstatus=z.render(raw);loss=score(out,v);assert z.latency()==0
  row=dict(label=label,x=v.tolist(),loss=loss,assessment=f.local.last,native_status=status,VST3_status=zstatus)
  if save:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,z))

assert not identity(read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID'])
with PAUSE.open('x')as p:json.dump(dict(owner=OWNER,reason='finite actual native EQ76 refit in fixed actual ZL context; previous complete kits preserved'),p)
try:
 record('actual_prefix_generation_and_zero_depth_routing_validation')
 prefix=full('ZL-native-EQ76-cycle02-prefix');control=full('ZL-native-EQ76-cycle02-zero-native-control');fullclients.extend([prefix,control])
 for node in [4,5,6,7,8,10,11,12]:prefix.bypass(node,True)
 prefix.gain(3,1);prefix.gain(4,0)
 for k in range(3):y,_=prefix.render();sf.write(ROOT/f'prefix-{k}.wav',y,48000,subtype='FLOAT')
 prefix.set(3,1,0);zero_prefix,_=prefix.render();sf.write(ROOT/'prefix-3.wav',zero_prefix,48000,subtype='FLOAT');control.set(3,1,0);zero_control,_=control.render()
 prefix.close();control.close();fullclients.clear()
 for k in range(4):
  c=NativeChain(ROOT/'prefix-0.wav',f'ZL-native-EQ76-cycle02-worker-{k}',fl_graph=True,engine_override='fl_native_source_variants_host.exe');z=WinVST3(f'ZL-native-EQ76-cycle02-real-VST3-{k}');z.load(component);clients.append((c,z));pool.put((c,z))
 eq(clients[0][0],origin,3);zero_eq,_=clients[0][0].render();routing_error=float(abs(zero_eq-zero_control).max());assert routing_error<=2e-7,routing_error
 (ROOT/'PREFIX_ROUTING_PROOF.json').write_text(json.dumps(dict(actual_native_zero_depth_prefix_to_full_routing_max_abs_error=routing_error,absolute_tolerance=2e-7,no_reference_samples_in_any_effect=True,WS_Chorus_source_phase_bypassed_only_in_training_replay=True,original_source_and_external_notes_unchanged=True),indent=2)+'\n')
 current=evaluate(('initial-control',origin));baseline=current;steps=np.r_[np.full(28,.4),[.2,.2],np.full(4,.02),np.full(28,.018),np.full(14,.012)];rng=np.random.default_rng(2026102376)
 with concurrent.futures.ThreadPoolExecutor(4)as executor:
  for sweep in range(4):
   # Coupled main gain/matrix/EQ proposals, still actual native DLL audio.
   cases=[]
   for trial in range(48):
    v=np.array(current['x']);indices=rng.choice(76,size=int(rng.choice([2,4,8,16])),replace=False);v[indices]+=rng.normal(size=len(indices))*steps[indices]*float(rng.choice([.5,1,2]))*(.7**sweep);cases.append((f'coupled-{sweep}-{trial}',v))
   selected=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
   if selected['loss']<current['loss']:current=selected
   for j in rng.permutation(76):
    cases=[]
    for factor in [-2,-1,1,2]:
     v=np.array(current['x']);v[j]+=factor*steps[j]*(.65**sweep);cases.append((f'axis-{sweep}-{j}-{factor}',v))
    selected=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
    if selected['loss']<current['loss']:current=selected
    record('actual_native_EQ76_and_fixed_ZL_fit',sweep=sweep,best_training_loss=current['loss'],control_training_loss=baseline['loss'])
 held=[]
 for phase in [1,2]:held.append(dict(phase=phase,control=evaluate(('heldout-control',origin),phase,False),candidate=evaluate(('heldout-candidate',current['x']),phase,False)))
 (ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'heldout.json').write_text(json.dumps(held,indent=2)+'\n');(ROOT/'BEST_TRAINING.json').write_text(json.dumps(current,indent=2)+'\n')
 # Fresh complete actual chains, with independently free-running Chorus.
 chosen=np.array(current['x']);a=full('ZL-native-EQ76-cycle02-independent-control');b=full('ZL-native-EQ76-cycle02-independent-candidate',chosen);fullclients.extend([a,b]);z0=clients[0][1];z1=clients[1][1];captures=[];audio=[];native_losses=[]
 record('fresh_twelve_complete_native_plus_ZL_paired_renders')
 for rep in range(12):
  raw0,status0=a.render();old,_=z0.render(raw0);old_loss=score(old,origin);raw1,status1=b.render();out,_=z1.render(raw1);loss=score(out,chosen);assessment=f.local.last;native_only=score(raw1,chosen);native_losses.append(native_only)
  captures.append(dict(rep=rep,base_loss=old_loss,loss=loss,assessment=assessment,native_only_loss=native_only,control_status=status0,candidate_status=status1));audio.append((old,out))
 delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(len(delta)));held_gain=float(np.mean([r['control']['loss']-r['candidate']['loss']for r in held]));robust=bool(np.mean(delta)>max(.0005,3*sem)and held_gain>0)
 state_dir=ROOT/'actual-native-states';state_dir.mkdir();nodes=[0,3,4,5,6,7,8,10,11,12,13,14]
 for n in nodes:b.save_state(n,state_dir/f'{n}.bin')
 b.set(3,1,0);expected,_=b.render();fresh=full('ZL-native-EQ76-cycle02-independent-state-replay',chosen);fullclients.append(fresh)
 for n in nodes:
  fresh.load_state(n,state_dir/f'{n}.bin');fresh.save_state(n,state_dir/f'{n}-resaved.bin');assert (state_dir/f'{n}.bin').read_bytes()==(state_dir/f'{n}-resaved.bin').read_bytes()
 fresh.set(3,1,0);again,_=fresh.render();state_error=float(abs(expected-again).max());assert state_error<=2e-7,state_error
 fresh.close();fullclients.remove(fresh);z1.save(ROOT/'UNCHANGED_ZL_COMPONENT_RESAVED.bin');assert component.read_bytes()==(ROOT/'UNCHANGED_ZL_COMPONENT_RESAVED.bin').read_bytes()
 summary=dict(training_cases=len(rows),training_control=baseline['loss'],training_candidate=current['loss'],heldout_mean_gain=held_gain,current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,native_only_candidate_mean=float(np.mean(native_losses)),native_zero_depth_saved_state_replay_max_abs_error=state_error,all12_native_saved_states_byte_exact=True,ZL_component_unchanged=True,only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,captures=captures)
 members=[];archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
 with tarfile.open(archive,'w:gz',compresslevel=3)as z:
  for rep,pair in enumerate(audio):
   for label,y in zip(['control','candidate'],pair):
    buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');blob=buf.getvalue();name=f'{label}-{rep}.wav';info=tarfile.TarInfo(name);info.size=len(blob);z.addfile(info,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
 with tarfile.open(archive)as z:
  for m in members:assert hashlib.sha256(z.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 summary['archive_members']=members
 median=sorted(range(12),key=lambda k:captures[k]['loss'])[6];sf.write(ROOT/'SELECTED_COMBINED_WIP.wav',audio[median][1],48000,subtype='FLOAT')
 native_candidate=dict(seed,x=chosen.tolist(),loss=summary['native_only_candidate_mean'],full_fresh_native_realizations=12,full_fresh_native_validation_pending=False,native_parameters_refitted_in_ZL_context=True,combined_ZL_mean=summary['candidate_mean'],robust_improvement_joint_ZL=robust,source_manifest=seed['source_manifest'])
 result=dict(prior,native_base=native_candidate,loss=summary['candidate_mean'],native_ZL_component_state=str(component),recorded_audio=str(ROOT/'SELECTED_COMBINED_WIP.wav'),native_parameters_changed=True,not_automatically_adopted_into_main_or_public_FL_project=True,not_compatible_with_standard_x95_exporter=True,extended_parameter_values_are_authoritative_in_component_state=True)
 for name,o in [('completion.json',summary),('CANDIDATE_COMBINED_RESEARCH_ONLY.json',result),('NATIVE_CANDIDATE_FOR_EXPORT.json',native_candidate)]: (ROOT/name).write_text(json.dumps(o,indent=2)+'\n')
 record('finite_native_EQ76_study_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print('NATIVE_EQ76_WITH_ZL_STUDY_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 record('failed_preserve_all_prior_complete_kits',error=traceback.format_exc());raise
finally:
 for c in fullclients:c.close()
 for c,z in clients:c.close();z.close()
 if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
