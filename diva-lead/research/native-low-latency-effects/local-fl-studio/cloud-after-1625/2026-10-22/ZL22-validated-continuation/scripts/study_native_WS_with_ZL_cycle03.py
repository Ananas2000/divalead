"""Actual 16-parameter native WaveShaper study in the current full ZL chain.
All supported2+4+8 curve metadata plus original polynomial are preserved.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,struct,tarfile,threading,time,traceback
import numpy as np
import soundfile as sf
from scipy.stats import qmc
from native_chain import NativeChain
from fl20_curve import apply_candidate,extended_curve_bytes
from win_vst3 import D,WinVST3
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-native-WS16-after-EQ76-03';ROOT.mkdir(exist_ok=False)
OWNER='native-and-ZL-finite-refit-20261023';PAUSE=N/'fl20-corrected-search.pause';STATE=N/'ZL_NATIVE_WS16_STUDY_STATE.json'
EQ=D/'ZL-native-EQ76-after-ZL17-03';eq_result=json.loads((EQ/'completion.json').read_text());prior=json.loads((EQ/('CANDIDATE_COMBINED_RESEARCH_ONLY.json'if eq_result['robust_improvement']else'PRIOR_COMBINED_CANDIDATE.json')).read_text())
seed=prior['native_base'];base=np.array(seed['x']);component=ROOT/'UNCHANGED_ZL_COMPONENT.bin';component.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
f=FeaturesOriginal();clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
origin=np.r_[base[76:78],seed['waveshaper_curve_adjustment'],seed['waveshaper_local_bump_adjustment'],seed['waveshaper_detail_bump_adjustment']]
steps=np.array([.04,.04,.025,.035,.004,.006,.008,.012,.002,.003,.004,.006,.008,.010,.012,.015])
def read(p):return json.loads(Path(p).read_text())
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),only_three_held_notes=True,source_Diva_and_ZL_component_unchanged=True,actual_native_hosts=[c.proc.pid for c,z in clients],actual_VST3_hosts=[z.child.pid for c,z in clients],reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 p=STATE.with_suffix('.partial');p.write_text(json.dumps(o,indent=2)+'\n');p.replace(STATE)
def native_case(v):
 x=base.copy();x[76:78]=v[:2];return dict(seed,x=x.tolist(),waveshaper_curve_adjustment=list(v[2:4]),waveshaper_local_bump_adjustment=list(v[4:8]),waveshaper_detail_bump_adjustment=list(v[8:16]))
def valid(v):
 s=native_case(v);b=extended_curve_bytes(np.array(s['x']),s['waveshaper_curve_adjustment'],s['waveshaper_local_bump_adjustment'],s['waveshaper_detail_bump_adjustment']);y=[struct.unpack_from('<d',b,34+24*k+8)[0]for k in range(129)];return bool(np.min(np.diff(y))>=-1e-10)
def configure(c,v):
 s=native_case(v);apply_candidate(c,np.array(s['x']),s)
 for k,value in s['chorus_overrides'].items():c.set(3,int(k),int(value))
def score(y):
 a=f.residual(y[:288000]);return float(a@a)+float(np.sum(base[:28]**2))*.00000025

def evaluate(case,reps=2,save=True):
 label,v=case;v=np.asarray(v,float);c,z=pool.get()
 try:
  configure(c,v);captures=[]
  for rep in range(reps):
   raw,status=c.render();out,zstatus=z.render(raw);loss=score(out);captures.append(dict(loss=loss,audio=out,assessment=f.local.last,native_status=status,VST3_status=zstatus))
  values=[r['loss']for r in captures];row=dict(label=label,shape=v.tolist(),loss=float(np.mean(values)),realization_losses=values,assessment=sorted(captures,key=lambda r:r['loss'])[len(captures)//2]['assessment'])
  if save:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,z))

with PAUSE.open('x')as p:json.dump(dict(owner=OWNER,reason='finite actual native WaveShaper16 refit in real ZL context'),p)
try:
 assert valid(origin);record('starting_actual_WS16_curve_and_full_chain_search',native_EQ76_accepted=eq_result['robust_improvement'])
 for k in range(4):
  c=NativeChain(seed['source_manifest']['native_input'],f'ZL-native-WS16-cycle03-worker-{k}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');z=WinVST3(f'ZL-native-WS16-cycle03-real-VST3-{k}');z.load(component);clients.append((c,z));pool.put((c,z))
 baseline=evaluate(('unchanged-control',origin),8);current=baseline;cases=[]
 for k,u in enumerate(qmc.LatinHypercube(16,seed=2026102317).random(192)):
  v=origin+(u*2-1)*steps*[.25,.5,1,2][k%4]
  if valid(v):cases.append((f'joint-LHS-{k}',v))
 with concurrent.futures.ThreadPoolExecutor(4)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if row['loss']<current['loss']:current=row
   if k%8==0:record('actual_WS16_joint_curve_candidates',best_training_mean=current['loss'],control_mean=baseline['loss'])
  for sweep in range(3):
   for j in range(16):
    cases=[]
    for factor in [-2,-1,1,2]:
     v=np.array(current['shape']);v[j]+=factor*steps[j]*(.5**sweep)
     if valid(v):cases.append((f'axis-{sweep}-{j}-{factor}',v))
    if cases:
     checked=list(executor.map(evaluate,cases));winner=min(checked,key=lambda r:r['loss'])
     if winner['loss']<current['loss']-.0001:current=winner
    record('actual_WS16_curve_coordinate_refinement',sweep=sweep,coordinate=j,best_training_mean=current['loss'],control_mean=baseline['loss'])
 finalists=[]
 for row in sorted(rows,key=lambda r:r['loss'])[:4]:finalists.append(evaluate(('fresh-finalist-'+row['label'],row['shape']),12,False))
 selected=min(finalists,key=lambda r:r['loss']);shape=np.array(selected['shape']);c0,z0=clients[0];c1,z1=clients[1];configure(c0,origin);configure(c1,shape);captures=[];audio=[];native_losses=[]
 record('fresh_twelve_independent_complete_native_WS_plus_ZL_pairs')
 for rep in range(12):
  raw0,st0=c0.render();old,_=z0.render(raw0);old_loss=score(old);raw1,st1=c1.render();out,_=z1.render(raw1);loss=score(out);assessment=f.local.last;native_losses.append(score(raw1));captures.append(dict(rep=rep,base_loss=old_loss,loss=loss,assessment=assessment));audio.append((old,out))
 delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(12));robust=bool(np.mean(delta)>max(.0005,3*sem))
 states=ROOT/'actual-native-states';states.mkdir();nodes=[0,3,4,5,6,7,8,10,11,12,13,14]
 for n in nodes:c1.save_state(n,states/f'{n}.bin')
 c1.set(3,1,0);zero,_=c1.render();c2=clients[2][0];configure(c2,shape)
 for n in nodes:c2.load_state(n,states/f'{n}.bin');c2.save_state(n,states/f'{n}-resaved.bin');assert (states/f'{n}.bin').read_bytes()==(states/f'{n}-resaved.bin').read_bytes()
 c2.set(3,1,0);again,_=c2.render();error=float(abs(zero-again).max());assert error<=2e-7,error
 z1.save(ROOT/'UNCHANGED_ZL_COMPONENT_RESAVED.bin');assert component.read_bytes()==(ROOT/'UNCHANGED_ZL_COMPONENT_RESAVED.bin').read_bytes()
 archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';members=[]
 with tarfile.open(archive,'w:gz',compresslevel=3)as z:
  for rep,pair in enumerate(audio):
   for label,y in zip(['control','candidate'],pair):
    b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();name=f'{label}-{rep}.wav';info=tarfile.TarInfo(name);info.size=len(blob);z.addfile(info,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
 with tarfile.open(archive)as z:
  for m in members:assert hashlib.sha256(z.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 median=sorted(range(12),key=lambda k:captures[k]['loss'])[6];sf.write(ROOT/'SELECTED_COMBINED_WIP.wav',audio[median][1],48000,subtype='FLOAT')
 native=native_case(shape);native.update(loss=float(np.mean(native_losses)),full_fresh_native_realizations=12,full_fresh_native_validation_pending=False,native_parameters_refitted_in_ZL_context=True,robust_improvement_joint_ZL=robust)
 summary=dict(training_cases=len(rows),training_control_mean=baseline['loss'],training_candidate_mean=current['loss'],current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,all12_native_saved_states_byte_exact=True,native_zero_depth_replay_max_abs_error=error,actual_curve_monotone_valid=True,ZL_component_unchanged=True,only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,captures=captures,archive_members=members)
 result=dict(prior,native_base=native,loss=summary['candidate_mean'],native_ZL_component_state=str(component),recorded_audio=str(ROOT/'SELECTED_COMBINED_WIP.wav'),native_parameters_changed=True,not_automatically_adopted_into_main_or_public_FL_project=True,not_compatible_with_standard_x95_exporter=True,extended_parameter_values_are_authoritative_in_component_state=True)
 for name,o in [('completion.json',summary),('CANDIDATE_COMBINED_RESEARCH_ONLY.json',result),('NATIVE_CANDIDATE_FOR_EXPORT.json',native)]: (ROOT/name).write_text(json.dumps(o,indent=2)+'\n')
 (ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));record('finite_WS16_study_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print('NATIVE_WS16_WITH_ZL_STUDY_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 record('failed_preserve_all_prior_complete_kits',error=traceback.format_exc());raise
finally:
 for c,z in clients:c.close();z.close()
 if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
