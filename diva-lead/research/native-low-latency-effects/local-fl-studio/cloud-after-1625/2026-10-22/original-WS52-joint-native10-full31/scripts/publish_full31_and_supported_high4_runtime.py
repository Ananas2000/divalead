"""Publish full31; reuse already verified joint48WAV archive without duplication."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');J=H/'WS52_PRIMARY_JOINT_RESEARCH';BASE=Path('/workspace/divalead-work/native-low-latency-effects/validated-bases/FL20_NATIVE_ZL_REBASED_10');OLD=Path('/workspace/divalead-work/stereo-refinement-20261025')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='publish_supported_full31');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL31_BUILD_COMPLETION.json');s=read(J/'completion.json');kit=Path(build['root']);archive=Path(build['ZIP']);assert s['robust_improvement']and s['new_primary_changed'];assert build['ZIP_actual_two_cold_cascade_max_abs_errors']==[0.,0.]and build['ZIP_native_FST_zero_depth_max_abs_errors']==[0.];assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256'];proof=read(OLD/'original-WS52-primary-joint-finite-result_PUBLICATION.json');assert proof['all_retained_study_files_and_WAVs_remote_Git_verified']and proof['local_audio_retained']
pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish supported full31 after exactcoldZIPreplay, joint48WAV already verified remote'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');assert os.system('git -C /workspace/divalead merge-base --is-ancestor '+proof['commit']+' origin/main')==0;protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP31';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-WS52-joint-native10-full31';research.mkdir()
  for p in J.iterdir():
   if p.is_file()and p.suffix in ['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for name in ['ZL31_BUILD_COMPLETION.json','WS52_JOINT_CURRENT_CONTEXT_PROOF.json']:shutil.copyfile(H/name,research/name)
  shutil.copyfile(OLD/'original-WS52-primary-joint-finite-result_PUBLICATION.json',research/'JOINT_ALL_FILES_AND_48_WAV_PUBLICATION.json');shutil.copyfile(OLD/'original-WS52-high4-first6-failed-not-adopted_PUBLICATION.json',research/'CURVE_ALONE_REJECTED_PUBLICATION.json')
  ready=read(BASE.with_name(BASE.name+'-COMBINED_CANDIDATE_READY.json'));native_archive=Path(ready['native_base_archive_path']);assert hashlib.sha256(native_archive.read_bytes()).hexdigest()==ready['native_base_archive_SHA256'];shutil.copyfile(native_archive,research/native_archive.name)
  scripts=research/'scripts';scripts.mkdir()
  for name in ['study_WS52_and_normal_primary_joint_original.py','build_original_target_stereo_wip31.py','publish_full31_and_supported_high4_runtime.py','adopt_and_check_full31_runtime.py','start_actual_full31_original_target_continuation.py','watch_WS52_joint_completed_backup.py']:shutil.copyfile(H/name,scripts/name)
  replay=research/'current-native-curve-runtime';replay.mkdir();shutil.copyfile('/tmp/divalead-local-1625/fl20_curve.py',replay/'fl20_curve.py');shutil.copyfile(H/'NATIVE09_FINGERPRINT_BEFORE_HIGH4.json',replay/'OLD_NATIVE09_FINGERPRINT_COMPATIBILITY.json')
  a=Path('/workspace/divalead-work/pc-stereo-20261024');runtime=research/'current-two-ZL-runtime';runtime.mkdir()
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py']:shutil.copyfile(a/name,runtime/name)
  intro='''# ZL31 WIP — штатная кривая52 и согласованный основной EQ

- [Полный ZIP FL20/26](ZL-WIP31/Diva_ZL31_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → ZL30 с4.168с → ZL31 с8.336с](ZL-WIP31/AB_ORIGINAL_ZL30_ZL31_WIP.mp3).
- [Lossless A/B](ZL-WIP31/AB_ORIGINAL_ZL30_ZL31_WIP.flac).
- [Инструкция FL Studio](ZL-WIP31/FL_STUDIO_RU.md).
- [Все файлы совместной серии и48WAV, уже сохранённые автоматически](original-WS52-primary-joint-finite-result/README_RU.md).
- [Отдельная кривая52 была отклонена](original-WS52-high4-first6-failed-not-adopted/README_RU.md).

Полного совпадения нет. Принята именно новая комбинация кривой и изменённого
PRIMARY после1189реальныхпредложений и12новыхпар, а не отвергнутая кривая52сама
по себе. Повторные попытки принять один и тот же не прошедший DSPвариант не делались.
Архив48проверочныхWAV ивсехфайлов серии уже побитово проверен вGit; повторная
копия огромногоархива не добавляется. Ссылки/receipt иmemberSHA сохранены здесь.

'''
  doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL31_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP31/','](../ZL-WIP31/').replace('](original-WS52-','](../original-WS52-')+'\nДля восстановления cloudподбора обязательно сначала установить current-native-curve-runtime/fl20_curve.py: он поддерживает high4метаданные и сохраняет прежние48fingerprints. Основнойmatcher проверяет fingerprint до рендеров, чтобы старыйhelper не проиграл другой звук. ПользователюFLStudio Pythonне нужен — FST содержит обычную129точечнуюкривую.\n')
  p=PUBLIC/'README_RU.md';p.write_text('[ZL31: прошедшая проверку комбинация WS52 и PRIMARY, полный ZIP и A/B](ZL31_CONTINUATION_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_SUPPORTED_WS52_JOINT_ZL31_20261026
Latest fullkit ZL-WIP31/Diva_ZL31_STEREO_WIP_complete.zip SHA{build['ZIP_SHA256']}; readZL31_CONTINUATION_RU.md andFL_STUDIO_RU.md. ONLYuploadedoriginalWAV target, neverv83/Finishproxy/effect. Nativebase10 adds4supportedhigh-inputcurvebumps(.65/.67/.69/.71) to48, sameordinary129pointnativeWSFST; changedWSandPRIMARY only, other11native/Diva281/3longincomingnotes41-37-36twice/ARP/ADSR/routes/POSTsame28(3SideAP+1StereoAP+LeftPeak1013.3HzQ4.786gain-1.04dB) unchanged. TWOactualZLs noFinish. Curve52ALONEfailedfirst6, notadopted; NEWDSPpoint requiresnewPRIMARYchanged,1189actualVST3fitcases/3newtraininginputs/2heldouts/frozenbefore12newpairs. BOTHfirst6ANDfirst10>max(.0005,3SEM), bothcoldpositive, all12stereoguards. First6gain.002670664231 SEM.000435112049 threshold.001305336146; first10gain.002548778783 SEM.000493900913 threshold.001481702738; cold+.004829697303/+.005098111877. First10loss1.295619568932. H24/ERB/relativephasebetter, upperharm/upperoff/whole/envelopetinyworse disclosed; nofullmatch/noaudition/no%claim. Strict2actualcoldZIPZLcascades0/0/nativeDLL-FSTzeroDepth0at2e-7/componentsbyteexact/ZLPDC0impulse0notASIO; smallnativeblockdifferences disclosed. NewFLPnotWindowsGUItested/noGUIexport. Alljoint48WAVandallfiles alreadyautomaticallypublic inoriginal-WS52-primary-joint-finite-result; retainedlocalaudiosafe forexport. Native10 at /workspace/divalead-work/native-low-latency-effects/validated-bases/FL20_NATIVE_ZL_REBASED_10; internalnative10ZIPinoriginal-WS52-joint-native10-full31. CRITICALcloudrestorebeforeusing10 installpublished original-WS52-joint-native10-full31/current-native-curve-runtime/fl20_curve.py at /tmp/divalead-local-1625/fl20_curve.py. Newhigh4 metadata fingerprint included, older48/native09 hashes/bytes unchangedverified. Mainnowasserts unchangedseedfingerprint==savedbundle BEFORErender, preventsoldhelperplayingwrongcurve. UserFLStudio onlyneedsstandardFST, noPython/newplugin. GUIupdateSOURCEWSandPRIMARYmandatory; POSTsame28. Keepallolderfullkits/PCGUI/privateoriginalsource48/refs. STOPownerLR-lowmid-primary-joint-20261026 canremoveonlyafter31adoption/actualcoldruntimecheck; oldsingleZLretiredstopsremain. Userbackupthreshold15percent; APIquota%NOTvisible, completedworkbackedimmediately+one-shotfinitebackup. Continueactualmatchinguntilmatch/actuallimit, neverendturnclaimbackground.
END_SUPPORTED_WS52_JOINT_ZL31_20261026

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL31 joint WS52-primary WIP and supported replay runtime');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_ZL30_ZL31_WIP.mp3',dest/'FL_STUDIO_RU.md',replay/'fl20_curve.py']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP31',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='10',all_joint48_WAVs_and_files_remote_verified_in_prior_automatic_backup=True,prior_automatic_backup_commit=proof['commit'],ZIP_replay_max_abs_errors=[0.,0.],native_ZIP_FST_zero_depth_error=0.,HTTP_checks=checks,all_old_kits_and_PC_GUI_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(H/'ZL31_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
