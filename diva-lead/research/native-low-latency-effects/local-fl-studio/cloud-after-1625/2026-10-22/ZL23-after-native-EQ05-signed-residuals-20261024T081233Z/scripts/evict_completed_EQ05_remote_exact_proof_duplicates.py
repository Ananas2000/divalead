"""Evict only byte-exact already-published EQ05 repeated proof copies."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
D=Path(__file__).resolve().parent
N=Path('/workspace/divalead-work/native-low-latency-effects')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='completed_EQ05_exact_duplicate_cleanup')
r=json.loads((N/'native-EQ76-current-native06-ZL23-cycle05-PUBLICATION.json').read_text())
P,R=h['P'],h['R'];pause=R/'auto-backup.pause'
owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='release only exact already-published rejectedEQ05 proof duplicates, retain every audio byte in Git'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert not h['git']('status','--porcelain')
  assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',r['commit'],'origin/main']).returncode==0
  name='TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';rel=r['public_path']+'/'+name
  blob=subprocess.check_output(['git','-C',str(P),'show',r['commit']+':'+rel])
  before={p:shutil.disk_usage(p).free for p in ['/workspace','/tmp']};paths=[]
  for p in [Path(r['study'])/name,P/rel]:
   if not p.exists():continue
   assert p.read_bytes()==blob
   if p.is_relative_to(P):h['git']('update-index','--skip-worktree','--',rel)
   p.unlink();paths.append(str(p))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),evicted_exact_duplicates=paths,bytes_each=len(blob),archive_SHA256=hashlib.sha256(blob).hexdigest(),all_audio_bytes_retained_in_public_Git=True,public_commit=r['commit'],public_path=rel,all_selected_WAVs_states_sources_metadata_preserved=True,restore_command='git -C /workspace/divalead show '+r['commit']+':'+rel+' > '+str(Path(r['study'])/name),free_bytes_before=before,free_bytes_after={p:shutil.disk_usage(p).free for p in before})
  (N/'NATIVE_EQ76_CYCLE05_EXACT_REMOTE_PROOF_DUPLICATE_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
  assert not h['git']('status','--porcelain');print(json.dumps(receipt))
finally:
 if pause.exists()and h['read'](pause).get('owner')==owner:pause.unlink()
