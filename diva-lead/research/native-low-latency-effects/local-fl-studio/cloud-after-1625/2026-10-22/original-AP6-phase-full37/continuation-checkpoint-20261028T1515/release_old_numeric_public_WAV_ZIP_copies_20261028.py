"""Offload exact recoverable older numeric audio/ZIP cache copies only."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='old_numeric_audio_cache_release');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='offload older363/367/369/371 local WAV/ZIP copies only; all remote versions and newest372/full37 retained'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Another publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','origin/main');assert git('rev-parse','HEAD')==commit;protected=h['protected']();opened=set()
  for p in Path('/proc').glob('[0-9]*/fd/*'):
   try:opened.add(p.resolve())
   except(OSError,RuntimeError):pass
  removed=[];before=shutil.disk_usage('/workspace').free
  for k in[363,367,369,371]:
   root=PUBLIC/f'stereo-cascade87-cohort-{k:04}'
   for p in root.rglob('*'):
    if not p.is_file()or p.suffix not in ['.wav','.zip']:continue
    assert p.resolve()not in opened;rel=p.relative_to(P).as_posix();b=p.read_bytes();oid=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert git('rev-parse',commit+':'+rel)==oid;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+rel)==b;removed.append(dict(path=rel,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest(),OID=oid,HTTP_byte_exact=True,restore_command='git restore --ignore-skip-worktree-bits -- '+rel));git('update-index','--skip-worktree','--',rel);p.unlink()
  assert not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert(PUBLIC/'ZL-WIP37/Diva_ZL37_STEREO_WIP_complete.zip').exists();assert(PUBLIC/'stereo-cascade87-cohort-0372/cohort-0372_complete_FL20_STEREO_WIP.zip').exists();proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_commit=commit,released_bytes=sum(x['bytes']for x in removed),root_free_before=before,root_free_after=shutil.disk_usage('/workspace').free,all_remote_versions_objects_states_projects_and_newest372_full37_preserved=True,removed=removed);(H/'OLD_NUMERIC_PUBLIC_AUDIO_CACHE_RELEASE_20261028.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='removed'}),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
