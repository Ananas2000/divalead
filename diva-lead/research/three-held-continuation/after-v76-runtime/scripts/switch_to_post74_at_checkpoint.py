"""After a new global full proof, preserve unaccepted numeric work and switch source."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,signal,subprocess,time,traceback
R=Path(__file__).resolve().parent;PY='/workspace/.venvs/divalead/bin/python';lock=(R/'post74-checkpoint-switch.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
frozen=[];retired=False;PAUSE=R/'auto-backup.pause';OWNER='checkpoint-switch-to-new-global-post74-source';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def write(p,d):q=p.with_suffix('.tmp');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def proc(pid):
 try:
  p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split();return dict(PID=pid,state=s[0],ppid=int(s[1]),start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
 except FileNotFoundError:return None
def state(phase,**kw):write(R/'post74-checkpoint-handoff-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,frozen_processes=frozen,old_processes_retired=retired,only_three_held=True,match_reached=False,**kw))
def freeze(pid,command):
 p=proc(pid);assert p and command in p['cmd'] and p['state'] not in ['T','Z'];os.kill(pid,signal.SIGSTOP);frozen.append(dict(PID=pid,start=p['start'],expected_command=command.decode()));return p
try:
 while not (R/'source-post74-blend/completed.json').is_file() or not json.loads((R/'source-post74blend-state.json').read_text()).get('slot_released'):time.sleep(2)
 best=json.loads(subprocess.check_output([PY,'-B',str(R/'auto_backup_three.py'),'--check-only'],env=env,text=True))
 if best['source_family']!='Post74 joint oscillator-filter':state('no_new_global_physical_winner_keep_current_cohort',best=best)
 else:
  old=json.loads((R/'active-three-source-family.json').read_text());assert old['source_family']=='PulseWidth51.90';assert json.loads((R/'post74-source-handoff-state.json').read_text())['phase']=='old_source_remains_best_resume_current_cohort'
  states={}
  for role in ['main','phase','balance']:
   while True:
    d=json.loads((R/('pw5190-'+role+'-state.json')).read_text());assert d['phase']!='failed',d
    if d['phase'].endswith('_fit'):break
    state('waiting_for_numeric_checkpoint_boundary',role=role);time.sleep(2)
   pid=d['controller_PID'];freeze(pid,str(R/('continue_pw5190_'+role+'.py')).encode());after=json.loads((R/('pw5190-'+role+'-state.json')).read_text());assert after==d
   fit=d['fit_PID'];p=proc(fit);assert p and p['ppid']==pid;command=next(x for x in p['cmd'] if x.startswith(str(R/'fit_three_').encode()));freeze(fit,command);desc=[fit]
   for ancestor in desc:
    for path in Path('/proc').iterdir():
     if not path.name.isdigit():continue
     c=proc(int(path.name))
     if not c or c['ppid']!=ancestor or c['state']=='Z':continue
     command=next((x for x in c['cmd'] if x.startswith(str(R/'fit_three_').encode())),None);assert command,c
     freeze(c['PID'],command);desc.append(c['PID'])
   states[role]=d;state('preserving_current_unaccepted_numeric_checkpoints')
  dest=R/'retired-PW-numeric-checkpoints';dest.mkdir(exist_ok=False);manifest=[]
  for role,d in states.items():
   run=Path(d['fit_log']).parent;location=json.loads((run/'numeric-location.json').read_text());scratch=Path(location['numeric_scratch']);out=dest/role;out.mkdir();shutil.copytree(scratch,out/'numeric');shutil.copyfile(run/'fit.log',out/'fit.log');shutil.copyfile(run/'numeric-location.json',out/'original-location.json');write(out/'state-at-checkpoint.json',dict(original_state=d,numeric_vectors_not_accepted_as_finished_proofs=True,match_reached=False))
   for p in (out/'numeric').rglob('*'):
    if not p.is_file():continue
    source=scratch/p.relative_to(out/'numeric');assert p.read_bytes()==source.read_bytes();manifest.append(dict(path=str(p.relative_to(dest)),bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
  write(dest/'manifest.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=manifest,all_original_bytes_preserved=True,only_unaccepted_inflight_numeric_work_retired=True,all_finished_proofs_retained=True,match_reached=False))
  for role in ['main','phase','balance']:subprocess.run([PY,'-B',str(R/('continue_post74joint_'+role+'.py')),'--check-only'],env=env,check=True)
  while True:
   try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
   except FileExistsError:time.sleep(2);continue
   with os.fdopen(fd,'w') as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
   break
  for _ in range(90):
   pub=json.loads((R/'auto-backup-state.json').read_text())
   if pub['phase']=='paused_for_manual_Git_work':break
   time.sleep(1)
  else:raise RuntimeError(pub)
  pid=pub['publisher_PID'];assert str(R/'auto_backup_three.py').encode() in proc(pid)['cmd'];os.kill(pid,signal.SIGTERM)
  for row in reversed(frozen):
   p=proc(row['PID']);assert p and p['start']==row['start'] and row['expected_command'].encode() in p['cmd'] and p['state']=='T';os.kill(row['PID'],signal.SIGTERM);os.kill(row['PID'],signal.SIGCONT)
  for row in frozen+[dict(PID=pid)]:
   for _ in range(100):
    p=proc(row['PID'])
    if not p or p['state']=='Z':break
    time.sleep(.1)
   else:raise RuntimeError('Retired process remains live')
  retired=True;write(R/'active-three-source-family.json',dict(source_family=best['source_family'],best_fully_proved_validation=best['best'],best_tone_score=best['tone_score'],old_parents_retired_at_idle=False,old_jobs_retired_after_exact_numeric_checkpoint=True,retired_unaccepted_numeric_checkpoint=str(dest),numeric_budget='2+1+1',minimum_free_workspace_MiB=256,minimum_free_publication_MiB=128,only_three_held=True))
  shutil.copyfile(R/'post74-source-handoff-state.json',R/'first-post74-idle-handoff-state.json')
  subprocess.run([PY,'-B',str(R/'start_three_services.py')],env=env,check=True);assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink()
  state('new_selected_source_cohort_started_budget2_1_1',best=best,numeric_checkpoint=str(dest),start_report=json.loads((R/'service-start-last.json').read_text()))
  final=json.loads((R/'post74-checkpoint-handoff-state.json').read_text());final.update(handoff_method='preserved_inflight_numeric_checkpoints_after_new_global_blend_proof',old_parents_retired=True,prior_idle_attempt=str(R/'first-post74-idle-handoff-state.json'));write(R/'post74-source-handoff-state.json',final)
except Exception:
 state('failed_preserve_checkpoints_and_diagnose',error=traceback.format_exc());raise
finally:
 if not retired:
  for row in reversed(frozen):
   p=proc(row['PID'])
   if p and p['start']==row['start'] and row['expected_command'].encode() in p['cmd'] and p['state']=='T':os.kill(row['PID'],signal.SIGCONT)
 if PAUSE.exists() and json.loads(PAUSE.read_text()).get('owner')==OWNER:PAUSE.unlink()
