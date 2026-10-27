"""Publish actual cold-verified native13/two-ZL WIP and complete FL20 instructions."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;OLD=H.with_name('stereo-refinement-20261025');Q=H/'MID_SIDE_PHASE_JOINT35';A=Path('/workspace/divalead-work/pc-stereo-20261024');h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_native13_full36');P,N,R,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL36_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);s=read(Q/'completion.json');proof=read(OLD/'original-Mid-Side-phase-joint35_PUBLICATION.json');assert s['robust_improvement']and proof['all_retained_study_files_and_WAVs_remote_Git_verified'];assert build['actual_two_cold_ZL_replay_errors']==[0.,0.]and build['actual_two_cold_full_native_trim_chain_errors']==[0.,0.];assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish complete actual native13 two-ZL WIP36, independently cold-replayed from ZIP'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Preserve another active publisher')
  time.sleep(.5)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);previous_full33=git('rev-parse','HEAD:'+str((PUBLIC/'ZL-WIP33').relative_to(P)))
  dest=PUBLIC/'ZL-WIP36';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-joint-phase-full36';research.mkdir()
  for p in Q.iterdir():
   if p.is_file()and p.suffix in['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for name in['ZL36_BUILD_COMPLETION.json','FULL35_INPUT_AND_COLD_PROOF.json','VERIFIED_MID_AP5_POSITIVE_AUXILIARY_WAV_RELEASE.json','CLOUD_FULL34_DRAFT_RECEIPT_20261027.json']:shutil.copyfile(H/name,research/name)
  shutil.copyfile(OLD/'original-Mid-Side-phase-joint35_PUBLICATION.json',research/'ALL_REAL_WAV_AND_FILES_PUBLICATION.json');shutil.copyfile(H/'ACTUAL_NATIVE_POST_TRIM_PROBE_VERIFIED/RESULTS.json',research/'ACTUAL_NATIVE_STEREO_SHAPER_CALIBRATION.json')
  scripts=research/'scripts';scripts.mkdir()
  for name in['build_complete_original_wip36.py','publish_complete_wip36.py','adopt_and_check_full36_runtime.py','start_actual_full36_original_target_continuation.py','native_post_trim.py','probe_actual_native_post_trim_verified.py','study_Mid_Side_phase_joint35_original.py','Mid_Side_phase_joint35_support.py','prepare_full36_inputs_and_cold_proof.py','check_current_original_chain_readiness.py','start_native_headless_display.py']:shutil.copyfile(H/name,scripts/name)
  runtime=research/'current-runtime';runtime.mkdir()
  for name in['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
  shutil.copyfile('/tmp/divalead-local-1625/fl20_curve.py',runtime/'fl20_curve.py');shutil.copyfile(OLD/'normal_real_ZL_refit.py',runtime/'normal_real_ZL_refit.py');shutil.copyfile(OLD/'backup_complete_finite_study.py',runtime/'backup_complete_finite_study.py');shutil.copyfile(OLD/'bounded_git_audio_backup.py',runtime/'bounded_git_audio_backup.py')
  intro='''# ZL36 WIP — совместная настройка Mid/Side-фазы

- [Полный ZIP FL20](ZL-WIP36/Diva_ZL36_STEREO_WIP_complete.zip).
- [A/B: оригинал → принятый353на35 →36](ZL-WIP36/AB_ORIGINAL_353_ZL36_WIP.mp3).
- [Lossless A/B](ZL-WIP36/AB_ORIGINAL_353_ZL36_WIP.flac).
- [Инструкция FL Studio](ZL-WIP36/FL_STUDIO_RU.md).
- [Все реальные WAV/данные](original-Mid-Side-phase-joint35/README_RU.md).

Полного совпадения нет. Небольшое улучшение исходного критерия подтверждено12новымипарами, с дополнительным приближением lowmid/верхнего L/Rбаланса к оригиналу. Источник Diva/три длинные входящие ноты/ARP/ADSR/native12/WS52/позднийnativeTrim сохранены. PRIMARY — уже принятый353, POST изменён только по частоте/Q существующих фазовых полос. Всего13native и2ZL. Точные настройки и ограничения ниже.

'''
  doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL36_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP36/','](../ZL-WIP36/').replace('](original-relative-air-','](../original-relative-air-'))
  p=PUBLIC/'README_RU.md';p.write_text('[ZL36: полный native13/two-ZL комплект, WAV/A-B и инструкция FL20](ZL36_CONTINUATION_RU.md).\n\n'+p.read_text())
  prior=H/'PRIOR_START_SKILL_BEFORE_CONDENSED_ZL36.md'
  if not prior.exists():shutil.copyfile(R/'start_skill_current.md',prior)
  startup=(H/'cloud_start_current.md').read_text();(R/'start_skill_current.md').write_text(startup);shutil.copyfile(R/'start_skill_current.md',h['BASE']/'start_skill_current.md');(research/'CLOUD_START_CURRENT.md').write_text(startup)
  (research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL36 WIP with actual native post-trim, FL20 kit and current runtime');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;assert git('rev-parse','HEAD:'+str((PUBLIC/'ZL-WIP33').relative_to(P)))==previous_full33;h['push_and_confirm'](commit)
  checks=[]
  for p in[dest/archive.name,dest/'AB_ORIGINAL_353_ZL36_WIP.mp3',dest/'FL_STUDIO_RU.md',runtime/'native_post_trim.py',research/'CLOUD_START_CURRENT.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP36',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='10',original_native12_plus_native_post_trim=True,native_trim_state_SHA256=build['post_trim_state_SHA256'],all_training_validation_WAVs_and_files_remote_verified_in_prior_backup=True,prior_backup_commit=proof['commit'],two_cold_actual_full_chain_replays=[0.,0.],HTTP_checks=checks,all_old_kits_history_PC_GUI_private_refs_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(H/'ZL36_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
