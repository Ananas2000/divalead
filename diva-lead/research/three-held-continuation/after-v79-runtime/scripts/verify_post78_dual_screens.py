"""Check actual 281-parameter dumps and incoming MIDI of every saved Diva trial."""
from pathlib import Path
import datetime,hashlib,json
R=Path(__file__).resolve().parent;S=Path('/tmp/divalead-source-post78-dual')
B=R/'source-post74joint-basis'
baseline=(B/'Diva_all281.tsv').read_text().splitlines()
expected=json.loads((B/'MIDI_events_48k.json').read_text())
names={'OSC:Tri1':'OSC: Triangle1On','OSC:Saw1':'OSC: Saw1On','OSC:PWM1':'OSC: Pwm1On','OSC:Sin2':'OSC: Sine2On','OSC:Tri2':'OSC: Triangle2On','OSC:Saw2':'OSC: Saw2On','OSC:PW2':'OSC: Pulse2On','OSC:PWM2':'OSC: PWM2On','VCF1:Fback':'VCF1: Feedback','VCF1:KeyScl':'VCF1: KeyFollow'}
indices={key:next(int(row.split('\t')[0]) for row in baseline[1:] if row.split('\t')[2]==name) for key,name in names.items()}
rows=[]
history=json.loads((S/'history.json').read_text())
assert len(history)==json.loads((S/'completed.json').read_text())['trials']
for row in history:
    case=S/('trial-'+format(row['index'],'03d'))
    actual=(case/'all281.tsv').read_text().splitlines()
    assert len(actual)==len(baseline)==282
    differences={int(a.split('\t')[0]) for a,b in zip(actual[1:],baseline[1:]) if a!=b}
    effective={field:(max(0,value) if field=='VCF1:Fback' else value) for field,value in row['fields'].items()}
    assert differences=={indices[field] for field,value in effective.items() if float(baseline[indices[field]+1].split('\t')[3])!=value},(row['index'],differences)
    for field,value in effective.items():
        assert float(actual[indices[field]+1].split('\t')[3])==value
    events=[list(map(int,line.split()[1:])) for line in (case/'Diva.log').read_text().splitlines() if line.startswith('NOTE ')]
    assert events==expected and sum(e[1]==144 for e in events)==6
    rows.append(dict(index=row['index'],changed_indices=sorted(differences),requested_values_exact_after_documented_feedback_nonnegative_clamp=True,all_other_parameters_byte_equal=True,original_three_held_MIDI_events_exact=True))
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_actual_Diva_dumps_and_MIDI_logs_checked=True,entries=rows,no_arpeggiator_envelope_or_note_schedule_changes=True,source_screens_are_not_full_release_proofs=True,match_reached=False)
(R/'post78-dual-parameter-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('ALL_ACTIVE_DUAL_VCO_TRIALS_ONLY_REQUESTED_281_PARAMETER_CHANGES_AND_EXACT_12_MIDI_EVENTS_PASS',flush=True)
