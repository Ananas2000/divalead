"""Graceful finite native refit; keep every completed public kit intact.

The finite studies cannot race the main matcher. On failure, resume the
previous accepted matcher; on success leave an owned handoff for real export.
"""
from pathlib import Path
import datetime,json,os,subprocess,time,traceback
D=Path(__file__).resolve().parent
N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=D/'ZL-native-context-cycle02';ROOT.mkdir(exist_ok=False)
OWNER='native-and-ZL-finite-refit-20261023'
PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{D.parent}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
STOPS=[N/'zl-continuation.stop',N/'zl-useful-full-backup.stop']
STATE=N/'NATIVE_ZL_CONTEXT_CYCLE02_STATE.json'
def read(p):return json.loads(Path(p).read_text())
def alive(pid):
 try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,only_three_held_notes=True,source_Diva_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def job(name,args=()):
 record('finite_actual_plugin_job_running',script=name,args=list(args))
 with (ROOT/(name+'.log')).open('w')as log:subprocess.run([PY,'-B',str(D/name),*args],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
def resume_previous():
 for p in STOPS:
  if p.exists()and read(p).get('owner')==OWNER:p.unlink()
 main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');watch=read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')
 started={}
 for name,state,log in [('continue_ZL_matching.py',main,'CONTEXT02_RECOVERY_MATCHER.log'),('watch_ZL_useful_complete_backups.py',watch,'CONTEXT02_RECOVERY_BACKUP.log')]:
  pid=state.get('PID',state.get('owner',{}).get('PID'))
  if pid and alive(pid):continue
  with(N/log).open('ab')as f:p=subprocess.Popen([PY,'-B',str(D/name),*(['--watch']if name.startswith('watch')else[])],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  started[name]=p.pid
 return started
try:
 assert not (N/'zl-continuation.stop').exists()and not (N/'zl-useful-full-backup.stop').exists()
 for p in STOPS:
  with p.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='finite cycle02 actual native EQ76/WS16 in the updated six-dynamic-band ZL context'),f)
 main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');watch=read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')
 pids=[main['owner']['PID'],watch['PID']];record('awaiting_completed_cohort_and_full_kit_boundary',PIDs=pids)
 deadline=time.monotonic()+1200
 while any(alive(pid)for pid in pids):
  if time.monotonic()>deadline:raise TimeoutError('No safe completed boundary within twenty minutes')
  time.sleep(.5)
 assert not (N/'fl20-corrected-search.pause').exists()
 prior=read(D/'ZL-continuous65/BEST_CANDIDATE.json');(ROOT/'PRIOR_MAIN_BEST.json').write_text(json.dumps(prior,indent=2)+'\n')
 for stem,root,label in [('EQ','ZL-native-EQ76-after-ZL13-02','native-EQ76-current-six-dynamic-ZL-cycle02'),('WS','ZL-native-WS16-after-EQ76-02','native-WS16-current-six-dynamic-ZL-cycle02')]:
  job(f'study_native_{stem}_with_ZL_cycle02.py')
  summary=read(D/root/'completion.json')
  (ROOT/(stem+'_SUMMARY.json')).write_text(json.dumps(summary,indent=2)+'\n')
  job('backup_finite_ZL_study.py',['--study',str(D/root),'--label',label])
 record('finite_studies_complete_ready_for_actual_native_base_and_full_ZIP_export',EQ=read(ROOT/'EQ_SUMMARY.json')['robust_improvement'],WS=read(ROOT/'WS_SUMMARY.json')['robust_improvement'],prior_mean=prior['loss'])
 print('NATIVE_CONTEXT_CYCLE02_FINITE_STUDIES_COMPLETE',flush=True)
except BaseException:
 error=traceback.format_exc();record('failed_finite_study_preserve_and_resume_prior_confirmed_best',error=error)
 recovery=resume_previous();(ROOT/'RECOVERY.json').write_text(json.dumps(dict(error=error,restarted=recovery),indent=2)+'\n');raise
