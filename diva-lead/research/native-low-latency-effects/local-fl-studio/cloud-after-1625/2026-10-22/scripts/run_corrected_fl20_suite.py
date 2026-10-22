"""Run corrected-context controls, export a complete WIP, then capacity research."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,time
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
W=Path('/tmp/divalead-native-effects');PY='/workspace/.venvs/divalead/bin/python'
STATE=N/'FL20_CORRECTED_SEARCH_CONTROLLER.json';STOP=N/'fl20-corrected-search.stop'
env=os.environ.copy();env.update(PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def identity(pid):
    try:
        f=Path(f'/proc/{pid}/stat').read_text().split()
        return dict(PID=pid,starttime=f[21],state=f[2],cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def state(phase,**extra):
    data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller=identity(os.getpid()),
        phase=phase,numeric_workers=4,host_context='Chorus_excluded_from_silent_warmup',
        objective_version='local_full_original_criteria_FL20_context_v1',source='physical_FL05_VCA_minus58',
        only_three_held_notes=True,actual_FL_GUI_validation_pending=True,match_reached=False,**extra)
    tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(STATE)
def run(script,args,log,extraenv=None):
    e=env.copy();e.update(extraenv or {})
    with Path(log).open('w')as f:
        child=subprocess.Popen([PY,'-B',str(script),*map(str,args)],env=e,stdout=f,stderr=f)
        while child.poll()is None:
            state('actual_native_work_running',child=identity(child.pid),script=str(script),log=str(log))
            if STOP.exists():
                # Finish the finite child; never leave DSP instances suspended.
                state('stop_requested_finish_current_finite_job',child=identity(child.pid),log=str(log))
            time.sleep(5)
        assert child.returncode==0,(str(script),child.returncode,str(log))
def accept(path):
    got=json.loads(path.read_text());assert not got.get('reference_match_reached')
    d=N/'FL20-corrected';d.mkdir(exist_ok=True)
    shutil.copyfile(path,d/'BEST_CANDIDATE.json')
    return path
try:
    waiting=B/'fl20-Chorus-shapes-EQ76-full-03/full-validated-candidate.json'
    while not waiting.exists():
        assert identity(97262) and identity(97262)['state']!='Z','Initial fitter exited without validation output'
        state('waiting_for_initial_full_EQ_fresh_validation',initial_fitter=identity(97262));time.sleep(5)
    candidate=waiting if json.loads(waiting.read_text())['robust_improvement']else B/'Chorus-shapes-correct-context-01/full-validated-candidate.json'
    candidate=accept(candidate)
    if not STOP.exists():
        root=B/'fl20-controls-full-01'
        run(B/'search_fl20_controls.py',[candidate,root],B/'fl20-controls-full-01.log')
        got=json.loads((root/'full-validated-candidate.json').read_text())
        if got['robust_improvement']:candidate=accept(root/'full-validated-candidate.json')
    kit=B/'FL20_NATIVE_06_WIP'
    run(B/'export_fl20_checkpoint.py',[candidate,kit],B/'FL20_NATIVE_06-export.log')
    run(W/'verify_fst_with_pyflp.py',[kit],B/'FL20_NATIVE_06-parse.log')
    run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/'FL20_NATIVE_06-latency.log')
    run(B/'finalize_fl20_kit.py',[kit,'Diva_NATIVE_06_WIP'],B/'FL20_NATIVE_06-finalize.log')
    (B/'FL20_NATIVE_06_READY.json').write_text(json.dumps(dict(kit=str(kit),candidate=str(candidate),
        ZIP=str(B/'Diva_NATIVE_06_WIP_complete_WIP.zip'),actual_FL_GUI_validation_pending=True,match_reached=False),indent=2)+'\n')
    if not STOP.exists():
        root=B/'fl20-common-postEQ-42-fit-01'
        run(B/'fit_fl20_postEQ.py',[candidate,root],B/'fl20-common-postEQ-42-fit-01.log')
    state('finite_suite_completed',candidate=str(candidate),kit=str(kit),next_research='Inspect common-postEQ fresh validation, extend exporter only if robust')
except BaseException:
    import traceback
    state('failed_preserve_files_and_diagnose',error=traceback.format_exc());raise
