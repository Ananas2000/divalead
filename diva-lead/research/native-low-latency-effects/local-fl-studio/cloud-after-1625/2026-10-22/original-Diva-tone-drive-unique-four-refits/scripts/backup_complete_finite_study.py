"""Back up a completed/aborted finite study losslessly; no result adoption."""
from pathlib import Path
import argparse,datetime,fcntl,gzip,hashlib,io,json,os,runpy,shutil,tarfile,time
from bounded_git_audio_backup import stage_archive,finish_manifest,verify_and_offload
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
a=argparse.ArgumentParser();a.add_argument('--root',required=True);a.add_argument('--label',required=True);a.add_argument('--note',required=True);a.add_argument('--retain-local-audio',action='store_true');args=a.parse_args();root=Path(args.root);assert root.is_dir()
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='finite_study_complete_backup');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
archive=H/(args.label+'_ALL_RETAINED_STUDY_FILES.tar.gz');assert not archive.exists();members=[]
with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
 for p in sorted(root.rglob('*')):
  if p.is_file()and p.suffix not in ['.f32','.dll','.exe']:
   b=p.read_bytes();name=p.relative_to(root).as_posix();info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()))
with tarfile.open(archive)as tar:
 for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish complete finite actual plugin study without adoption'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Another publisher still owns the Git pause; completed archive preserved for retry')
  time.sleep(.5)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/args.label;dest.mkdir()
  for p in root.iterdir():
   if p.is_file()and p.suffix in ['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,dest/p.name)
  (dest/'ARCHIVE_MEMBER_SHA256.json').write_text(json.dumps(members,indent=2)+'\n');manifest=stage_archive(P,git,archive,dest);scripts=dest/'scripts';scripts.mkdir()
  for p in H.glob('*.py'):
   if any(token in p.name for token in ['Diva','divine','coadapt','normal_real','backup_complete','bounded_git']):shutil.copyfile(p,scripts/p.name)
  (dest/'README_RU.md').write_text('# Исследование сохранено, результат не принят\n\n'+args.note+'\n\nАрхив содержит все оставшиеся реальные source/processed/native WAV, пресеты, состояния, all281/MIDIаудиты, логи и метаданные этой серии. Если в нём вложен validationWAVs.tar.gz, он сохранён побитово и содержит дополнительные WAV. Только восстановимые .f32 scratchдубликаты не включены. ARCHIVE_MEMBER_SHA256.json перечисляет каждую запись; ARCHIVE_MANIFEST.json задаёт точную сборку из48MiBparts. Всё ordinaryGit, без измененияаудио. Это не новый готовый звук. Основной полный комплект указан в текущем публичном README; цель — исходныйоригинал, три длинные входящие ноты на фразу и normalnative/twoZLобработка.\n')
  finish_manifest(h,dest,manifest['parts']);git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve complete finite '+args.label+' actual plugin study without adoption');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);verify_and_offload(P,git,commit,manifest['parts'],H/(args.label+'-public-structural-cache'))
  # Remove only byte-verified public copies of closed study audio/archives.
  freed=[]
  for row in members:
   p=root/row['name']
   if not args.retain_local_audio and(p.suffix=='.wav'or p.name.endswith('.tar.gz')):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];freed.append(row);p.unlink()
  archive.unlink();assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),all_retained_study_files_and_WAVs_remote_Git_verified=True,evicted_private_copies=freed,local_audio_retained=args.retain_local_audio,not_adopted=True,reference_match_reached=False);(H/(args.label+'_PUBLICATION.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='evicted_private_copies'}),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner and read(pause).get('PID')==os.getpid():pause.unlink()
