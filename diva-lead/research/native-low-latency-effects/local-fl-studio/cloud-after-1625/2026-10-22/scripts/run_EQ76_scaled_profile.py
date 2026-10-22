"""Finite scaled-objective research; resume the verified continuous controller.

Only real native DLL renders are scored. Saved losses remain unscaled.
The current finite cohort finishes before this process uses the same four slots.
"""
from pathlib import Path
import datetime,hashlib,json,os,shutil,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
PY='/workspace/.venvs/divalead/bin/python'
PAUSE=N/'fl20-corrected-search.pause';STATE=N/'FL20_CORRECTED_SEARCH_CONTROLLER.json'
RECORD=N/'FL20_SCALED_EQ76_FINITE_PROFILE.json'
OWNER='EQ76-scaled1000-controlled-finite-experiment'
ROOT=B/'fl20-EQ76-scaled1000-profile-01'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
         DIVALEAD_LBFGS_OBJECTIVE_SCALE='1000',DIVALEAD_LBFGS_MAXCALLS='6500',DIVALEAD_LBFGS_MAXITER='40')

def read(path):
    for attempt in range(8):
        try:return json.loads(Path(path).read_text())
        except json.JSONDecodeError:
            if attempt==7:raise
            time.sleep(.05)

def identity(pid):
    try:
        p=Path('/proc')/str(pid);fields=(p/'stat').read_text().split()
        if fields[2]=='Z':return None
        return dict(PID=pid,starttime=fields[21],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None

def record(phase,**extra):
    data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),
              phase=phase,root=str(ROOT),objective_scale=1000,unscaled_audio_criterion_unchanged=True,
              only_three_held_notes=True,actual_FL_GUI_export_pending=True,match_reached=False,**extra)
    temp=RECORD.with_suffix('.partial');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(RECORD)

def wait_idle():
    deadline=time.monotonic()+1800
    while True:
        state=read(STATE)
        assert identity(state['controller']['PID'])=={k:v for k,v in state['controller'].items()if k!='state'}
        if state['phase']=='paused_by_control_or_actual_disk_reserve':return state
        assert time.monotonic()<deadline,'Existing finite cohort did not reach idle boundary'
        record('waiting_for_existing_finite_job_and_validation',current_phase=state['phase'],progress=state.get('progress'))
        time.sleep(5)

def run(script,args,log,profile=False):
    with Path(log).open('w')as out:
        child=subprocess.Popen([PY,'-B',str(script),*map(str,args)],env=env,stdout=out,stderr=out)
        try:
            while child.poll()is None:
                ps=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False)
                hosts=[identity(int(p))for p in ps.stdout.split()]
                hosts=[v for v in hosts if v and 'fl_native_'in v['cmdline']and '.exe'in v['cmdline']]
                progress=read(ROOT/'search-state.json')if profile and(ROOT/'search-state.json').exists()else None
                record('finite_scaled_native_EQ76_running'if profile else'full_native_kit_verification_or_backup',
                       child=identity(child.pid),actual_native_hosts=hosts,numeric_workers_observed=len(hosts),progress=progress,log=str(log))
                time.sleep(5)
            assert child.returncode==0,(str(script),child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)

def replace_idle_controller(candidate):
    state=wait_idle();saved={k:v for k,v in state['controller'].items()if k!='state'}
    assert identity(saved['PID'])==saved
    assert 'continue_corrected_fl20.py'in saved['cmdline']
    os.kill(saved['PID'],signal.SIGTERM)
    deadline=time.monotonic()+15
    while identity(saved['PID']):
        assert time.monotonic()<deadline;time.sleep(.1)
    run(B/'start_corrected_fl20.py',['--seed',candidate],B/'EQ76-scaled1000-resume-controller.log')
    assert read(STATE)['phase']=='paused_by_control_or_actual_disk_reserve'

assert read(PAUSE)['owner']==OWNER,'This finite branch does not own the pause'
assert not ROOT.exists(),'Never overwrite a completed or active research directory'
chosen=None;resumed=False
try:
    wait_idle()
    seed=B/'EQ76-scaled1000-profile-seed.json'
    seed.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes());base=read(seed)
    assert base['full_fresh_native_realizations']>=6 and not base.get('source_post_EQ')
    assert not base.get('full_fresh_native_validation_pending',False)
    chosen=seed
    run(B/'fit_fl20_EQ76_scaled.py',[seed,ROOT],B/'fl20-EQ76-scaled1000-profile-01.log',True)
    got=read(ROOT/'full-validated-candidate.json')
    accepted=bool(got['robust_improvement']and got['loss']<base['loss'])
    if accepted:chosen=ROOT/'full-validated-candidate.json'
    complete=N/'FL20-corrected/completed'/ROOT.name;complete.mkdir(parents=True,exist_ok=False)
    for source in ROOT.glob('*.json'):shutil.copyfile(source,complete/source.name)
    shutil.copyfile(B/'EQ76_scaled_experiment_setup.json',complete/'experiment_setup.json')
    public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
    published=[read(p)['mean_original_objective']for p in public.glob('WIP[0-9][0-9]/verification/NATIVE_PRESET_VERIFICATION.json')]
    picked=read(chosen)
    if picked['loss']<min(published)-.006:
        number=max([int(d.name[3:])for d in public.glob('WIP[0-9][0-9]')if d.is_dir()]+[9])+1
        code=f'{number:02}';label=f'Diva_NATIVE_{code}_WIP';kit=B/f'FL20_NATIVE_{code}_WIP'
        run(B/'export_fl20_checkpoint.py',[chosen,kit],B/f'{label}-export.log')
        proof=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json')
        assert proof['mean_original_objective']<min(published)-.004,'Improvement did not survive independent export'
        run(W/'verify_fst_with_pyflp.py',[kit],B/f'{label}-parse.log')
        run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/f'{label}-latency.log')
        run(B/'finalize_fl20_kit.py',[kit,label],B/f'{label}-finalize.log')
        zipped=B/(label+'_complete_WIP.zip')
        forecast=2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)+64*2**20
        if shutil.disk_usage('/workspace').free<forecast:
            run(B/'archive_historical_AB_cache.py',[],B/f'{label}-lossless-cache-space.log')
        assert shutil.disk_usage('/workspace').free>=forecast,'Preserve the actual disk reserve before Git backup'
        (B/f'FL20_NATIVE_{code}_READY.json').write_text(json.dumps(dict(kit=str(kit),candidate=str(chosen),ZIP=str(zipped),match_reached=False),indent=2)+'\n')
        publisher=B/f'publish_fl20_WIP_{code}.py';publisher.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
        run(publisher,[],B/f'{label}-Git.log')
        chosen=kit/'verification/candidate.json'
    replace_idle_controller(chosen);resumed=True
    record('finite_scaled_profile_completed_continuous_controller_ready',accepted_scaled_candidate=accepted,
           scaled_fresh_mean=got['loss'],fresh_control_mean=got['seed_fresh_mean_loss'],
           accepted_candidate=str(chosen),corrected_controller=read(STATE)['controller'])
except BaseException:
    record('finite_scaled_profile_failed_preserve_and_resume',error=traceback.format_exc(),last_validated_candidate=str(chosen)if chosen else None)
    raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
