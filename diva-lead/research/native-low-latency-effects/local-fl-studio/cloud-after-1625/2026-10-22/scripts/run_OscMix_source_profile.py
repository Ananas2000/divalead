"""Hand off to verified source08, profile it, publish any robust improvement.

The normal controller remains paused while the finite four-worker source fit
runs. Every controller replacement is at an observed idle boundary and checks
PID, starttime and cmdline. A failed fit falls back to the complete WIP08.
"""
from pathlib import Path
import datetime,json,os,signal,subprocess,time,traceback
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
P=Path('/workspace/divalead');W=Path('/tmp/divalead-native-effects');PY='/workspace/.venvs/divalead/bin/python'
PAUSE=N/'fl20-corrected-search.pause';STATE=N/'FL20_CORRECTED_SEARCH_CONTROLLER.json';FINITE=N/'FL20_FINITE_SOURCE_PROFILE.json'
owner='verified-OscMix6p3-finite-profile';root=B/'fl20-OscMix6p3-EQ76-profile-01'
fallback=B/'FL20_NATIVE_08_WIP/verification/candidate.json';seed=B/'OscMix6p3-profile-seed.json'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
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
def record(phase,**extra):
    data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,
        source='Actual audited Diva OscMix6.3, PWModDepth+1, VCA ModDepth-58',root=str(root),
        only_three_held_notes=True,actual_FL_GUI_export_pending=True,match_reached=False,**extra)
    temp=FINITE.with_suffix('.partial');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(FINITE)
def run(script,args,log,profile=False):
    with Path(log).open('w')as f:
        child=subprocess.Popen([PY,'-B',str(script),*map(str,args)],env=env,stdout=f,stderr=f)
        try:
            while child.poll()is None:
                progress=read(root/'search-state.json')if profile and(root/'search-state.json').exists()else None
                ps=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE)
                hosts=[identity(int(p))for p in ps.stdout.split()];hosts=[v for v in hosts if v and 'fl_native_'in v['cmdline']and'.exe'in v['cmdline']]
                record('finite_source_EQ_fit_running'if profile else'finite_source_verification_or_backup_running',
                    child=identity(child.pid),actual_native_hosts=hosts,numeric_workers_observed=len(hosts),progress=progress,log=str(log));time.sleep(5)
            assert child.returncode==0,(str(script),child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
def idle_handoff(candidate):
    deadline=time.monotonic()+300
    while True:
        state=read(STATE)
        if state['phase']=='paused_by_control_or_actual_disk_reserve':break
        assert time.monotonic()<deadline;record('waiting_for_current_validated_cycle_idle_boundary',current_phase=state['phase']);time.sleep(5)
    saved=state['controller'];current=identity(saved['PID'])
    assert current and current['starttime']==saved['starttime']and current['cmdline']==saved['cmdline']
    assert 'continue_corrected_fl20.py'in current['cmdline']
    # The current finite child has completed and the controller is paused.
    os.kill(saved['PID'],signal.SIGTERM)
    deadline=time.monotonic()+15
    while identity(saved['PID']):assert time.monotonic()<deadline;time.sleep(.1)
    run(B/'start_corrected_fl20.py',['--seed',candidate],B/(Path(candidate).parent.name+'-source-controller-handoff.log'))
    assert read(STATE)['phase']=='paused_by_control_or_actual_disk_reserve'
    record('verified_source_controller_handoff_complete',new_controller=read(STATE)['controller'],candidate=str(candidate))

assert not PAUSE.exists(),'Another finite branch owns corrected CPU pause'
with PAUSE.open('x')as f:json.dump(dict(owner=owner,root=str(root),reason='Profile the verified best complete OscMix6.3 source, then resume corrected continuous search'),f)
chosen=fallback
try:
    idle_handoff(fallback)
    run(B/'fit_fl20_EQ76_with_shapes.py',[seed,root],B/'fl20-OscMix6p3-EQ76-profile-01.log',profile=True)
    got=read(root/'full-validated-candidate.json')
    # This seed already passed an independent6+6 source comparison. The full
    # profile must additionally beat both its fresh control and complete08.
    if got['robust_improvement']and got['loss']<read(fallback)['loss']-.003:
        chosen=root/'full-validated-candidate.json'
        public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
        number=max([int(d.name[3:])for d in public.glob('WIP[0-9][0-9]')if d.is_dir()]+[8])+1
        code=f'{number:02}';label=f'Diva_NATIVE_{code}_WIP';kit=B/f'FL20_NATIVE_{code}_WIP'
        run(B/'export_fl20_checkpoint.py',[chosen,kit],B/f'{label}-export.log')
        proof=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json')
        assert proof['mean_original_objective']<read(fallback)['loss']-.003
        run(W/'verify_fst_with_pyflp.py',[kit],B/f'{label}-parse.log')
        run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/f'{label}-latency.log')
        run(B/'finalize_fl20_kit.py',[kit,label],B/f'{label}-finalize.log')
        if __import__('shutil').disk_usage('/workspace').free<100*2**20:
            run(B/'archive_historical_AB_cache.py',[],B/f'{label}-lossless-cache-space.log')
        (B/f'FL20_NATIVE_{code}_READY.json').write_text(json.dumps(dict(kit=str(kit),candidate=str(chosen),ZIP=str(B/(label+'_complete_WIP.zip')),match_reached=False),indent=2)+'\n')
        script=B/f'publish_fl20_WIP_{code}.py';script.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
        run(script,[],B/f'{label}-Git.log')
        chosen=kit/'verification/candidate.json'
    # A second idle replacement installs the freshly validated profile. If no
    # robust win survived full export, complete08 remains the source baseline.
    idle_handoff(chosen)
    record('finite_profile_completed_continuous_controller_ready',accepted_candidate=str(chosen),
        corrected_controller=read(STATE)['controller'],profile_robust=got['robust_improvement'])
except BaseException:
    record('finite_profile_failed_preserve_and_resume_verified_source',error=traceback.format_exc(),fallback=str(fallback))
    raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==owner:PAUSE.unlink()
