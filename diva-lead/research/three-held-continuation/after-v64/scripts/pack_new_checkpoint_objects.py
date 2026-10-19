"""Preserve every new loose Git object while compacting only this checkpoint."""
from pathlib import Path
import os,sys,hashlib,json,subprocess,zlib,shutil,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');O=REPO/'.git/objects'
T=Path('/tmp/divalead-v63-verified-incremental-pack');T.mkdir(exist_ok=False)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO).split()[0]==subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO).split()[0]
refs=subprocess.check_output(['git','show-ref'],cwd=REPO)
all_ids=set(subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'],cwd=REPO).splitlines())
loose=[]
for p in sorted(O.glob('[0-9a-f][0-9a-f]/*')):
    if not p.is_file() or len(p.name)!=38:continue
    oid=p.parent.name+p.name;data=p.read_bytes()
    assert hashlib.sha1(zlib.decompress(data)).hexdigest()==oid
    backup=T/'loose-backup'/p.parent.name/p.name;backup.parent.mkdir(parents=True,exist_ok=True)
    backup.write_bytes(data);assert backup.read_bytes()==data
    loose.append((oid,p,backup))
assert loose
bare=T/'verify.git';subprocess.run(['git','init','--bare','-q',str(bare)],check=True)
env=dict(os.environ,GIT_OBJECT_DIRECTORY=str(bare/'objects'),GIT_ALTERNATE_OBJECT_DIRECTORIES=str(O))
with (T/'pack.log').open('w') as log:
    run=subprocess.run(['git','pack-objects','--threads=1','--window=50','--depth=50','--window-memory=128m',str(T/'pack')],cwd=REPO,env=env,input=('\n'.join(x[0] for x in loose)+'\n').encode(),stdout=subprocess.PIPE,stderr=log,check=True)
name=run.stdout.decode().strip();pack=T/('pack-'+name+'.pack');index=pack.with_suffix('.idx')
for p in [pack,index]:os.link(p,bare/'objects/pack'/p.name)
with (T/'verify-pack.log').open('w') as log:subprocess.run(['git','verify-pack','-v',str(index)],stdout=log,stderr=subprocess.STDOUT,check=True)
actual=set(subprocess.check_output(['git','--git-dir='+str(bare),'cat-file','--batch-all-objects','--batch-check=%(objectname)']).splitlines())
assert actual=={x[0].encode() for x in loose}
before=shutil.disk_usage(REPO).free
assert pack.stat().st_size+index.stat().st_size<before-128*1024**2
for p in [pack,index]:
    dest=O/'pack'/p.name;assert not dest.exists();shutil.copyfile(p,dest)
    assert hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(p.read_bytes()).digest()
# The persistent pack is installed and independently indexed before any removal.
for oid,p,backup in loose:
    assert p.read_bytes()==backup.read_bytes();p.unlink()
assert all_ids==set(subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'],cwd=REPO).splitlines())
assert refs==subprocess.check_output(['git','show-ref'],cwd=REPO)
with (T/'fsck.log').open('w') as log:subprocess.run(['git','fsck','--full'],cwd=REPO,stdout=log,stderr=subprocess.STDOUT,check=True)
assert not (O/'info/alternates').exists()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),loose_objects=len(loose),all_object_IDs_preserved=True,refs_and_worktree_unchanged=True,persistent_new_pack=str(O/'pack'/pack.name),pack_bytes=pack.stat().st_size,pack_SHA256=hashlib.sha256(pack.read_bytes()).hexdigest(),exact_loose_backup=str(T/'loose-backup'),temporary_cache_not_required_for_runtime=True,no_alternates=True,git_fsck_full_passed=True,free_before=before,free_after=shutil.disk_usage(REPO).free)
(R/'v63-incremental-Git-pack.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
