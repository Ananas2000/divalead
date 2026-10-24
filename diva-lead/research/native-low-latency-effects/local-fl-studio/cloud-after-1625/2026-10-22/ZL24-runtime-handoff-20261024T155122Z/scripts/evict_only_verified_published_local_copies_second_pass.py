"""Offload redundant kit/restoration copies after complete Git/HTTP verification."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
A=Path(__file__).resolve().parent;P=Path('/workspace/divalead');public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22';kit=public/'ZL-WIP24';receipt=json.loads((A/'ZL24_FULL_PUBLICATION.json').read_text());commit=receipt['commit']
assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',commit,'origin/main']).returncode==0
assert receipt['HTTP_checks'][0]['HTTP_byte_exact'];before=shutil.disk_usage('/workspace').free;removed=[]
root=A/'FL20_ZL24_STEREO_WIP'
if root.exists():
 for p in root.rglob('*'):
  if p.is_file():assert p.read_bytes()==(kit/p.relative_to(root)).read_bytes()
 removed.append(dict(path=str(root),every_file_byte_exact_to_published_current_kit=True));shutil.rmtree(root)
archive=A/'Diva_ZL24_STEREO_WIP_complete.zip'
if archive.exists():
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['complete_ZIP_SHA256'];removed.append(dict(path=str(archive),SHA256=receipt['complete_ZIP_SHA256'],remote_commit=commit,remote_path=str((kit/archive.name).relative_to(P))));archive.unlink()
manifest=(public/'SHA256SUMS.txt').read_bytes();assert manifest==subprocess.check_output(['git','-C',str(P),'show','HEAD:'+str((public/'SHA256SUMS.txt').relative_to(P))]);known={line.split('  ',1)[0]for line in manifest.decode().splitlines()}
inner_manifest=Path('/tmp/divalead-PC-20261024-analysis/Diva_ZL23_LOCAL_COMPLETE.zip.manifest.json')
if inner_manifest.exists():known.update(r['sha256']for r in json.loads(inner_manifest.read_text()))
old=A/'ZL24-independent-ZIP-restore';skipped=[]
if old.exists():
 valid=True
 for p in old.rglob('*'):
  if not p.is_file():continue
  b=p.read_bytes();digest=hashlib.sha256(b).hexdigest()
  if digest in known:continue
  if p.name=='SHA256SUMS.txt':
   for line in b.decode().splitlines():
    sha,name=line.split('  ',1);q=p.parent/name
    if not q.is_file()or hashlib.sha256(q.read_bytes()).hexdigest()!=sha:valid=False
   continue
  if p.suffix=='.md'and any(q.read_bytes().startswith(b)for q in kit.glob('*.md')):continue
  valid=False;skipped.append(str(p))
 if valid:removed.append(dict(path=str(old),every_member_in_published_SHA_manifest_or_reproducible_validated_manifest_or_retained_document_prefix=True));shutil.rmtree(old)
source=A/'local-fl-matching/sessions/2026-10-24/ZL23_upstream/FL20_ZL_23_WIP';oldmanifest=Path('/tmp/divalead-PC-20261024-analysis/Diva_ZL23_LOCAL_COMPLETE.zip.manifest.json')
if source.exists()and oldmanifest.exists():
 expected={r['path']:r['sha256']for r in json.loads(oldmanifest.read_text())}
 for p in source.rglob('*'):
  if p.is_file():assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['local-fl-matching/'+str(p.relative_to(A/'local-fl-matching'))]
 removed.append(dict(path=str(source),byte_exact_original_public_ZL23_ZIP_members=True,restore_from='local-fl-studio/2026-10-24/Diva_ZL23_LOCAL_COMPLETE.zip, SHA3a03978ea429dbf93f4c4807dc3eb0c1f9fbf158cbec5b4b965859392ec3478d'));shutil.rmtree(source)
r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed_only_redundant_published_kit_copies=removed,skipped_unproved_members=skipped,root_freed=shutil.disk_usage('/workspace').free-before,current_public_ZL24_all_presets_WAV_components_retained=True,real_GUI_inputs_and_current_nativebase06_and_original_reference_untouched=True)
(A/'PUBLISHED_LOCAL_KIT_COPY_EVICTION_SECOND_PASS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
