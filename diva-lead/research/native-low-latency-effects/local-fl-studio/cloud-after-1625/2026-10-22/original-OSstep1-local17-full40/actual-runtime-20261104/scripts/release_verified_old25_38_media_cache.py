"""Release remote byte-verified old25..38 generated media caches; keep all kits in Git."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
from bounded_git_audio_backup import verify_and_offload
V=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='nov4_old_fullkit_media_cache');P,C,PUBLIC=[h[k]for k in['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='release only closed old25..38 generated media caches after remote exact verification; active39/565/559/557/source/private files kept'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Another publisher owns Git lock')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');commit=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);before=shutil.disk_usage('/workspace').free;inventory=[]
  for n in range(25,39):
   for p in(PUBLIC/f'ZL-WIP{n}').rglob('*'):
    if p.is_file()and p.suffix in['.wav','.zip','.flac','.mp3']and p.name not in ['Diva_original_lead_reference.wav','Diva_SOURCE_FROZEN_48k.wav']:inventory.append(p)
  plan=[];total=0
  for p in sorted(inventory,key=lambda p:(p.stat().st_size,str(p)),reverse=True):
   if total>=80*2**20:break
   total+=p.stat().st_size;plan.append(p)
  rows=[]
  for p in plan:
   data=p.read_bytes();rel=p.relative_to(P).as_posix();oid=git('rev-parse','HEAD:'+rel);assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+rel)==data;rows.append(dict(path=rel,OID=oid,SHA256=hashlib.sha256(data).hexdigest(),bytes=len(data),HTTP_byte_exact=True));(V/'OLD25_38_MEDIA_CACHE_RELEASE_PLAN.json').write_text(json.dumps(dict(commit=commit,rows=rows,all_current40_576_565_559_557_and_original_reference_and_private_files_kept=True),indent=2)+'\n');git('update-index','--skip-worktree','--',rel);p.unlink()
  verify_and_offload(P,git,commit,rows,V/'old25-38-media-structural-cache');assert not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;after=shutil.disk_usage('/workspace').free;proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,rows=rows,before_free_bytes=before,after_free_bytes=after,actual_released_bytes=after-before,only_verified_old_generated_media_cache_released=True,all_original_old_Git_trees_and_PC_GUI_preserved=True,current40_576_565_559_557_native_state_source_and_private_uploads_kept=True,no_unknown_or_private_packs_deleted=True);(V/'OLD25_38_MEDIA_CACHE_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}))
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
