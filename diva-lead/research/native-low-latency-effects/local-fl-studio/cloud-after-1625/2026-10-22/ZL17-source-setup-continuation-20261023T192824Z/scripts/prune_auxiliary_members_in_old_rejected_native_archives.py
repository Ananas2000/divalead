"""Old rejected-cohort archives: keep every main/training/recorded WAV.

Only auxiliary prefix/fresh-check WAVs may be dropped after the original
archive/member hashes and the explicit robust=False decision are checked.
No Git objects, releases, presets, metadata or accepted trials are removed.
"""
from pathlib import Path
import datetime,gzip,hashlib,io,json,os,re,tarfile
N=Path('/workspace/divalead-work/native-low-latency-effects');storage=Path('/workspace/divalead-work/offline-storage/archived-rejected-native-cohort-WAVs');rows=[];decisions=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
open_paths=set()
for proc in Path('/proc').glob('[0-9]*'):
 try:
  for fd in(proc/'fd').iterdir():
   try:open_paths.add(os.readlink(fd))
   except OSError:pass
 except (OSError,PermissionError):pass
for receipt_path in sorted(storage.glob('*.receipt.json')):
 original=json.loads(receipt_path.read_text());root=Path(original['root']);archive=Path(original['archive']);validation=root/'full-validated-candidate.json';completion=root/'completion.json'
 if not validation.is_file()or not completion.is_file()or str(archive.resolve())in open_paths:continue
 choice=json.loads(validation.read_text())
 if choice.get('robust_improvement')is not False:continue
 recorded=Path(choice.get('recorded_audio','')).name
 protected={'best-with-tail.wav','best-training-with-tail.wav',recorded}
 remove=[r for r in original['items']if r['member']not in protected and re.fullmatch(r'(actual-WS-Chorus-prefix|full-fresh-realization)-[0-9]+\.wav',r['member'])]
 if not remove:continue
 retained=[r for r in original['items']if r not in remove];assert retained and any(r['member']in protected for r in retained)
 assert sha(archive)==original['archive_SHA256'];before=archive.stat().st_size;temp=archive.with_suffix(archive.suffix+'.aux-prune-partial');assert not temp.exists()
 with tarfile.open(archive)as src:
  assert{m.name for m in src.getmembers()}=={r['member']for r in original['items']}
  for r in original['items']:assert hashlib.sha256(src.extractfile(r['member']).read()).hexdigest()==r['SHA256']
  with tarfile.open(temp,'w:gz',compresslevel=3)as dst:
   by_hash={}
   for r in retained:
    info=tarfile.TarInfo(r['member']);info.size=r['bytes']
    if r['SHA256']in by_hash:
     info.type=tarfile.LNKTYPE;info.linkname=by_hash[r['SHA256']];info.size=0;dst.addfile(info)
    else:dst.addfile(info,io.BytesIO(src.extractfile(r['member']).read()));by_hash[r['SHA256']]=r['member']
 with tarfile.open(temp)as dst:
  for r in retained:assert hashlib.sha256(dst.extractfile(r['member']).read()).hexdigest()==r['SHA256']
 assert temp.stat().st_size<before
 # Save the original decision and complete SHA manifest before replacing the
 # generated archive. Every protected member remains byte-for-byte identical.
 evidence=dict(root=str(root),original_receipt=original,validation=choice,completion=json.loads(completion.read_text()),removed=remove,retained=retained)
 proof=root/'ARCHIVE_AUXILIARY_PRUNING_PROOF.json.gz';blob=gzip.compress(json.dumps(evidence).encode(),mtime=0);assert not proof.exists();proof.write_bytes(blob);decisions.append(evidence)
 temp.replace(archive);new=dict(original,archive_SHA256=sha(archive),items=retained,auxiliary_prefix_and_unselected_fresh_checks_pruned=True,original_decision_and_hashes=str(proof),all_main_training_recorded_WAV_members_bit_exact=True,only_explicit_robust_false_cohort=True);receipt_path.write_text(json.dumps(new,indent=2)+'\n');rows.append(dict(root=str(root),archive=str(archive),before_bytes=before,after_bytes=archive.stat().st_size,removed_members=[r['member']for r in remove],retained_members=[r['member']for r in retained],new_archive_SHA256=new['archive_SHA256']));print('PRUNED_REJECTED_ARCHIVE_AUX_ONLY',root.name,before-archive.stat().st_size,flush=True)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),policy='Only already rejected robust=False auxiliary captures; retain every main, training, recorded WAV and all metadata/states/Git versions',archives=len(rows),freed_bytes=sum(r['before_bytes']-r['after_bytes']for r in rows),rows=rows)
(N/'OLD_REJECTED_ARCHIVE_AUX_PRUNING_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');(N/'OLD_REJECTED_ARCHIVE_AUX_PRUNING_DECISION_PROOFS.json.gz').write_bytes(gzip.compress(json.dumps(decisions).encode(),mtime=0));print('OLD_REJECTED_ARCHIVE_PRUNING_COMPLETE',json.dumps({k:v for k,v in report.items()if k!='rows'}),flush=True)
