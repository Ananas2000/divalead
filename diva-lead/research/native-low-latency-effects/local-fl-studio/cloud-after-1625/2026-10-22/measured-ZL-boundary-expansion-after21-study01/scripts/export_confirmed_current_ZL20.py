"""Complete current87parameter progress as a new fully replayed FL20 kit."""
from pathlib import Path
import datetime,json,runpy,shutil,time,traceback
D=Path(__file__).resolve().parent
N=Path('/workspace/divalead-work/native-low-latency-effects')
R=Path('/workspace/divalead-work/three-held-continuation')
STATE=N/'ZL20_MANUAL_FULL_EXPORT_CONTROLLER.json'
def record(phase,**kw):
    o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(o,indent=2)+'\n');p.replace(STATE)
try:
    deadline=time.monotonic()+180
    while(R/'auto-backup.pause').exists():
        if time.monotonic()>deadline:raise TimeoutError('Git writer still owns pause')
        time.sleep(.2)
    assert shutil.disk_usage('/workspace').free>=192*2**20
    assert shutil.disk_usage('/tmp').free>=220*2**20
    helpers=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='manual_actual_full_ZL20')
    prior=helpers['read'](N/'LATEST_EXTERNAL_ZL_PUBLICATION.json')
    assert prior['full_kit']=='ZL-WIP19'
    record('actual_full_ZL20_render_then_independent_ZIP_replay')
    helpers['build']('20')
    kit=D.parent/'FL20_ZL_20_WIP'
    report=helpers['read'](kit/'verification/ZL_FULL_VERIFICATION.json')
    replay=helpers['read'](kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json')
    assert report['mean_original_objective']<prior['original_objective_export_mean']-.0005
    assert replay['six_fresh_whole_chain_mean']<prior['ZIP_replay_mean']-.0005
    helpers['publish']('20')
    record('full_ZL20_pushed_only_after_actual_full_render_ZIP_replay_and_gain_checks',full_export_mean=report['mean_original_objective'],independent_ZIP_replay_mean=replay['six_fresh_whole_chain_mean'])
except BaseException:
    record('export_failed_or_did_not_pass_keep_current_main_and_prior_full_kit',error=traceback.format_exc())
    raise
