from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy
from bounded_git_audio_backup import verify_and_offload
J=Path(__file__).resolve().parent;O=J.parent/'stereo-refinement-20261025';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='resume_positive_part02_after_environment_reconnect');P,C,PUBLIC=[h[k]for k in ['P','R','PUBLIC']];pause=C/'auto-backup.pause';git=h['git']
old=json.loads((pause if pause.exists()else J/'STALE_GIT_PAUSE_AFTER_ENVIRONMENT_RECONNECT.json').read_text());assert old['owner']=='authorized-local-backed-copy-cleanup-20261023';stat=Path('/proc')/str(old['PID'])/'stat';assert not stat.exists()or stat.read_text().split()[2]=='Z';(J/'STALE_GIT_PAUSE_AFTER_ENVIRONMENT_RECONNECT.json').write_text(json.dumps(old,indent=2)+'\n');
if pause.exists():pause.unlink()
label='original-native12-POST-RightAP12800-Q25-current620-NEW12-passed-20261107-part02of06';dest=PUBLIC/label;manifest=json.loads(next(dest.glob('*.ARCHIVE_MANIFEST.json')).read_text());members=json.loads((dest/'ARCHIVE_MEMBER_SHA256.json').read_text());part=Path('/tmp/original-native12-POST-RightAP12800-Q25-current620-NEW12-passed-20261107-immutable-split-inputs/part-02')
for row in members:assert hashlib.sha256((part/row['name']).read_bytes()).hexdigest()==row['SHA256']
with pause.open('x')as f:json.dump(dict(owner=old['owner'],PID=os.getpid(),reason='finish already pushed exact part02 verification and bounded offload after environment reconnect'),f)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','HEAD');assert commit==git('rev-parse','origin/main')=='813ef98fc012dc5f181d87bfa5002ac3fd200532'
  for row in manifest['parts']:
   blob=h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+row['path']);assert len(blob)==row['bytes']and hashlib.sha256(blob).hexdigest()==row['SHA256']
  verify_and_offload(P,git,commit,manifest['parts'],O/(label+'-resumed-public-structural-cache'))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),all_retained_study_files_and_WAVs_remote_Git_verified=True,local_audio_retained=True,resumed_after_environment_reconnect=True,not_adopted=True,reference_match_reached=False);(O/(label+'_PUBLICATION.json')).write_text(json.dumps(receipt,indent=2)+'\n')
  archive=Path('/tmp')/(label+'_ALL_RETAINED_STUDY_FILES.tar.gz');assert archive.exists();archive.unlink();print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
