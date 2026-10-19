"""Prepare and verify a lossless pack of every Git object outside the checkout."""
from pathlib import Path
import subprocess,json,hashlib,datetime,os
REPO=Path('/workspace/divalead');T=Path('/tmp/divalead-verified-object-pack-v2');T.mkdir(exist_ok=False)
objects=subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'],cwd=REPO).splitlines();assert len(set(objects))==len(objects)
(T/'all-objects.txt').write_bytes(b'\n'.join(sorted(objects))+b'\n');refs=subprocess.check_output(['git','show-ref'],cwd=REPO);(T/'refs-before.txt').write_bytes(refs)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
verify=T/'verification.git';subprocess.run(['git','init','--bare','-q',str(verify)],check=True)
packenv=dict(os.environ,GIT_OBJECT_DIRECTORY=str(verify/'objects'),GIT_ALTERNATE_OBJECT_DIRECTORIES=str(REPO/'.git/objects'))
with (T/'all-objects.txt').open('rb') as inp,(T/'pack.log').open('w') as err:
 result=subprocess.run(['git','pack-objects','--threads=1','--window=50','--depth=50','--window-memory=128m',str(T/'pack')],cwd=REPO,stdin=inp,stderr=err,stdout=subprocess.PIPE,env=packenv,check=True)
name=result.stdout.decode().strip();pack=T/('pack-'+name+'.pack');index=pack.with_suffix('.idx');assert pack.exists() and index.exists()
with (T/'verify-pack.log').open('w') as out:subprocess.run(['git','verify-pack','-v',str(index)],stdout=out,stderr=subprocess.STDOUT,check=True)
for p in [pack,index]:os.link(p,verify/'objects/pack'/p.name)
actual=subprocess.check_output(['git','--git-dir='+str(verify),'cat-file','--batch-all-objects','--batch-check=%(objectname)']).splitlines();assert set(actual)==set(objects)
assert refs==subprocess.check_output(['git','show-ref'],cwd=REPO)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_objects_including_unreachable_preserved=True,objects=len(objects),pack=str(pack),index=str(index),pack_bytes=pack.stat().st_size,index_bytes=index.stat().st_size,pack_file_SHA256=hashlib.sha256(pack.read_bytes()).hexdigest(),index_file_SHA256=hashlib.sha256(index.read_bytes()).hexdigest(),all_new_object_IDs_equal_original_set=True,verify_pack_passed=True,current_repository_NOT_modified=True)
(T/'verified-pack.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
