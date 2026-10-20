from pathlib import Path
import os,json,hashlib,shutil
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ledger=R/'immutable-audio-dedup.json';entries=json.loads(ledger.read_text()) if ledger.exists() else []
before=shutil.disk_usage(R).free;files=[]
for p in R.rglob('*.wav'):
 parts=p.relative_to(R).parts
 if not p.is_file() or p.is_symlink():continue
 completed_proof=parts[0].startswith(('verified-','drift24-verified-','tslop0-verified-','pw5190-verified-','post74joint-verified-','post80plate68-verified-')) and (R/parts[0]/'validation.json').is_file()
 completed_build=parts[0].endswith('-build') and (R/parts[0]/'ZIP-proof.json').is_file() and (R/parts[0]/'clean-ZIP-Windows-proof.json').is_file()
 if parts[0]=='baseline' or parts[0]=='source-drift24-proof' or completed_proof or completed_build:files.append(p)
for folder in list((REPO/'diva-lead').glob('v*-wip'))+[REPO/'diva-lead/research/three-held-continuation']:
 files.extend(p for p in folder.rglob('*.wav') if p.is_file() and not p.is_symlink())
masters={};count=0;logical=0
for p in sorted(set(files),key=lambda p:(0 if 'baseline' in p.parts else 1,str(p))):
 data=p.read_bytes();key=(len(data),hashlib.sha256(data).hexdigest())
 if key not in masters:masters[key]=p;continue
 master=masters[key]
 if (p.stat().st_dev,p.stat().st_ino)==(master.stat().st_dev,master.stat().st_ino):continue
 assert p.stat().st_dev==master.stat().st_dev and p.read_bytes()==master.read_bytes()
 temporary=p.with_name(p.name+'.dedup-tmp');assert not temporary.exists();os.link(master,temporary);os.replace(temporary,p);assert hashlib.sha256(p.read_bytes()).hexdigest()==key[1]
 entries.append(dict(path=str(p),immutable_master=str(master),SHA256=key[1],bytes=key[0],content_unchanged=True,copy_to_independent_inode_before_any_in_place_edit=True));count+=1;logical+=key[0]
 temp=ledger.with_suffix('.tmp');temp.write_text(json.dumps(entries,indent=2)+'\n');temp.replace(ledger)
print(json.dumps(dict(immutable_duplicates_shared=count,logical_duplicate_bytes=logical,actual_workspace_free_bytes_before=before,actual_workspace_free_bytes_after=shutil.disk_usage(R).free,all_paths_and_SHA_preserved=True)))
