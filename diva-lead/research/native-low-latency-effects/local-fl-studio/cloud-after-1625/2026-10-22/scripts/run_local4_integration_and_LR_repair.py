"""Owned-boundary actual DLL integration, independent24 comparison and L/R repair."""
from pathlib import Path
import datetime,gzip,json,os,shutil,signal,subprocess,time,traceback
B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
STATE=N/'FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='validated-local4-curve-integration-and-postLR-repair';PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
published=None

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
        published_checkpoint=published,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATE)
def idle():
    deadline=time.monotonic()+1800
    while True:
        s=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');assert same(s['controller'])
        if s['phase']=='paused_by_control_or_actual_disk_reserve':return s
        assert time.monotonic()<deadline
        record('waiting_for_active_finite_cohort',prior_progress=s.get('progress'));time.sleep(5)
def run(script,args,log,root=None,stage='actual_native_validation',extras=None):
    with Path(log).open('w')as f:
        child=subprocess.Popen([PY,'-B',str(script),*map(str,args)],env=dict(env,**(extras or{})),stdout=f,stderr=f)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                hosts=[identity(int(p))for p in ids];hosts=[p for p in hosts if p and 'fl_native_'in p['cmdline']and '.exe'in p['cmdline']]
                progress=read(root/'search-state.json')if root and(root/'search-state.json').exists()else None
                record(stage,child=identity(child.pid),actual_native_hosts=hosts,numeric_workers_observed=len(hosts),
                    root=str(root)if root else None,progress=progress,script=str(script),log=str(log));time.sleep(5)
            assert child.returncode==0,(str(script),child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
def durable(root):
    dest=N/'FL20-corrected/completed'/root.name;dest.mkdir(parents=True,exist_ok=True)
    for p in root.glob('*.json'):
        data=p.read_bytes()
        if len(data)>200000:
            packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data;(dest/(p.name+'.gz')).write_bytes(packed)
        else:shutil.copyfile(p,dest/p.name)
def install(candidate):
    run(B/'start_corrected_fl20.py',['--check-only','--seed',candidate],B/'local4-final-startup-preflight.log',stage='preflight_complete_supported_curve')
    s=idle();saved=s['controller'];assert same(saved)
    os.kill(saved['PID'],signal.SIGTERM);deadline=time.monotonic()+15
    while same(saved):assert time.monotonic()<deadline;time.sleep(.1)
    run(B/'start_corrected_fl20.py',['--seed',candidate],B/'local4-controller-handoff.log',stage='installing_verified_supported_curve')
    assert read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['phase']=='paused_by_control_or_actual_disk_reserve'
def publish(candidate,control_mean):
    global published
    public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
    number=max(int(p.name[3:])for p in public.glob('WIP[0-9][0-9]')if p.is_dir())+1;code=f'{number:02}';label=f'Diva_NATIVE_{code}_WIP';kit=B/f'FL20_NATIVE_{code}_WIP'
    run(B/'export_fl20_checkpoint.py',[candidate,kit],B/(label+'-export.log'),stage='actual_full_WIP_export_and_native_FST_roundtrip')
    export=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json')
    assert export['mean_original_objective']<control_mean-.0005,'Keep the full actual export and diagnose the independent comparison before publishing'
    run(W/'verify_fst_with_pyflp.py',[kit],B/(label+'-parse.log'),stage='independent_FST_parse')
    run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/(label+'-latency.log'),stage='actual_latency_block_and_causal_controls')
    run(B/'finalize_fl20_kit.py',[kit,label],B/(label+'-finalize.log'),stage='complete_FL20_project_AB_instructions_and_ZIP')
    zipped=B/(label+'_complete_WIP.zip');forecast=64*2**20+2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)
    if shutil.disk_usage('/workspace').free<forecast:run(B/'archive_historical_AB_cache.py',[],B/(label+'-lossless-cache-space.log'),stage='losslessly_archiving_only_old_AB_cache')
    assert shutil.disk_usage('/workspace').free>=forecast
    (B/f'FL20_NATIVE_{code}_READY.json').write_text(json.dumps(dict(kit=str(kit),candidate=str(candidate),ZIP=str(zipped),match_reached=False),indent=2)+'\n')
    publisher=B/f'publish_fl20_WIP_{code}.py';publisher.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
    run(publisher,[],B/(label+'-Git.log'),stage='normal_protected_Git_full_backup')
    published='WIP'+code
    return kit/'verification/candidate.json'
assert read(PAUSE)['owner']==OWNER
try:
    idle();assert shutil.disk_usage('/tmp').free>700*2**20
    seed=B/'post-LR-repair-validated-seed.json';seed.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes())
    smoke=B/'fl20-post-LR-structural-repair-02'
    run(B/'probe_fl20_postLR_EQ.py',[seed,smoke],B/(smoke.name+'.log'),smoke,'actual_native_repaired_LR_isolation_positive_controls',dict(DIVALEAD_POSTLR_MAXCALLS='5',DIVALEAD_POSTLR_MAXPASSES='1'))
    durable(smoke)
    audit=B/'local4-WS-integration-audit-01'
    run(B/'verify_local4_curve_integration.py',[],B/(audit.name+'.log'),audit,'actual_local4_saved_state_vs_shared_helper_audio')
    durable(audit)
    comparison=B/'local4-current-EQ-independent24-01'
    run(B/'compare_supported_native_candidates24.py',[comparison,audit/'current-validated-incumbent.json',audit/'supported-old-EQ-proposal.json',audit/'supported-current-EQ-proposal.json'],B/(comparison.name+'.log'),comparison,'independent12_selection_then24_plus24_current_incumbent_holdout')
    durable(comparison);got=read(comparison/'full-validated-candidate.json');control=read(audit/'current-validated-incumbent.json')
    curve_accepted=bool(got['robust_improvement']and got['loss']<control['loss'])
    if curve_accepted:
        installed=publish(comparison/'full-validated-candidate.json',got['seed_fresh_mean_loss']);install(installed)
    # Current supported curve, including new local metadata if it was adopted.
    lr_seed=B/'post-LR-repaired-profile-current-seed.json';lr_seed.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes())
    root=B/'fl20-post-LR-EQ-02'
    run(B/'probe_fl20_postLR_EQ.py',[lr_seed,root],B/(root.name+'.log'),root,'actual_repaired_native_post_LR_EQ_ensemble3_profile',dict(DIVALEAD_POSTLR_MAXCALLS='1800',DIVALEAD_POSTLR_MAXPASSES='16'))
    durable(root)
    record('local4_integration_and_repaired_LR_profile_complete_matching_resumes',
        supported_local4_curve_accepted=curve_accepted,
        independent_curve_result=read(comparison/'completion.json'),LR_profile_result=read(root/'completion.json'),
        post_LR_graph_not_automatically_adopted=True,controller=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['controller'])
except BaseException:
    record('local4_or_LR_integration_failed_preserve_and_resume_validated_matching',error=traceback.format_exc());raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
