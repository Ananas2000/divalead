"""Losslessly archive only old rejected native-cohort scratch WAVs, never releases."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,tarfile
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
rows=json.loads((N/'REJECTED_NATIVE_WAV_ARCHIVE_DRYRUN.json').read_text())['rows']
current=json.loads((N/'FL20-corrected/BEST_CANDIDATE.json').read_text());active=subprocess.check_output(['ps','-eo','args='],text=True)
archives=B/'archived-rejected-native-cohort-WAVs';archives.mkdir(exist_ok=True)
checks=[];before=os.statvfs('/tmp');free_before=before.f_bavail*before.f_frsize
for row in rows[18:]:
 root=Path(row['root']);assert root.parent==B and root.name.startswith('fl20-20261022T184644Z-')
 result=json.loads((root/'full-validated-candidate.json').read_text());assert not result['robust_improvement']and result['loss']>=1.573
 assert (root/'completion.json').exists()and str(root)not in active
 files=sorted(root.glob('*.wav'));assert files
 protected={current.get('recorded_audio'),*[v for k,v in current.get('source_manifest',{}).items()if isinstance(v,str)]}
 assert not any(str(p)in protected for p in files)
 items=[dict(path=str(p),member=p.name,bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest())for p in files]
 archive=archives/(root.name+'.tar.gz');assert not archive.exists()
 with tarfile.open(archive,'w:gz',compresslevel=6)as z:
  for p in files:z.add(p,arcname=p.name,recursive=False)
 with tarfile.open(archive,'r:gz')as z:
  assert len(z.getmembers())==len(items)
  for item in items:
   member=z.extractfile(item['member']);h=hashlib.sha256();size=0
   while True:
    block=member.read(1024*1024)
    if not block:break
    h.update(block);size+=len(block)
   assert size==item['bytes']and h.hexdigest()==item['SHA256']
 for item in items:
  p=Path(item['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==item['SHA256'];p.unlink()
 receipt=dict(root=str(root),archive=str(archive),archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),items=items,
    all_decompressed_file_SHA256_verified_before_unlink=True,all_JSON_models_logs_presets_retained=True)
 (archives/(root.name+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');checks.append(receipt)
 print('LOSSLESS_REJECTED_COHORT_ARCHIVED',root.name,len(items),flush=True)
after=os.statvfs('/tmp');proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),cohorts=checks,
 old_rejected_numeric_cohort_WAVs_only=True,all_source_and_current_candidates_and_public_kits_preserved=True,
 every_original_WAV_byte_recoverable=True,actual_free_bytes_before=free_before,actual_free_bytes_after=after.f_bavail*after.f_frsize)
(N/'REJECTED_NATIVE_WAV_LOSSLESS_ARCHIVING_BATCH2.json').write_text(json.dumps(proof,indent=2)+'\n')
print('REJECTED_WAV_LOSSLESS_ARCHIVING_COMPLETE',len(checks),'free_MiB',proof['actual_free_bytes_after']/2**20,'gain_MiB',(proof['actual_free_bytes_after']-free_before)/2**20,flush=True)
