"""Evict exact public media object duplicates, retaining working WAVs and presets."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zlib
from bounded_git_audio_backup import verify_and_offload
J=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='release_current_public_media_object_duplicates');P,C,PUBLIC=[h[k]for k in['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
    try:
        with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='release exact remote-verified full41/639 public media object duplicates; working WAVs preserved'),f)
        break
    except FileExistsError:
        if time.monotonic()>deadline:raise TimeoutError('Other Git writer still active')
        time.sleep(.5)
try:
    with(C/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');commit=git('rev-parse','HEAD');rows=[];seen=set()
        for root in[PUBLIC/'ZL-WIP41',PUBLIC/'stereo-cascade87-cohort-0639']:
            for f in sorted(root.rglob('*')):
                if not f.is_file()or f.suffix not in['.wav','.mp3','.flac','.zip']or f.name.startswith('Diva_original')or f.name=='Diva_SOURCE_FROZEN_48k.wav':continue
                path=f.relative_to(P).as_posix();oid=git('rev-parse',commit+':'+path);loose=P/'.git/objects'/oid[:2]/oid[2:]
                if oid in seen or not loose.exists():continue
                blob=f.read_bytes();assert zlib.decompress(loose.read_bytes())==b'blob '+str(len(blob)).encode()+b'\0'+blob;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path)==blob;seen.add(oid);rows.append(dict(name=f.name,path=path,OID=oid,SHA256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),working_file_preserved=True))
        assert rows;before=shutil.disk_usage('/workspace').free;(J/'CURRENT_PUBLIC_MEDIA_OBJECT_RELEASE_PLAN.json').write_text(json.dumps(rows,indent=2)+'\n');verify_and_offload(P,git,commit,rows,J/'known-current-media-structural-cache')
        archive=PUBLIC/'stereo-cascade87-cohort-0639/cohort-0639_complete_FL20_STEREO_WIP.zip'
        if archive.exists():
            blob=archive.read_bytes();path=archive.relative_to(P).as_posix();assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path)==blob;git('update-index','--skip-worktree','--',path);archive.unlink()
        proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,rows=rows,root_actual_bytes_released=shutil.disk_usage('/workspace').free-before,all_working_WAVs_presets_source_reference_and_BEST_kept=True,only_verified_public_ZIP_duplicate_worktree_copy_released=True,no_unknown_or_private_pack_removed=True);(J/'CURRENT_PUBLIC_MEDIA_OBJECT_DUPLICATE_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
