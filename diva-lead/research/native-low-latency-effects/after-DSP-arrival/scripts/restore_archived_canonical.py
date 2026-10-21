"""Restore one explicitly named old derived cache WAV, preserving its exact bytes."""
from pathlib import Path
import hashlib,json,os,shutil,sys,tarfile
R=Path('/workspace/divalead-work/all-repository-selection');root=R/'archived-dominated-canonical';rows=[]
for p in sorted(root.glob('*.tar.gz.json')):
 d=json.loads(p.read_text())
 for row in d['files']:rows.append((d,row))
if len(sys.argv)!=2:
 print('Usage: restore_archived_canonical.py c123');print('Archived candidates:',', '.join(sorted(r['candidate'] for d,r in rows)));raise SystemExit(0)
selected=[(d,r) for d,r in rows if r['candidate']==sys.argv[1]];assert len(selected)==1
archive,row=selected[0];dest=Path(row['original_path']);assert dest.parent==R/'canonical'
if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==row['SHA256'];print('ALREADY_RESTORED_BYTE_EXACT',row['candidate']);raise SystemExit(0)
assert row['bytes']+16*1024**2<shutil.disk_usage('/workspace').free
path=Path(archive['archive']);assert hashlib.sha256(path.read_bytes()).hexdigest()==archive['archive_SHA256']
with tarfile.open(path,'r:gz') as tar:
 member=tar.getmember(row['member']);data=tar.extractfile(member).read()
assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA256']
temp=dest.with_suffix('.restoring');assert not temp.exists();temp.write_bytes(data);temp.chmod(member.mode);os.utime(temp,ns=(row['mtime_ns'],row['mtime_ns']));temp.replace(dest);print('RESTORED_BYTE_EXACT',row['candidate'])
