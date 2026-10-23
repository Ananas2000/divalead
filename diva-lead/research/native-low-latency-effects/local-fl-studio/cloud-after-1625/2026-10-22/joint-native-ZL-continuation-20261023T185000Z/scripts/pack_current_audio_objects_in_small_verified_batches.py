"""Bounded lossless Git compression; keep every object, ref and release."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,runpy,shutil,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='bounded_pack_helpers')
P=s['P'];N=s['N'];R=s['R'];git=s['git'];read=s['read'];objects=P/'.git/objects'
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause';work=D/('bounded-audio-Git-pack-'+str(os.getpid()));work.mkdir()
with pause.open('x')as p:json.dump(dict(owner=owner,PID=os.getpid(),reason='small verified lossless audio object packs; no history removal'),p)
rows=[]
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');head=git('rev-parse','HEAD');old=s['protected']();before=shutil.disk_usage('/workspace').free
  names={}
  for line in git('rev-list','--objects','--all','--unpacked').splitlines():
   fields=line.split(' ',1)
   if len(fields)==2 and fields[1].lower().endswith('.wav'):
    oid=fields[0];path=objects/oid[:2]/oid[2:]
    if path.is_file():names[oid]=fields[1]
  candidates=sorted(names,key=lambda oid:names[oid]);batches=[];batch=[];size=0
  for oid in candidates:
   path=objects/oid[:2]/oid[2:];n=path.stat().st_size
   if batch and(size+n>60*2**20 or len(batch)>=24):batches.append(batch);batch=[];size=0
   batch.append(oid);size+=n
  if batch:batches.append(batch)
  for number,ids in enumerate(batches[:12]):
   loose=sum((objects/oid[:2]/oid[2:]).stat().st_size for oid in ids)
   if loose>shutil.disk_usage('/workspace').free-96*2**20:break
   pack=work/f'batch-{number}.pack';idx=pack.with_suffix('.idx')
   with pack.open('wb')as out:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--delta-base-offset','--threads=2','--window=24','--depth=40'],input=''.join(oid+' '+names[oid]+'\n'for oid in ids).encode(),stdout=out,check=True)
   result=subprocess.check_output(['git','-C',str(P),'index-pack','-o',str(idx),str(pack)],text=True).strip();assert re.fullmatch('[0-9a-f]{40}',result)
   verify=subprocess.check_output(['git','-C',str(P),'verify-pack','-v',str(idx)],text=True);found={line.split()[0]for line in verify.splitlines()if re.match('[0-9a-f]{40} blob ',line)};assert found==set(ids)
   packed=pack.stat().st_size+idx.stat().st_size;row=dict(batch=number,objects=len(ids),loose_bytes=loose,pack_bytes=packed,installed=False)
   if packed<loose-1024*1024 and packed<shutil.disk_usage('/workspace').free-96*2**20:
    for src,ext in [(pack,'pack'),(idx,'idx')]:
     target=objects/'pack'/f'pack-{result}.{ext}';assert not target.exists();temp=target.with_suffix(target.suffix+'.divalead-partial');shutil.copyfile(src,temp);assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(temp.read_bytes()).digest();temp.replace(target)
    subprocess.run(['git','-C',str(P),'verify-pack',str(objects/'pack'/f'pack-{result}.idx')],check=True)
    # Remove only original loose copies represented by the verified new pack.
    for oid in ids:(objects/oid[:2]/oid[2:]).unlink()
    checked=subprocess.check_output(['git','-C',str(P),'cat-file','--batch-check'],input='\n'.join(ids)+'\n',text=True)
    assert len(checked.splitlines())==len(ids)and ' missing'not in checked
    row.update(installed=True,pack_id=result)
   rows.append(row);pack.unlink();idx.unlink();print('VERIFIED_BOUNDED_AUDIO_PACK',json.dumps(row),flush=True)
  subprocess.run(['git','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL)
  assert git('rev-parse','HEAD')==head and not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items())
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),HEAD_unchanged=head,all_old_complete_kit_tree_OIDs_preserved=True,all_objects_and_Git_history_preserved=True,Git_connectivity_passed=True,before_free_bytes=before,after_free_bytes=shutil.disk_usage('/workspace').free,batches=rows)
  (N/'CURRENT_BOUNDED_LOSSLESS_AUDIO_GIT_PACKING.json').write_text(json.dumps(receipt,indent=2)+'\n');print('LOSSLESS_AUDIO_PACKING_COMPLETE',json.dumps({k:v for k,v in receipt.items()if k!='batches'}),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
