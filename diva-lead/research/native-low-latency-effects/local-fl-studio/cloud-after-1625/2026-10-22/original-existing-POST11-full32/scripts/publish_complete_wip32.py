"""Publish the verified existing-band POST11 improvement and full FL20 kit."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
H=Path(__file__).resolve().parent;OLD=H.with_name('stereo-refinement-20261025');Q=Path('/tmp/divalead-post-joint11-20261026-01')
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_full32')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL32_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);s=read(Q/'completion.json');proof=read(OLD/'original-existing-POST11-finite-result_PUBLICATION.json')
assert s['robust_improvement']and build['ZIP_actual_two_cold_cascade_max_abs_errors']==[0.,0.]
assert read(H/'POST11_CURRENT_CONTEXT_MATCH.json')['PRIMARY_POST_and_native_context_match_frozen_validation']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256']and proof['all_retained_study_files_and_WAVs_remote_Git_verified']
pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish full32 actual cold-replayed original-target existing-band improvement'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',proof['commit'],'origin/main'],check=True);protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP32';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-existing-POST11-full32';research.mkdir()
  for p in Q.iterdir():
   if p.is_file()and p.suffix in ['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for name in ['ZL32_BUILD_COMPLETION.json','POST11_CURRENT_CONTEXT_MATCH.json','VERIFIED_AP5_CLOSED_ARCHIVE_RELEASE.json']:shutil.copyfile(H/name,research/name)
  shutil.copyfile(OLD/'original-existing-POST11-finite-result_PUBLICATION.json',research/'ALL_STUDY_FILES_AND_WAV_PUBLICATION.json')
  scripts=research/'scripts';scripts.mkdir()
  for name in ['study_existing_POST11_joint_original.py','verify_existing_POST11_cold_and_latency.py','build_original_target_stereo_wip32.py','publish_complete_wip32.py','adopt_and_check_full32_runtime.py','start_actual_full32_original_target_continuation.py','watch_existing_POST11_completed_backup.py']:shutil.copyfile(H/name,scripts/name)
  replay=research/'current-native-curve-runtime';replay.mkdir();shutil.copyfile('/tmp/divalead-local-1625/fl20_curve.py',replay/'fl20_curve.py')
  runtime=research/'current-two-ZL-runtime';runtime.mkdir();a=Path('/workspace/divalead-work/pc-stereo-20261024')
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py']:shutil.copyfile(a/name,runtime/name)
  intro='''# ZL32 WIP — перенастройка существующих полос второго EQ

- [Полный ZIP для FL Studio](ZL-WIP32/Diva_ZL32_STEREO_WIP_complete.zip).
- [A/B: оригинал → numeric301 → ZL32](ZL-WIP32/AB_ORIGINAL_301_ZL32_WIP.mp3).
- [Lossless A/B](ZL-WIP32/AB_ORIGINAL_301_ZL32_WIP.flac).
- [Инструкция FL Studio](ZL-WIP32/FL_STUDIO_RU.md).
- [Все реальные WAV и файлы проверки](original-existing-POST11-finite-result/README_RU.md).

Небольшое устойчивое улучшение исходного критерия на 12 новых парах.
Полного совпадения нет. Источник, nativebase10/WS52, три длинные ноты и
PRIMARY301 сохранены; изменены 11 параметров прежних пяти полос POST.
Добавления полос или плагинов нет. Отдельные показатели стерео и огибающей
слегка хуже; точные изменения и ограничения приведены ниже.

'''
  doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL32_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP32/','](../ZL-WIP32/').replace('](original-existing-','](../original-existing-')+'\nCloud replay: use current-native-curve-runtime/fl20_curve.py before reconstructing native10; it supports optional high4 metadata. Ordinary FL presets require no Python. All study WAVs are already byte-verified in the linked finite-result archive.\n')
  p=PUBLIC/'README_RU.md';p.write_text('[ZL32: перенастроенные существующие полосы POST, полный ZIP/WAV/FLP и A/B](ZL32_CONTINUATION_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_FULL_ZL32_EXISTING_POST11_20261026
Latest full kit ZL-WIP32/Diva_ZL32_STEREO_WIP_complete.zip SHA256 {build['ZIP_SHA256']}; read ZL32_CONTINUATION_RU.md and FL_STUDIO_RU.md. ONLY original uploaded WAV is target; never v83/Finish. Full31 native10/WS52/source281/three held notes 41-37-36 twice/ARP/ADSR/routes unchanged; PRIMARY numeric301 unchanged. Joint retune11 existing POST controls: SideAP10207.6/Q2.198,2149.8/Q4.702,930/Q11.336; StereoAP782.9/Q20.561; LeftPeak994/Q5.871/-1.70dB. No new filters, TWO actual ZLs, no Finish. POST SHA256 460cc43537b391236b3e8821910eede427bb6334bcce64e6e4f7be03a84e985d. 229 actual proposals,3 new inputs/2 heldouts; frozen before12 fresh pairs. First6 gain.001605084122 SEM.000002427358, first10 gain.001608731104 SEM.000003252253, both above unchanged .0005/3SEM; both cold positive and all stereo guards. First10 original loss1.290952050075, not perceptual%. Mixed phase/envelope/stereo and lowmid+.015721dB disclosed. Full match NOT reached; no listening/GUI/ASIO claim. Two actual cold chain replays0/0 plus two independent ZIP replays0/0, component bytes exact, PDC0/impulse0. Native12 bytes unchanged31, prior native10 DLL/FST proof remains valid. All42 training/validation WAV already remote in original-existing-POST11-finite-result. Use supported high4 fl20_curve.py before native10 reconstruction; fingerprint startup assertion mandatory. Adopt via current scripts only while STOP owner POST11-latest-context-20261026; startup verifies both runtime cold checks and fingerprint, continues cohort308+. Every accepted numeric point backed automatically. Quota% not exposed; user requests backup at15%, therefore save completed work immediately. Preserve old kits/PC tree/private refs and original source. Continue actual matching until match/actual limit; never end turn claiming background.
END_FULL_ZL32_EXISTING_POST11_20261026

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL32 WIP with independently validated existing POST retune');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_301_ZL32_WIP.mp3',dest/'FL_STUDIO_RU.md',replay/'fl20_curve.py']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP32',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='10',all_study_WAVs_and_files_remote_verified_in_prior_automatic_backup=True,prior_automatic_backup_commit=proof['commit'],ZIP_replay_max_abs_errors=[0.,0.],HTTP_checks=checks,all_old_kits_and_PC_GUI_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (H/'ZL32_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
