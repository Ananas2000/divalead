"""Finish already-positive fixed12 Fine32 study after provenance-only fix."""
from pathlib import Path
import datetime,json,os,runpy,subprocess,time,traceback
D=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'fine32-provenance-recovery-01';ROOT.mkdir(exist_ok=False)
OWNER='native-WS-fine32-provenance-recovery-20261024';STOPS=[N/'zl-continuation.stop',N/'zl-useful-full-backup.stop'];PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{D.parent}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def read(p):return json.loads(Path(p).read_text())
def alive(pid):
    try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
    except FileNotFoundError:return False
def record(phase,**kw):
    o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw);p=N/'FINE32_PROVENANCE_RECOVERY_CONTROLLER.json';tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(o,indent=2)+'\n');tmp.replace(p)
def resume():
    for p in STOPS:
        if p.exists()and read(p).get('owner')==OWNER:p.unlink()
    result={}
    for script,extra,state in [('continue_ZL_matching.py',[],'FL20_ZL_CONTINUOUS_CONTROLLER.json'),('watch_ZL_useful_complete_backups.py',['--watch'],'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')]:
        d=read(N/state);pid=d.get('PID',d.get('owner',{}).get('PID'))
        if pid and alive(pid)and os.fsencode(str(D/script))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0'):continue
        with(N/('FINE32_PROVENANCE_RESUMED_'+script+'.log')).open('ab')as f:p=subprocess.Popen([PY,'-B',str(D/script),*extra],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        result[script]=p.pid
    return result
try:
    for p in STOPS:
        with p.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='finish actual already-positive nativeFine32 after provenance-only freezer fix'),f)
    pids=[read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID'],read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')['PID']];record('await_safe_completed_main_boundary',PIDs=pids);deadline=time.monotonic()+1200
    while any(alive(pid)for pid in pids):
        if time.monotonic()>deadline:raise TimeoutError('No safe completed boundary within20minutes')
        time.sleep(.5)
    assert not(N/'fl20-corrected-search.pause').exists()
    study=D/'ZL-native-WS-fine32-current-ZL20-01';summary=read(study/'completion.json');assert summary['robust_improvement']and len(summary['captures'])==12
    prior=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert Path(prior['native_ZL_component_state']).read_bytes()==(study/'UNCHANGED_ZL_COMPONENT.bin').read_bytes(),'New incumbent needs a new independent comparison; never overwrite it blindly'
    ready=D.parent/'FL20_NATIVE_ZL_REBASED_05-COMBINED_CANDIDATE_READY.json';assert read(ready)['loss']==summary['candidate_mean']
    h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='finish_positive_fine32_supported_export');record('actual_full21_export_and_independent_ZIP_replay_same_incumbent_as_original12');h['build']('21',candidate=str(ready));kit=D.parent/'FL20_ZL_21_WIP';report=read(kit/'verification/ZL_FULL_VERIFICATION.json');proof=read(kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json');assert report['mean_original_objective']<summary['current_control_mean']-.0005;assert proof['six_fresh_whole_chain_mean']<summary['current_control_mean']-.0005;h['publish']('21')
    chosen=read(ready);chosen.update(accepted_full_public_kit='ZL21',native_WS_fine32_adopted_after_full_export_and_Git=True,independent_full_ZIP_replay_mean=proof['six_fresh_whole_chain_mean']);tmp=D/'ZL-continuous65/BEST_CANDIDATE.partial';tmp.write_text(json.dumps(chosen,indent=2)+'\n');tmp.replace(D/'ZL-continuous65/BEST_CANDIDATE.json')
    receipt=dict(public_kit='ZL21',native_base=str(D.parent/'FL20_NATIVE_ZL_REBASED_05'),paired12_control_mean=summary['current_control_mean'],paired12_candidate_mean=summary['candidate_mean'],paired12_SEM=summary['paired_difference_SEM'],full_export_mean=report['mean_original_objective'],independent_ZIP_mean=proof['six_fresh_whole_chain_mean'],all281_Diva_and12_MIDI_unchanged=True,only_three_held_notes=True,provenance_fix_only_no_repeated_paired12_or_tolerance_change=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
    (ROOT/'ADOPTED_ONLY_AFTER_REAL_FULL_ZIP_AND_PUSH.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'NATIVE_WS_FINE32_FULL_KIT_ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');record('positive_fine32_adopted_after_actual_full21_and_Git',result=receipt);print('REAL_FULL21_FINE32_ADOPTED',json.dumps(receipt),flush=True)
except BaseException:
    record('failed_preserve_current_main_and_completed_positive_study',error=traceback.format_exc());raise
finally:
    restarted=resume();(N/'FINE32_PROVENANCE_RECOVERY_MATCHER_RESTART.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PIDs=restarted,reference_match_reached=False),indent=2)+'\n');print('ACTUAL_MATCHER_AND_WATCHER_RESUMED',json.dumps(restarted),flush=True)
