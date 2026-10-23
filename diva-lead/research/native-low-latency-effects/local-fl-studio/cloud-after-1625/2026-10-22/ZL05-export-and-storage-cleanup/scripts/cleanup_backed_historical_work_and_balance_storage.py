from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');WK=Path('/workspace/divalead-work')
plan=json.loads((N/'WORK_REMOTE_BACKED_DUPLICATE_PLAN.json').read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=P,text=True).split()[0]==head
protected=set()
for root in ['/workspace/divalead-work','/tmp/divalead-local-1625','/tmp/divalead-native-effects']:
 for p in Path(root).rglob('*'):
  if p.is_symlink():
   try:protected.add(str(p.resolve(strict=True)))
   except FileNotFoundError:pass
for proc in Path('/proc').glob('[0-9]*'):
 try:
  for p in (proc/'fd').iterdir():
   try:protected.add(os.readlink(p))
   except OSError:pass
 except (PermissionError,FileNotFoundError):pass
def free():return {x:shutil.disk_usage(x).free for x in ['/workspace','/tmp']}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
before=free();removed=[];kept=[]
for row in plan:
 p=Path(row['local']);rel=p.relative_to(WK)
 assert rel.parts[0]not in ['native-low-latency-effects','three-held-continuation','current-source-history-probe','current-source-proof','wine-clean-check']
 if str(p)in protected:kept.append(row);continue
 if not p.is_file()or p.is_symlink():continue
 size=p.stat().st_size;assert hashlib.sha1(f'blob {size}\0'.encode()+p.read_bytes()).hexdigest()==row['blob']
 p.unlink();removed.append(row)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_commit=head,before=before,after=free(),removed=removed,protected=kept,restore='git show '+head+':<git_path> > <local_path>')
(N/'REMOTE_BACKED_HISTORICAL_WORK_CLEANUP.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('EXACT_BACKED_WORK_COPIES',json.dumps(dict(removed=len(removed),protected=len(kept),before=before,after=receipt['after'])),flush=True)
# Relocate retained old rejected-cohort archives across volumes, preserving all
# paths through one directory symlink. Every file is verified before unlink.
src=Path('/tmp/divalead-local-1625/archived-rejected-native-cohort-WAVs');dst=WK/'offline-storage'/'archived-rejected-native-cohort-WAVs'
assert src.is_dir()and not src.is_symlink()and not dst.exists()
size=sum(p.stat().st_size for p in src.rglob('*')if p.is_file());assert shutil.disk_usage('/workspace').free>size+512*2**20
before2=free();dst.parent.mkdir(exist_ok=True);shutil.copytree(src,dst)
items=[]
for p in src.rglob('*'):
 if p.is_file():
  assert not p.is_symlink();q=dst/p.relative_to(src);assert q.is_file()and p.stat().st_size==q.stat().st_size
  a=sha(p);assert a==sha(q);items.append(dict(relative=str(p.relative_to(src)),bytes=p.stat().st_size,SHA256=a))
assert len(items)==sum(1 for p in dst.rglob('*')if p.is_file())
old=src.with_name(src.name+'.verified-relocation-original');assert not old.exists();src.rename(old);src.symlink_to(dst,target_is_directory=True)
assert all(sha(src/r['relative'])==r['SHA256'] for r in items)
shutil.rmtree(old)
receipt2=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=str(src),destination=str(dst),before=before2,after=free(),files=items,policy='Retained all archives byte-for-byte; old path still resolves via directory symlink.')
(N/'RETAINED_ARCHIVES_CROSS_VOLUME_RELOCATION.json').write_text(json.dumps(receipt2,indent=2)+'\n')
print('RETAINED_ARCHIVE_REBALANCE',json.dumps(dict(files=len(items),bytes=size,before=before2,after=receipt2['after'])),flush=True)
