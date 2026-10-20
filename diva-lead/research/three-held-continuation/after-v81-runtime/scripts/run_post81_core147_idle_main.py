"""Use the two slots of an already idle main parent; preserve handoff ownership."""
from pathlib import Path
import datetime,fcntl,json,os,signal,subprocess,sys,time,traceback
R=Path(__file__).resolve().parent
lock=(R/'post81-core147-idle-main.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
stopped=None
def proc(pid):
    try:
        p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split()
        return dict(PID=pid,state=s[0],ppid=int(s[1]),start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
    except FileNotFoundError:return None
def children(pid):
    return [d for p in Path('/proc').iterdir() if p.name.isdigit() and (d:=proc(int(p.name))) and d['ppid']==pid and d['state']!='Z']
def state(phase,**kw):
    p=R/'post81-core147-idle-main-state.json';q=p.with_suffix('.tmp')
    q.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,stopped_handoff=stopped,numeric_workers=2,idle_main_slot_released=stopped is None,only_three_held=True,match_reached=False,**kw),indent=2)+'\n');q.replace(p)
def terminate(signum,frame):raise SystemExit('Signal '+str(signum))
signal.signal(signal.SIGTERM,terminate)
try:
    handoff=json.loads((R/'post80-source-handoff-state.json').read_text())
    assert handoff['phase']=='waiting_for_current_previous_source_fits_to_finish',handoff
    oldmain=handoff['stopped_parents']['main'];m=proc(oldmain['PID'])
    assert m and m['state']=='T' and m['start']==oldmain['starttime_ticks'] and not children(m['PID'])
    coordinator=proc(handoff['PID'])
    expected=str(R/'handoff_to_post80_plate_source.py').encode()
    if coordinator and expected not in coordinator['cmd']:
        assert b'handoff_to_post80_plate_source.py' in coordinator['cmd'] and Path('/proc',str(coordinator['PID']),'cwd').resolve()==R
        expected=b'handoff_to_post80_plate_source.py'
    assert coordinator and expected in coordinator['cmd'] and coordinator['state']!='T'
    os.kill(coordinator['PID'],signal.SIGSTOP)
    stopped=dict(PID=coordinator['PID'],starttime_ticks=coordinator['start'],expected_command=expected.decode())
    after=json.loads((R/'post80-source-handoff-state.json').read_text())
    assert after['stopped_parents']['main']==oldmain and after['phase']=='waiting_for_current_previous_source_fits_to_finish'
    assert proc(oldmain['PID'])['state']=='T' and not children(oldmain['PID'])
    state('fitting_existing147_in_already_idle_main_two_worker_slot',old_main_parent_owned_by_handoff=oldmain)
    with (R/'post81-core147-idle-main-fit.log').open('w') as log:
        subprocess.run([sys.executable,'-B',str(R/'fit_post81_core147.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_CORE147_WORKERS='2'),stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True,timeout=7200)
    decision=json.loads((R/'post81-core147-research/decision.json').read_text())
    state('finite_core147_finished_resume_owned_handoff',decision=decision)
except Exception:
    state('failed_preserve_core_work_and_resume_handoff',error=traceback.format_exc());raise
finally:
    resumed=None
    if stopped:
        p=proc(stopped['PID'])
        if p and p['start']==stopped['starttime_ticks'] and stopped['expected_command'].encode() in p['cmd'] and p['state']=='T':
            os.kill(p['PID'],signal.SIGCONT);resumed=p['PID']
    prior=json.loads((R/'post81-core147-idle-main-state.json').read_text())
    prior.update(idle_main_slot_released=True,resumed_exact_handoff_PID=resumed,release_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (R/'post81-core147-idle-main-state.json').write_text(json.dumps(prior,indent=2)+'\n')
    print('IDLE_MAIN_TWO_WORKER_SLOT_RELEASED_AND_EXACT_HANDOFF_RESUMED',resumed,flush=True)
