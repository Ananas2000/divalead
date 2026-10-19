from pathlib import Path
import os,json,hashlib,time,subprocess
BASE=Path('/workspace/divalead-work');R=BASE/'three-held-continuation';REPO=Path('/workspace/divalead')
audit=json.loads((R/'required-runtime-audio-and-libraries.json').read_text());protected=set(audit['required_paths'])
def collect(v):
 if isinstance(v,dict):
  for x in v.values():collect(x)
 elif isinstance(v,list):
  for x in v:collect(x)
 elif isinstance(v,str) and v.startswith('/workspace/') and v.endswith('.wav'):protected.add(v)
for p in BASE.glob('*/BEST_ACTUAL.json'):
 try:
  d=json.loads(p.read_text());collect(d)
  if 'validation' in d:collect(json.loads(Path(d['validation']).read_text()))
 except FileNotFoundError:pass
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();tree=subprocess.check_output(['git','ls-tree','-rz','--full-tree',head],cwd=REPO)
blobs={}
for row in tree.split(b'\0'):
 if not row:continue
 mode,path=row.split(b'\t',1);parts=mode.split()
 if parts[1]==b'blob' and path.endswith(b'.wav'):blobs[os.fsdecode(path)]=parts[2].decode()
masters={};sizes=set()
for name,oid in blobs.items():
 p=REPO/name
 if not p.is_file() or p.is_symlink():continue
 content=p.read_bytes();key=(len(content),hashlib.sha256(content).hexdigest());masters.setdefault(key,dict(repository_path=name,blob=oid));sizes.add(len(content))
rows=[]
for v in BASE.rglob('validation.json'):
 if R in v.parents:continue
 if time.time()-v.stat().st_mtime<1800:continue
 for p in v.parent.glob('*.wav'):
  if str(p) in protected or not p.is_file() or p.is_symlink():continue
  st=p.stat();inode=(st.st_dev,st.st_ino)
  if time.time()-max(st.st_mtime,st.st_ctime)<1800:continue
  if st.st_size not in sizes:continue
  key=(st.st_size,hashlib.sha256(p.read_bytes()).hexdigest())
  if key in masters:rows.append(dict(path=str(p),bytes=st.st_size,SHA256=key[1],commit=head,inode=st.st_ino,device=st.st_dev,link_count=st.st_nlink,**masters[key]))
groups={}
for row in rows:groups.setdefault((row['device'],row['inode']),[]).append(row)
rows=[row for group in groups.values() if len(group)==group[0]['link_count'] for row in group]
report=dict(historical_private_duplicates=len(rows),logical_bytes=sum(x['bytes'] for x in rows),current_three_held_tree_excluded=True,actual_runtime_dependency_paths_protected=True,protected_paths=sorted(protected),files=rows)
(R/'published-audio-cache-plan.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['protected_paths','files']},flush=True)
