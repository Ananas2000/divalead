"""Current-instance idle restart; preserve every running fit and prior checkpoint."""
from pathlib import Path
import os,sys,signal,json,time,subprocess,datetime
R=Path(__file__).resolve().parent;statefile=R/sys.argv[1];script=sys.argv[2];label=sys.argv[3];old=json.loads(statefile.read_text());pid=old['controller_PID'];p=Path('/proc',str(pid));assert str(R/script).encode() in p.joinpath('cmdline').read_bytes();start=p.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]
while True:
 state=json.loads(statefile.read_text())
 if state['controller_PID']!=pid:
  print('ALREADY_REPLACED_BY_RECOVERY',state['controller_PID'],flush=True);raise SystemExit(0)
 if state['phase']=='failed':raise RuntimeError(state)
 if state['phase'] in ['waiting_for_changed_proved_three_basis','paused_low_workspace_space']:
  assert p.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]==start;os.kill(pid,signal.SIGSTOP);children=[]
  for q in Path('/proc').iterdir():
   if q.name.isdigit():
    try:
     st=q.joinpath('stat').read_text().rsplit(')',1)[1].split()
     if int(st[1])==pid and st[0]!='Z':children.append(int(q.name))
    except (FileNotFoundError,ProcessLookupError):pass
  if not children:os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT);break
  os.kill(pid,signal.SIGCONT)
 time.sleep(5)
for _ in range(50):
 try:
  if p.joinpath('stat').read_text().rsplit(')',1)[1].split()[0]=='Z':break
 except FileNotFoundError:break
 time.sleep(.1)
else:raise RuntimeError('old controller did not exit')
with (R/(label+'-updated-controller.log')).open('a') as log:proc=subprocess.Popen([sys.executable,'-B',str(R/script)],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
reserve=int(os.environ.get('DIVALEAD_MIN_FREE_MIB','1024'))
(R/(label+'-idle-resource-handoff.json')).write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),one_time_current_instance_only=True,old_PID=pid,new_PID=proc.pid,old_state=state,running_fit_not_interrupted=True,new_reserve_MiB=reserve,all_audio_quality_limits_unchanged=True),indent=2)+'\n');print('IDLE_CONTROLLER_RESTARTED_WITH_MIB_RESERVE',reserve,label,proc.pid,flush=True)
