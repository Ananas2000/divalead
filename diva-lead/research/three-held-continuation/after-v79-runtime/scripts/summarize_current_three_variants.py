"""Rank only fully proved user-authorized three-held variants; retain noise tradeoffs."""
from pathlib import Path
import datetime,hashlib,json
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');script=R/'auto_backup_three.py';ns={'__file__':str(script),'__name__':'current_variant_review'};exec(compile(script.read_text().split("\nif '--check-only' in sys.argv:",1)[0],str(script),'exec'),ns)
rows=[];groups={}
for path,d,family,basis in ns['choices']():
 model_sha=hashlib.sha256(Path(d['core_model']).read_bytes()).hexdigest();preset_sha=hashlib.sha256(Path(d['source_preset']).read_bytes()).hexdigest();key=(model_sha,preset_sha)
 if key in groups:groups[key]['also_proved_as'].append(path.parent.name);continue
 row=dict(model=path.parent.name,validation=str(path),source_family=family,changed_Diva_fields=d.get('changed_source_fields',{}),tone_score=d['tone_score'],score=d['score'],upper_off_error=d['metrics']['upper_off'],crest_RMS_dB=d['crest_RMS_dB'],core_model_SHA256=model_sha,preset_SHA256=preset_sha,also_proved_as=[],incoming_notes_per_phrase=3,all_original_quality_guards_and_12_cases_checked=True,match_reached=False);rows.append(row);groups[key]=row
rows.sort(key=lambda x:x['tone_score'])
front=[row['model'] for row in rows if not any(other['tone_score']<=row['tone_score'] and other['upper_off_error']<=row['upper_off_error'] and (other['tone_score']<row['tone_score'] or other['upper_off_error']<row['upper_off_error']) for other in rows)]
complete=json.loads((P/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text());numbered=[]
for p in sorted([p for p in (P/'diva-lead').iterdir() if p.is_dir() and __import__('re').fullmatch(r'v\d+(?:[-_].*)?',p.name)],key=lambda p:int(p.name.split('-')[0][1:])):
 v=p/'verification/selected_validation.json';d=json.loads(v.read_text()) if v.exists() else {}
 numbered.append(dict(version=p.name,retained_unchanged=True,incoming_notes_per_phrase=3 if d.get('original_three_held_MIDI_events_unchanged') else None,known_three_tone_score=d.get('tone_score') if d.get('original_three_held_MIDI_events_unchanged') else None,unknown_architecture_not_inferred=True))
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scored_unique_fully_proved_three_held_models=len(rows),best_by_original_fixed_tone_error=rows[0]['model'],all_numbered_versions_retained=len(numbered),selected_complete_release=complete['version'],selected_complete_tone=complete['tone_score'],tone_and_offharmonic_error_Pareto_alternatives=front,subjective_audition_performed=False,old_sixteen_note_versions_not_used_for_current_selection=True,measurements_are_not_similarity_percentages=True,no_files_deleted_by_this_review=True,match_reached=False,numbered_versions=numbered,ranked_three_held=rows)
(R/'current-three-note-variant-registry.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['numbered_versions','ranked_three_held']}),flush=True)
