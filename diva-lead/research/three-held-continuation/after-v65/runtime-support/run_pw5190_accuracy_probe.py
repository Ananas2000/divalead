"""Use the balance/power CPU slot for a bounded physical Diva probe, then resume."""
from pathlib import Path
import datetime, json, os, signal, subprocess, sys, time

ROOT = Path(__file__).resolve().parent
CONTROL = ROOT / 'source-pw5190-accuracy-control'
CONTROL.mkdir(exist_ok=False)
paused = []
record = dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              processes=paused, only_three_held=True)

def save():
    (CONTROL / 'paused-balance-power.json').write_text(json.dumps(record, indent=2) + '\n')

def fields(pid):
    return Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()

try:
    # Wait for the current third-slot owner to finish and resume its exact PIDs.
    while True:
        previous = json.loads((ROOT / 'source-pw5190-gain-control/paused-balance-power.json').read_text())
        if 'resumed_UTC' in previous:
            break
        time.sleep(5)
    state = json.loads((ROOT / 'balance-power-continuation-state.json').read_text())
    parent = state['controller_PID']
    assert b'continue_three_balance_power.py' in Path('/proc', str(parent), 'cmdline').read_bytes()
    start = fields(parent)[19]
    os.kill(parent, signal.SIGSTOP)
    paused.append(dict(PID=parent, starttime_ticks=start))
    save()
    table = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            row = fields(int(path.name))
            table[int(path.name)] = (int(row[1]), row[19])
        except (FileNotFoundError, ProcessLookupError):
            pass
    pids = [parent]
    for pid in pids:
        for child, (ppid, start) in table.items():
            if ppid != pid or child in pids:
                continue
            pids.append(child)
            try:
                assert fields(child)[19] == start
                os.kill(child, signal.SIGSTOP)
                paused.append(dict(PID=child, starttime_ticks=start))
                save()
            except (FileNotFoundError, ProcessLookupError):
                pass
    with (CONTROL / 'source.log').open('w') as log:
        subprocess.run([sys.executable, '-B', str(ROOT / 'probe_pw5190_accuracy.py')],
                       env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'),
                       stdin=subprocess.DEVNULL, stdout=log, stderr=log, check=True, timeout=1200)
    completed = json.loads(Path('/tmp/divalead-pw5190-accuracy/completed.json').read_text())
    (CONTROL / 'completed.json').write_text(json.dumps(completed, indent=2) + '\n')
    print('SOURCE_CURRENT65_COMPLETED', completed['trials'], completed['best']['fields'],
          completed['best']['tone_score'], flush=True)
finally:
    resumed = []
    for row in reversed(paused):
        try:
            if fields(row['PID'])[19] != row['starttime_ticks']:
                continue
            os.kill(row['PID'], signal.SIGCONT)
            resumed.append(row['PID'])
        except (FileNotFoundError, ProcessLookupError):
            pass
    record.update(resumed_PIDs=resumed, resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('ORIGINAL_BALANCE_POWER_RESUMED', resumed, flush=True)
