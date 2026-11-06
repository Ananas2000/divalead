"""Keep all current media files; offload only their exact remote-verified loose Git duplicates."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil
from bounded_git_audio_backup import verify_and_offload
V=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='offload_current40_known_loose_audio_only');P,C,PUBLIC=[h[k]for k in ['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='keep all current working WAV files; release exact remote-backed duplicate loose Git objects only'),f)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');commit=git('rev-parse','HEAD');before=shutil.disk_usage('/workspace').free;rows=[]
  for p in(PUBLIC/'ZL-WIP40').rglob('*.wav'):
   if p.name.startswith('Diva_'):continue
   blob=p.read_bytes();rel=p.relative_to(P).as_posix();oid=git('rev-parse','HEAD:'+rel)
   if not(P/'.git/objects'/oid[:2]/oid[2:]).is_file():continue
   assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==oid;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+rel)==blob;rows.append(dict(path=rel,OID=oid,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest(),HTTP_byte_exact=True))
  verify_and_offload(P,git,commit,rows,V/'current40-known-loose-audio-structural-cache');assert not git('status','--porcelain');assert all((P/r['path']).is_file()and hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['SHA256']for r in rows);proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,rows=rows,actual_freed_bytes=shutil.disk_usage('/workspace').free-before,all_current_WAV_files_kept=True,no_original_source_or_unknown_private_pack_touched=True);(V/'CURRENT40_KNOWN_LOOSE_AUDIO_OFFLOAD.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
