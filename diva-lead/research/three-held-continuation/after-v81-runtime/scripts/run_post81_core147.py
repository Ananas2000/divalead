"""Borrow only the active balance worker's one CPU slot for a finite Diva screen."""
from pathlib import Path
import datetime,fcntl,json,os,signal,subprocess,sys,time,traceback
R=Path(__file__).resolve().parent;C=R/'source-post81core147-control';C.mkdir(exist_ok=False)
lock=(R/'source-post81core147-owner.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
stopped=[]
def write(p,d):q=p.with_suffix('.tmp');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def proc(pid):
 try:
  p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split()
  return dict(PID=pid,ppid=int(s[1]),state=s[0],start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
 except FileNotFoundError:return None
def save(phase,**kw):
 write(R/'source-post81core147-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,processes=stopped,numeric_workers=1,slot_released=not bool(stopped),only_three_held=True,screening_only_not_full_proof=True,match_reached=False,**kw))
def stop(pid,expected):
 d=proc(pid);assert d and expected in d['cmd'] and d['state'] not in ['Z','T'],d
 os.kill(pid,signal.SIGSTOP);stopped.append(dict(PID=pid,starttime_ticks=d['start'],expected_command=expected.decode()));save('temporarily_claiming_balance_worker_slot')
def terminate(signum,frame):raise SystemExit('Signal '+str(signum))
signal.signal(signal.SIGTERM,terminate)
try:
 while True:
  handoff_path=R/'post80-source-handoff-state.json'
  handoff=json.loads(handoff_path.read_text()) if handoff_path.exists() else {}
  if handoff.get('phase','').startswith('failed'):raise RuntimeError(handoff)
  if handoff.get('phase') in ['new_selected_source_cohort_started_budget2_1_1','previous_source_remains_best_resume_current_cohort']:break
  save('waiting_for_completed_source_handoff');time.sleep(5)
 family=json.loads((R/'active-three-source-family.json').read_text())['source_family']
 prefix={'Post80 Plate2 damping68':'post80plate68','Post74 joint oscillator-filter':'post74joint'}[family]
 while True:
  state=json.loads((R/(prefix+'-balance-state.json')).read_text())
  if state['phase'] in ['three_balance42_fit','three_power69_fit']:break
  save('waiting_for_current_balance_fit_slot');time.sleep(2)
 parent=state['controller_PID'];stop(parent,str(R/('continue_'+prefix+'_balance.py')).encode())
 after=json.loads((R/(prefix+'-balance-state.json')).read_text());assert (after['phase'],after['fit_PID'])==(state['phase'],state['fit_PID'])
 fit=state['fit_PID'];f=proc(fit);assert f and f['ppid']==parent
 stop(fit,str(R/('fit_three_balance42.py' if state['phase']=='three_balance42_fit' else 'fit_three_power69.py')).encode())
 pending=[fit]
 for ancestor in pending:
  for path in Path('/proc').iterdir():
   if not path.name.isdigit():continue
   d=proc(int(path.name))
   if not d or d['ppid']!=ancestor or d['state']=='Z':continue
   assert d['cmd'][0]==b'/workspace/.venvs/divalead/bin/python',d
   expected=next((x for x in d['cmd'] if x.startswith(str(R/'fit_three_').encode())),None);assert expected,d
   stop(d['PID'],expected);pending.append(d['PID'])
 save('actual_Diva_oscillator_filter_finite_screen',stopped_parent=parent,original_balance_state=state)
 with (C/'probe.log').open('w') as log:
  subprocess.run([sys.executable,'-B',str(R/'fit_post81_core147.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True,timeout=7200)
 completed=json.loads(Path('/tmp/divalead-source-post81core147/completed.json').read_text());write(C/'completed.json',completed)
 save('finite_actual_Diva_screen_completed',trials=completed['trials'],best=completed['best'])
except Exception:
 save('failed_preserve_screen_and_release_slot',error=traceback.format_exc());raise
finally:
 resumed=[]
 for row in reversed(stopped):
  d=proc(row['PID'])
  if d and d['start']==row['starttime_ticks'] and row['expected_command'].encode() in d['cmd']:
   os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
 prior=json.loads((R/'source-post81core147-state.json').read_text());prior.update(slot_released=True,resumed_exact_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());write(R/'source-post81core147-state.json',prior)
 print('EXACT_CURRENT_BALANCE_WORKER_SLOT_RELEASED',resumed,flush=True)
