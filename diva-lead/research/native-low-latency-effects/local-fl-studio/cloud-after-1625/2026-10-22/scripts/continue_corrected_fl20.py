"""One resumable corrected-context controller, with real DSP and full WIP backups."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,shutil,signal,subprocess,sys,time,traceback
B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
STATE=N/'FL20_CORRECTED_SEARCH_CONTROLLER.json';STOP=N/'fl20-corrected-search.stop';PAUSE=N/'fl20-corrected-search.pause'
PY='/workspace/.venvs/divalead/bin/python';env=os.environ.copy()
env.update(PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
lock=(N/'fl20-corrected-search-controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def read(p):
    for attempt in range(8):
        try:return json.loads(Path(p).read_text())
        except json.JSONDecodeError:
            if attempt==7:raise
            time.sleep(.05)
def identity(pid):
    try:
        f=Path(f'/proc/{pid}/stat').read_text().split()
        if f[2]=='Z':return None
        return dict(PID=pid,starttime=f[21],state=f[2],cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def same(saved):
    current=identity(saved['PID'])
    return current and current['starttime']==saved['starttime']and current['cmdline']==saved['cmdline']
def hosts(parent):
    # This kernel does not expose /proc/PID/task/PID/children. ps uses PPID.
    r=subprocess.run(['ps','-o','pid=','--ppid',str(parent)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert r.returncode in [0,1],r.stderr
    child_ids=r.stdout.split()
    result=[]
    for pid in child_ids:
        q=identity(int(pid))
        if q and 'fl_native_'in q['cmdline']and '.exe'in q['cmdline']:result.append(q)
    return result

def state(phase,**extra):
    obj=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller=identity(os.getpid()),
        phase=phase,configured_numeric_workers=4,host_context='Chorus_excluded_from_silent_warmup',
        source='physical_Diva_source_audited_in_manifest',source_preset=best['source_manifest']['source_preset']if 'best'in globals()else None,objective_version='local_full_original_criteria_FL20_context_v1',
        actual_FL_GUI_validation_pending=True,only_three_held_notes=True,match_reached=False,**extra)
    t=STATE.with_suffix('.partial');t.write_text(json.dumps(obj,indent=2)+'\n');t.replace(STATE)
def run(script,args,log,root=None,extras=None):
    e=dict(env,**(extras or {}))
    with Path(log).open('w')as out:
        child=subprocess.Popen([PY,'-B',str(script),*map(str,args)],env=e,stdout=out,stderr=out)
        try:
            while child.poll()is None:
                progress=read(root/'search-state.json')if root and(root/'search-state.json').exists()else None
                live=hosts(child.pid)
                state('corrected_pipeline_step_running',child=identity(child.pid),actual_native_hosts=live,numeric_workers_observed=len(live),
                    script=str(script),log=str(log),root=str(root)if root else None,progress=progress,
                    stop_requested=STOP.exists(),finish_current_finite_job_before_stop=True)
                time.sleep(5)
            assert child.returncode==0,(str(script),child.returncode,str(log))
        finally:
            if child.poll()is None:
                child.send_signal(signal.SIGINT)
                child.wait(timeout=60)

def durable(root):
    dest=N/'FL20-corrected/completed'/root.name;dest.mkdir(parents=True,exist_ok=True)
    for p in root.glob('*.json'):
        data=p.read_bytes()
        if len(data)>200000:
            packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data
            (dest/(p.name+'.gz')).write_bytes(packed)
        else:shutil.copyfile(p,dest/p.name)
def accept(path):
    obj=read(path);assert obj.get('full_fresh_native_realizations',0)>=6 and not obj.get('source_post_EQ')
    assert obj.get('source_manifest')and not obj.get('reference_match_reached',False)
    dest=N/'FL20-corrected/BEST_CANDIDATE.json';dest.parent.mkdir(exist_ok=True)
    tmp=dest.with_suffix('.partial');tmp.write_text(json.dumps(obj,indent=2)+'\n');tmp.replace(dest)
    return obj
def publish(path):
    # Every published improvement includes the complete native project/WAV/FST kit.
    public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
    numbers=[int(p.name[3:])for p in public.glob('WIP[0-9][0-9]')if p.is_dir()]
    number=max(numbers+[6])+1;code=f'{number:02}';kit=B/f'FL20_NATIVE_{code}_WIP';label=f'Diva_NATIVE_{code}_WIP'
    run(B/'export_fl20_checkpoint.py',[path,kit],B/f'{label}-export.log')
    run(W/'verify_fst_with_pyflp.py',[kit],B/f'{label}-parse.log')
    run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/f'{label}-latency.log')
    run(B/'finalize_fl20_kit.py',[kit,label],B/f'{label}-finalize.log')
    zipped=B/(label+'_complete_WIP.zip')
    forecast=2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)+64*2**20
    if shutil.disk_usage('/workspace').free<forecast:
        run(B/'archive_historical_AB_cache.py',[],B/f'{label}-lossless-cache-space.log')
    assert shutil.disk_usage('/workspace').free>=forecast,'Cannot safely back up full WIP without actual disk reserve'
    (B/f'FL20_NATIVE_{code}_READY.json').write_text(json.dumps(dict(kit=str(kit),candidate=str(path),ZIP=str(zipped),match_reached=False),indent=2)+'\n')
    publisher=B/f'publish_fl20_WIP_{code}.py'
    publisher.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
    run(publisher,[],B/f'{label}-Git.log')
    return read(kit/'verification/NATIVE_PRESET_VERIFICATION.json')['mean_original_objective']

seed=Path(sys.argv[1]);attach=read(sys.argv[2])if len(sys.argv)>2 else None
best=accept(seed)
public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
completed_public=[read(p)['mean_original_objective']for p in public.glob('WIP[0-9][0-9]/verification/NATIVE_PRESET_VERIFICATION.json')]
last_published=min(completed_public or[1.6490413730747606]);session=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
try:
    # Attach to one verified finite research process without starting a second cohort.
    if attach:
        ident=attach['process'];root=Path(attach['root'])
        while same(ident):
            live=hosts(ident['PID']);progress=read(root/'search-state.json')if(root/'search-state.json').exists()else None
            state('attached_actual_common_EQ_research_running',attached=ident,actual_native_hosts=live,
                numeric_workers_observed=len(live),root=str(root),progress=progress);time.sleep(5)
        if(root/'completion.json').exists():
            durable(root);extended=read(root/'full-validated-candidate.json')
            (N/'FL20-corrected/COMMON_EQ_RESEARCH_RESULT.json').write_text(json.dumps(extended,indent=2)+'\n')
    generation=0;failures=0
    while not STOP.exists():
        while PAUSE.exists()or shutil.disk_usage('/workspace').free<64*2**20 or shutil.disk_usage('/tmp').free<512*2**20:
            state('paused_by_control_or_actual_disk_reserve',root_free_MiB=shutil.disk_usage('/workspace').free/2**20,
                tmp_free_MiB=shutil.disk_usage('/tmp').free/2**20,best_loss=best['loss'])
            if STOP.exists():break
            time.sleep(10)
        if STOP.exists():break
        source=best['source_manifest'];assert hashlib.sha256(Path(source['source_audio']).read_bytes()).hexdigest()==source['source_audio_SHA256']
        assert read(source['fresh_proof'])['all281_exact_against_variant']
        generation+=1;tag=f'fl20-{session}-{generation:04}';root=B/tag;seedpath=B/(tag+'-seed.json')
        seedpath.write_text(json.dumps(best,indent=2)+'\n')
        script=('fit_fl20_EQ76_coordinates.py'if generation%4==1 else'fit_fl20_EQ76_scaled.py')if generation%2 else'search_fl20_controls.py'
        try:
            run(B/script,[seedpath,root],B/(tag+'.log'),root,
                dict(DIVALEAD_FL20_GENERATION=str(generation),DIVALEAD_LBFGS_MAXCALLS='6500',DIVALEAD_LBFGS_MAXITER='40'))
            durable(root);got=read(root/'full-validated-candidate.json');failures=0
            if got.get('robust_improvement')and got['loss']<best['loss']:
                best=accept(root/'full-validated-candidate.json')
                if best['loss']<last_published*.985:
                    try:last_published=publish(root/'full-validated-candidate.json')
                    except BaseException:
                        (N/'FL20_CORRECTED_PUBLICATION_FAILURE.json').write_text(json.dumps(dict(error=traceback.format_exc(),
                            best_loss=best['loss'],numeric_search_continues=True,inspect_Git_before_retry=True),indent=2)+'\n')
                        # A dirty Git index must be diagnosed before another write.
                        if subprocess.check_output(['git','-C',str(P),'status','--porcelain'],text=True).strip():
                            raise RuntimeError('Interrupted publication left reviewable Git changes; preserve and diagnose')
        except BaseException:
            failures+=1
            (N/f'FL20-corrected/failure-{session}-{generation}.json').write_text(json.dumps(dict(error=traceback.format_exc(),
                seed=str(seedpath),root=str(root),consecutive_failures=failures,match_reached=False),indent=2)+'\n')
            active=subprocess.check_output(['ps','-eo','args='],text=True)
            orphaned=any('fl_native_'in line and '.exe'in line and root.name in line for line in active.splitlines())
            if failures>=2 or orphaned:raise
            state('finite_job_failed_next_distinct_method_keeps_validated_seed',best_loss=best['loss'],failure=traceback.format_exc())
    state('stopped_after_finite_job_by_control_file',best_loss=best['loss'])
except BaseException:
    state('failed_preserve_and_diagnose',best_loss=best['loss'],error=traceback.format_exc());raise
