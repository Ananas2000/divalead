"""Finish finite experiment preservation while normal three-note research continues."""
from pathlib import Path
import datetime,fcntl,json,os,subprocess,sys,time,traceback
R=Path(__file__).resolve().parent
lock=(R/'post78-followup-stage.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def save(phase,**extra):
    p=R/'post78-followup-stage.tmp'
    p.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,match_reached=False,**extra),indent=2)+'\n')
    p.replace(R/'post78-followup-stage.json')
try:
    while True:
        coupled=json.loads((R/'source-post77coupled-state.json').read_text())
        cleaner=json.loads((R/'post77-cleaner-hf100-state.json').read_text())
        alternative=json.loads((R/'post77-cleaner-alternative-state.json').read_text())
        shapes=json.loads((R/'source-post78-shapes-state.json').read_text())
        if coupled.get('slot_released') and cleaner.get('phase_slot_released') and shapes.get('slot_released') and Path('/tmp/divalead-source-post78-shapes/completed.json').exists() and alternative['phase'] in ['no_separate_quieter_alternative_found','quieter_alternative_rejected_by_actual_quality','quieter_alternative_fully_proved_not_claimed_primary_winner']:
            break
        for name,d in [('coupled',coupled),('cleaner',cleaner),('alternative',alternative),('shapes',shapes)]:
            if d['phase'].startswith('failed'):raise RuntimeError((name,d))
        save('waiting_for_completed_finite_jobs',coupled_phase=coupled['phase'],cleaner_phase=cleaner['phase'],alternative_phase=alternative['phase'],shape_phase=shapes['phase'])
        time.sleep(15)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    save('checking_actual_shape_dumps_MIDI_and_archiving_all_cases')
    for name in ['verify_post78_shape_screens.py','archive_post78_shape_screens.py']:
        subprocess.run([sys.executable,'-B',str(R/name)],env=env,check=True)
    source=json.loads(Path('/tmp/divalead-source-post78-shapes/completed.json').read_text())
    global_tone=min(json.loads(p.read_text())['tone_score'] for p in R.glob('post74joint-verified-*/validation.json'))
    better=bool(source['best']['fields'] and source['best']['feasible'] and source['best']['tone_score']<global_tone-1e-6)
    save('all_finite_jobs_closed_and_shape_archives_verified',shape_trials=source['trials'],shape_best=source['best'],current_global_fully_proved_tone=global_tone,shape_source_requires_new_matching_own_NEW_full_proof=better,all_finite_CPU_slots_released=True,normal_source_specific_controllers_continue=True)
    print('POST78_FOLLOWUP_READY_ALL_FINITE_SLOTS_RELEASED',better,flush=True)
except Exception:
    save('failed_preserve_everything_and_diagnose',error=traceback.format_exc());raise
