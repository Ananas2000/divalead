"""Preserve every actual Diva screening render losslessly in bounded archives."""
from pathlib import Path
import hashlib,io,json,tarfile
R=Path(__file__).resolve().parent;D=Path('/tmp/divalead-post78-dual-physical-archives');D.mkdir(exist_ok=False)
archives=[]
for tag in ['post78-dual']:
 S=Path('/tmp/divalead-source-'+tag);report=json.loads((S/'completed.json').read_text());n=report['trials']
 assert n==len(json.loads((S/'history.json').read_text()))
 for start in range(0,n,7):
  files=[]
  for i in range(start,min(start+7,n)):
   files.extend((p,'actual-Diva/'+str(p.relative_to(S))) for p in sorted((S/('trial-'+format(i,'03d'))).rglob('*')) if p.is_file())
  if start==0:files.extend((S/name,'actual-Diva/'+name) for name in ['history.json','completed.json'])
  path=D/(tag+'-trials-'+format(start,'02d')+'-'+format(min(start+6,n-1),'02d')+'.tar.gz');expected={};masters={}
  with tarfile.open(path,'w:gz',compresslevel=6) as tar:
   for p,name in files:
    content=p.read_bytes();digest=hashlib.sha256(content).hexdigest();expected[name]=digest;info=tarfile.TarInfo(name);info.mtime=0;key=(len(content),digest)
    if key in masters:
     info.type=tarfile.LNKTYPE;info.linkname=masters[key];tar.addfile(info)
    else:
     masters[key]=name;info.size=len(content);tar.addfile(info,io.BytesIO(content))
  with tarfile.open(path) as tar:
   assert set(tar.getnames())==set(expected)
   for member in tar:assert hashlib.sha256(tar.extractfile(member).read()).hexdigest()==expected[member.name]
  assert path.stat().st_size<50_000_000
  archives.append(dict(file=path.name,bytes=path.stat().st_size,SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),decompressed_members_SHA_verified=True,members=expected,screen_only_no_full_proof_claim=True))
manifest=dict(original_Diva_three_held_screening_trials=n,source_screen_only_not_complete_kit=True,all_render_bytes_retained=True,match_reached=False,archives=archives)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(archives=len(archives),trials=n,total_bytes=sum(r['bytes'] for r in archives),all_members_SHA_verified=True)),flush=True)
