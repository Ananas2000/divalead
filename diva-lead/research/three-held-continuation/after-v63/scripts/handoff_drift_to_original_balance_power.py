"""One current-instance handoff, only after the separate Drift fit is idle."""
from pathlib import Path
import os,sys,signal,json,time,subprocess,datetime
R=Path(__file__).resolve().parent
old=json.loads((R/'drift24-continuation-state.json').read_text());pid=old['controller_PID'];p=Path('/proc',str(pid))
assert b'continue_drift24.py' in (p/'cmdline').read_bytes()
start=(p/'stat').read_text().rsplit(')',1)[1].split()[19]
while True:
    state=json.loads((R/'drift24-continuation-state.json').read_text())
    assert state['controller_PID']==pid
    if state['phase']=='failed':raise RuntimeError(state)
    if state['phase'] in ['waiting_for_changed_proved_three_basis','paused_low_workspace_space']:
        assert (p/'stat').read_text().rsplit(')',1)[1].split()[19]==start
        os.kill(pid,signal.SIGSTOP)
        children=[]
        for q in Path('/proc').iterdir():
            if not q.name.isdigit():continue
            try:
                st=(q/'stat').read_text().rsplit(')',1)[1].split()
                if int(st[1])==pid and st[0]!='Z':children.append(int(q.name))
            except (FileNotFoundError,ProcessLookupError):pass
        if not children:
            os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT);break
        os.kill(pid,signal.SIGCONT)
    time.sleep(5)
for _ in range(100):
    try:
        if (p/'stat').read_text().rsplit(')',1)[1].split()[0]=='Z':break
    except FileNotFoundError:break
    time.sleep(.1)
else:raise RuntimeError('old Drift controller did not exit')
with (R/'balance-power-controller.log').open('a') as log:
    proc=subprocess.Popen([sys.executable,'-B',str(R/'continue_three_balance_power.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
(R/'drift-to-original-balance-power-handoff.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),one_time_current_instance_only=True,old_Drift_PID=pid,new_original_three_controller_PID=proc.pid,old_state=state,running_fit_not_interrupted=True,Drift_all_data_retained=True,source_family='original-user-selected-three',numeric_workers=1,minimum_free_MiB=1024,all_audio_quality_limits_unchanged=True),indent=2)+'\n')
print('IDLE_DRIFT_SLOT_NOW_ORIGINAL_THREE_BALANCE42_POWER69',proc.pid,flush=True)
