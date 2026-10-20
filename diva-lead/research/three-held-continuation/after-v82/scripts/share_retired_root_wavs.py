"""Share only byte-identical, retired top-level WAVs; keep all paths and audio."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,time
R=Path(__file__).resolve().parent;B=R.parent
before=shutil.disk_usage(R).free;masters={};rows=[];scanned=0
for p in sorted(B.glob('*.wav')):
 if p.is_symlink() or not p.is_file():continue
 st=p.stat()
 if time.time()-max(st.st_mtime,st.st_ctime)<1800:continue
 data=p.read_bytes();h=hashlib.sha256(data).hexdigest();key=(len(data),h);scanned+=1
 if key not in masters:masters[key]=p;continue
 master=masters[key]
 if p.samefile(master):continue
 now=p.stat();assert (now.st_dev,now.st_ino,now.st_size,now.st_mtime_ns,now.st_ctime_ns)==(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns),str(p)
 assert data==master.read_bytes() and now.st_dev==master.stat().st_dev
 tmp=p.with_name(p.name+'.retired-exact-share-tmp');assert not tmp.exists()
 os.link(master,tmp);os.replace(tmp,p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 rows.append(dict(path=str(p),immutable_master=str(master),bytes=len(data),SHA256=h))
 if len(rows)%100==0:print('Shared retired exact WAV duplicates:',len(rows),flush=True)
d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),retired_WAVs_scanned=scanned,paths_shared=len(rows),all_paths_bytes_SHA_preserved=True,unique_audio_deleted=False,copy_to_independent_inode_before_future_edit=True,root_free_before=before,root_free_after=shutil.disk_usage(R).free,entries=rows)
(R/'post73-retired-root-WAV-sharing.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({k:v for k,v in d.items() if k!='entries'}),flush=True)
