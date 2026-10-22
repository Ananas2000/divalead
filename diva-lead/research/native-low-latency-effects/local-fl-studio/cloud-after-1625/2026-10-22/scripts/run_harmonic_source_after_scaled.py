"""Run one physical Diva source screen after the current finite EQ profile.

No candidate is installed by this screen. Existing validated continuous work
resumes through the source probe's owned pause/finally mechanism.
"""
from pathlib import Path
import datetime,json,os,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=B/'fl20-Diva-harmonic-source-03';STATE=N/'FL20_HARMONIC_SOURCE_SCREEN_STATE.json'
env=dict(os.environ,PYTHONPATH='/tmp/divalead-native-effects:'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')

def read(p):
    for attempt in range(8):
        try:return json.loads(Path(p).read_text())
        except json.JSONDecodeError:
            if attempt==7:raise
            time.sleep(.05)

def identity(pid):
    try:
        p=Path('/proc')/str(pid);s=(p/'stat').read_text().split()
        if s[2]=='Z':return None
        return dict(PID=pid,starttime=s[21],state=s[2],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None

def save(phase,**extra):
    obj=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),
             phase=phase,root=str(ROOT),only_three_held_notes=True,actual_FL_GUI_export_pending=True,
             original_reference_match_reached=False,**extra)
    t=STATE.with_suffix('.partial');t.write_text(json.dumps(obj,indent=2)+'\n');t.replace(STATE)

try:
    assert not ROOT.exists(),'Do not overwrite an existing source experiment'
    deadline=time.monotonic()+3600
    while True:
        state=read(N/'FL20_SCALED_EQ76_FINITE_PROFILE.json')
        if state['phase']=='finite_scaled_profile_completed_continuous_controller_ready':break
        assert 'failed'not in state['phase'],'Scaled finite job failed; diagnose its actual error first'
        owner=state['owner'];now=identity(owner['PID'])
        assert now and now['starttime']==owner['starttime']and now['cmdline']==owner['cmdline']
        assert time.monotonic()<deadline,'Current finite profile did not complete within its declared queue window'
        save('waiting_for_scaled_profile_completion',actual_prior_job_phase=state['phase']);time.sleep(5)
    deadline=time.monotonic()+60
    while(N/'fl20-corrected-search.pause').exists():
        assert time.monotonic()<deadline,'Another owner still has the corrected pause';time.sleep(1)
    main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');owner=main['controller'];now=identity(owner['PID'])
    assert now and now['starttime']==owner['starttime']and now['cmdline']==owner['cmdline']
    with(B/'fl20-Diva-harmonic-source-03.log').open('w')as log:
        child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(B/'probe_corrected_Diva_harmonic_source.py'),str(ROOT)],env=env,stdout=log,stderr=log)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                processes=[identity(int(p))for p in ids];processes=[p for p in processes if p and '.exe'in p['cmdline']]
                reports=list(ROOT.glob('*/verification.json'))
                save('physical_Diva_source_and_native_DLL_screen_running',child=identity(child.pid),
                     actual_DSP_processes=processes,source_cases_completed=len(reports),
                     current_main_controller_phase=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['phase'])
                time.sleep(5)
            assert child.returncode==0,('Source screen failed',child.returncode,str(B/'fl20-Diva-harmonic-source-03.log'))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)
    chosen=read(ROOT/'PROVISIONAL_SELECTED.json')
    save('physical_source_screen_complete_not_automatically_adopted',completion=read(ROOT/'completion.json'),
         selected_source=chosen['source_preset'],robust_improvement=chosen['robust_improvement'],
         selected_fresh_mean=chosen['loss'],control_fresh_mean=chosen['seed_fresh_mean_loss'],
         next_step='If robust, audit independent actual Diva chunk reload and pair against current FX before any adoption')
except BaseException:
    save('source_screen_failed_preserve_and_diagnose',error=traceback.format_exc());raise
