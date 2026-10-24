"""Recover fixed-source study without competing with main for limited /tmp."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,traceback
D=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');OWNER='Diva-PWM-sync-recovery-after-storage-20261023';PAUSE=N/'fl20-corrected-search.pause';STOPS=[N/'zl-continuation.stop',N/'zl-useful-full-backup.stop'];STATE=N/'PWM_SYNC_SEQUENTIAL_RECOVERY_CONTROLLER.json';PY='/workspace/.venvs/divalead/bin/python';env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{D.parent}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def read(p):return json.loads(Path(p).read_text())
def alive(pid):
 try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,only_three_held_notes=True,reference_match_reached=False,**kw);q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');watch=read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json');assert not alive(main['owner']['PID'])and not alive(watch['PID'])
assert shutil.disk_usage('/tmp').free>=140*2**20
if PAUSE.exists():
 assert read(PAUSE)['owner']=='external-ZL-continuous65-refinement';PAUSE.rename(N/'STALE_NUMERIC_PAUSE_PRESERVED_AFTER_ENOSPC.json')
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='Finish remaining fixed-source cases sequentially after verified old-copy eviction; main current best validated'),f)
for p in STOPS:
 with p.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='Finite sequential recovery avoids /tmp competition'),f)
try:
 record('recovering_verified_source_cases_sequentially_main_safely_stopped',last_confirmed_main_mean=read(D/'ZL-continuous65/BEST_CANDIDATE.json')['loss'])
 with(N/'ACTUAL_DIVA_PWM_SYNC_RECOVERED_STUDY.log').open('w')as log:p=subprocess.Popen([PY,'-B',str(D/'recover_actual_Diva_PWM_sync_in_native04.py')],env=env,stdout=log,stderr=subprocess.STDOUT)
 record('actual_recovered_source_study_running',actual_study_PID=p.pid);assert p.wait()==0
 record('fixed_source_study_completed_preserve_results_for_publication',summary={k:v for k,v in read(D/'Diva-PWM-sync-current-native04-ZL-01-recovered/completion.json').items()if k not in ['captures','archive_members']})
except BaseException:
 record('recovery_failed_preserve_all_existing_completed_cases',error=traceback.format_exc());raise
finally:
 if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
 for p in STOPS:
  if p.exists()and read(p).get('owner')==OWNER:p.unlink()
 started={}
 for name,args,statefile in [('continue_ZL_matching.py',[],'FL20_ZL_CONTINUOUS_CONTROLLER.json'),('watch_ZL_useful_complete_backups.py',['--watch'],'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')]:
  state=read(N/statefile);pid=state.get('PID',state.get('owner',{}).get('PID')if isinstance(state.get('owner'),dict)else None)
  if pid and alive(pid)and os.fsencode(str(D/name))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0'):continue
  with(N/('RECOVERED_PWM_SYNC_'+name+'.log')).open('ab')as log:p=subprocess.Popen([PY,'-B',str(D/name),*args],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  started[name]=p.pid
 (N/'PWM_SYNC_POST_STORAGE_RECOVERY_MATCHER_RESTART.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_started=started,current_best_mean=read(D/'ZL-continuous65/BEST_CANDIDATE.json')['loss'],reference_match_reached=False),indent=2)+'\n');print('ACTUAL_MATCHER_AND_BACKUP_RESUMED',json.dumps(started),flush=True)
