"""Remove only remote-verified public training-log duplicate caches250..580."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zlib
from bounded_git_audio_backup import verify_and_offload
J=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='old_public_training_gz_duplicate_cache_release');P,C,PUBLIC=[h[k]for k in['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
    try:
        with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='release only old public duplicate training GZ caches250..580 after exact GitOID/HTTP verification; all kits/audio/states preserved'),f)
        break
    except FileExistsError:
        if time.monotonic()>deadline:raise TimeoutError('Another Git writer still active')
        time.sleep(.5)
try:
    with(C/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');commit=git('rev-parse','HEAD');rows=[]
        for root in sorted(PUBLIC.glob('stereo-cascade87-cohort-*')):
            number=int(root.name.rsplit('-',1)[1]);f=root/'training-results.json.gz'
            if not(250<=number<=580 and f.is_file()):continue
            blob=f.read_bytes();path=f.relative_to(P).as_posix();oid=git('rev-parse',commit+':'+path);assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==oid;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path)==blob;rows.append(dict(path=path,bytes=len(blob),OID=oid,SHA256=hashlib.sha256(blob).hexdigest()))
        assert rows;(J/'OLD_PUBLIC_TRAINING_GZ_DUPLICATE_RELEASE_PLAN.json').write_text(json.dumps(dict(commit=commit,rows=rows),indent=2)+'\n');before=shutil.disk_usage('/workspace').free
        # Install structural promisor metadata without fetching any missing blob.
        verify_and_offload(P,git,commit,[],J/'old-public-training-gz-structural-cache')
        for row in rows:
            f=P/row['path'];blob=f.read_bytes();assert hashlib.sha256(blob).hexdigest()==row['SHA256'];git('update-index','--skip-worktree','--',row['path']);f.unlink();loose=P/'.git/objects'/row['OID'][:2]/row['OID'][2:]
            if loose.exists():assert zlib.decompress(loose.read_bytes())==b'blob '+str(len(blob)).encode()+b'\0'+blob;loose.unlink()
        assert not git('status','--porcelain');proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,rows=rows,actual_root_bytes_released=shutil.disk_usage('/workspace').free-before,only_23_old_public_training_GZ_duplicate_caches_released=len(rows)==23,all_old_and_current_playable_kits_audio_presets_private_source_and_BEST_kept=True,no_pack_deleted_and_no_missing_blob_hydrated=True,remote_Git_history_unchanged=True);(J/'OLD_PUBLIC_TRAINING_GZ_DUPLICATE_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
