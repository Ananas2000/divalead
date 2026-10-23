"""Omit ONLY verified remote-backed old release artifacts from local checkout.
No version or Git object is deleted. Restore one with the recorded git command.
"""
from pathlib import Path
import collections,datetime,fcntl,hashlib,json,os,re,shutil,subprocess
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
OWNER='authorized-local-backed-copy-cleanup-20261023'
def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=P,input=input)
def free():return {x:shutil.disk_usage(x).free for x in ['/workspace','/tmp']}
with (R/'auto-backup-Git.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert json.loads((R/'auto-backup.pause').read_text())['owner']==OWNER
 assert not git('status','--porcelain')
 head=git('rev-parse','HEAD').decode().strip();assert git('ls-remote','origin','refs/heads/main').decode().split()[0]==head
 tree={}
 for row in git('ls-tree','-rlz','HEAD').split(b'\0'):
  if not row:continue
  info,path=row.split(b'\t',1);mode,typ,oid,size=info.split()
  if typ==b'blob':tree[path.decode()]=(mode.decode(),oid.decode(),int(size))
 selected=[]
 for path,(mode,oid,size) in tree.items():
  p=P/path
  if not p.is_file() or p.is_symlink() or mode!='100644':continue
  oldzip=('/' not in path and re.fullmatch(r'Diva_lead_v\d+_WIP_checkpoint\.zip',path))
  oldaudio=re.fullmatch(r'diva-lead/v(?:[1-9]|[1-7]\d|8[0-2])-wip/.+\.(?:wav|mp3|flac)',path)
  if oldzip or oldaudio:
   assert p.stat().st_size==size
   h=hashlib.sha1();h.update(f'blob {size}\0'.encode())
   with p.open('rb') as f:
    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
   assert h.hexdigest()==oid,path
   selected.append(dict(path=path,blob=oid,bytes=size,reason='old root complete ZIP' if oldzip else 'old numbered-release audio'))
 before=free();manifest=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_verified_commit=head,remote='https://github.com/Ananas2000/divalead',policy='Local checkout omissions only. Every byte remains in HEAD and origin/main. No git rm, history rewrite, or object deletion.',restore_one='git restore --ignore-skip-worktree-bits -- <path>',before_free_bytes=before,files=selected)
 receipt=N/'REMOTE_BACKED_LOCAL_RELEASE_OMISSIONS_20261023.json';receipt.write_text(json.dumps(manifest,indent=2)+'\n')
 git('update-index','--skip-worktree','-z','--stdin',input=b''.join(x['path'].encode()+b'\0' for x in selected))
 for x in selected:(P/x['path']).unlink()
 assert git('rev-parse','HEAD').decode().strip()==head
 assert not git('status','--porcelain')
 manifest.update(after_free_bytes=free(),file_count=len(selected),logical_removed_bytes=sum(x['bytes']for x in selected))
 receipt.write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({k:v for k,v in manifest.items()if k!='files'},indent=2))
