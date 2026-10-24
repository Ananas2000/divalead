"""Drop only obsolete extracted/check ZIP copies, after full remote ZIP proof."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,subprocess,zipfile
P=Path('/workspace/divalead');B=Path('/tmp/divalead-local-1625');D=B/'internet-plugins-20261023';N=Path('/workspace/divalead-work/native-low-latency-effects')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip();assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=P,text=True).split()[0]==head
open_paths=[]
for proc in Path('/proc').glob('[0-9]*'):
 try:
  for f in(proc/'fd').iterdir():
   try:open_paths.append(os.readlink(f))
   except OSError:pass
 except (OSError,PermissionError):pass
def free():return {p:shutil.disk_usage(p).free for p in ['/workspace','/tmp']}
before=free();removed=[];skipped=[]
for number in range(21,23):
 code=f'{number:02}';label=f'Diva_ZL_{code}_WIP';rel=f'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP{code}/{label}_complete_WIP.zip'
 blob=subprocess.check_output(['git','show',head+':'+rel],cwd=P);zip_sha=hashlib.sha256(blob).hexdigest()
 with zipfile.ZipFile(io.BytesIO(blob))as z:
  assert z.testzip()is None;known={hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()if not name.endswith('/')}
  entries={name:z.read(name)for name in z.namelist()if not name.endswith('/')}
 roots=[B/f'FL20_ZL_{code}_WIP',D/f'ZL{code}-actual-ZIP-replay']
 for root in roots:
  if not root.exists()or root.is_symlink():continue
  if any(p.startswith(str(root)+'/')for p in open_paths):skipped.append(dict(path=str(root),reason='actual open file'));continue
  files=[];valid=True
  for p in root.rglob('*'):
   if p.is_symlink():valid=False;break
   if not p.is_file():continue
   b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
   if h not in known:
    if p.name!='SHA256SUMS.txt':valid=False;skipped.append(dict(path=str(root),reason='file not contained byte-exact in remote full ZIP',file=str(p)));break
    # Restored validation stage predates the later-added ZIP proof. Its own
    # checksum manifest is reproducible: verify each listed file's bytes.
    for line in b.decode().splitlines():
     digest,name=line.split('  ',1);q=p.parent/name
     if not q.is_file()or hashlib.sha256(q.read_bytes()).hexdigest()!=digest:valid=False;break
    if not valid:break
   files.append(dict(relative=str(p.relative_to(root)),bytes=len(b),SHA256=h))
  if valid:
   removed.append(dict(path=str(root),remote_commit=head,remote_ZIP_git_path=rel,remote_ZIP_SHA256=zip_sha,files=files,policy='Every file present byte-exact in remote ZIP except validated reproducible pre-proof checksum manifest; no active files.'))
   shutil.rmtree(root)
 zipcopy=B/(label+'_complete_WIP.zip')
 if zipcopy.exists():
  assert hashlib.sha256(zipcopy.read_bytes()).hexdigest()==zip_sha
  removed.append(dict(path=str(zipcopy),remote_commit=head,remote_ZIP_git_path=rel,remote_ZIP_SHA256=zip_sha,was_symlink=zipcopy.is_symlink()));zipcopy.unlink()
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),before=before,after=free(),protected_latest_complete_kit='ZL23 and newer; nativebase06/source/all main retained',protected_native_builder_base=str(B/'FL20_NATIVE_17_WIP'),removed=removed,skipped=skipped,restore='git show <remote_commit>:<remote_ZIP_git_path> > old-kit.zip; unzip into a NEW directory. GitHub versions/objects untouched.')
(N/'ZL21_ZL22_EXPANDED_STAGES_REMOTE_VERIFIED_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(removed_paths=len(removed),skipped=skipped,before=before,after=receipt['after']),indent=2))
