"""Remote-back up closed historical derived A/B archives before local eviction."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,tarfile
H=Path(__file__).resolve().parent;OLD=H.parent/'all-repository-selection/archived-historical-AB';O=H.parent/'stereo-refinement-20261025';R=H/'OLD_DERIVED_AB_REMOTE_BACKUP_20261028_BATCH02';R.mkdir();opened=set();rows=[];total=0
for fd in Path('/proc').glob('[0-9]*/fd/*'):
 try:opened.add(fd.resolve())
 except(OSError,RuntimeError):pass
for meta in sorted(OLD.glob('*.tar.gz.json')):
 d=json.loads(meta.read_text());p=Path(d['archive'])
 if not p.is_file()or p.resolve()in opened:continue
 assert d['derived_AB_cache_only']and d['all_decompressed_bytes_verified'];blob=p.read_bytes();assert hashlib.sha256(blob).hexdigest()==d['archive_SHA256']
 with tarfile.open(p)as tar:
  for row in d['files']:
   member=tar.extractfile(row['member']).read();assert len(member)==row['bytes']and hashlib.sha256(member).hexdigest()==row['SHA256']
 os.link(p,R/p.name);(R/meta.name).write_bytes(meta.read_bytes());rows.append(dict(original_archive=str(p),original_metadata=str(meta),archive_name=p.name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()));total+=len(blob)
 if total>=64*2**20:break
assert rows
(R/'ORIGINAL_LOCATION_AND_SHA256.json').write_text(json.dumps(rows,indent=2)+'\n');(R/'backup_and_release_old_derived_AB_batch.py').write_bytes(Path(__file__).read_bytes())
label='recoverable-old-derived-AB-cache-batch02-20261028'
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(O/'backup_complete_finite_study.py'),'--root',str(R),'--label',label,'--note','Архив для освобождения локального места, НЕ новый подбор и НЕ кандидат. Сохранены точные ранее lossless-архивированные старые производные A/B сравнения и их исходные manifest/метаданные. Каждый вложенный WAV и каждый исходный TAR проверены по SHA256 до загрузки. Все actual candidate/source WAV, состояния, нынешние 404/37, оригинал и прежние публичные версии оставлены. Исходные закрытые private TAR удаляются только после полной удалённой проверки этой ordinaryGit копии; ORIGINAL_LOCATION_AND_SHA256.json задаёт прежние пути.'],check=True)
receipt=json.loads((O/(label+'_PUBLICATION.json')).read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified'];freed=0
for row in rows:
 p=Path(row['original_archive']);assert p.is_file()and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];meta=Path(row['original_metadata']);d=json.loads(meta.read_text());assert d['archive_SHA256']==row['SHA256'];d['remote_verified_lossless_archive_recovery']=dict(commit=receipt['commit'],public_path=receipt['public_path'],archive_member=row['archive_name'],original_location=str(p),original_SHA256=row['SHA256']);d['local_archive_copy_evicted_after_complete_remote_byte_proof']=True;meta.write_text(json.dumps(d,indent=2)+'\n');p.unlink();freed+=row['bytes']
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),freed_bytes=freed,commit=receipt['commit'],public_path=receipt['public_path'],only_old_derived_AB_private_archives_released=True,all_candidate_source_current_original_WAVs_and_states_preserved=True,rows=rows);(H/'OLD_DERIVED_AB_REMOTE_VERIFIED_LOCAL_RELEASE_20261028_BATCH02.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
