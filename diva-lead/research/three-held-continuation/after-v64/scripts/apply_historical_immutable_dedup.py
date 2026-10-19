"""Share exact duplicate completed historical WAVs; retain paths and every byte."""
from pathlib import Path
import os,json,hashlib,shutil,time
R=Path(__file__).resolve().parent
plan=json.loads((R/'historical-immutable-dedup-plan.json').read_text())
ledger=R/'historical-immutable-audio-dedup.json'
entries=json.loads(ledger.read_text()) if ledger.exists() else []
before=shutil.disk_usage(R).free;changed=0
for row in plan['files']:
 p=Path(row['path']);master=Path(row['immutable_master'])
 if not p.is_file() or not master.is_file():continue
 if p.samefile(master):continue
 assert (p.parent/'validation.json').is_file() and (master.parent/'validation.json').is_file()
 assert time.time()-max(p.stat().st_mtime,p.stat().st_ctime)>1800
 assert p.stat().st_dev==master.stat().st_dev
 content=p.read_bytes();assert content==master.read_bytes()
 assert hashlib.sha256(content).hexdigest()==row['SHA256']
 temporary=p.with_name(p.name+'.immutable-share-tmp');assert not temporary.exists()
 os.link(master,temporary);os.replace(temporary,p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256']
 entries.append(dict(row,content_unchanged=True,copy_to_independent_inode_before_any_in_place_edit=True))
 tmp=ledger.with_suffix('.tmp');tmp.write_text(json.dumps(entries,indent=2)+'\n');tmp.replace(ledger);changed+=1
print(json.dumps(dict(immutable_WAV_paths_shared=changed,all_paths_and_SHA_preserved=True,free_bytes_before=before,free_bytes_after=shutil.disk_usage(R).free)))
