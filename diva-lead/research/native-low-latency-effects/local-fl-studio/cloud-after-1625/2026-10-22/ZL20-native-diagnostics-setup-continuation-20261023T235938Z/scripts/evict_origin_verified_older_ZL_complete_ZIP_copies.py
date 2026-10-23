"""Only local duplicate ZIP copies before ZL20; full GitHub kits stay intact."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='old_ZIP_space_helpers');P=s['P'];R=s['R'];N=s['N'];PUBLIC=s['PUBLIC'];git=s['git'];read=s['read']
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='evict only byte-exact origin-backed old complete ZIP worktree duplicates; preserve all GitHub versions'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');s['fetch_main']();head=git('rev-parse','HEAD');assert head==git('rev-parse','origin/main');old=s['protected']();rows=[]
  for number in range(1,20):
   code=f'{number:02}';p=PUBLIC/f'ZL-WIP{code}/Diva_ZL_{code}_WIP_complete_WIP.zip'
   if not p.is_file():continue
   rel=p.relative_to(P).as_posix();blob=subprocess.check_output(['git','-C',str(P),'show','origin/main:'+rel]);assert blob==p.read_bytes();rows.append(dict(path=rel,SHA256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),remote_commit=head,restore_command='git restore --ignore-skip-worktree-bits -- '+rel));git('update-index','--skip-worktree','--',rel);p.unlink()
  assert not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+rel)==oid for rel,oid in old.items())
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),freed_bytes=sum(r['bytes']for r in rows),files=rows,all_GitHub_complete_kits_and_Git_objects_and_history_preserved=True,locally_protected_complete_ZIPs='ZL20 and every newer kit; native base registry preserved')
  journal=N/'OLDER_ZL_LOCAL_ZIP_COPIES_EVICTION.json'
  if journal.exists():receipt['previous']=read(journal)
  (N/'OLDER_ZL_LOCAL_ZIP_COPIES_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='files'}))
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
