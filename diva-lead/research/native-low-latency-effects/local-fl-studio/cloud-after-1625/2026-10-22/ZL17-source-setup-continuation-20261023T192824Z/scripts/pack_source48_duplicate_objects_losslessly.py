"""Retain all Git objects, compress full archive/part duplicates together."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,runpy,shutil,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='source48_lossless_pack_helpers');P=s['P'];N=s['N'];R=s['R'];PUBLIC=s['PUBLIC'];git=s['git'];read=s['read'];objects=P/'.git/objects';owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='losslessly pack verified original/part Git objects and evict remote-backed private archive duplicate only'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');s['fetch_main']();head=git('rev-parse','HEAD');assert head==git('rev-parse','origin/main');old=s['protected']();before={p:shutil.disk_usage(p).free for p in ['/workspace','/tmp']}
  relroot=(PUBLIC/'actual-Diva-OscMix6p5-fixed-independent48-confirmation').relative_to(P).as_posix();filename='FORTYEIGHT_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';manifest=read(P/relroot/(filename+'.SPLIT_ARCHIVE_MANIFEST.json'));archive=D/'ZL-Diva-source-OscMix6p5-independent48-adoption-01'/filename;assert sha(archive)==manifest['original_SHA256'];whole=hashlib.sha256();oids=[]
  original_oid=git('rev-parse','f3ed5c50c4d6fc5660478dbc18e5585f714c267e:'+relroot+'/'+filename);oids.append(original_oid)
  for part in manifest['parts']:
   oid=git('rev-parse','HEAD:'+relroot+'/'+part['name']);blob=subprocess.check_output(['git','-C',str(P),'cat-file','blob',oid]);assert len(blob)==part['bytes']and hashlib.sha256(blob).hexdigest()==part['SHA256'];whole.update(blob);oids.append(oid)
  assert whole.hexdigest()==manifest['original_SHA256']and len(set(oids))==4
  # All source archive bytes already verified in remote HEAD parts. Remove the
  # private duplicate; it is also still present as a local Git object/bundle.
  archive.unlink();restore=dict(original_path=str(archive),SHA256=manifest['original_SHA256'],bytes=manifest['original_bytes'],remote_commit=head,parts_manifest=relroot+'/'+filename+'.SPLIT_ARCHIVE_MANIFEST.json',local_original_blob=original_oid,restore_local_command='git cat-file blob '+original_oid+' > '+str(archive),remote_restore='Read the three listed part blobs from GitHub, concatenate in order, verify full SHA256.');(N/'SOURCE48_PRIVATE_ARCHIVE_REMOTE_BACKED_EVICTION.json').write_text(json.dumps(restore,indent=2)+'\n')
  work=D/('source48-four-object-pack-'+str(os.getpid()));work.mkdir();pack=work/'source48.pack';idx=pack.with_suffix('.idx');loose=[objects/oid[:2]/oid[2:]for oid in oids];assert all(p.is_file()for p in loose);loose_bytes=sum(p.stat().st_size for p in loose)
  with pack.open('wb')as out:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--delta-base-offset','--threads=1','--window=4','--depth=10'],input=''.join(oid+' source48-proof-archive\n'for oid in oids).encode(),stdout=out,check=True)
  digest=subprocess.check_output(['git','-C',str(P),'index-pack','-o',str(idx),str(pack)],text=True).strip();assert re.fullmatch('[0-9a-f]{40}',digest);v=subprocess.check_output(['git','-C',str(P),'verify-pack','-v',str(idx)],text=True);assert{line.split()[0]for line in v.splitlines()if re.match('[0-9a-f]{40} blob ',line)}==set(oids)
  packed=pack.stat().st_size+idx.stat().st_size;installed=False
  if packed<loose_bytes-8*2**20 and packed<shutil.disk_usage('/workspace').free-96*2**20:
   for src,ext in [(pack,'pack'),(idx,'idx')]:
    dest=objects/'pack'/f'pack-{digest}.{ext}';assert not dest.exists();temp=dest.with_suffix(dest.suffix+'.source48-partial');shutil.copyfile(src,temp);assert sha(temp)==sha(src);temp.replace(dest)
   subprocess.run(['git','-C',str(P),'verify-pack',str(objects/'pack'/f'pack-{digest}.idx')],check=True)
   for p in loose:p.unlink()
   checked=subprocess.check_output(['git','-C',str(P),'cat-file','--batch-check'],input='\n'.join(oids)+'\n',text=True);assert len(checked.splitlines())==4 and ' missing'not in checked;installed=True
  pack.unlink();idx.unlink();subprocess.run(['git','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL);assert git('rev-parse','HEAD')==head and not git('status','--porcelain');assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items());receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),HEAD_unchanged=head,all_original_and_part_Git_objects_retained=True,Git_connectivity_passed=True,all_prior_complete_kit_tree_OIDs_preserved=True,before_free_bytes=before,after_free_bytes={p:shutil.disk_usage(p).free for p in before},loose_bytes=loose_bytes,pack_bytes=packed,new_pack_installed=installed,pack_id=digest,private_archive_eviction=restore);(N/'SOURCE48_LOSSLESS_FOUR_OBJECT_PACKING.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
