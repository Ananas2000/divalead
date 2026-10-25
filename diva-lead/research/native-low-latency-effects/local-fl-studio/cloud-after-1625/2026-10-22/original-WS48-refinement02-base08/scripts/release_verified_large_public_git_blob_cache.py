"""Recover public fetch-on-demand blob cache only; keep worktree/allrefs/private."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,zlib
from bounded_git_audio_backup import verify_and_offload
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='authorized_public_blob_cache_recovery');P,N,R=[h[k]for k in ['P','N','R']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023';private='41e9bf7d7adba68226614297644c9661181bff6d'
assert git('config','--get','remote.origin.promisor')=='true'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='release hashverified large public cachedblobsonly, never files/ref/private data'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','HEAD');assert commit==git('rev-parse','origin/main');refs=git('show-ref');subprocess.run(['git','--no-lazy-fetch','-C',str(P),'cat-file','-e',private],check=True)
  rows=read(H/'PUBLIC_LARGE_LOOSE_CACHE_CANDIDATES.json');parts=[];before=shutil.disk_usage('/workspace').free;compressed=0
  for row in rows:
   oid=row['OID'];assert oid!=private;p=P/'.git/objects'/oid[:2]/oid[2:]
   if not p.exists():continue
   raw=zlib.decompress(p.read_bytes());assert hashlib.sha1(raw).hexdigest()==oid;head,body=raw.split(b'\0',1);assert head==b'blob '+str(len(body)).encode();path=row['paths'][0];assert git('rev-parse',commit+':'+path)==oid
   parts.append(dict(path=path,OID=oid,SHA256=hashlib.sha256(body).hexdigest(),bytes=len(body)));compressed+=p.stat().st_size
  verify_and_offload(P,git,commit,parts,H/'large-public-loose-cache-structural-promisor-02')
  assert git('show-ref')==refs and git('rev-parse','HEAD')==commit and not git('status','--porcelain');subprocess.run(['git','--no-lazy-fetch','-C',str(P),'cat-file','-e',private],check=True)
  result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),current_remote_main_commit=commit,public_loose_cache_blobs_released=len(parts),compressed_bytes=compressed,root_free_before=before,root_free_after=shutil.disk_usage('/workspace').free,all_worktree_files_and_refs_unchanged=True,private_original_source48_blob_still_available_without_network=True,all_old_kits_and_PC_GUI_retained=True,standard_promisor_fetch_on_demand=True,verified_public_blobs=parts)
  (H/'VERIFIED_PUBLIC_LOOSE_CACHE_RECOVERY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='verified_public_blobs'}),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
