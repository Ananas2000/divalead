"""Evict only older, current-remote-byte-proved WAV/ZIP checkout duplicates."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shlex,shutil,time,urllib.parse
T=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='release_old_numeric_cache_after38');P,C,PUBLIC=[h[k]for k in ['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+600
assert json.loads((T/'ADOPTED_FULL38_RUNTIME_CHECK.json').read_text())['actual_new_runtime_two_cold_two_ZL_chain_errors']==[0.,0.]
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='release only old numeric local audio/ZIP copies; current38/predecessor413/full37/source/reference retained'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','origin/main');assert git('rev-parse','HEAD')==commit;protected=h['protected']();opened=set();before=shutil.disk_usage('/workspace').free;rows=[]
  for fd in Path('/proc').glob('[0-9]*/fd/*'):
   try:opened.add(fd.resolve())
   except(OSError,RuntimeError):pass
  roots=sorted((d for d in PUBLIC.glob('stereo-cascade87-cohort-*')if d.is_dir()and int(d.name.rsplit('-',1)[-1])<413),key=lambda d:int(d.name.rsplit('-',1)[-1]))
  for root in roots:
   for p in sorted(root.rglob('*')):
    if not p.is_file()or p.is_symlink()or p.suffix not in['.wav','.zip']:continue
    if any(word in p.name.lower()for word in['original','reference','diva_source']):continue
    assert p.resolve()not in opened;data=p.read_bytes();rel=p.relative_to(P).as_posix();oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert git('rev-parse',commit+':'+rel)==oid;url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+urllib.parse.quote(rel,safe='/');assert h['read_public_bytes'](url)==data;rows.append(dict(path=rel,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),Git_blob=oid,HTTP_byte_exact=True,restore_command='git restore --ignore-skip-worktree-bits -- '+shlex.quote(rel)));git('update-index','--skip-worktree','--',rel);p.unlink()
    if shutil.disk_usage('/workspace').free>=272*2**20:break
   if shutil.disk_usage('/workspace').free>=272*2**20:break
  assert not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert(PUBLIC/'ZL-WIP38/Diva_ZL38_STEREO_WIP_complete.zip').is_file();assert(PUBLIC/'ZL-WIP37/Diva_ZL37_STEREO_WIP_complete.zip').is_file();assert(PUBLIC/'stereo-cascade87-cohort-0413/cohort-0413_complete_FL20_STEREO_WIP.zip').is_file()
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_main_commit=commit,only_exact_recoverable_older_numeric_checkout_cache_released=True,current38_predecessor413_full37_and_all_states_sources_references_retained=True,all_remote_versions_and_Git_refs_preserved=True,logical_bytes_released=sum(r['bytes']for r in rows),root_free_before=before,root_free_after=shutil.disk_usage('/workspace').free,rows=rows);(T/'OLDER_NUMERIC_PUBLIC_CACHE_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
