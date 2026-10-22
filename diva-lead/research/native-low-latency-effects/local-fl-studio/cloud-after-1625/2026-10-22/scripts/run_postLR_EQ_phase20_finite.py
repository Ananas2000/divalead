"""Reserve the next completed cohort for one actual native curve experiment."""
from pathlib import Path
import datetime,json,os,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
PAUSE=N/'fl20-corrected-search.pause';STATE=N/'FL20_POST_LR_EQ_PHASE20_FINITE.json'
OWNER='native-post-LR-EQ-phase20-finite-experiment';ROOT=B/'fl20-post-LR-EQ-phase20-01'
env=dict(os.environ,PYTHONPATH='/tmp/divalead-native-effects:'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_POSTLR_MAXCALLS='1800',DIVALEAD_POSTLR_MAXPASSES='12',DIVALEAD_POSTLR_INITIAL_PROFILE=str(B/'fl20-post-LR-EQ-02/full-validated-candidate.json'))

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
           phase=phase,root=str(ROOT),only_three_held_notes=True,extra_post_LR_graph_not_yet_deployable=True,
           original_reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATE)

assert not ROOT.exists(),'Never overwrite a real active or completed experiment'
deadline=time.monotonic()+3600
while True:
    dep=N/'FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json'
    d=read(dep)if dep.exists()else{}
    if d.get('phase')in ['local4_integration_and_repaired_LR_profile_complete_matching_resumes']and not PAUSE.exists():break
    assert time.monotonic()<deadline,'Inspect the prior finite experiment; do not compete for its CPU cohort'
    record('queued_after_repaired_post_LR_EQ16_profile',dependency_phase=d.get('phase'));time.sleep(5)
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Finish the current cohort, then add actual native per-channel Stereo Shaper delay/phase controls to the completed post-LR EQ16 research profile. Keep published WIP13 installed until any new graph passes full integration and actual restored-state audio checks.'),f)
try:
    deadline=time.monotonic()+1800
    while True:
        main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');saved=main['controller'];now=identity(saved['PID'])
        assert now and now['starttime']==saved['starttime']and now['cmdline']==saved['cmdline']
        if main['phase']=='paused_by_control_or_actual_disk_reserve':break
        assert time.monotonic()<deadline,'The active finite cohort did not complete'
        record('waiting_for_active_EQ_fit_and_fresh_validation',prior_job_progress=main.get('progress'));time.sleep(5)
    seed=B/'post-LR-EQ-phase20-frozen-validated-seed.json';seed.write_bytes((B/'post-LR-repaired-profile-current-seed.json').read_bytes())
    base=read(seed);assert base['full_fresh_native_realizations']>=6 and base.get('waveshaper_curve_format')=='native_monotone_bump_v1'
    with(B/'fl20-post-LR-EQ-phase20-01.log').open('w')as log:
        child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(B/'probe_fl20_postLR_EQ_phase20.py'),str(seed),str(ROOT)],env=env,stdout=log,stderr=log)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                hosts=[identity(int(p))for p in ids];hosts=[p for p in hosts if p and 'fl_native_'in p['cmdline']and '.exe'in p['cmdline']]
                progress=read(ROOT/'search-state.json')if(ROOT/'search-state.json').exists()else None
                record('actual_native_post_LR_EQ_plus_SS_phase20_ensemble_running',child=identity(child.pid),actual_native_hosts=hosts,
                       numeric_workers_observed=len(hosts),progress=progress);time.sleep(5)
            assert child.returncode==0,('Native curve screen failed',child.returncode,str(B/'fl20-post-LR-EQ-phase20-01.log'))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
    result=read(ROOT/'full-validated-candidate.json')
    record('post_LR_EQ_phase20_complete_not_automatically_adopted',completion=read(ROOT/'completion.json'),
           robust_improvement=result['robust_improvement'],candidate=str(ROOT/'full-validated-candidate.json'),
           next_step='If robust, integrate the additional L/R native-EQ graph and actual mixer routing through playback, FST/FLP export, latency and restored-state audio before adoption')
except BaseException:
    record('post_LR_EQ_phase20_failed_preserve_and_diagnose',error=traceback.format_exc());raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
