"""Publish actual cold-verified native13/two-ZL WIP and complete FL20 instructions."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;OLD=H.with_name('stereo-refinement-20261025');Q=H/'POST_AP6_JOINT_REFINEMENT36';A=Path('/workspace/divalead-work/pc-stereo-20261024');h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_native13_full37');P,N,R,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL37_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);s=read(Q/'completion.json');proof=read(OLD/'original-AP6-joint-refinement36-positive_PUBLICATION.json');assert s['robust_improvement']and proof['all_retained_study_files_and_WAVs_remote_Git_verified'];assert build['actual_two_cold_ZL_replay_errors']==[0.,0.]and build['actual_two_cold_full_native_trim_chain_errors']==[0.,0.];assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
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
  dest=PUBLIC/'ZL-WIP37';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-AP6-phase-full37';research.mkdir()
  for p in Q.iterdir():
   if p.is_file()and p.suffix in['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for name in['ZL37_BUILD_COMPLETION.json','FULL37_INPUT_AND_COLD_PROOF.json','GRADIENT36_REMOTE_VERIFIED_REMAINING_AUDIO_RELEASE_20261028.json','CLOUD_FULL37_DRAFT_RECEIPT_20261028.json']:shutil.copyfile(H/name,research/name)
  shutil.copyfile(OLD/'original-AP6-joint-refinement36-positive_PUBLICATION.json',research/'ALL_REAL_WAV_AND_FILES_PUBLICATION.json');shutil.copyfile(H/'ACTUAL_NATIVE_POST_TRIM_PROBE_VERIFIED/RESULTS.json',research/'ACTUAL_NATIVE_STEREO_SHAPER_CALIBRATION.json')
  scripts=research/'scripts';scripts.mkdir()
  for name in['build_complete_original_wip37.py','publish_complete_wip37.py','adopt_and_check_full37_runtime.py','start_actual_full37_original_target_continuation.py','native_post_trim.py','probe_actual_native_post_trim_verified.py','study_POST_AP6_joint_refinement36.py','POST_AP6_joint_refinement36_support.py','prepare_full37_inputs_and_cold_proof.py','check_current_original_chain_readiness.py','start_native_headless_display.py']:shutil.copyfile(H/name,scripts/name)
  runtime=research/'current-runtime';runtime.mkdir()
  for name in['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
  shutil.copyfile('/tmp/divalead-local-1625/fl20_curve.py',runtime/'fl20_curve.py');shutil.copyfile(OLD/'normal_real_ZL_refit.py',runtime/'normal_real_ZL_refit.py');shutil.copyfile(OLD/'backup_complete_finite_study.py',runtime/'backup_complete_finite_study.py');shutil.copyfile(OLD/'bounded_git_audio_backup.py',runtime/'bounded_git_audio_backup.py')
  intro='# ZL37 WIP — дальнейшее приближение к исходному оригиналу\n\n- [Полный ZIP FL20](ZL-WIP37/Diva_ZL37_STEREO_WIP_complete.zip).\n- [A/B: оригинал →36→37](ZL-WIP37/AB_ORIGINAL_ZL36_ZL37_WIP.mp3).\n- [Lossless A/B](ZL-WIP37/AB_ORIGINAL_ZL36_ZL37_WIP.flac).\n- [Инструкция FL Studio](ZL-WIP37/FL_STUDIO_RU.md).\n- [Все реальные WAV/данные](original-AP6-joint-refinement36-positive/README_RU.md).\n\nПолного совпадения нет. Новый выигрыш исходного критерия подтверждён12новыми парами, включая оба cold. Изменён только второйZL: StereoAllPass6 и совместная настройка частоты/Q существующих AP3/5. Источник Diva/три длинные входящие ноты/ARP/ADSR/native12/WS52/PRIMARY36/позднийnativeTrim сохранены. Всего13native и2ZL. Точные настройки, границы и ограничения ниже.\n\n'
  doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL37_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP37/','](../ZL-WIP37/').replace('](original-AP6-joint-refinement36-positive/','](../original-AP6-joint-refinement36-positive/'))
  p=PUBLIC/'README_RU.md';p.write_text('[ZL37: полный native13/two-ZL комплект, WAV/A-B и инструкция FL20](ZL37_CONTINUATION_RU.md).\n\n'+p.read_text())
  prior=H/'PRIOR_START_SKILL_BEFORE_CONDENSED_ZL37.md'
  if not prior.exists():shutil.copyfile(R/'start_skill_current.md',prior)
  startup=(H/'cloud_start_current.md').read_text();(R/'start_skill_current.md').write_text(startup);shutil.copyfile(R/'start_skill_current.md',h['BASE']/'start_skill_current.md');(research/'CLOUD_START_CURRENT.md').write_text(startup)
  (research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL37 WIP with actual native post-trim, FL20 kit and current runtime');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;assert git('rev-parse','HEAD:'+str((PUBLIC/'ZL-WIP33').relative_to(P)))==previous_full33;h['push_and_confirm'](commit)
  checks=[]
  for p in[dest/archive.name,dest/'AB_ORIGINAL_ZL36_ZL37_WIP.mp3',dest/'FL_STUDIO_RU.md',runtime/'native_post_trim.py',research/'CLOUD_START_CURRENT.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP37',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='10',original_native12_plus_native_post_trim=True,native_trim_state_SHA256=build['post_trim_state_SHA256'],all_training_validation_WAVs_and_files_remote_verified_in_prior_backup=True,prior_backup_commit=proof['commit'],two_cold_actual_full_chain_replays=[0.,0.],HTTP_checks=checks,all_old_kits_history_PC_GUI_private_refs_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(H/'ZL37_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
