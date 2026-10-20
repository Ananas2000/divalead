"""Check actual 281-parameter dumps and incoming MIDI of every saved Diva trial."""
from pathlib import Path
import datetime,hashlib,json
R=Path(__file__).resolve().parent;S=Path('/tmp/divalead-source-post78-shapes')
B=R/'source-post74joint-basis'
baseline=(B/'Diva_all281.tsv').read_text().splitlines()
expected=json.loads((B/'MIDI_events_48k.json').read_text())
names={'OSC:Shape1':'OSC: Shape1','OSC:Shape2':'OSC: Shape2'}
indices={key:next(int(row.split('\t')[0]) for row in baseline[1:] if row.split('\t')[2]==name) for key,name in names.items()}
rows=[]
history=json.loads((S/'history.json').read_text())
assert len(history)==json.loads((S/'completed.json').read_text())['trials']
for row in history:
    case=S/('trial-'+format(row['index'],'03d'))
    actual=(case/'all281.tsv').read_text().splitlines()
    assert len(actual)==len(baseline)==282
    differences={int(a.split('\t')[0]) for a,b in zip(actual[1:],baseline[1:]) if a!=b}
    assert differences=={indices[field] for field in row['fields']},(row['index'],differences)
    for field,value in row['fields'].items():
        assert float(actual[indices[field]+1].split('\t')[3])==value
    events=[list(map(int,line.split()[1:])) for line in (case/'Diva.log').read_text().splitlines() if line.startswith('NOTE ')]
    assert events==expected and sum(e[1]==144 for e in events)==6
    rows.append(dict(index=row['index'],changed_indices=sorted(differences),requested_values_exact_in_actual_parameter_dump=True,all_other_parameters_byte_equal=True,original_three_held_MIDI_events_exact=True))
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_actual_Diva_dumps_and_MIDI_logs_checked=True,entries=rows,no_arpeggiator_envelope_or_note_schedule_changes=True,source_screens_are_not_full_release_proofs=True,match_reached=False)
(R/'post78-shape-parameter-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('ALL_SHAPE_FRESH_DIVA_TRIALS_ONLY_REQUESTED_281_PARAMETER_CHANGES_AND_EXACT_12_MIDI_EVENTS_PASS',flush=True)
