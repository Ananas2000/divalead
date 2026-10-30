"""Evict only loose public blob cache proven in the freshly fetched main tree."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,time,zlib
from bounded_git_audio_backup import verify_and_offload
H=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='current_public_blob_cache_recovery');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=C/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023';private='41e9bf7d7adba68226614297644c9661181bff6d';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='release only current-remote-tree hash-verified public loose blob cache, not worktree/ref/private data'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Another publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','origin/main');assert git('rev-parse','HEAD')==commit;refs=git('show-ref');subprocess.run(['git','--no-lazy-fetch','-C',str(P),'cat-file','-e',private],check=True);mapping={}
  for line in git('ls-tree','-r',commit,'--',PUBLIC.relative_to(P).as_posix()).splitlines():
   meta,path=line.split('\t',1);mode,kind,oid=meta.split()
   if kind=='blob':mapping.setdefault(oid,[]).append(path)
  parts=[];compressed=0;before=shutil.disk_usage('/workspace').free
  for oid,paths in mapping.items():
   if oid==private:continue
   path=P/'.git/objects'/oid[:2]/oid[2:]
   if not path.is_file()or path.stat().st_size<512*1024:continue
   data=zlib.decompress(path.read_bytes());assert hashlib.sha1(data).hexdigest()==oid;header,body=data.split(b'\0',1);assert header==b'blob '+str(len(body)).encode();parts.append(dict(path=paths[0],OID=oid,SHA256=hashlib.sha256(body).hexdigest(),bytes=len(body)));compressed+=path.stat().st_size
  if parts:verify_and_offload(P,git,commit,parts,H/'current-public-cache-structural-20261030T0945')
  assert git('show-ref')==refs and git('rev-parse','HEAD')==commit and not git('status','--porcelain');subprocess.run(['git','--no-lazy-fetch','-C',str(P),'cat-file','-e',private],check=True)
  result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_main_commit=commit,public_loose_blobs_released=len(parts),compressed_bytes_released=compressed,root_free_before=before,root_free_after=shutil.disk_usage('/workspace').free,all_refs_index_worktree_and_private_original_source48_preserved=True,current36_and_all_old_remote_versions_retained=True,verified_public_blob_rows=parts);(H/'CURRENT_VERIFIED_PUBLIC_BLOB_CACHE_RELEASE_AFTER38_20261030.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='verified_public_blob_rows'}),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
