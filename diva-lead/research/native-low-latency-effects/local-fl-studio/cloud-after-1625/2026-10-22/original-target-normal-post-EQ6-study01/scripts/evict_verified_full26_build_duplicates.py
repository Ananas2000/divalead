"""Remove only byte-verified redundant build/restore copies of published WIP26."""
from pathlib import Path
import hashlib,json,shutil,datetime
H=Path(__file__).resolve().parent;receipt=json.loads((H/'ZL26_FULL_PUBLICATION.json').read_text());P=Path('/workspace/divalead');pub=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP26';base=Path('/tmp/divalead-full26-20261025');before=shutil.disk_usage('/tmp').free;removed=[]
assert all(r['HTTP_byte_exact']for r in receipt['HTTP_checks'])
for root in [base/'FL20_ZL26_STEREO_WIP',base/'independent-ZIP-restore/FL20_ZL26_STEREO_WIP']:
 if not root.exists():continue
 for p in root.rglob('*'):
  if not p.is_file():continue
  if p.name=='SHA256SUMS.txt':
   for line in p.read_text().splitlines():
    digest,name=line.split('  ',1);assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
  else:assert p.read_bytes()==(pub/p.relative_to(root)).read_bytes(),p
 removed.append(dict(path=str(root),all_members_exact_to_published_current_kit_or_valid_reproducible_manifest=True));shutil.rmtree(root)
archive=base/'Diva_ZL26_STEREO_WIP_complete.zip'
if archive.exists():
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==receipt['complete_ZIP_SHA256'];assert archive.read_bytes()==(pub/archive.name).read_bytes();removed.append(dict(path=str(archive),SHA256=receipt['complete_ZIP_SHA256']));archive.unlink()
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed_only_recoverable_published_build_duplicates=removed,observed_tmp_bytes_freed=shutil.disk_usage('/tmp').free-before,current_public_full26_all_audio_presets_components_retained=True,all_source_native_GUI_and_private_actual_validation_WAVs_retained=True)
(H/'FULL26_VERIFIED_BUILD_DUPLICATE_EVICTION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
