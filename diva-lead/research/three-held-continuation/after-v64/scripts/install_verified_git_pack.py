"""Install the verified all-object pack without changing refs or worktree bytes."""
from pathlib import Path
import os,json,hashlib,shutil,subprocess,zlib,datetime
REPO=Path('/workspace/divalead');R=Path(__file__).resolve().parent;T=Path('/tmp/divalead-verified-object-pack-v2');d=json.loads((T/'verified-pack.json').read_text());O=REPO/'.git/objects';pack=Path(d['pack']);index=Path(d['index']);ids=(T/'all-objects.txt').read_text().splitlines()
assert d['verify_pack_passed'] and d['all_new_object_IDs_equal_original_set']
assert (T/'refs-before.txt').read_bytes()==subprocess.check_output(['git','show-ref'],cwd=REPO)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
assert digest(pack)==d['pack_file_SHA256'] and digest(index)==d['index_file_SHA256']
backup=T/'original-loose-backup';backup.mkdir(exist_ok=False);before=shutil.disk_usage(REPO).free;loose=[]
for oid in ids:
 p=O/oid[:2]/oid[2:]
 if not p.is_file():continue
 content=p.read_bytes();assert hashlib.sha1(zlib.decompress(content)).hexdigest()==oid
 target=backup/oid[:2]/oid[2:];target.parent.mkdir(exist_ok=True);target.write_bytes(content);assert target.read_bytes()==content;loose.append(oid)
 print('GIT_LOOSE_BACKUP_VERIFIED',len(loose),flush=True) if len(loose)%1000==0 else None
alt=O/'info/alternates';old_alt=alt.read_bytes() if alt.exists() else None;temporary_alt=False
# Every object has already been independently verified in verification.git.
# A temporary alternate is used only if root cannot fit both representations.
if pack.stat().st_size+index.stat().st_size>shutil.disk_usage(REPO).free-128*1024**2:
 content=(old_alt or b'');content+=b'\n' if content and not content.endswith(b'\n') else b'';content+=str(T/'verification.git/objects').encode()+b'\n';tmp=alt.with_suffix('.verified-tmp');tmp.write_bytes(content);tmp.replace(alt);temporary_alt=True
 assert set(subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'],cwd=REPO,text=True).splitlines())==set(ids)
def install():
 for source in [pack,index]:
  dest=O/'pack'/source.name;assert not dest.exists();tmp=dest.with_suffix(dest.suffix+'.verified-tmp')
  with source.open('rb') as inp,tmp.open('wb') as out:shutil.copyfileobj(inp,out,8*1024**2);out.flush();os.fsync(out.fileno())
  assert digest(tmp)==digest(source);tmp.replace(dest)
 with (T/'persistent-verify-pack.log').open('w') as log:subprocess.run(['git','verify-pack','-v',str(O/'pack'/index.name)],stdout=log,stderr=subprocess.STDOUT,check=True)
if not temporary_alt:install()
for oid in loose:
 p=O/oid[:2]/oid[2:];assert p.read_bytes()==(backup/oid[:2]/oid[2:]).read_bytes();p.unlink()
if temporary_alt:install()
if temporary_alt:
 if old_alt is None:alt.unlink()
 else:tmp=alt.with_suffix('.restored-tmp');tmp.write_bytes(old_alt);tmp.replace(alt)
assert (T/'refs-before.txt').read_bytes()==subprocess.check_output(['git','show-ref'],cwd=REPO)
actual=subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'],cwd=REPO,text=True).splitlines();assert set(actual)==set(ids)
with (T/'repository-fsck.log').open('w') as log:subprocess.run(['git','fsck','--full'],cwd=REPO,stdout=log,stderr=subprocess.STDOUT,check=True)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_Git_objects_including_unreachable_preserved=True,all_object_IDs_exact=True,Git_refs_and_clean_worktree_unchanged=True,objects=len(ids),loose_objects_repacked=len(loose),persistent_pack=str(O/'pack'/pack.name),pack_SHA256=d['pack_file_SHA256'],pack_bytes=pack.stat().st_size,byte_verified_old_loose_backup=str(backup),old_loose_backup_temporary_but_complete_pack_persistent=True,no_temporary_runtime_alternate_remaining=True,git_fsck_full_passed=True,free_bytes_before=before,free_bytes_after=shutil.disk_usage(REPO).free)
(R/'verified-git-pack-installed.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
