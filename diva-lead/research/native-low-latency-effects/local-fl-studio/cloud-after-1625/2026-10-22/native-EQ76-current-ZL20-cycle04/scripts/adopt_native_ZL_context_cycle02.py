"""Confirm final native refit against prior main, export/replay, then adopt.

Never publish research parameter JSON as a working user preset. Native base02
must be built from actual states and the full ZIP must actually replay first.
"""
from pathlib import Path
import datetime,hashlib,io,json,os,runpy,subprocess,tarfile,traceback
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3
D=Path(__file__).resolve().parent;B=D.parent
N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=D/'ZL-native-base-rebase-adoption-02';ROOT.mkdir(exist_ok=False)
OWNER='native-and-ZL-finite-refit-20261023';PY='/workspace/.venvs/divalead/bin/python'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();clients=[];native_clients=[]
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{B}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
STOPS=[N/'zl-continuation.stop',N/'zl-useful-full-backup.stop'];STATE=N/'NATIVE_ZL_CONTEXT_CYCLE02_ADOPTION_STATE.json'
def read(p):return json.loads(Path(p).read_text())
def alive(pid):
 try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,only_three_held_notes=True,source_Diva_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def job(script,args):
 record('actual_native_base_export_and_verification',script=script)
 with(ROOT/(script+'.log')).open('w')as log:subprocess.run([PY,'-B',str(D/script),*args],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
def score(y,seed):
 r=features.residual(y[:288000]);return float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
def native(seed,tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');native_clients.append(c);apply_candidate(c,np.array(seed['x']),seed)
 for k,v in seed['chorus_overrides'].items():c.set(3,int(k),int(v))
 return c
def resume():
 for p in STOPS:
  if p.exists()and read(p).get('owner')==OWNER:p.unlink()
 result={}
 for name,extra,log in [('continue_ZL_matching.py',[],'ZL_CONTEXT02_ACCEPTED_MATCHER.log'),('watch_ZL_useful_complete_backups.py',['--watch'],'ZL_CONTEXT02_ACCEPTED_BACKUP.log')]:
  with(N/log).open('ab')as f:p=subprocess.Popen([PY,'-B',str(D/name),*extra],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  result[name]=p.pid
 return result
try:
 prior=read(D/'ZL-continuous65/BEST_CANDIDATE.json');(ROOT/'PRIOR_MAIN_BEST_BEFORE_REBASE.json').write_text(json.dumps(prior,indent=2)+'\n')
 assert read(N/'NATIVE_ZL_CONTEXT_CYCLE02_STATE.json')['phase']=='finite_studies_complete_ready_for_actual_native_base_and_full_ZIP_export'
 assert all(read(p)['owner']==OWNER for p in STOPS)
 assert not alive(read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID'])
 assert not alive(read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')['PID'])
 EQ=D/'ZL-native-EQ76-after-ZL13-02';WS=D/'ZL-native-WS16-after-EQ76-02'
 accepted=[r for r in [EQ,WS]if read(r/'completion.json')['robust_improvement']]
 if not accepted:
  record('no_native_refit_passed_keep_prior_main_and_all_public_kits');print('NO_NATIVE_CYCLE02_ADOPTION',flush=True)
 else:
  source=accepted[-1];proposal=read(source/'CANDIDATE_COMBINED_RESEARCH_ONLY.json');seed=proposal['native_base'];oldseed=prior['native_base']
  component=ROOT/'CANDIDATE_COMPONENT.bin';component.write_bytes(Path(proposal['native_ZL_component_state']).read_bytes());assert component.read_bytes()==Path(prior['native_ZL_component_state']).read_bytes()
  a=native(oldseed,'ZL-native-context02-final-control');b=native(seed,'ZL-native-context02-final-candidate')
  z0=WinVST3('ZL-native-context02-final-real-control');z1=WinVST3('ZL-native-context02-final-real-candidate');clients.extend([z0,z1])
  for z in clients:z.load(component);assert z.latency()==0
  record('twelve_new_full_chain_pairs_against_latest_main_not_intermediate_EQ');rows=[];audio=[]
  for rep in range(12):
   raw0,_=a.render();old,_=z0.render(raw0);loss0=score(old,oldseed);raw1,_=b.render();out,_=z1.render(raw1);loss1=score(out,seed)
   rows.append(dict(rep=rep,base_loss=loss0,loss=loss1,assessment=features.local.last));audio.append((old,out));record('twelve_new_full_chain_pairs_against_latest_main_not_intermediate_EQ',completed_pairs=rep+1)
  for c in native_clients:c.close()
  native_clients.clear()
  for c in clients:c.close()
  clients.clear()
  delta=np.array([r['base_loss']-r['loss']for r in rows]);sem=float(np.std(delta,ddof=1)/np.sqrt(12));robust=bool(np.mean(delta)>max(.0005,3*sem));members=[];archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
  with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
   for rep,pair in enumerate(audio):
    for label,y in zip(['control','candidate'],pair):
     out=io.BytesIO();sf.write(out,y,48000,format='WAV',subtype='FLOAT');blob=out.getvalue();name=f'{label}-{rep}.wav';entry=tarfile.TarInfo(name);entry.size=len(blob);tar.addfile(entry,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
  with tarfile.open(archive)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
  median=sorted(range(12),key=lambda k:rows[k]['loss'])[6];selected=ROOT/'SELECTED_COMBINED_WIP.wav';sf.write(selected,audio[median][1],48000,subtype='FLOAT')
  summary=dict(cohort='native-context-cycle02-after-'+Path(prior['native_ZL_component_state']).parent.name,current_control_mean=float(np.mean([r['base_loss']for r in rows])),candidate_mean=float(np.mean([r['loss']for r in rows])),paired_difference_SEM=sem,robust_improvement=robust,source_study=str(source),captures=rows,archive_members=members,only_three_held_notes=True,source_Diva_and_ZL_component_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
  (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n')
  job('backup_finite_ZL_study.py',['--study',str(ROOT),'--label','native-final-context02-current-main-revalidation'])
  if not robust:record('final_paired12_rejected_keep_prior_main',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']})
  else:
   proposal.update(loss=summary['candidate_mean'],native_ZL_component_state=str(component),recorded_audio=str(selected),not_automatically_adopted_into_main_or_public_FL_project=True)
   proposed=ROOT/'PROPOSED_COMBINED_CANDIDATE.json';proposed.write_text(json.dumps(proposal,indent=2)+'\n')
   base=B/'FL20_NATIVE_ZL_REBASED_02';ready=base.with_name(base.name+'-COMBINED_CANDIDATE_READY.json')
   job('prepare_native_base_for_combined_ZL.py',['--candidate',str(proposed),'--destination',str(base)])
   job('package_verified_native_base.py',['--ready',str(ready)])
   shared=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='cycle02_explicit_candidate_full_export')
   code=f"{max(int(p.name[-2:])for p in shared['PUBLIC'].glob('ZL-WIP[0-9][0-9]'))+1:02}"
   record('new_native_base_ready_full_actual_FL20_ZIP_export',code=code,native_base=str(base))
   shared['build'](code,candidate=str(ready))
   kit=B/f'FL20_ZL_{code}_WIP';report=read(kit/'verification/ZL_FULL_VERIFICATION.json');proof=read(kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json')
   assert report['mean_original_objective']<summary['current_control_mean']-.0005
   assert proof['six_fresh_whole_chain_mean']<summary['current_control_mean']-.0005
   shared['publish'](code)
   choice=read(ready);choice.update(not_automatically_adopted_into_main_or_public_FL_project=False,accepted_full_public_kit='ZL'+code,independent_full_ZIP_replay_mean=proof['six_fresh_whole_chain_mean'])
   tmp=D/'ZL-continuous65/BEST_CANDIDATE.partial';tmp.write_text(json.dumps(choice,indent=2)+'\n');tmp.replace(D/'ZL-continuous65/BEST_CANDIDATE.json')
   (ROOT/'ADOPTED_AFTER_FULL_KIT_REPLAY.json').write_text(json.dumps(dict(public_kit='ZL'+code,paired_control=summary['current_control_mean'],paired_candidate=summary['candidate_mean'],full_export_mean=report['mean_original_objective'],ZIP_replay_mean=proof['six_fresh_whole_chain_mean'],native_base=str(base),reference_match_reached=False),indent=2)+'\n')
   record('native_context02_adopted_only_after_full_kit_push_and_replay',public_kit='ZL'+code,candidate_mean=choice['loss'])
except BaseException:
 record('failed_preserve_last_confirmed_main_and_all_reviewable_artifacts',error=traceback.format_exc());raise
finally:
 for c in native_clients:c.close()
 for c in clients:c.close()
 main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')
 if not alive(main['owner']['PID'])and all(p.exists()and read(p).get('owner')==OWNER for p in STOPS):
  restarted=resume();(N/'NATIVE_CONTEXT02_MATCHER_AND_FULL_BACKUP_RESTART.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PIDs=restarted,best_mean=read(D/'ZL-continuous65/BEST_CANDIDATE.json')['loss'],reference_match_reached=False),indent=2)+'\n');print('ACTUAL_MATCHER_AND_COMPLETE_BACKUP_RESTARTED',json.dumps(restarted),flush=True)
