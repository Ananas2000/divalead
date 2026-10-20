"""Finish active PW fits, compare every completed result, switch only at idle."""
from pathlib import Path
import datetime,fcntl,json,os,signal,subprocess,sys,time,traceback
R=Path(__file__).resolve().parent;PY='/workspace/.venvs/divalead/bin/python';lock=(R/'post74-source-handoff.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
stopped={};retired=False;owner='idle-handoff-to-proved-post74-source';PAUSE=R/'auto-backup.pause';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def write(p,d):q=p.with_suffix('.tmp');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def proc(pid):
 try:
  p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split();return dict(PID=pid,state=s[0],ppid=int(s[1]),start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
 except FileNotFoundError:return None
def children(pid):
 return [d for p in Path('/proc').iterdir() if p.name.isdigit() and (d:=proc(int(p.name))) and d['ppid']==pid and d['state']!='Z']
def state(phase,**kw):write(R/'post74-source-handoff-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,stopped_parents=stopped,old_parents_retired=retired,only_three_held=True,match_reached=False,**kw))
def wait_dead(pid):
 for _ in range(100):
  p=proc(pid)
  if not p or p['state']=='Z':return
  time.sleep(.1)
 raise RuntimeError('PID remains alive: '+str(pid))
try:
 while len(stopped)<3:
  for role in ['main','phase','balance']:
   if role in stopped:continue
   if role=='balance' and not json.loads((R/'source-post74fit-state.json').read_text()).get('slot_released'):continue
   d=json.loads((R/('pw5190-'+role+'-state.json')).read_text());phase=d['phase']
   assert phase!='failed',d
   if phase not in ['fresh_Diva_Windows_own_NEW_12_cases_proof','waiting_for_changed_proved_three_basis','paused_low_workspace_space']:continue
   pid=d['controller_PID'];p=proc(pid);command=str(R/('continue_pw5190_'+role+'.py')).encode();assert p and command in p['cmd'] and p['state']!='T'
   os.kill(pid,signal.SIGSTOP);time.sleep(.02);after=json.loads((R/('pw5190-'+role+'-state.json')).read_text());cs=children(pid)
   if after!=d or any(any(b'/fit_three_' in x for x in c['cmd']) for c in cs):os.kill(pid,signal.SIGCONT);continue
   stopped[role]=dict(PID=pid,starttime_ticks=p['start'],expected_command=command.decode(),state_at_idle=d)
   state('finishing_current_proofs_without_starting_more_old_source_fits')
  state('waiting_for_current_old_source_fits_to_finish',idle_roles=list(stopped))
  if len(stopped)<3:time.sleep(2)
 for role,row in stopped.items():
  while children(row['PID']):time.sleep(2)
  d=row['state_at_idle']
  if d['phase']=='fresh_Diva_Windows_own_NEW_12_cases_proof':
   runname=next(x for x in Path(d['fit']).parts if x.startswith('round-'));target=R/('pw5190-verified-live-'+role+'-'+runname.removeprefix('round-'));run=R/('pw5190-live-'+role)/runname
   if (target/'validation.json').is_file():receipt=dict(fresh_proof_completed=True,validation=str(target/'validation.json'),parent_stopped_before_housekeeping=True,controller_decision_not_fabricated=True)
   else:
    from three_candidate_decision import quality_rejection
    receipt=quality_rejection(run/'validation.log',target);assert receipt is not None,'Unknown infrastructure failure during old source proof';receipt['parent_stopped_before_housekeeping']=True
   write(run/'idle-handoff-receipt.json',receipt)
 state('checking_newest_completed_models_on_new_physical_source')
 with (R/'source-post74-transplant02-controller.log').open('w') as log:subprocess.run([PY,'-B',str(R/'prove_post74_source_transplant02.py')],env=env,stdout=log,stderr=log,check=True)
 while not (R/'public-v75-verification.json').is_file():
  s=json.loads((R/'v75-preparation-controller-state.json').read_text());assert not s['phase'].startswith('failed'),s;state('waiting_for_full75_publication_before_cohort_handoff');time.sleep(3)
 best=json.loads(subprocess.check_output([PY,'-B',str(R/'auto_backup_three.py'),'--check-only'],env=env,text=True))
 if best['source_family']!='Post74 joint oscillator-filter':
  state('old_source_remains_best_resume_current_cohort',best=best)
 else:
  for role in ['main','phase','balance']:subprocess.run([PY,'-B',str(R/('continue_post74joint_'+role+'.py')),'--check-only'],env=env,check=True)
  while True:
   try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
   except FileExistsError:time.sleep(2);continue
   with os.fdopen(fd,'w') as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
   break
  for _ in range(90):
   pub=json.loads((R/'auto-backup-state.json').read_text())
   if pub['phase']=='paused_for_manual_Git_work':break
   time.sleep(1)
  else:raise RuntimeError(pub)
  pid=pub['publisher_PID'];p=proc(pid);assert p and str(R/'auto_backup_three.py').encode() in p['cmd'];os.kill(pid,signal.SIGTERM);wait_dead(pid)
  for role,row in stopped.items():
   p=proc(row['PID']);assert p and p['start']==row['starttime_ticks'] and row['expected_command'].encode() in p['cmd'] and p['state']=='T' and not children(row['PID'])
   os.kill(row['PID'],signal.SIGTERM);os.kill(row['PID'],signal.SIGCONT);wait_dead(row['PID'])
  retired=True
  write(R/'active-three-source-family.json',dict(source_family=best['source_family'],best_fully_proved_validation=best['best'],best_tone_score=best['tone_score'],old_parents_retired_at_idle=True,numeric_budget='2+1+1',minimum_free_workspace_MiB=256,minimum_free_publication_MiB=128,old_PW_source_preserved=True,only_three_held=True))
  subprocess.run([PY,'-B',str(R/'start_three_services.py')],env=env,check=True)
  assert json.loads(PAUSE.read_text())['owner']==owner;PAUSE.unlink()
  state('new_selected_source_cohort_started_budget2_1_1',best=best,start_report=json.loads((R/'service-start-last.json').read_text()))
except Exception:
 state('failed_preserve_data_and_diagnose',error=traceback.format_exc());raise
finally:
 if not retired:
  for row in stopped.values():
   p=proc(row['PID'])
   if p and p['start']==row['starttime_ticks'] and row['expected_command'].encode() in p['cmd'] and p['state']=='T':os.kill(row['PID'],signal.SIGCONT)
 if PAUSE.exists() and json.loads(PAUSE.read_text()).get('owner')==owner:PAUSE.unlink()
