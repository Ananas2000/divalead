"""Restore exact fixed inputs and later interrupted snapshots from verified Git archives."""
from pathlib import Path
import datetime,hashlib,json,shutil,tarfile,urllib.request
V=Path(__file__).resolve().parent;P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22';ROOT=Path('/tmp/divalead-OS-local17-joint109-left004-current39-20261031');CACHE=Path('/tmp/divalead-recovery-20261104');CACHE.mkdir();ROOT.mkdir();reports=[]

def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def download(row,commit,dest):
 rel=row['path'];assert rel.startswith('diva-lead/research/')and '..'not in Path(rel).parts;assert len(commit)==40 and all(c in'0123456789abcdef'for c in commit)
 url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+rel;temp=dest.with_suffix(dest.suffix+'.partial');h=hashlib.sha256();size=0
 with urllib.request.urlopen(url,timeout=60)as response,temp.open('wb')as out:
  while block:=response.read(1024*1024):out.write(block);h.update(block);size+=len(block)
 assert size==row['bytes']and h.hexdigest()==row['SHA256'];temp.rename(dest)

for label,commit in [('original-OS-local17-joint109-left004-live-snapshot-20261031','21a8ce34080ce2af3652a8c122bd990b9e853560'),('original-OS-local17-native-joint109-left004-interrupted-20261031','dc5ee50eca63062963453050c3218c8f11ebdb0b')]:
 folder=PUBLIC/label;manifest_path=next(folder.glob('*.ARCHIVE_MANIFEST.json'));manifest=json.loads(manifest_path.read_text());members=json.loads((folder/'ARCHIVE_MEMBER_SHA256.json').read_text());whole=CACHE/manifest['original_filename']
 with whole.open('wb')as out:
  for k,row in enumerate(manifest['parts']):
   part=CACHE/(label+'-part-'+str(k));download(row,commit,part)
   with part.open('rb')as f:shutil.copyfileobj(f,out)
   part.unlink()
 assert whole.stat().st_size==manifest['original_bytes']and sha(whole)==manifest['original_SHA256'];expected={r['name']:r for r in members};count=0
 with tarfile.open(whole)as archive:
  entries=archive.getmembers();assert [m.name for m in entries]==[r['name']for r in members]
  for m in entries:
   rel=Path(m.name);assert m.isreg()and not rel.is_absolute()and '..'not in rel.parts;target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);assert m.size==expected[m.name]['bytes'];temp=target.with_name(target.name+'.recovering')
   with archive.extractfile(m)as source,temp.open('wb')as out:shutil.copyfileobj(source,out)
   assert sha(temp)==expected[m.name]['SHA256'];temp.replace(target);count+=1
 reports.append(dict(public_label=label,commit=commit,archive_SHA256=manifest['original_SHA256'],all_member_bytes_verified=True,files_restored=count))
progress=json.loads((ROOT/'PROGRESS_NOT_ADOPTED.json').read_text());proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(ROOT),archives=reports,recovered_recorded_training_cases=progress['training_cases'],recovered_training_loss=progress['selected']['loss'],original_study_interrupted_not_complete=True,recovered_candidate_not_adopted=True,original_three_incoming_notes_and_reference_only=True,reference_match_reached=False);(V/'INTERRUPTED_OS_LOCAL17_DATA_RESTORED.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
