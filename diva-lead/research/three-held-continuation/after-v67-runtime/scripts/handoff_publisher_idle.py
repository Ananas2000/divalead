"""Reload the checked publisher code only at its cooperative idle boundary."""
from pathlib import Path
import datetime, fcntl, json, os, signal, subprocess, time
ROOT=Path(__file__).resolve().parent;PAUSE=ROOT/'auto-backup.pause'
assert not PAUSE.exists()
owner='idle-publisher-code-handoff-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
PAUSE.write_text(json.dumps(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))+'\n')
for _ in range(120):
    state=json.loads((ROOT/'auto-backup-state.json').read_text())
    if state['phase']=='paused_for_manual_Git_work':break
    time.sleep(1)
else:raise RuntimeError(state)
old=state['publisher_PID'];assert str(ROOT/'auto_backup_three.py').encode() in Path('/proc',str(old),'cmdline').read_bytes()
with (ROOT/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd='/workspace/divalead')
    os.kill(old,signal.SIGTERM)
    for _ in range(40):
        try:alive=Path('/proc',str(old),'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
        except FileNotFoundError:alive=False
        if not alive:break
        time.sleep(.1)
    else:raise RuntimeError('Old publisher is still alive')
    with (ROOT/'auto-backup-controller.log').open('a') as log:
        process=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(ROOT/'auto_backup_three.py')],
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,
            stdout=log,stderr=log,start_new_session=True)
    for _ in range(60):
        state=json.loads((ROOT/'auto-backup-state.json').read_text())
        if state['publisher_PID']==process.pid and state['phase']=='paused_for_manual_Git_work':break
        time.sleep(.2)
    else:raise RuntimeError(state)
    assert json.loads(PAUSE.read_text())['owner']==owner
    PAUSE.unlink()
    report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_PID=old,new_PID=process.pid,
                idle_handoff=True,numeric_fits_untouched=True,private_code_current=True)
    (ROOT/'publisher-idle-handoff-latest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
