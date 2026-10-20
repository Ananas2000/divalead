"""Reject accidental mixing/loosening when registering the new physical source."""
from pathlib import Path
import copy,datetime,json
R=Path(__file__).resolve().parent;p=R/'auto_backup_three.py';source=p.read_text().split("\nif '--check-only' in sys.argv:",1)[0];ns={'__file__':str(p),'__name__':'post74_registration_check'};exec(compile(source,str(p),'exec'),ns)
proof=R/'source-post74joint-basis/validation.json';d,family,basis=ns['checked'](proof);assert family=='Post74 joint oscillator-filter'
changes=[('unknown_family',lambda x:x.update(source_family='Unproved source')),('wrong_parameter',lambda x:x['changed_source_fields'].update({'OSC:PW':51.90})),('wrong_source_preset',lambda x:x.update(source_preset=str(R/'source-pw5190-basis/Diva_THREE_HELD_BASELINE.h2p'))),('wrong_own_NEW',lambda x:x.update(NEW_independent_prebase=str(R/'source-pw5190-basis/NEW-independent-base-pdc.wav'))),('changed_MIDI_flag',lambda x:x.update(original_three_held_MIDI_events_unchanged=False)),('loosened_guard',lambda x:x['guard_limits'].update(stereo_phase=1.003))]
results=[];tmp=proof.parent/'.registration-negative-control.json';assert not tmp.exists()
try:
 for name,mutate in changes:
  bad=copy.deepcopy(d);mutate(bad);tmp.write_text(json.dumps(bad)+'\n')
  try:ns['checked'](tmp)
  except AssertionError:results.append(dict(case=name,rejected=True))
  else:raise AssertionError('Fault incorrectly accepted: '+name)
finally:tmp.unlink(missing_ok=True)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),real_fully_proved_source_accepted=True,real_source_family=family,negative_controls=results,quality_guards_and_matching_source_requirements_preserved=True,match_reached=False)
(R/'post74-source-registration-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
