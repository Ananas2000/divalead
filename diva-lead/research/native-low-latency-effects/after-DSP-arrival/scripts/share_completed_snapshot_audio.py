"""Share only byte-identical unlinked WAVs in completed historical snapshots."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,stat,subprocess
ROOT=Path('/workspace/divalead-work/all-repository-selection/validated-snapshots');N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
head=subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip();before=shutil.disk_usage('/workspace').free
files=[p for p in ROOT.rglob('*.wav') if p.is_file() and not p.is_symlink() and p.stat().st_nlink==1]
by_size={}
for path in files:by_size.setdefault(path.stat().st_size,[]).append(path)
known={};rows=[];hashed=0
for size,group in by_size.items():
 if len(group)<2:continue
 for path in sorted(group):
  old=path.stat();digest=hashlib.sha256(path.read_bytes()).hexdigest();hashed+=1;key=(size,digest,stat.S_IMODE(old.st_mode),old.st_uid,old.st_gid)
  if key not in known:known[key]=path;continue
  source=known[key];now=path.stat()
  if now.st_nlink!=1 or now.st_ino==source.stat().st_ino:continue
  assert (now.st_size,now.st_mtime_ns)==(old.st_size,old.st_mtime_ns)
  assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
  temp=path.with_name(path.name+'.exact-sharing-'+str(os.getpid()));assert not temp.exists();os.link(source,temp)
  assert hashlib.sha256(temp.read_bytes()).hexdigest()==digest;os.replace(temp,path)
  assert path.stat().st_ino==source.stat().st_ino and hashlib.sha256(path.read_bytes()).hexdigest()==digest
  rows.append(dict(path=str(path),shared_with=str(source),bytes=size,SHA256=digest))
assert subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip()==head
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Atomic hardlink sharing of identical generated WAVs in completed immutable historical snapshots; all paths and audio bytes retained',root=str(ROOT),unlinked_WAVs_scanned=len(files),files_hashed=hashed,shared_files=len(rows),all_numbered_release_paths_and_Git_objects_untouched=True,HEAD_unchanged=head,actual_free_bytes_before=before,actual_free_bytes_after=shutil.disk_usage('/workspace').free,shared_immutable_files_require_new_inode_before_any_future_edit=True,files=rows)
(N/'COMPLETED_SNAPSHOT_EXACT_AUDIO_SHARING.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='files'}),flush=True)
