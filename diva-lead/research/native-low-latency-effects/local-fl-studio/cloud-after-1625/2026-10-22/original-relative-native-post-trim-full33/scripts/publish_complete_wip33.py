"""Publish actual cold-verified native13/two-ZL WIP and complete FL20 instructions."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;OLD=H.with_name('stereo-refinement-20261025');Q=H/'RELATIVE_AIR_NATIVE_POST_TRIM';A=Path('/workspace/divalead-work/pc-stereo-20261024');h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_native13_full33');P,N,R,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL33_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);s=read(Q/'completion.json');proof=read(OLD/'original-relative-air-actual-native-post-trim_PUBLICATION.json');assert s['robust_improvement']and proof['all_retained_study_files_and_WAVs_remote_Git_verified'];assert build['actual_two_cold_ZL_replay_errors']==[0.,0.]and build['actual_two_cold_full_native_trim_chain_errors']==[0.,0.];assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish complete actual native13 two-ZL WIP33, independently cold-replayed from ZIP'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Preserve another active publisher')
  time.sleep(.5)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP33';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-relative-native-post-trim-full33';research.mkdir()
  for p in Q.iterdir():
   if p.is_file()and p.suffix in['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for name in['ZL33_BUILD_COMPLETION.json','VERIFIED_OLD_LOCAL_KIT_ZIP_CACHE_RELEASE.json','VERIFIED_REJECTED_RELATIVE_ARCHIVE_DUPLICATES_RELEASE.json','CLOUD_START_DRAFT_RECEIPT.json']:shutil.copyfile(H/name,research/name)
  shutil.copyfile(OLD/'original-relative-air-actual-native-post-trim_PUBLICATION.json',research/'ALL_REAL_WAV_AND_FILES_PUBLICATION.json');shutil.copyfile(H/'ACTUAL_NATIVE_POST_TRIM_PROBE_VERIFIED/RESULTS.json',research/'ACTUAL_NATIVE_STEREO_SHAPER_CALIBRATION.json')
  scripts=research/'scripts';scripts.mkdir()
  for name in['build_complete_original_wip33.py','publish_complete_wip33.py','adopt_and_check_full33_runtime.py','start_actual_full33_original_target_continuation.py','native_post_trim.py','probe_actual_native_post_trim_verified.py','study_relative_air_native_post_trim_original.py','relative_air_native_trim_support.py','finish_native_trim_backup_after_space_recovery.py','offload_old_verified_local_kit_ZIPs.py','check_current_original_chain_readiness.py','start_native_headless_display.py']:shutil.copyfile(H/name,scripts/name)
  runtime=research/'current-runtime';runtime.mkdir()
  for name in['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
  shutil.copyfile('/tmp/divalead-local-1625/fl20_curve.py',runtime/'fl20_curve.py');shutil.copyfile(OLD/'normal_real_ZL_refit.py',runtime/'normal_real_ZL_refit.py');shutil.copyfile(OLD/'backup_complete_finite_study.py',runtime/'backup_complete_finite_study.py');shutil.copyfile(OLD/'bounded_git_audio_backup.py',runtime/'bounded_git_audio_backup.py')
  intro='''# ZL33 WIP — относительная динамика и штатный Stereo Shaper после EQ

- [Полный ZIP FL20](ZL-WIP33/Diva_ZL33_STEREO_WIP_complete.zip).
- [A/B: оригинал → ZL32 → ZL33](ZL-WIP33/AB_ORIGINAL_ZL32_ZL33_WIP.mp3).
- [Lossless A/B](ZL-WIP33/AB_ORIGINAL_ZL32_ZL33_WIP.flac).
- [Инструкция FL Studio](ZL-WIP33/FL_STUDIO_RU.md).
- [Все реальные WAV и данные проверки](original-relative-air-actual-native-post-trim/README_RU.md).

Полного совпадения нет. Подтверждено небольшое улучшение исходного критерия
на12новыхпарах с сохранением чистоты и более строгой границей верхнего
стереобаланса. ДВАZL и13nativeэффектов; новый nativeStereoShaper стоит
ПОСЛЕ второгоZL. Сохранены три длинные входящие ноты, источникDiva/ARP/ADSR,
WS52/исходные12native и POST32. Подробности и ограничения ниже.

'''
  doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL33_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP33/','](../ZL-WIP33/').replace('](original-relative-air-','](../original-relative-air-'))
  p=PUBLIC/'README_RU.md';p.write_text('[ZL33: полный native13/two-ZL комплект, WAV/A-B и инструкция FL20](ZL33_CONTINUATION_RU.md).\n\n'+p.read_text())
  prior=H/'PRIOR_START_SKILL_BEFORE_CONDENSED_ZL33.md'
  if not prior.exists():shutil.copyfile(R/'start_skill_current.md',prior)
  startup=(H/'cloud_start_current.md').read_text();(R/'start_skill_current.md').write_text(startup);shutil.copyfile(R/'start_skill_current.md',h['BASE']/'start_skill_current.md');(research/'CLOUD_START_CURRENT.md').write_text(startup)
  (research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL33 WIP with actual native post-trim, FL20 kit and current runtime');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[]
  for p in[dest/archive.name,dest/'AB_ORIGINAL_ZL32_ZL33_WIP.mp3',dest/'FL_STUDIO_RU.md',runtime/'native_post_trim.py',research/'CLOUD_START_CURRENT.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP33',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='10',original_native12_plus_native_post_trim=True,native_trim_state_SHA256=build['post_trim_state_SHA256'],all_training_validation_WAVs_and_files_remote_verified_in_prior_backup=True,prior_backup_commit=proof['commit'],two_cold_actual_full_chain_replays=[0.,0.],HTTP_checks=checks,all_old_kits_history_PC_GUI_private_refs_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(H/'ZL33_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
