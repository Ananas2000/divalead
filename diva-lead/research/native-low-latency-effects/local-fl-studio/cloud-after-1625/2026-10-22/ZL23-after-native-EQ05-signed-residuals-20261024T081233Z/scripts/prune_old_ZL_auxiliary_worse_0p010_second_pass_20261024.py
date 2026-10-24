"""Keep every old candidate preset/main WAV; drop only stale repeated checks.

Protect current/recent, every tenth cohort and all published-kit source cohorts.
Only candidates worse by>0.010 on the same fixed criterion qualify. This is
explicit pruning of auxiliary stochastic repeats, not a claim they are in Git.
"""
from pathlib import Path
import datetime,gzip,hashlib,io,json,os,tarfile
import numpy as np
import soundfile as sf
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');ROOT=D/'ZL-continuous65';N=Path('/workspace/divalead-work/native-low-latency-effects');PUBLIC=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');best=json.loads((ROOT/'BEST_CANDIDATE.json').read_text());latest=max(int(p.name.split('-')[1])for p in ROOT.glob('cohort-[0-9][0-9][0-9][0-9]'));protected={1};protected_paths={str(Path(best['native_ZL_component_state']).parent)}
for p in PUBLIC.glob('ZL*-validated-continuation/canonical-export-input/candidate-research-only.json'):
 row=json.loads(p.read_text());value=row.get('source_accepted_cohort')
 if isinstance(value,int):protected.add(value)
open_paths=set()
for proc in Path('/proc').glob('[0-9]*'):
 try:
  for fd in(proc/'fd').iterdir():
   try:open_paths.add(os.readlink(fd))
   except OSError:pass
 except(OSError,PermissionError):pass
decisions=[];freed=0
for folder in sorted(ROOT.glob('cohort-[0-9][0-9][0-9][0-9]')):
 number=int(folder.name.split('-')[1]);archive=folder/'independent6-control-candidate-WAVs.tar.gz';completion=folder/'completion.json';selected=folder/'SELECTED_CANDIDATE_WIP.wav'
 if number in protected or number%10==0 or number>latest-20 or str(folder)in protected_paths or str(archive)in open_paths:continue
 if not archive.is_file()or not completion.is_file()or not selected.is_file():continue
 row=json.loads(completion.read_text())
 if row.get('robust_improvement')is not True or row['candidate_mean']<=best['loss']+.010:continue
 members=row.get('archive_members',[])
 if len(members)!=12:continue
 main,sr=sf.read(selected,dtype='float32');assert sr==48000;matching=[]
 with tarfile.open(archive)as tar:
  for member in members:
   blob=tar.extractfile(member['name']).read();assert hashlib.sha256(blob).hexdigest()==member['SHA256']
   if member['name'].startswith('candidate-'):
    audio,rate=sf.read(io.BytesIO(blob),dtype='float32');assert rate==sr
    if np.array_equal(audio,main):matching.append(member['name'])
 assert matching,folder
 with archive.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 size=archive.stat().st_size;proof=dict(cohort=number,current_best_mean=best['loss'],old_candidate_mean=row['candidate_mean'],original_archive=str(archive),original_archive_SHA256=digest,original_bytes=size,main_selected_WAV=str(selected),main_file_SHA256=hashlib.sha256(selected.read_bytes()).hexdigest(),retained_main_matches_archive_members_decoded_float32_exact=matching,complete_original_validation=row,all_parameters_components_training_and_heldout_metadata_retained=True,removed_only_auxiliary_stochastic_control_and_unselected_candidate_repeats=True)
 marker=folder/'AUXILIARY_VALIDATION_PRUNING_PROOF.json.gz';assert not marker.exists();marker.write_bytes(gzip.compress(json.dumps(proof).encode(),mtime=0));archive.unlink();decisions.append(proof);freed+=size;print('PRUNED_OLD_CLEARLY_WORSE_AUX_ONLY',number,size,flush=True)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),policy='Every main candidate WAV/component/metadata retained; only>0.010worse old auxiliary repeated validation archives pruned. Current/recent20/published-source/every10th protected.',freed_bytes=freed,archives=len(decisions),protected_published_source_cohorts=sorted(protected),last20_cohorts_protected=True,all_GitHub_versions_and_Git_objects_untouched=True,auxiliary_stochastic_repeats_not_claimed_remotely_backed=True)
(N/'OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_SECOND_PASS_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_SECOND_PASS_DECISION_PROOFS.json.gz').write_bytes(gzip.compress(json.dumps(decisions).encode(),mtime=0));print('OLD_CLEARLY_WORSE_AUX_PRUNING_COMPLETE',json.dumps(receipt),flush=True)
