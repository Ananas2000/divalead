"""Restore selected or all exact historical cached WAVs from retained Git blobs."""
from pathlib import Path
import json,hashlib,sys,subprocess
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');rows=json.loads((R/'published-audio-cache-eviction.json').read_text())['files'];count=0
for row in rows:
 if len(sys.argv)>1 and sys.argv[1] not in row['path']:continue
 p=Path(row['path'])
 if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];continue
 master=REPO/row['repository_path']
 data=master.read_bytes() if master.is_file() and hashlib.sha256(master.read_bytes()).hexdigest()==row['SHA256'] else subprocess.check_output(['git','cat-file','blob',row['blob']],cwd=REPO)
 assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA256'];p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.restored-tmp');assert not tmp.exists();tmp.write_bytes(data);tmp.replace(p);count+=1
print('HISTORICAL_PUBLISHED_WAV_COPIES_RESTORED_BYTE_EXACT',count)
