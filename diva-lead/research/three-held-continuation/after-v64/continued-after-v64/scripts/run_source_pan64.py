"""Bounded actual-Diva source probe in one existing CPU slot, three held notes."""
from pathlib import Path
import os,sys,json,signal,subprocess,datetime
R=Path(__file__).resolve().parent;T=R/'source-pan64-control';T.mkdir(exist_ok=False)
state=json.loads((R/'balance-power-continuation-state.json').read_text());pid=state['controller_PID'];assert b'continue_three_balance_power.py' in Path('/proc',str(pid),'cmdline').read_bytes();os.kill(pid,signal.SIGSTOP);table={}
for q in Path('/proc').iterdir():
    if not q.name.isdigit():continue
    try:
        st=(q/'stat').read_text().rsplit(')',1)[1].split();table[int(q.name)]=(int(st[1]),st[19])
    except (FileNotFoundError,ProcessLookupError):pass
ids=[pid]
for parent in ids:
    for child,(ppid,_) in table.items():
        if ppid==parent and child not in ids:ids.append(child)
rows=[]
for p in ids:
    try:os.kill(p,signal.SIGSTOP);rows.append(dict(PID=p,starttime_ticks=table[p][1]))
    except ProcessLookupError:pass
record=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),temporarily_paused_for_three_held_Diva_probe=True,processes=rows)
(T/'paused-balance-power.json').write_text(json.dumps(record,indent=2)+'\n')
try:
    with (T/'source.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'source_pan64.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdout=log,stderr=log,check=True,timeout=1200)
    d=json.loads(Path('/tmp/divalead-source-pan64/completed.json').read_text());(T/'completed.json').write_text(json.dumps(d,indent=2)+'\n');print('SOURCE_PAN64_ACTUAL_DIVA_PROBES_COMPLETE',d['trials'],d['best']['fields'],d['best']['tone_score'],flush=True)
finally:
    resumed=[]
    for row in reversed(rows):
        try:
            st=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
            if st[19]!=row['starttime_ticks']:continue
            os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
        except (FileNotFoundError,ProcessLookupError):pass
    record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(T/'paused-balance-power.json').write_text(json.dumps(record,indent=2)+'\n');print('ORIGINAL_BALANCE_POWER_RESUMED',resumed,flush=True)
