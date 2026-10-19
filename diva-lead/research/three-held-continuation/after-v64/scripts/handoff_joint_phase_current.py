"""Current-instance-only idle handoff from phase18 to alternating phase18/fine55."""
from pathlib import Path
import os,signal,json,time,subprocess,datetime
R=Path(__file__).resolve().parent;initial=json.loads((R/'phase-continuation-state.json').read_text());pid=initial['controller_PID'];p=Path('/proc',str(pid));start=p.joinpath('stat').read_text().rsplit(')',1)[1].split()[19];assert b'continue_phase18.py' in p.joinpath('cmdline').read_bytes()
while True:
 state=json.loads((R/'phase-continuation-state.json').read_text());assert state['controller_PID']==pid and state['phase']!='failed'
 if state['phase'] in ['waiting_for_changed_proved_three_basis','paused_low_workspace_space']:
  assert p.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]==start;os.kill(pid,signal.SIGSTOP);children=[]
  for q in Path('/proc').iterdir():
   if q.name.isdigit():
    try:
     st=q.joinpath('stat').read_text().rsplit(')',1)[1].split()
     if int(st[1])==pid and st[0]!='Z':children.append(int(q.name))
    except (FileNotFoundError,ProcessLookupError):pass
  if not children:
   os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT);break
  os.kill(pid,signal.SIGCONT)
 time.sleep(5)
for _ in range(50):
 try:
  if p.joinpath('stat').read_text().rsplit(')',1)[1].split()[0]=='Z':break
 except FileNotFoundError:break
 time.sleep(.1)
else:raise RuntimeError('old phase controller did not exit')
with (R/'joint-phase-controller.log').open('a') as log:proc=subprocess.Popen([os.sys.executable,'-B',str(R/'continue_three_joint_phase.py')],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),start_new_session=True)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),one_time_current_instance_only=True,old_PID=pid,old_starttime=start,new_PID=proc.pid,old_state_at_handoff=state,unfinished_fit_interrupted=False,all_previous_round_data_preserved=True,phase18_and_fine55_alternate_one_worker=True)
(R/'joint-phase-handoff.json').write_text(json.dumps(report,indent=2)+'\n');print('PHASE18_IDLE_HANDOFF_TO_ALTERNATING_JOINT_PHASE_COMPLETE',proc.pid,flush=True)
