"""Archive an immutable input/seed snapshot; do not freeze or alter a live fitter."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--controller',required=True);p.add_argument('--label',required=True);args=p.parse_args()
J=Path(__file__).resolve().parent;R=Path(args.root);D=Path('/tmp')/(args.label+'-immutable-inputs');D.mkdir();N=J.parent/'native-low-latency-effects';state=json.loads((N/args.controller).read_text());pid=state['PID'];stat=(Path('/proc')/str(pid)/'stat').read_text().split();assert stat[2]!='Z';assert(R/'EXACT109_PARAMETER_SPECS.json').is_file();selected=[]
names=['PRIOR_COMBINED_CANDIDATE.json','PRIMARY.bin','POST.bin','ANCHOR40_PRIMARY.bin','ANCHOR40_POST.bin','CANDIDATE_Diva.h2p','CURRENT_DIVA_EXACT_SOURCE_PROOF.json','CONTROL_LATEST_ASSESSMENTS.json','ANCHOR40_ASSESSMENTS.json','PREDECLARED_PROTOCOL.json','SEED64_ACTUAL_RESULTS.json','SELECTED_FEASIBLE_SEED.json','FIT_SEED_PRIMARY.bin','FIT_SEED_POST.bin','FEASIBLE_SEED_FULL_WIP.wav','EXACT109_PARAMETER_SPECS.json','BOTH_WORKERS_BOTH_ZLS_NEUTRAL_IDENTITY.json','GUI_OSSTEP2_NATIVE_STATE.bin']
def copy(source,name):
    blob=source.read_bytes();target=D/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob);assert source.read_bytes()==blob;selected.append(dict(original_relative_path=source.relative_to(R).as_posix(),snapshot_relative_path=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
for source in sorted(R.iterdir()):
    if source.is_file()and(source.name in names or(source.name.startswith('TRAINING_')and source.suffix=='.wav')or source.name.endswith('-actual-WS-resaved.bin')):copy(source,source.name)
for folder in ['CANDIDATE_DIVA_REAL_RUN','COLD_CANDIDATE_SOURCE_REPLAY']:
    for source in sorted((R/folder).rglob('*')):
        if source.is_file():copy(source,source.relative_to(R).as_posix())
# Preserve the exact RIFF/PEAK timestamp bytes as well as samples, rather than
# claiming a regenerated soundfile container will have the same file hash.
copy(R/'candidate-source-with-tail.f32','EXACT_PADDED_SOURCE_INPUT_FROM_F32.wav')
(D/'FIXED_INPUT_ORIGINAL_PATH_SHA256.json').write_text(json.dumps(selected,indent=2)+'\n')
(D/'LIVE_STUDY_SCOPE.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_study_root=str(R),actual_live_PID=pid,actual_live_starttime=stat[21],phase_at_snapshot=state['phase'],cases_at_snapshot=state.get('cases'),fixed_inputs_and_frozen_seed_only=True,mutable_fit_progress_not_claimed_frozen=True,exact_padded_input_restore_mapping='EXACT_PADDED_SOURCE_INPUT_FROM_F32.wav -> candidate-source-with-tail.f32',complete_original_protocol='PREDECLARED_PROTOCOL.json',not_adopted=True,search_not_complete=True,reference_match_reached=False),indent=2)+'\n')
code=D/'replay-code';code.mkdir()
for source in J.glob('*.py'):shutil.copyfile(source,code/source.name)
for root,name in [(J.parent/'continuation-20261030','joint_primary_post_fit.py'),(J.parent/'stereo-refinement-20261026','checked_mean_three_real_primary_fit.py'),(J.parent/'stereo-refinement-20261026','normal_staged_primary_fit.py'),(J.parent/'pc-stereo-20261024','native_post_trim.py')]:shutil.copyfile(root/name,code/name)
O=J.parent/'stereo-refinement-20261025';subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(O/'backup_complete_finite_study.py'),'--root',str(D),'--label',args.label,'--note','Immutable inputs/source/all281/MIDI/frozen seed and exact padded WAV container of an actually live fit; original DSP protocol in PREDECLARED_PROTOCOL.json. Not a completed search or adopted sound. Restore FIXED_INPUT_ORIGINAL_PATH_SHA256.json members to original_study_root from LIVE_STUDY_SCOPE.json; the padded source .wav maps exactly to the original .f32 filename. Original live study files are not removed by this snapshot.'],check=True)
receipt=json.loads((O/(args.label+'_PUBLICATION.json')).read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified'];(J/(args.label+'_FIXED_PUBLICATION.json')).write_text(json.dumps(dict(receipt=receipt,original_study_root=str(R),fixed_original_members=selected),indent=2)+'\n');print(json.dumps(dict(commit=receipt['commit'],fixed_original_members=len(selected),actual_original_study_not_modified=True,not_adopted=True)),flush=True)
