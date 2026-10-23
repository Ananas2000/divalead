from pathlib import Path
import argparse,hashlib,json,zipfile
p=argparse.ArgumentParser();p.add_argument('--ready',required=True);a=p.parse_args();ready=Path(a.ready);choice=json.loads(ready.read_text());base=Path(choice['native_base_export_directory'])
for name in ['README_RU.md','FL_STUDIO_RU.md']:(base/name).write_text('Internal native base for the full native+ZL chain. It is not the recommended standalone sound. Restore the full public ZL kit for FL Studio use.\n')
files=sorted(p for p in base.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(base/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(base).as_posix()+'\n'for p in files))
archive=base.with_name(base.name+'-verified-base.zip');assert not archive.exists()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted(base.rglob('*')):
  if p.is_file():z.write(p,base.name+'/'+p.relative_to(base).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in base.rglob('*'):
  if p.is_file():assert z.read(base.name+'/'+p.relative_to(base).as_posix())==p.read_bytes()
choice.update(native_base_archive_path=str(archive),native_base_archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest());ready.write_text(json.dumps(choice,indent=2)+'\n');print('VERIFIED_NATIVE_BASE_ARCHIVE_READY',archive,choice['native_base_archive_SHA256'],flush=True)
