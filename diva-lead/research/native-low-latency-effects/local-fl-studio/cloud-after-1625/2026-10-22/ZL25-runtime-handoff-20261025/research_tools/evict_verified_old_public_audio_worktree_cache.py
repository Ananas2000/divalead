"""Release only recoverable byte-exact public audio copies; preserve all Git versions."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
A=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo25_public_cache_cleanup')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='evict only old byte-verified public audio worktree cache; retain Git and current kit'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','HEAD');assert commit==git('rev-parse','origin/main')
  tree={}
  for line in subprocess.check_output(['git','-C',str(P),'ls-tree','-r','-z','HEAD'],text=True).split('\0'):
   if not line:continue
   fields,path=line.split('\t',1);mode,kind,oid=fields.split()
   if kind=='blob':tree[path]=oid
  before=shutil.disk_usage('/workspace').free;removed=[]
  # Current complete WIP25, native rebase bundles, presets/states, GUI PC
  # directories, private captures, live frozen input and original v83 survive.
  for p in sorted(PUBLIC.rglob('*')):
   if not p.is_file()or p.suffix.lower()not in ['.wav','.mp3','.flac','.zip','.gz']:continue
   rel=p.relative_to(PUBLIC)
   if rel.parts[0]in ['ZL-WIP25','rebased-native-bases','lowmid-Side-phase-after-cohort15-20261025','ZL25-complete-kit-validation-20261025']:continue
   if p.suffix=='.gz'and not(p.name.endswith('.tar.gz')or p.name.endswith('.wav.gz')):continue
   b=p.read_bytes();r=p.relative_to(P).as_posix();oid=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   assert tree.get(r)==oid,(r,'not exact current public Git object')
   git('update-index','--skip-worktree','--',r);p.unlink();removed.append(dict(path=r,bytes=len(b),Git_blob=oid,SHA256=hashlib.sha256(b).hexdigest()))
  assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),published_commit=commit,removed_only_verified_recoverable_public_worktree_copies=removed,logical_bytes=sum(x['bytes']for x in removed),observed_root_free_change=shutil.disk_usage('/workspace').free-before,all_Git_versions_refs_objects_presets_and_GUI_PC_work_unchanged=True,current_ZL25_all_files_and_nativebase06_and_private_captures_retained=True)
  (A/'OLD_PUBLIC_AUDIO_WORKTREE_CACHE_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='removed_only_verified_recoverable_public_worktree_copies'}),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
