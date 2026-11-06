"""Preserve closed interrupted fit data, explicitly distinguishing it from completion."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--controller',required=True);p.add_argument('--label',required=True);p.add_argument('--fixed-receipt');args=p.parse_args()
J=Path(__file__).resolve().parent;R=Path(args.root);N=J.parent/'native-low-latency-effects';D=Path('/tmp')/(args.label+'-closed-evidence');D.mkdir();state=json.loads((N/args.controller).read_text());assert state['root']==str(R)and not(R/'completion.json').exists();stat=Path('/proc')/str(state['PID'])/'stat';assert not stat.exists()or stat.read_text().split()[2]=='Z'
fixed=None;lookup={}
if args.fixed_receipt:
    fixed=json.loads(Path(args.fixed_receipt).read_text());assert fixed['receipt']['all_retained_study_files_and_WAVs_remote_Git_verified'];members=json.loads((Path('/workspace/divalead')/fixed['receipt']['public_path']/'ARCHIVE_MEMBER_SHA256.json').read_text());remote={r['name']:r for r in members}
    for row in fixed['fixed_original_members']:assert remote[row['snapshot_relative_path']]['SHA256']==row['SHA256'];lookup[row['original_relative_path']]=row
mapping=[]
for file in sorted(R.rglob('*')):
    if not file.is_file()or(file.suffix in['.f32','.dll','.exe']and file.name!='candidate-source-with-tail.f32'):continue
    original=file.relative_to(R).as_posix();blob=file.read_bytes();digest=hashlib.sha256(blob).hexdigest();record=dict(original_relative_path=original,bytes=len(blob),SHA256=digest)
    if original in lookup and lookup[original]['SHA256']==digest:record.update(reused_from_fixed_commit=fixed['receipt']['commit'],fixed_public_path=fixed['receipt']['public_path'],fixed_archive_member=lookup[original]['snapshot_relative_path'])
    else:
        name='EXACT_PADDED_SOURCE_INPUT_FROM_F32.wav'if file.name=='candidate-source-with-tail.f32'else original;target=D/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);record['this_archive_member']=name
    mapping.append(record)
partial=R/'PARTIAL_TRAINING_RESULTS.json.gz';recorded_rows=None
if partial.exists():recorded_rows=len(json.loads(__import__('gzip').decompress(partial.read_bytes())))
(D/'INTERRUPTED_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n');(D/'COMPLETE_ORIGINAL_FILE_RESTORE_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
scope=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_study_root=str(R),reported_last_cases=state.get('cases'),recorded_partial_training_rows=recorded_rows,interrupted_after_environment_reconnect=True,process_not_live=True,search_not_completed=True,no_completed_negative_or_NEW12_acceptance_claim=True,not_adopted=True,reference_match_reached=False,original_files_retained=True,fixed_receipt_reused=bool(fixed),restore_all_original_relative_paths_from_map=True,latest_full41_revalidation_required_before_any_future_adoption=True)
(D/'INTERRUPTED_SCOPE.json').write_text(json.dumps(scope,indent=2)+'\n');code=D/'replay-code';code.mkdir();shutil.copyfile(Path(__file__),code/Path(__file__).name)
for file in J.glob('*.py'):shutil.copyfile(file,code/file.name)
O=J.parent/'stereo-refinement-20261025';subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(O/'backup_complete_finite_study.py'),'--root',str(D),'--label',args.label,'--note','INTERRUPTED, not a completed negative or accepted result. Exact source/inputs/chunks/all281/MIDI/seed/partial GZ/recorded progress components retained. COMPLETE_ORIGINAL_FILE_RESTORE_MAP.json links byte-verified reused fixed members and this new overlay; reconstruct original relative paths from all referenced archives. Exact padded source WAV bytes map to the original .f32 filename. Current full41 remains accepted; any future old-context candidate requires revalidation against the latest BEST. Original local study files retained.'],check=True)
receipt=json.loads((O/(args.label+'_PUBLICATION.json')).read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified'];(J/(args.label+'_PUBLICATION.json')).write_text(json.dumps(dict(receipt=receipt,scope=scope,all_original_members_covered_by_verified_fixed_or_overlay=True),indent=2)+'\n');print(json.dumps(dict(commit=receipt['commit'],**scope)),flush=True)
