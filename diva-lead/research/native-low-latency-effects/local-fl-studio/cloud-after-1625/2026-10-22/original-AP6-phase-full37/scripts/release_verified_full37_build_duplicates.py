"""Release generated kit duplicates only after the public37 byte checks passed."""
from pathlib import Path
import datetime,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=Path('/workspace/divalead');public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP37';proof=json.loads((H/'ZL37_FULL_PUBLICATION.json').read_text());assert all(x['HTTP_byte_exact']for x in proof['HTTP_checks']);b=json.loads((H/'ZL37_BUILD_COMPLETION.json').read_text());root=Path(b['root']);archive=Path(b['ZIP']);restore=root.parent/'independent-ZIP-restore'/root.name;rows=[]
for p in root.rglob('*'):
 if p.is_file():
  target=public/p.relative_to(root);assert target.is_file()and target.read_bytes()==p.read_bytes();rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),public=target.relative_to(P).as_posix()))
assert archive.read_bytes()==(public/archive.name).read_bytes();assert hashlib.sha256(archive.read_bytes()).hexdigest()==b['ZIP_SHA256'];initial=(restore/'SHA256SUMS.txt').read_text();(H/'FULL37_INITIAL_ZIP_RESTORE_SHA256SUMS.txt').write_text(initial)
for line in initial.splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((restore/name).read_bytes()).hexdigest()==digest
for p in restore.rglob('*'):
 if p.is_file()and p.name!='SHA256SUMS.txt':assert p.read_bytes()==(public/p.relative_to(restore)).read_bytes()
before=shutil.disk_usage('/workspace').free;count=sum(p.stat().st_size for r in [root,restore]for p in r.rglob('*')if p.is_file())+archive.stat().st_size;shutil.rmtree(root);shutil.rmtree(restore.parent);archive.unlink();result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),public_commit=proof['commit'],all_full37_public_audio_states_projects_and_completeZIP_preserved=True,only_three_generated_verified_duplicate_locations_removed=True,logical_bytes=count,root_free_before=before,root_free_after=shutil.disk_usage('/workspace').free,original_initial_restore_manifest_preserved_separately=True,all_private_root_copy_rows=rows);(H/'VERIFIED_FULL37_BUILD_DUPLICATE_RELEASE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='all_private_root_copy_rows'}),flush=True)
