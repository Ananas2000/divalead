"""Graceful finite measured ZL boundary expansion study."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,time,traceback
D=Path(__file__).resolve().parent
N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=D/'ZL-boundary-expansion-sequential-controller-01'
ROOT.mkdir(exist_ok=False)
OWNER='ZL-measured-boundary-finite-study-20261024'
PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{D.parent}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
STOPS=[N/'zl-continuation.stop',N/'zl-useful-full-backup.stop']
STATE=N/'ZL_MEASURED_BOUNDARY_CONTROLLER.json'
def read(p):return json.loads(Path(p).read_text())
def alive(pid):
    try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
    except FileNotFoundError:return False
def record(phase,**kw):
    o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,only_three_held_notes=True,source_Diva_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
    q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def job(script,args=()):
    record('finite_actual_plugin_or_backup_job_running',script=script)
    with(ROOT/(script+'.log')).open('w')as log:subprocess.run([PY,'-B',str(D/script),*args],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
def resume():
    for p in STOPS:
        if p.exists()and read(p).get('owner')==OWNER:p.unlink()
    result={}
    for name,extra,statefile in [('continue_ZL_matching.py',[],'FL20_ZL_CONTINUOUS_CONTROLLER.json'),('watch_ZL_useful_complete_backups.py',['--watch'],'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')]:
        state=read(N/statefile);pid=state.get('PID',state.get('owner',{}).get('PID'))
        if pid and alive(pid)and os.fsencode(str(D/name))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0'):continue
        with(N/('ZL_MEASURED_BOUNDARY_RECOVERY_'+name+'.log')).open('ab')as log:p=subprocess.Popen([PY,'-B',str(D/name),*extra],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        result[name]=p.pid
    return result
ready=False
try:
    assert all(not p.exists()for p in STOPS)
    for p in STOPS:
        with p.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='finite real native EQ76 fit at a safe completed cohort boundary'),f)
    pids=[read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID'],read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')['PID']]
    record('awaiting_safe_completed_cohort_boundary',PIDs=pids)
    deadline=time.monotonic()+1200
    while any(alive(pid)for pid in pids):
        if time.monotonic()>deadline:raise TimeoutError('No safe completed boundary within20minutes')
        time.sleep(.5)
    assert not(N/'fl20-corrected-search.pause').exists()
    assert shutil.disk_usage('/tmp').free>=160*2**20,'Reserve160MiB for native EQ study'
    job('study_measured_ZL_boundary_expansion.py')
    completion=read(D/'ZL-measured-boundary-expansion-after21-01/completion.json')
    job('backup_finite_ZL_study.py',['--study',str(D/'ZL-measured-boundary-expansion-after21-01'),'--label','measured-ZL-boundary-expansion-after21-study01'])
    if completion['robust_improvement']:
        job('adopt_measured_ZL_boundaries_and_export.py')
        record('native_EQ76_adopted_only_after_full_supported_export_ZIP_replay_and_push')
    else:record('native_EQ76_candidate_rejected_resume_confirmed_main',summary={k:v for k,v in completion.items()if k not in ['captures','archive_members']})
except BaseException:
    record('failed_preserve_and_resume_current_confirmed_main',error=traceback.format_exc())
    raise
finally:
    if not ready:
        restarted=resume();(N/'ZL_MEASURED_BOUNDARY_MATCHER_RESTART.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PIDs=restarted,reference_match_reached=False),indent=2)+'\n')
