"""Evict only old published study proof copies; preserve Git and every kit."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='storage_helpers')
P=s['P'];R=s['R'];N=s['N'];PUBLIC=s['PUBLIC'];git=s['git'];read=s['read']
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='evict origin-verified completed old research proof worktree copies only'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
  s['fetch_main']()
  commit=git('rev-parse','HEAD');assert commit==git('rev-parse','origin/main');old=s['protected']();rows=[]
  for label in ['native-EQ76-with-ZL-after08','native-WS16-with-ZL-afterEQ76','native-EQ76-current-six-dynamic-ZL-cycle02','native-WS16-current-six-dynamic-ZL-cycle02','native-final-context02-current-main-revalidation','native-EQ76-current-six-dynamic-ZL-cycle03','native-WS16-current-six-dynamic-ZL-cycle03','native-final-context03-current-main-revalidation','actual-Diva-tone-current-ZL-source-study','actual-Diva-22-PWM-sync-native04-rejected-study01','native-WS19-controls-current-ZL-study01','actual-Diva-Drift-Plate-native04-study01','extra-static-filters-two-free-slots-after-ZL20-study01']:
   root=PUBLIC/label
   for p in sorted(root.iterdir()):
    if not p.is_file()or not(p.name.endswith('WAVs.tar.gz')or(p.name.startswith('prefix-')and p.suffix=='.wav')):continue
    rel=p.relative_to(P).as_posix();blob=subprocess.check_output(['git','-C',str(P),'show','origin/main:'+rel]);assert blob==p.read_bytes()
    row=dict(path=rel,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest(),remote_commit=commit,restore_command='git restore --ignore-skip-worktree-bits -- '+rel)
    git('update-index','--skip-worktree','--',rel);p.unlink();rows.append(row)
  assert not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+rel)==oid for rel,oid in old.items())
  journal=N/'OLD_COMPLETED_STUDY_WORKTREE_PROOF_EVICTION.json'
  previous=read(journal)if journal.exists()else None
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),policy='Only completed published research archives/prefix worktree copies; Git versions/history/complete kits/selected main WAVs all retained',freed_bytes=sum(r['bytes']for r in rows),files=rows,previous=previous,all_old_full_kit_tree_OIDs_preserved=True)
  (N/'OLD_COMPLETED_STUDY_WORKTREE_PROOF_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='files'}))
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
