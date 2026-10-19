"""Losslessly retain the unused historical Wine test prefix while freeing space."""
from pathlib import Path
import tarfile,hashlib,json,shutil,os,datetime
B=Path('/workspace/divalead-work');source=B/'wine-clean-check';archive=B/'historical-wine-clean-check.tar.gz';report=B/'historical-wine-clean-check-archive.json'
assert source.is_dir() and not archive.exists() and not report.exists()
# Current audio hosts use divalead-setup/wine2. Never archive a live Wine prefix.
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0')
  if args and b'wine' in Path(args[0].decode(errors='ignore')).name.encode():assert not any(b'wine-clean-check' in x for x in args)
 except (FileNotFoundError,ProcessLookupError):pass
before=shutil.disk_usage(B).free;rows=[]
for p in sorted(source.rglob('*')):
 st=p.lstat();row=dict(path=str(p.relative_to(B)),mode=st.st_mode,mtime_ns=st.st_mtime_ns)
 if p.is_symlink():row['symlink']=os.readlink(p)
 elif p.is_file():row.update(bytes=st.st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
 rows.append(row)
with tarfile.open(archive,'w:gz',compresslevel=1,dereference=False) as tar:tar.add(source,arcname=source.name)
with tarfile.open(archive,'r:gz') as tar:
 for row in rows:
  info=tar.getmember(row['path'])
  if 'SHA256' in row:
   with tar.extractfile(info) as f:assert hashlib.sha256(f.read()).hexdigest()==row['SHA256'],row['path']
  if 'symlink' in row:assert info.issym() and info.linkname==row['symlink']
for row in rows:
 p=B/row['path'];assert p.lstat().st_mtime_ns==row['mtime_ns']
 if 'SHA256' in row:assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256']
data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original=str(source),archive=str(archive),archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),archive_bytes=archive.stat().st_size,all_members_byte_verified=True,live_Wine_prefix_unchanged='/workspace/divalead-setup/wine2',retained_on_persistent_storage=True,restore_command='tar -xzf /workspace/divalead-work/historical-wine-clean-check.tar.gz -C /workspace/divalead-work',files=rows,free_bytes_before=before)
report.write_text(json.dumps(data,indent=2)+'\n')
shutil.rmtree(source)
data['free_bytes_after']=shutil.disk_usage(B).free;report.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:v for k,v in data.items() if k!='files'}),flush=True)
