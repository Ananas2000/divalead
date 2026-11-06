from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
from bounded_git_audio_backup import verify_and_offload
U=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='release_verified_closed_duplicate_ZIP_cache');P,C,PUBLIC=[h[k]for k in['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='release only verified remote closed standalone ZIP duplicate cache, retain all active project/state/source files'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');commit=git('rev-parse','HEAD');before=shutil.disk_usage('/workspace').free;rows=[]
  for name in['ZL-WIP40/Diva_ZL40_STEREO_WIP_complete.zip','original-OSstep1-local17-full40/FL20_NATIVE_ZL_REBASED_12_verified_base.zip']:
   p=PUBLIC/name
   if not p.exists():continue
   blob=p.read_bytes();rel=p.relative_to(P).as_posix();oid=git('rev-parse','HEAD:'+rel);assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==oid;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+rel)==blob;rows.append(dict(path=rel,OID=oid,SHA256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),HTTP_byte_exact=True));(U/'CLOSED_ZIP_DUPLICATE_CACHE_RELEASE_PLAN.json').write_text(json.dumps(dict(commit=commit,rows=rows,all_actual_full40_project_FST_states_and_accepted565_and_native12_source_files_kept=True),indent=2)+'\n');git('update-index','--skip-worktree','--',rel);p.unlink()
  verify_and_offload(P,git,commit,rows,U/'closed-zip-known-structural-cache');assert not git('status','--porcelain');after=shutil.disk_usage('/workspace').free;proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,rows=rows,before_free_bytes=before,after_free_bytes=after,actual_released_bytes=after-before,only_standalone_closed_ZIP_worktree_and_known_loose_blob_cache=True,ordinary_remote_Git_ZIP_unchanged=True,full40_FLProject_states_source_and_accepted565_and_private_uploads_kept=True,no_unknown_or_private_packs_deleted=True);(U/'CLOSED_ZIP_DUPLICATE_CACHE_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}))
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
