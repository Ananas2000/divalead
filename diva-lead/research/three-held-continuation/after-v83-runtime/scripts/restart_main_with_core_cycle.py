"""Finish the active main fit/proof, then reload its expanded existing-coefficient cycle."""
from pathlib import Path
import datetime,fcntl,json,os,signal,subprocess,time,traceback
R=Path(__file__).resolve().parent;PY='/workspace/.venvs/divalead/bin/python'
lock=(R/'core-cycle-main-reload.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
held=None;retired=False
def proc(pid):
    try:
        p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split()
        return dict(PID=pid,state=s[0],ppid=int(s[1]),start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
    except FileNotFoundError:return None
def children(pid):return [d for p in Path('/proc').iterdir() if p.name.isdigit() and (d:=proc(int(p.name))) and d['ppid']==pid and d['state']!='Z']
def write(p,d):q=p.with_suffix('.tmp');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def state(phase,**kw):write(R/'post82-core-cycle-reload-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,held=held,retired=retired,all_original_guards_unchanged=True,match_reached=False,**kw))
try:
    while True:
        d=json.loads((R/'post80plate68-main-state.json').read_text());assert d['phase']!='failed',d
        if d['phase'] in ['fresh_Diva_Windows_own_NEW_12_cases_proof','waiting_for_changed_proved_three_basis','paused_low_workspace_space']:
            p=proc(d['controller_PID']);assert p and str(R/'continue_post80plate68_main.py').encode() in p['cmd'] and p['state']!='T'
            os.kill(p['PID'],signal.SIGSTOP);time.sleep(.02)
            after=json.loads((R/'post80plate68-main-state.json').read_text())
            if after!=d or any(any(b'/fit_three_' in x for x in child['cmd']) for child in children(p['PID'])):
                os.kill(p['PID'],signal.SIGCONT);time.sleep(.2);continue
            held=dict(PID=p['PID'],start=p['start'],command=str(R/'continue_post80plate68_main.py'),original_state=d);break
        state('waiting_for_current_main_fit_to_finish');time.sleep(.25)
    state('waiting_for_current_actual_proof_to_finish')
    while children(held['PID']):time.sleep(.2)
    if d['phase']=='fresh_Diva_Windows_own_NEW_12_cases_proof':
        roundname=next(x for x in Path(d['fit']).parts if x.startswith('round-'))
        target=R/('post80plate68-verified-live-main-'+roundname.removeprefix('round-'));run=R/'post80plate68-live-main'/roundname
        if (target/'validation.json').exists():receipt=dict(validation=str(target/'validation.json'),fresh_proof_completed=True,parent_stopped_before_housekeeping=True,controller_housekeeping_not_fabricated=True)
        else:
            from three_candidate_decision import quality_rejection
            receipt=quality_rejection(run/'validation.log',target);assert receipt is not None,'Infrastructure failure in the previous main proof'
        write(run/'core-cycle-idle-reload-receipt.json',receipt)
    p=proc(held['PID']);assert p and p['state']=='T' and p['start']==held['start'] and not children(p['PID'])
    os.kill(p['PID'],signal.SIGTERM);os.kill(p['PID'],signal.SIGCONT)
    for _ in range(100):
        q=proc(p['PID'])
        if not q or q['state']=='Z':break
        time.sleep(.1)
    else:raise RuntimeError('Previous main remains live')
    retired=True
    subprocess.run([PY,'-B',str(R/'start_three_services.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),check=True)
    report=json.loads((R/'service-start-last.json').read_text())
    assert sum(row['newly_started'] for row in report['services'])==1
    assert next(row for row in report['services'] if row['script']=='continue_post80plate68_main.py')['newly_started']
    state('main_reloaded_with_core147_HF100_gain93_cycle',start_report=report)
except Exception:
    state('failed_preserve_all_finished_proofs_and_diagnose',error=traceback.format_exc());raise
finally:
    if held and not retired:
        p=proc(held['PID'])
        if p and p['state']=='T' and p['start']==held['start'] and held['command'].encode() in p['cmd']:os.kill(p['PID'],signal.SIGCONT)
