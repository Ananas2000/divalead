"""Full traversal; classify four known audio codec dependency build checkouts."""
from pathlib import Path
import datetime,json,os,subprocess,urllib.parse
base=Path('/workspace');errors=[];projects=[];dependencies=[];visited=0
known_caches={
 '/workspace/divalead-setup/codec/fdk-aac':'mstorsjo/fdk-aac',
 '/workspace/divalead-setup/codec/fdkaac':'nu774/fdkaac',
 '/workspace/divalead-setup/codec-research/fdk-aac':'mstorsjo/fdk-aac',
 '/workspace/divalead-tools/fdk-aac':'mstorsjo/fdk-aac'}
for root,dirs,files in os.walk(base,followlinks=False,onerror=lambda e:errors.append(str(e))):
 visited+=1
 if '.git'in dirs or '.git'in files:
  p=Path(root);real=p.resolve();assert real.is_relative_to(base)
  def git(*args):return subprocess.check_output(['git','-C',str(p),*args],text=True).strip()
  assert Path(git('rev-parse','--show-toplevel')).resolve()==real
  # Canonical origin identity precedes the platform HTTPS proxy rewrite.
  remote=git('config','--get','remote.origin.url');u=urllib.parse.urlsplit(remote);assert u.hostname=='github.com';name=u.path.strip('/').removesuffix('.git');assert len(name.split('/'))==2
  row=dict(name=name,host=u.hostname,commit=git('rev-parse','--verify','HEAD^{commit}'),mount_path=p.relative_to(base).as_posix(),submodule_entries=sum(line.startswith('160000 ')for line in git('ls-files','--stage').splitlines()))
  if str(p)in known_caches:
   assert name==known_caches[str(p)];row.update(classification='audio codec dependency build/cache, not a user project checkout',dirty_status_lines=len(git('status','--porcelain').splitlines()),preserved_unchanged=True);dependencies.append(row)
  else:projects.append(row)
  if '.git'in dirs:dirs.remove('.git')
assert not errors,errors
assert len({r['name']for r in projects})==len(projects)
assert {r['mount_path']for r in projects}=={'divalead'}
assert len(dependencies)==len(known_caches)
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),complete_workspace_traversal=True,visited_directories=visited,errors=errors,repositories=projects,classified_dependency_build_caches=dependencies,preservation_archives_not_declared_as_checkouts=True)
out=Path('/workspace/divalead-work/native-low-latency-effects/CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(complete_workspace_traversal=True,visited_directories=visited,errors=errors,repositories=projects,classified_audio_codec_dependency_build_caches=len(dependencies))))
