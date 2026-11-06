"""Stage large verified proof archives with bounded checkout space, ordinary Git."""
from pathlib import Path
import hashlib,json,shutil,subprocess,zlib
def stage_archive(P,git,source,dest):
 source=Path(source);dest=Path(dest);size=source.stat().st_size;part_size=48*2**20;parts=[];whole=hashlib.sha256();number=0
 with source.open('rb')as f:
  while block:=f.read(part_size):
   number+=1;name=source.name if size<=part_size else source.name+f'.part-{number:03d}';rel=(dest/name).relative_to(P).as_posix();oid=subprocess.check_output(['git','-C',str(P),'hash-object','-w','--stdin'],input=block).decode().strip();assert hashlib.sha1(b'blob '+str(len(block)).encode()+b'\0'+block).hexdigest()==oid;digest=hashlib.sha256(block).hexdigest();whole.update(block);git('update-index','--add','--cacheinfo','100644,'+oid+','+rel);git('update-index','--skip-worktree','--',rel);parts.append(dict(name=name,path=rel,OID=oid,SHA256=digest,bytes=len(block)))
 manifest=dict(original_filename=source.name,original_bytes=size,original_SHA256=whole.hexdigest(),parts=parts,exact_reassembly='Read parts in listed order, concatenate and verify total size/SHA256; bytes are unchanged.')
 assert sum(p['bytes']for p in parts)==size
 (dest/(source.name+'.ARCHIVE_MANIFEST.json')).write_text(json.dumps(manifest,indent=2)+'\n');return manifest
def finish_manifest(h,dest,parts):
 P,PUBLIC=h['P'],h['PUBLIC'];hashes={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'};hashes.update({p['name']:p['SHA256']for p in parts});(dest/'FILE_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n');h['aggregate']();f=PUBLIC/'SHA256SUMS.txt';known={line.split('  ',1)[1]:line.split('  ',1)[0]for line in f.read_text().splitlines()};known.update({str((P/row['path']).relative_to(PUBLIC)):row['SHA256']for row in parts});f.write_text(''.join(digest+'  '+path+'\n'for path,digest in sorted(known.items())))
def verify_and_offload(P,git,commit,parts,metadata_directory):
 for row in parts:
  blob=subprocess.check_output(['git','-C',str(P),'show',commit+':'+row['path']]);assert hashlib.sha256(blob).hexdigest()==row['SHA256']and len(blob)==row['bytes']
 directory=Path(metadata_directory);directory.mkdir(exist_ok=False);out=directory/'structural.pack';ids=[line.split()[0]for line in subprocess.check_output(['git','--no-lazy-fetch','-C',str(P),'rev-list','--objects','--filter=blob:none','--missing=allow-promisor','origin/main'],text=True).splitlines()]
 with out.open('wb')as f:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(ids)+'\n').encode(),stdout=f,check=True)
 ph=subprocess.check_output(['git','index-pack',str(out)],text=True).strip();target=P/'.git/objects/pack'/('pack-'+ph);Path(str(target)+'.promisor').touch()
 for suffix in ['.pack','.idx']:shutil.copyfile(out.with_suffix(suffix),str(target)+suffix);out.with_suffix(suffix).unlink()
 for row in parts:
  oid=row['OID'];loose=P/'.git/objects'/oid[:2]/oid[2:]
  if loose.exists():
   raw=zlib.decompress(loose.read_bytes());assert hashlib.sha1(raw).hexdigest()==oid and hashlib.sha256(raw.split(b'\0',1)[1]).hexdigest()==row['SHA256'];loose.unlink()
 subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL)
