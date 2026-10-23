"""Drop only local duplicates of the three already HTTP-verified proof parts."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='proof_part_space_helpers');P=s['P'];N=s['N'];R=s['R'];PUBLIC=s['PUBLIC'];git=s['git'];read=s['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='evict only published proof-part duplicate worktree copies; original private full archive and Git/HTTP parts retained'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');s['fetch_main']();head=git('rev-parse','HEAD');assert head==git('rev-parse','origin/main');old=s['protected']();dest=PUBLIC/'actual-Diva-OscMix6p5-fixed-independent48-confirmation';manifest=read(dest/'FORTYEIGHT_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz.SPLIT_ARCHIVE_MANIFEST.json');rows=[]
  original=D/'ZL-Diva-source-OscMix6p5-independent48-adoption-01/FORTYEIGHT_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
  with original.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==manifest['original_SHA256']
  for item in manifest['parts']:
   p=dest/item['name'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['SHA256'];rel=p.relative_to(P).as_posix();blob=subprocess.check_output(['git','-C',str(P),'show','origin/main:'+rel]);assert hashlib.sha256(blob).hexdigest()==item['SHA256'];git('update-index','--skip-worktree','--',rel);p.unlink();rows.append(dict(path=rel,bytes=item['bytes'],SHA256=item['SHA256'],remote_commit=head,restore_command='git restore --ignore-skip-worktree-bits -- '+rel))
  assert not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items());receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),freed_bytes=sum(r['bytes']for r in rows),parts=rows,original_private_full_archive=str(original),all96_WAV_bytes_still_in_remote_Git_and_private_full_archive=True,all_versions_Git_history_complete_kits_and_objects_preserved=True);(N/'SOURCE48_PROOF_PART_WORKTREE_DUPLICATE_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='parts'}))
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
