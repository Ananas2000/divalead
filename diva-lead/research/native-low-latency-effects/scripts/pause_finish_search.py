"""Pause idle old Finish fit controllers for the user's native-effects priority."""
from pathlib import Path
import datetime, json, os, signal, time

R=Path('/workspace/divalead-work/three-held-continuation')
items=[]
for kind in ['main','phase','balance']:
    state=json.loads((R/f'post80plate68-{kind}-state.json').read_text())
    assert state['phase'] in ['paused_low_workspace_space','waiting_for_changed_proved_three_basis']
    pid=state['controller_PID']
    proc=Path('/proc')/str(pid)
    argv=(proc/'cmdline').read_bytes().split(b'\0')
    assert str(R/f'continue_post80plate68_{kind}.py').encode() in argv
    children=[]
    for other in Path('/proc').iterdir():
        if not other.name.isdigit():continue
        try:
            fields=(other/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[1])==pid and fields[0]!='Z':children.append(int(other.name))
        except (FileNotFoundError,ProcessLookupError):pass
    assert not children,children
    stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
    assert stat[0] not in ['Z','T']
    items.append(dict(kind=kind,PID=pid,starttime_ticks=stat[19],argv=[a.decode() for a in argv if a],previous_state=state))
best=json.loads((R/'POST80PLATE68_MAIN_BEST_ACTUAL.json').read_text())
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='native-low-latency-effects',
            active=True,reason='User prioritizes replacing high-latency Finish with FL native effects before further matching.',
            preserved_best_three_held_model=best,only_three_held_notes=True,controllers=items,
            missing_uploads=['Fruity Chorus_x64.dll','Fruity Stereo Shaper_x64.dll','QuickFontCache_x64.dll'],
            native_audio_render_verified=False,match_reached=False)
target=R/'native-effects-priority.json'
with target.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
for item in items:
    proc=Path('/proc')/str(item['PID'])
    stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
    assert stat[19]==item['starttime_ticks']
    os.kill(item['PID'],signal.SIGTERM)
deadline=time.monotonic()+5
while time.monotonic()<deadline:
    live=[]
    for item in items:
        try:
            fields=Path('/proc',str(item['PID']),'stat').read_text().rsplit(')',1)[1].split()
            if fields[0]!='Z' and fields[19]==item['starttime_ticks']:live.append(item['PID'])
        except FileNotFoundError:pass
    if not live:break
    time.sleep(.1)
assert not live,live
report['all_three_old_controllers_stopped_at_idle_without_active_fit_children']=True
target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(mode=report['mode'],stopped_PIDs=[x['PID'] for x in items],preserved_best=best)),flush=True)
