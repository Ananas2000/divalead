"""Borrow the already owned third slot, repair one point, then resume the fit."""
from pathlib import Path
import datetime,json,os,signal,subprocess,sys
ROOT=Path(__file__).resolve().parent;CONTROL=ROOT/'source-pw5190-allguards-control';CONTROL.mkdir(exist_ok=False)
def table():
    result={}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            result[int(path.name)]=dict(state=fields[0],ppid=int(fields[1]),starttime=fields[19],cmd=(path/'cmdline').read_bytes().split(b'\0'))
        except (FileNotFoundError,ProcessLookupError):pass
    return result
processes=table();owners=[pid for pid,v in processes.items() if v['state']!='Z' and str(ROOT/'run_pw5190_coupled135.py').encode() in v['cmd']]
assert len(owners)==1,owners
targets=[pid for pid,v in processes.items() if v['ppid']==owners[0] and str(ROOT/'fit_pw5190_coupled135.py').encode() in v['cmd']]
assert len(targets)==1,targets
paused=[];record=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),coupled_coordinator_PID=owners[0],processes=paused,original_balance_owner_untouched=True)
def save():
    (CONTROL/'paused-coupled.json').write_text(json.dumps(record,indent=2)+'\n')
try:
    root=targets[0];os.kill(root,signal.SIGSTOP);paused.append(dict(PID=root,starttime_ticks=processes[root]['starttime']));save()
    processes=table();ids=[root]
    for parent in ids:
        for child,v in processes.items():
            if v['ppid']!=parent or child in ids:continue
            ids.append(child)
            try:os.kill(child,signal.SIGSTOP);paused.append(dict(PID=child,starttime_ticks=v['starttime']));save()
            except ProcessLookupError:pass
    with (CONTROL/'repair.log').open('w') as log:
        subprocess.run([sys.executable,'-B',str(ROOT/'repair_pw5190_gain_all_guards.py')],
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,
            stdout=log,stderr=log,check=True,timeout=900)
finally:
    resumed=[]
    for row in reversed(paused):
        try:
            fields=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
            if fields[19]!=row['starttime_ticks']:continue
            os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
        except (FileNotFoundError,ProcessLookupError):pass
    record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
    print('COUPLED135_RESUMED_AFTER_GAIN_GUARD_REPAIR',resumed,flush=True)
