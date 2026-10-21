"""Losslessly archive only dominated pre-v50 derived comparison-cache WAVs."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tarfile
R=Path('/workspace/divalead-work/all-repository-selection');N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects');P=Path('/workspace/divalead')
archive_root=R/'archived-dominated-canonical';archive_root.mkdir(exist_ok=True)
rank=json.loads((R/'ranking.json').read_text());selected=[]
for row in rank['results']:
 aliases=row.get('aliases',[]);path=Path(row['canonical_path'])
 if row.get('pareto_dominated') and row.get('weighted_score',0)>=1.2 and aliases and all(3<=a.get('version',1000)<50 and a.get('version')!=8 for a in aliases):
  if path.is_file() and not path.is_symlink() and path.parent==R/'canonical' and path.stat().st_nlink==1:selected.append((row,path))
selected.sort(key=lambda v:v[0]['weighted_score'],reverse=True);selected=selected[:80]
head=subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip();before=shutil.disk_usage('/workspace').free;batches=[]
for i in range(0,len(selected),8):
 group=selected[i:i+8];name=f'old-dominated-canonical-{os.getpid()}-{i//8:02d}.tar.gz';temp=W/name;records=[]
 for row,path in group:
  st=path.stat();records.append(dict(candidate=row['id'],original_path=str(path),member=path.name,bytes=st.st_size,SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),weighted_score=row['weighted_score'],pareto_dominated=True,aliases=row['aliases'],mtime_ns=st.st_mtime_ns))
 with tarfile.open(temp,'w:gz',compresslevel=6) as archive:
  for _,path in group:archive.add(path,arcname=path.name,recursive=False)
 with tarfile.open(temp,'r:gz') as archive:
  assert set(archive.getnames())=={r['member'] for r in records}
  for r in records:assert hashlib.sha256(archive.extractfile(r['member']).read()).hexdigest()==r['SHA256']
 if temp.stat().st_size+64*1024**2>=shutil.disk_usage('/workspace').free:raise RuntimeError('Bounded archive would invade actual native-search reserve')
 target=archive_root/name;assert not target.exists();shutil.copyfile(temp,target);assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(temp.read_bytes()).digest()
 with tarfile.open(target,'r:gz') as archive:
  for r in records:assert hashlib.sha256(archive.extractfile(r['member']).read()).hexdigest()==r['SHA256']
 receipt=dict(archive=str(target),archive_SHA256=hashlib.sha256(target.read_bytes()).hexdigest(),files=records,all_decompressed_bytes_verified=True,only_derived_comparison_cache=True)
 (archive_root/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
 for r in records:
  path=Path(r['original_path']);assert path.stat().st_nlink==1 and path.stat().st_mtime_ns==r['mtime_ns'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['SHA256'];path.unlink()
 batches.append(receipt);print('DOMINATED_CACHE_BATCH_LOSSLESS_ARCHIVED',i//8,len(records),sum(r['bytes'] for r in records),target.stat().st_size,flush=True)
assert subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip()==head
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Only derived canonical cache copies of dominated versions3..49, score>=1.2; version8, all3-note>=57 and all released WAVs/presets/ZIPs untouched',archived_WAVs=sum(len(b['files']) for b in batches),all_paths_recoverable_from_per_batch_receipts=True,all_models_scores_source_presets_retained=True,all_decompressed_SHA256_verified=True,actual_free_bytes_before=before,actual_free_bytes_after=shutil.disk_usage('/workspace').free,HEAD_unchanged=head,batches=batches)
(N/'DOMINATED_OLD_CANONICAL_LOSSLESS_ARCHIVING.json').write_text(json.dumps(report,indent=2)+'\n');print('OLD_CANONICAL_STORAGE_RECOVERY',report['archived_WAVs'],report['actual_free_bytes_after']-before,flush=True)
