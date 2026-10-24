"""Actual native Chorus/phase/mix fit in fixed current real ZL context.

Research runs beside main without modifying its candidate or owned controls.
Any win must later be revalidated against the then-current main component.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,tarfile,threading,traceback
import numpy as np
import soundfile as sf
from scipy.stats import qmc
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import D,WinVST3
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-native-Chorus9-after-ZL22-02';ROOT.mkdir(exist_ok=False)
STATE=N/'ZL_NATIVE_CHORUS9_CURRENT22_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();prior=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];base=np.array(seed['x']);assert len(base)==95
component=ROOT/'UNCHANGED_ZL_COMPONENT.bin';component.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
origin=base[86:95].copy();steps=np.array([.015,.018,.018,.025,.025,.025,.018,.012,64.]);scales=np.array([1024,5000,1024,5000,5000,5000,5000,12800,1.]);hi=np.r_[np.ones(8),4096.]
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_native_hosts=[c.proc.pid for c,z in clients],actual_VST3_hosts=[z.child.pid for c,z in clients],only_three_held_notes=True,source_Diva_and_ZL_component_unchanged=True,main_candidate_not_modified=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def quant(v):return np.round(np.clip(v,0,hi)*scales)/scales
def native_case(v):
 x=base.copy();x[86:95]=quant(v);return dict(seed,x=x.tolist())
def configure(c,v):
 case=native_case(v);apply_candidate(c,np.array(case['x']),case)
 for key,value in case['chorus_overrides'].items():c.set(3,int(key),int(value))
def score(y):
 r=features.residual(y[:288000]);return float(r@r)+float(np.sum(base[:28]**2))*.00000025
def evaluate(case,reps=4,save=True):
 label,v=case;v=quant(v);c,z=pool.get()
 try:
  configure(c,v);losses=[];assessments=[]
  for rep in range(reps):
   raw,status=c.render();out,zstatus=z.render(raw);losses.append(score(out));assessments.append(features.local.last)
  row=dict(label=label,chorus_phase9=v.tolist(),loss=float(np.mean(losses)),realization_losses=losses,assessment=assessments[np.argsort(losses)[len(losses)//2]])
  if save:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,z))
main=json.loads((N/'FL20_ZL_CONTINUOUS_CONTROLLER.json').read_text());proc=Path('/proc')/str(main['owner']['PID']);assert not proc.exists()or(proc/'stat').read_text().split()[2]=='Z'
try:
 record('starting_actual_native_Chorus9_with_current_ZL')
 for k in range(4):
  c=NativeChain(seed['source_manifest']['native_input'],f'ZL-native-Chorus9-current22-worker-{k}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');z=WinVST3(f'ZL-native-Chorus9-current22-VST3-{k}');z.load(component);clients.append((c,z));pool.put((c,z))
 baseline=evaluate(('unchanged-control',origin),12);current=baseline;cases=[]
 for mix in [.2,.35,.5,.65]:
  for phase in [0,1024,2048,2149,3072,4096]:
   v=origin.copy();v[7]=mix;v[8]=phase;cases.append((f'broad-mix-phase-{mix}-{phase}',v))
 for k,u in enumerate(qmc.LatinHypercube(9,seed=2026102471).random(96)):cases.append((f'coupled-LHS-{k}',origin+(u*2-1)*steps*[.5,1,2,4][k%4]))
 with concurrent.futures.ThreadPoolExecutor(4)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if row['loss']<current['loss']:current=row
   if k%4==0:record('actual_native_Chorus9_coupled_candidates',best_training_mean=current['loss'],control_mean=baseline['loss'])
  for sweep in range(3):
   for j in range(9):
    cases=[]
    for factor in [-2,-1,1,2]:
     v=np.array(current['chorus_phase9']);v[j]+=factor*steps[j]*(.55**sweep);cases.append((f'coordinate-{sweep}-{j}-{factor}',v))
    selected=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
    if selected['loss']<current['loss']-.00015:current=selected
    record('actual_native_Chorus9_coordinate_refinement',sweep=sweep,coordinate=j,best_training_mean=current['loss'],control_mean=baseline['loss'])
 finalists=[evaluate(('new-finalist-'+r['label'],r['chorus_phase9']),12,False)for r in sorted(rows,key=lambda r:r['loss'])[:4]];winner=min(finalists,key=lambda r:r['loss']);shape=np.array(winner['chorus_phase9'])
 c0,z0=clients[0];c1,z1=clients[1];configure(c0,origin);configure(c1,shape);captures=[];audio=[];native_losses=[];record('twelve_new_actual_Chorus_control_candidate_pairs')
 for rep in range(12):
  raw0,_=c0.render();old,_=z0.render(raw0);loss0=score(old);raw1,_=c1.render();out,_=z1.render(raw1);loss1=score(out);assessment=features.local.last;native_losses.append(score(raw1));captures.append(dict(rep=rep,base_loss=loss0,loss=loss1,assessment=assessment));audio.append((old,out));record('twelve_new_actual_Chorus_control_candidate_pairs',completed_pairs=rep+1)
 delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(12));robust=bool(np.mean(delta)>max(.0005,3*sem));states=ROOT/'actual-native-states';states.mkdir();nodes=[0,3,4,5,6,7,8,10,11,12,13,14]
 for node in nodes:c1.save_state(node,states/f'{node}.bin')
 c1.set(3,1,0);expected,_=c1.render();configure(c0,shape)
 for node in nodes:c0.load_state(node,states/f'{node}.bin');c0.save_state(node,states/f'{node}-resaved.bin');assert(states/f'{node}.bin').read_bytes()==(states/f'{node}-resaved.bin').read_bytes()
 c0.set(3,1,0);actual,_=c0.render();error=float(abs(actual-expected).max());assert error<=2e-7,error
 z1.save(ROOT/'UNCHANGED_ZL_COMPONENT_RESAVED.bin');assert component.read_bytes()==(ROOT/'UNCHANGED_ZL_COMPONENT_RESAVED.bin').read_bytes();assert z1.latency()==0
 members=[];archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
 with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
  for rep,pair in enumerate(audio):
   for label,y in zip(['control','candidate'],pair):
    out=io.BytesIO();sf.write(out,y,48000,format='WAV',subtype='FLOAT');blob=out.getvalue();name=f'{label}-{rep}.wav';entry=tarfile.TarInfo(name);entry.size=len(blob);tar.addfile(entry,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
 with tarfile.open(archive)as tar:
  for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 median=sorted(range(12),key=lambda k:captures[k]['loss'])[6];selected=ROOT/'SELECTED_COMBINED_WIP.wav';sf.write(selected,audio[median][1],48000,subtype='FLOAT')
 summary=dict(cohort='native-Chorus9-current22-study',training_cases=len(rows),training_control_mean=baseline['loss'],training_candidate_mean=current['loss'],current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,all12_native_saved_states_byte_exact=True,native_zero_depth_replay_max_abs_error=error,ZL_component_unchanged=True,only_three_held_notes=True,requires_latest_main_component_revalidation=False,incumbent_fixed_at_owned_completed_boundary=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,captures=captures,archive_members=members)
 native=native_case(shape);native.update(loss=float(np.mean(native_losses)),full_fresh_native_realizations=12,full_fresh_native_validation_pending=False,native_parameters_refitted_in_ZL_context=True,robust_improvement_joint_ZL=robust)
 proposal=dict(prior,native_base=native,loss=summary['candidate_mean'],native_ZL_component_state=str(component),recorded_audio=str(selected),native_parameters_changed=True,not_automatically_adopted_into_main_or_public_FL_project=True)
 (ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
 for name,o in [('completion.json',summary),('CANDIDATE_COMBINED_RESEARCH_ONLY.json',proposal),('NATIVE_CANDIDATE_FOR_EXPORT.json',native)]: (ROOT/name).write_text(json.dumps(o,indent=2)+'\n')
 record('native_Chorus9_context_study_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});(ROOT/'ACTUAL_STUDY_CONTROLLER_SNAPSHOT.json').write_bytes(STATE.read_bytes());print('NATIVE_CHORUS9_CURRENT_ZL_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 record('failed_keep_prior_main_and_all_public_kits',error=traceback.format_exc());raise
finally:
 for c,z in clients:c.close();z.close()
