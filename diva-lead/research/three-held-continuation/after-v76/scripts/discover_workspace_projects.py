"""Discover all project Git roots, explicitly identifying retained AAC build deps."""
from pathlib import Path
import datetime,json,os,re,subprocess,sys,urllib.parse
W=Path('/workspace').resolve();R=Path(__file__).resolve().parent
candidates=set();walk_errors=[];symlinks=[];count=0
for base,dirs,files in os.walk(W,followlinks=False,onerror=lambda e:walk_errors.append(str(e))):
 count+=1;p=Path(base)
 if '.git' in dirs or '.git' in files:candidates.add(p)
 if '.git' in dirs:dirs.remove('.git')
 for name in dirs:
  s=p/name
  if s.is_symlink():
   target=s.resolve();entry=dict(path=str(s),target=str(target),exists=target.exists());symlinks.append(entry)
   if target.exists() and (target/'.git').exists():candidates.add(target)
assert not walk_errors,walk_errors
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],text=True,stderr=subprocess.PIPE).strip()
def identity(remote):
 if '://' in remote:
  u=urllib.parse.urlparse(remote);host=u.hostname;path=u.path.strip('/')
 else:
  m=re.fullmatch(r'(?:[^/@]+@)?([^/:]+):(.+)',remote);assert m,'Unusable remote (not printed)';host=m[1];path=m[2].strip('/')
 path=path.removesuffix('.git');assert host=='github.com' and re.fullmatch(r'[^/]+/[^/]+',path)
 return host,path
rows=[];seen=set()
for candidate in sorted(candidates):
 root=Path(git(candidate,'rev-parse','--show-toplevel')).resolve();assert root.is_relative_to(W) and root!=W
 if root in seen:continue
 seen.add(root);host,name=identity(git(root,'remote','get-url','origin'));head=git(root,'rev-parse','--verify','HEAD^{commit}');assert re.fullmatch('[0-9a-f]{40}',head)
 rows.append(dict(name=name,host=host,commit=head,mount_path=str(root.relative_to(W))))
deps={'divalead-setup/codec/fdk-aac':'mstorsjo/fdk-aac','divalead-setup/codec/fdkaac':'nu774/fdkaac','divalead-setup/codec-research/fdk-aac':'mstorsjo/fdk-aac','divalead-tools/fdk-aac':'mstorsjo/fdk-aac'}
projects=[];excluded=[]
for row in rows:
 if row['mount_path'] in deps:
  assert row['name']==deps[row['mount_path']];excluded.append(dict(**row,reason='Explicitly retained AAC build dependency, not a project checkout.'))
 else:projects.append(row)
assert len(excluded)==4 and len(projects)==1 and projects[0]['name']=='Ananas2000/divalead',projects
assert len({(r['host'],r['name'].lower()) for r in projects})==len(projects)
for i,a in enumerate(projects):
 for b in projects[i+1:]:assert not (Path(a['mount_path']).is_relative_to(Path(b['mount_path'])) or Path(b['mount_path']).is_relative_to(Path(a['mount_path'])))
d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),walked_directories=count,walk_errors=walk_errors,symlink_directories=symlinks,all_git_roots=rows,explicitly_excluded_build_dependencies=excluded,projects=projects,complete_walk=True)
out=R/(sys.argv[1] if len(sys.argv)>1 else 'post74-checkout-discovery.json');out.write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(dict(projects=projects,walked_directories=count,git_roots=len(rows),excluded_dependencies=len(excluded),walk_errors=walk_errors)))
