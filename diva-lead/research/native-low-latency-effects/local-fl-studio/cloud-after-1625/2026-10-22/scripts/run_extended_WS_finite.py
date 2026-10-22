"""Reserve the next completed cohort for one actual native curve experiment."""
from pathlib import Path
import datetime,json,os,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
PAUSE=N/'fl20-corrected-search.pause';STATE=N/'FL20_EXTENDED_WS_FINITE_PROFILE.json'
OWNER='native-extended-WS-curve-finite-experiment';ROOT=B/'fl20-WS-extended-curve-01'
env=dict(os.environ,PYTHONPATH='/tmp/divalead-native-effects:'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')

def read(p):
    for attempt in range(8):
        try:return json.loads(Path(p).read_text())
        except json.JSONDecodeError:
            if attempt==7:raise
            time.sleep(.05)

def identity(pid):
    try:
        p=Path('/proc')/str(pid);v=(p/'stat').read_text().split()
        if v[2]=='Z':return None
        return dict(PID=pid,starttime=v[21],state=v[2],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None

def record(phase,**extra):
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),
           phase=phase,root=str(ROOT),only_three_held_notes=True,extra_curve_not_yet_deployable=True,
           original_reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATE)

assert not ROOT.exists(),'Never overwrite a real active or completed experiment'
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Finish the active coordinate fit and fresh controls, then test a richer monotone curve in the actual WaveShaper DLL'),f)
try:
    deadline=time.monotonic()+1800
    while True:
        main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');saved=main['controller'];now=identity(saved['PID'])
        assert now and now['starttime']==saved['starttime']and now['cmdline']==saved['cmdline']
        if main['phase']=='paused_by_control_or_actual_disk_reserve':break
        assert time.monotonic()<deadline,'The active finite cohort did not complete'
        record('waiting_for_active_EQ_fit_and_fresh_validation',prior_job_progress=main.get('progress'));time.sleep(5)
    seed=B/'extended-WS-frozen-validated-seed.json';seed.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes())
    base=read(seed);assert base['full_fresh_native_realizations']>=6 and not base.get('waveshaper_curve_adjustment')
    with(B/'fl20-WS-extended-curve-01.log').open('w')as log:
        child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(B/'probe_fl20_extended_WS.py'),str(seed),str(ROOT)],env=env,stdout=log,stderr=log)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                hosts=[identity(int(p))for p in ids];hosts=[p for p in hosts if p and 'fl_native_'in p['cmdline']and '.exe'in p['cmdline']]
                progress=read(ROOT/'search-state.json')if(ROOT/'search-state.json').exists()else None
                record('actual_native_extended_curve_screen_running',child=identity(child.pid),actual_native_hosts=hosts,
                       numeric_workers_observed=len(hosts),progress=progress);time.sleep(5)
            assert child.returncode==0,('Native curve screen failed',child.returncode,str(B/'fl20-WS-extended-curve-01.log'))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
    result=read(ROOT/'full-validated-candidate.json')
    record('extended_curve_screen_complete_not_automatically_adopted',completion=read(ROOT/'completion.json'),
           robust_improvement=result['robust_improvement'],candidate=str(ROOT/'full-validated-candidate.json'),
           next_step='If robust, integrate the extra curve coordinates through playback, all fitters, FST/FLP export and restore before adoption')
except BaseException:
    record('extended_curve_screen_failed_preserve_and_diagnose',error=traceback.format_exc());raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
