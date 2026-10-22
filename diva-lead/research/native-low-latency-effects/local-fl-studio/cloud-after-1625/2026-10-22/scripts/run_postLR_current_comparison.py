"""Reserve a finite independent comparison after both native post-LR profiles."""
from pathlib import Path
import datetime,gzip,json,os,shutil,signal,subprocess,time,traceback
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
STATE=N/'FL20_POST_LR_CURRENT_COMPARISON_FINITE.json';PAUSE=N/'fl20-corrected-search.pause'
ROOT=B/'post-LR16-20-vs-current-independent24-01';OWNER='post-LR-research-vs-current-independent-holdout'
env=dict(os.environ,PYTHONPATH='/tmp/divalead-native-effects:'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
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
def record(phase,**extra):
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,
        actual_FL_GUI_validation_pending=True,only_three_held_notes=True,reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATE)
assert not ROOT.exists()
deadline=time.monotonic()+3600
while True:
    dep=N/'FL20_POST_LR_EQ_PHASE20_FINITE.json';d=read(dep)if dep.exists()else{}
    if d.get('phase')=='post_LR_EQ_phase20_complete_not_automatically_adopted'and not PAUSE.exists():break
    if d.get('phase')=='post_LR_EQ_phase20_failed_preserve_and_diagnose':
        record('dependency_failed_no_competing_cohort_started',dependency=d);raise SystemExit(1)
    assert time.monotonic()<deadline
    record('queued_after_native_post_LR_phase20_profile',dependency_phase=d.get('phase'));time.sleep(5)
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Compare both actual post-LR branches and both grafts against the latest validated supported incumbent using independent24+24 full native captures'),f)
try:
    deadline=time.monotonic()+1800
    while True:
        d=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');saved=d['controller'];now=identity(saved['PID'])
        assert now and now['starttime']==saved['starttime']and now['cmdline']==saved['cmdline']
        if d['phase']=='paused_by_control_or_actual_disk_reserve':break
        assert time.monotonic()<deadline
        record('waiting_for_complete_current_EQ_or_controls_and_full_validation',prior_progress=d.get('progress'));time.sleep(5)
    assert shutil.disk_usage('/tmp').free>800*2**20,'Preserve current captures; free only proved scratch before independent24 comparison'
    control=B/'post-LR-independent24-latest-supported-control.json';control.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes());incumbent=read(control)
    proposals=[]
    for label,source in [('gain16',B/'fl20-post-LR-EQ-02/full-validated-candidate.json'),('phase20',B/'fl20-post-LR-EQ-phase20-01/full-validated-candidate.json')]:
        candidate=read(source);assert candidate['full_fresh_native_realizations']>=12
        assert candidate['source_manifest']['source_audio_SHA256']==incumbent['source_manifest']['source_audio_SHA256']
        proposals.append(source)
        graft=dict(incumbent,**{k:v for k,v in candidate.items()if k.startswith('post_LR_')},
            not_compatible_with_standard_x95_exporter=True,full_fresh_native_realizations=0,
            full_fresh_native_validation_pending=True,research_graph_not_automatically_adopted=True)
        path=B/('post-LR-'+label+'-grafted-on-latest-supported-EQ.json');path.write_text(json.dumps(graft,indent=2)+'\n');proposals.append(path)
    log=B/(ROOT.name+'.log')
    with log.open('w')as f:
        child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(B/'compare_research_postLR_to_current.py'),str(ROOT),str(control),*map(str,proposals)],env=env,stdout=f,stderr=f)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                hosts=[identity(int(p))for p in ids];hosts=[p for p in hosts if p and 'fl_native_'in p['cmdline']and '.exe'in p['cmdline']]
                record('independent_current_incumbent_native_graph_comparison_running',child=identity(child.pid),
                    actual_native_hosts=hosts,numeric_workers_observed=len(hosts),root=str(ROOT),log=str(log));time.sleep(5)
            assert child.returncode==0,(child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
    dest=N/'FL20-corrected/completed'/ROOT.name;dest.mkdir(parents=True,exist_ok=True)
    for p in ROOT.glob('*.json'):
        data=p.read_bytes()
        if len(data)>200000:
            packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data;(dest/(p.name+'.gz')).write_bytes(packed)
        else:shutil.copyfile(p,dest/p.name)
    record('post_LR_vs_current_independent24_complete_matching_resumes',completion=read(ROOT/'completion.json'),
        candidate=str(ROOT/'full-validated-candidate.json'),new_graph_not_automatically_adopted=True)
except BaseException:
    record('post_LR_vs_current_failed_preserve_and_resume_validated_matching',error=traceback.format_exc());raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
