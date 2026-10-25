"""Publish finite study in <=32MiB raw-audio batches without filling workspace."""
from pathlib import Path
import argparse,datetime,fcntl,gzip,hashlib,io,json,os,runpy,shutil,tarfile
from bounded_git_audio_backup import stage_archive,finish_manifest,verify_and_offload
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');a=argparse.ArgumentParser();a.add_argument('--root',required=True);a.add_argument('--label',required=True);a.add_argument('--note',required=True);args=a.parse_args();root=Path(args.root)
summary=json.loads((root/'completion.json').read_text());assert not summary['robust_improvement']
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='bounded_complete_rejected_source_study');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023';dest=PUBLIC/args.label;allparts=[];done=[]
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='bounded complete source study backup, each verified chunk released before next'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest.mkdir();metadata=dest/'metadata';metadata.mkdir()
  for p in sorted(root.rglob('*')):
   if p.is_file()and p.suffix not in ['.wav','.f32','.exe','.dll']and not p.name.endswith('.tar.gz'):
    out=metadata/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix in ['.tsv','.log']:out=out.with_name(out.name+'.gz');out.write_bytes(gzip.compress(p.read_bytes(),mtime=0))
    else:shutil.copyfile(p,out)
  scripts=dest/'scripts';scripts.mkdir()
  for p in H.glob('*.py'):
   if any(t in p.name for t in ['Diva_source_wide','backup_large_study','bounded_git']):shutil.copyfile(p,scripts/p.name)
  def commit_one(archive,members,private_audio,number):
   assert shutil.disk_usage('/workspace').free>128*2**20
   manifest=stage_archive(P,git,archive,dest);allparts.extend(manifest['parts']);(dest/(archive.name+'.MEMBER_SHA256.json')).write_text(json.dumps(members,indent=2)+'\n')
   note='# Отклонённое исследование: поэтапный полный бэкап\n\n'+args.note+'\n\nНи один кандидат этой серии не принят. Оригинал — единственная цель, v83/Finish не цель и не эффект. Три длинные входящие ноты/ARP/ADSR сохранены. Ни GUIэкспорта, ни полного совпадения не заявляется.\n\nАрхивы идут отдельными партиями с memberSHA и ARCHIVE_MANIFEST для точной сборки parts. Метаданные/пресеты/состояния/281/MIDIаудиты/логи в metadata. Каждая завершённая партия проверена в опубликованном Git до удаления её локальных WAVдубликатов.\n'
   (dest/'README_RU.md').write_text(note+f'\nЗавершено партий: {number}. Полный бэкап ещё не завершён, пока BACKUP_COMPLETE.json отсутствует.\n');finish_manifest(h,dest,allparts);git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve '+args.label+' actual audio batch '+str(number));commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);verify_and_offload(P,git,commit,manifest['parts'],H/(args.label+'-public-cache-'+str(number)))
   for row,p in private_audio:
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];p.unlink()
   if archive.exists():archive.unlink()
   done.append(dict(number=number,commit=commit,archive=manifest,member_count=len(members)));(H/(args.label+'_PROGRESS.json')).write_text(json.dumps(done,indent=2)+'\n');assert not git('status','--porcelain');print('VERIFIED_BATCH',number,commit,flush=True)
  number=0
  for archive in sorted(root.glob('*.tar.gz')):
   number+=1;members=[]
   with tarfile.open(archive)as tar:
    for entry in tar:
     if entry.isfile():b=tar.extractfile(entry).read();members.append(dict(name=entry.name,SHA256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
   commit_one(archive,members,[],number)
  wavs=sorted(p for p in root.rglob('*.wav')if p.is_file());batches=[];batch=[];size=0
  for p in wavs:
   if batch and size+p.stat().st_size>32*2**20:batches.append(batch);batch=[];size=0
   batch.append(p);size+=p.stat().st_size
  if batch:batches.append(batch)
  for files in batches:
   number+=1;archive=H/(args.label+f'_AUDIO_BATCH_{number:03d}.tar.gz');assert not archive.exists();members=[];private=[]
   with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
    for p in files:
     b=p.read_bytes();name=p.relative_to(root).as_posix();row=dict(name=name,SHA256=hashlib.sha256(b).hexdigest(),bytes=len(b));members.append(row);private.append((row,p));entry=tarfile.TarInfo(name);entry.size=len(b);tar.addfile(entry,io.BytesIO(b))
   with tarfile.open(archive)as tar:
    for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
   commit_one(archive,members,private,number)
  report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_original_remaining_study_WAVs_and_existing_validation_archives_remote_Git_verified=True,study_not_adopted=True,reference_match_reached=False,batches=done)
  (dest/'BACKUP_COMPLETE.json').write_text(json.dumps(report,indent=2)+'\n');p=dest/'README_RU.md';p.write_text(p.read_text().replace('Полный бэкап ещё не завершён, пока BACKUP_COMPLETE.json отсутствует.','Полный бэкап завершён; см. BACKUP_COMPLETE.json.'));finish_manifest(h,dest,allparts);git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Mark complete bounded '+args.label+' actual WAV backup');commit=git('rev-parse','HEAD');h['push_and_confirm'](commit);report['completion_commit']=commit;(H/(args.label+'_PUBLICATION.json')).write_text(json.dumps(report,indent=2)+'\n');print('ALL_BATCHES_COMPLETE',commit,flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
