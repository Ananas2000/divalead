"""Check current/previous FL instructions against actual packaged files and source."""
from pathlib import Path
import datetime,json,re,sys
D=Path(sys.argv[1]);OLD=Path(sys.argv[2]);R=Path(__file__).resolve().parent
current=D.name.split('-')[0];previous=OLD.name.split('-')[0]
links=[]
for name in ['FL_STUDIO_RU.md','README.md','COMPARISON_RU.md','BUILDING.md']:
    text=(D/name).read_text()
    for destination in re.findall(r'\]\(([^)]+)\)',text):
        if '://' in destination or destination.startswith('#'):continue
        assert (D/destination.split('#')[0]).is_file(),(name,destination)
        links.append(dict(document=name,target=destination,exists=True))
    versions=set(re.findall(r'\b[vV](\d+)\b',text))
    assert versions<=set([current[1:],previous[1:]]),(name,versions)
guide=(D/'FL_STUDIO_RU.md').read_text()
assert 'AB_REFERENCE_'+previous.upper()+'_'+current.upper()+'_WIP' in guide
for token in re.findall(r'`([^`]+)`',guide):
    if token.endswith(('.dll','.fxp','.h2p','.mid','.wav','.mp3')) and not token.startswith('.'):
        assert (D/token).is_file(),token
proof=json.loads((D/'verification/selected_validation.json').read_text())
old=json.loads((OLD/'verification/selected_validation.json').read_text())
assert proof['tone_score']<old['tone_score']
assert (D/'Diva_THREE_HELD_180BPM.mid').read_bytes()==(OLD/'Diva_THREE_HELD_180BPM.mid').read_bytes()
if proof['source_family']==old['source_family']:
    assert (D/'verification/Diva_all281.tsv').read_bytes()==(OLD/'verification/Diva_all281.tsv').read_bytes()
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),version=current,previous=previous,all_relative_documentation_targets_exist=True,checked_links=links,three_held_MIDI_byte_equal=True,source_family=proof['source_family'],only_existing_Finish_model_fields_changed=json.loads((D/'verification/Finish_changed_fields.json').read_text()),old_tone=old['tone_score'],new_tone=proof['tone_score'],FL_GUI_tested=False,match_reached=False)
(R/(current+'-FL-instruction-file-checks.json')).write_text(json.dumps(report,indent=2)+'\n')
print('CURRENT_KIT_FL_DOCUMENTATION_AND_FILE_NAMES_VERIFIED',current,len(links),flush=True)
