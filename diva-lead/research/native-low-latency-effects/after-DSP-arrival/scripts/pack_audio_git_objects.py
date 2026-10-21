"""Lossless bounded Git packing; never remove unique objects or release files."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation');W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
owner='native-audio-lossless-pack-'+str(os.getpid());pause=R/'auto-backup.pause'
with pause.open('x') as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
def git(*args,**kw):return subprocess.check_output(['git','-C',str(P),*args],**kw)
def protection():
 return git('ls-tree','HEAD:diva-lead')+git('ls-tree','HEAD')
rows=[]
try:
 deadline=time.monotonic()+90
 while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':
  assert time.monotonic()<deadline;time.sleep(1)
 with (R/'auto-backup-Git.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain').strip();head=git('rev-parse','HEAD');trees=protection();before=shutil.disk_usage('/workspace').free
  objects=P/'.git/objects';inventory=json.loads((W/'GIT_LOOSE_OBJECT_INVENTORY.json').read_text())
  candidates=[r for r in inventory if r['extension']=='.wav' and 'AB' in r['name'] and (objects/r['oid'][:2]/r['oid'][2:]).is_file()]
  candidates.sort(key=lambda r:r['name'])
  for batch in range(4):
   selected=candidates[batch*16:(batch+1)*16]
   if not selected:break
   work=W/f'audio-git-pack-{os.getpid()}-{batch}';work.mkdir();pack=work/'audio.pack';idx=work/'audio.idx'
   ids=''.join(r['oid']+'\n' for r in selected).encode();loose=sum((objects/r['oid'][:2]/r['oid'][2:]).stat().st_size for r in selected)
   with pack.open('wb') as out:
    subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--threads=1','--window=16','--depth=40'],input=ids,stdout=out,check=True)
   result=git('index-pack','-o',str(idx),str(pack),text=True).strip();sha=result.split()[-1]
   assert len(sha)==40 and pack.read_bytes()[-20:].hex()==sha
   subprocess.run(['git','-C',str(P),'verify-pack','-v',str(idx)],stdout=subprocess.DEVNULL,check=True)
   packed=pack.stat().st_size+idx.stat().st_size
   if packed>=loose or packed+8*1024**2>=shutil.disk_usage('/workspace').free:
    rows.append(dict(batch=batch,objects=len(selected),loose_bytes=loose,pack_bytes=packed,installed=False));continue
   for src,suffix in [(pack,'pack'),(idx,'idx')]:
    dest=objects/'pack'/f'pack-{sha}.{suffix}';temp=dest.with_suffix(dest.suffix+'.native-partial');shutil.copyfile(src,temp)
    assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(temp.read_bytes()).digest();temp.replace(dest)
   subprocess.run(['git','-C',str(P),'prune-packed'],check=True)
   assert git('rev-parse','HEAD')==head and protection()==trees
   rows.append(dict(batch=batch,objects=len(selected),loose_bytes=loose,pack_bytes=packed,installed=True,pack_sha=sha));print('LOSSLESS_AUDIO_PACK',rows[-1],flush=True)
  subprocess.run(['git','-C',str(P),'fsck','--connectivity-only','--no-dangling'],stdout=subprocess.DEVNULL,check=True)
  assert not git('status','--porcelain').strip()
  (N/'LOSSLESS_AUDIO_GIT_PACKING.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Verified small Git packs, only redundant loose objects pruned',before_free_bytes=before,after_free_bytes=shutil.disk_usage('/workspace').free,HEAD_unchanged=head.decode().strip(),release_trees_and_all_history_retained=True,connectivity_passed=True,batches=rows),indent=2)+'\n')
finally:
 if pause.exists() and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
