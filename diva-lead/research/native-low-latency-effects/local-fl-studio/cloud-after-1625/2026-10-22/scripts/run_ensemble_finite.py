"""Run one phase-ensemble EQ fit at an owned idle boundary, then resume search."""
from pathlib import Path
import datetime,gzip,json,os,shutil,signal,subprocess,time,traceback
B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects')
STATE=N/'FL20_ENSEMBLE_EQ_FINITE.json';PAUSE=N/'fl20-corrected-search.pause'
ROOT=B/'fl20-EQ76-ensemble3-01';OWNER='three-real-Chorus-training-realizations-EQ76-finite-profile'
PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
         DIVALEAD_COORD_MAXCALLS='3000',DIVALEAD_COORD_MAXPASSES='9')
def read(p):
    for i in range(8):
        try:return json.loads(Path(p).read_text())
        except json.JSONDecodeError:
            if i==7:raise
            time.sleep(.05)
def identity(pid):
    try:
        p=Path('/proc')/str(pid);s=(p/'stat').read_text().split()
        if s[2]=='Z':return None
        return dict(PID=pid,starttime=s[21],state=s[2],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def same(saved):
    now=identity(saved['PID']);return now and now['starttime']==saved['starttime']and now['cmdline']==saved['cmdline']
def record(phase,**extra):
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,
        only_three_held_notes=True,actual_FL_GUI_validation_pending=True,match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATE)
def idle():
    deadline=time.monotonic()+1800
    while True:
        s=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');assert same(s['controller'])
        if s['phase']=='paused_by_control_or_actual_disk_reserve':return s
        assert time.monotonic()<deadline,'Preserve the active finite cohort and diagnose its timeout'
        record('waiting_for_current_finite_cohort_and_full_validation',prior_progress=s.get('progress'));time.sleep(5)
def run(script,args,root,stage):
    log=B/(root.name+'.log')
    with log.open('w')as f:
        child=subprocess.Popen([PY,'-B',str(B/script),*map(str,args)],env=env,stdout=f,stderr=f)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                hosts=[identity(int(p))for p in ids];hosts=[p for p in hosts if p and 'fl_native_'in p['cmdline']and '.exe'in p['cmdline']]
                progress=read(root/'search-state.json')if(root/'search-state.json').exists()else None
                record(stage,child=identity(child.pid),actual_native_hosts=hosts,numeric_workers_observed=len(hosts),
                    root=str(root),progress=progress,log=str(log));time.sleep(5)
            assert child.returncode==0,(script,child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
def durable(root):
    dest=N/'FL20-corrected/completed'/root.name;dest.mkdir(parents=True,exist_ok=True)
    for p in root.glob('*.json'):
        data=p.read_bytes()
        if len(data)>200000:
            zipped=gzip.compress(data,mtime=0);assert gzip.decompress(zipped)==data
            (dest/(p.name+'.gz')).write_bytes(zipped)
        else:shutil.copyfile(p,dest/p.name)
assert not ROOT.exists(),'Never overwrite active or completed audio work'
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Finish the current full native validation; compare an EQ fit averaged over three real Chorus outputs with two separate heldout outputs and fresh12+12 renders'),f)
control=B/'ensemble3-validated-incumbent.json'
try:
    idle();assert shutil.disk_usage('/workspace').free>64*2**20 and shutil.disk_usage('/tmp').free>512*2**20
    control.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes());incumbent=read(control)
    assert incumbent['full_fresh_native_realizations']>=6 and not incumbent.get('full_fresh_native_validation_pending')
    run('fit_fl20_EQ76_ensemble.py',[control,ROOT],ROOT,'actual_native_EQ76_ensemble3_training')
    durable(ROOT);got=read(ROOT/'full-validated-candidate.json');accepted=False;installed=control
    if got['robust_improvement']and got['loss']<incumbent['loss']:
        comp=B/'fl20-EQ76-ensemble3-independent-01'
        run('compare_supported_native_candidates.py',[comp,control,ROOT/'full-validated-candidate.json'],comp,
            'independent_selection_then12_plus12_ensemble_holdout');durable(comp)
        verified=read(comp/'full-validated-candidate.json')
        if verified['robust_improvement']and verified['loss']<incumbent['loss']:
            # The old controller is explicitly idle and owns no numeric children.
            installed=comp/'full-validated-candidate.json'
            run('start_corrected_fl20.py',['--check-only','--seed',installed],B/'ensemble3-startup-preflight','preflight_validated_ensemble')
            s=idle();saved=s['controller'];assert same(saved)
            os.kill(saved['PID'],signal.SIGTERM);deadline=time.monotonic()+15
            while same(saved):assert time.monotonic()<deadline;time.sleep(.1)
            run('start_corrected_fl20.py',['--seed',installed],B/'ensemble3-controller-handoff','installing_verified_ensemble_improvement')
            assert read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['phase']=='paused_by_control_or_actual_disk_reserve'
            accepted=True
    record('ensemble3_complete_continuous_matching_resumes',completion=read(ROOT/'completion.json'),
        ensemble_improvement_accepted=accepted,installed_candidate=str(installed),
        controller=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['controller'])
except BaseException:
    record('ensemble3_failed_preserve_and_resume_validated_search',error=traceback.format_exc(),original_validated_candidate=str(control));raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
