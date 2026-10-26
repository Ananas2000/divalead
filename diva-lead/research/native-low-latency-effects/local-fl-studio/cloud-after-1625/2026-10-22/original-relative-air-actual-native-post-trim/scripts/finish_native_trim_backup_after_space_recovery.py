"""Finish this task's staged, verified archive without repacking or losing audio."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
H=Path(__file__).resolve().parent;OLD=H.with_name('stereo-refinement-20261025');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='recover_native_trim_backup');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git,read=h['git'],h['read'];label='original-relative-air-actual-native-post-trim';Q=H/'RELATIVE_AIR_NATIVE_POST_TRIM';dest=PUBLIC/label;archive=Path('/tmp')/(label+'_ALL_RETAINED_STUDY_FILES.tar.gz');manifest=read(dest/(archive.name+'.ARCHIVE_MANIFEST.json'));assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['original_SHA256'];pause=C/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='complete own staged full native trim archive after moving regenerable outer copy off full root'),f)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);scope=dest.relative_to(P).as_posix()+'/'
  for args in [('diff','--cached','--name-only'),('diff','--name-only'),('ls-files','--others','--exclude-standard')]:assert all(p.startswith(scope)for p in git(*args).splitlines())
  h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  for row in manifest['parts']:
   assert git('rev-parse',':'+row['path'])==row['OID'];blob=subprocess.check_output(['git','-C',str(P),'show',':'+row['path']]);assert len(blob)==row['bytes']and hashlib.sha256(blob).hexdigest()==row['SHA256']
  for p in Q.iterdir():
   if p.is_file()and p.suffix in['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):assert(dest/p.name).read_bytes()==p.read_bytes()
  scripts=dest/'scripts';scripts.mkdir(exist_ok=True)
  for name in ['native_post_trim.py','probe_actual_native_post_trim_verified.py','study_relative_air_native_post_trim_original.py','relative_air_native_trim_support.py','finish_native_trim_backup_after_space_recovery.py']:shutil.copyfile(H/name,scripts/name)
  shutil.copyfile(OLD/'backup_complete_finite_study.py',scripts/'backup_complete_finite_study.py')
  (dest/'README_RU.md').write_text('''# Реальная native-коррекция после двух ZL: проверка пройдена, полного комплекта ещё нет

Новый относительный PRIMARY и небольшое ослабление левого канала настоящим
Fruity Stereo Shaper после двух ZL. На12новыхпарах прошли исходный критерий,
first6ANDfirst10/3SEM, cold2, более строгий верхний stereoRMSпредел1.48,
сохранение lowmid и ограничение избытка воздуха. Полного совпадения нет.
До независимой проверки и полного FL20 ZIP этот результат не принят в BEST.

Все реальные WAV, состояния, калибровка и код серии сохранены в ordinaryGit.
ARCHIVE_MEMBER_SHA256.json описывает записи, ARCHIVE_MANIFEST задаёт сборку
48MiBparts. Байты не изменены. При первом сохранении закончился корневой диск
после успешного помещения всех частей вGitindex. Проверенную внешнюю временную
копию перенесли в/tmp, завершили тот же архив и push без повторного рендера.
Исходные WAV и выбранные компоненты сохранены.
''')
  from bounded_git_audio_backup import finish_manifest,verify_and_offload
  finish_manifest(h,dest,manifest['parts']);git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve complete passed actual native post-trim study and recover bounded-space backup');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);verify_and_offload(P,git,commit,manifest['parts'],H/'native-trim-recovery-public-structural-cache')
  members={r['name']:r for r in read(dest/'ARCHIVE_MEMBER_SHA256.json')};evicted=[]
  for p in Q.glob('*WAVs.tar.gz'):
   row=members[p.name];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];p.unlink();evicted.append(row)
  archive.unlink();assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),all_retained_study_files_and_WAVs_remote_Git_verified=True,all_selected_WAVs_and_states_retained=True,only_verified_private_validation_archive_duplicates_evicted=evicted,local_audio_retained=True,not_adopted=True,reference_match_reached=False,recovered_from_root_disk_full_without_losing_audio=True);(OLD/(label+'_PUBLICATION.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='only_verified_private_validation_archive_duplicates_evicted'}),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
