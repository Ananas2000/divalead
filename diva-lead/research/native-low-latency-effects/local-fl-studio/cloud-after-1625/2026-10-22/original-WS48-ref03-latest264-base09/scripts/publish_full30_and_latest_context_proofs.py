"""Publish complete supported WIP30 plus latest-context48WAV; initial48 linked."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil
from bounded_git_audio_backup import stage_archive,finish_manifest,verify_and_offload
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');J=H/'WS48_REF03_LATEST_CONTEXT';BASE=Path('/workspace/divalead-work/native-low-latency-effects/validated-bases/FL20_NATIVE_ZL_REBASED_09')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='publish_full30_original_only');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL30_BUILD_COMPLETION.json');summary=read(J/'completion.json');kit=Path(build['root']);archive=Path(build['ZIP']);assert summary['robust_independent_confirmation'] and build['ZIP_actual_two_cold_cascade_max_abs_errors']==[0.,0.] and build['ZIP_native_FST_zero_depth_max_abs_errors']==[0.];assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256'];initial=read(Path('/workspace/divalead-work/stereo-refinement-20261025/original-WS48-ref03-initial-context-proof_PUBLICATION.json'));assert initial['all_retained_study_files_and_WAVs_remote_Git_verified']
pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish full ZL30 after latest-context12 and strict fullZIPreplay, initial48 alreadypublic'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP30';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-WS48-ref03-latest264-base09';research.mkdir();parts=[];local_archives=[]
  for p in J.iterdir():
   if p.is_file()and p.suffix in ['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for p in J.glob('*.tar.gz'):
   manifest=stage_archive(P,git,p,research);parts+=manifest['parts'];local_archives.append(p)
  for name in ['ZL30_BUILD_COMPLETION.json','WS48_REF03_LATEST_CONTEXT_MATCH.json']:shutil.copyfile(H/name,research/name)
  shutil.copyfile(Path('/workspace/divalead-work/stereo-refinement-20261025/original-WS48-ref03-initial-context-proof_PUBLICATION.json'),research/'INITIAL_CONTEXT_PUBLICATION.json')
  ready=read(BASE.with_name(BASE.name+'-COMBINED_CANDIDATE_READY.json'));native_archive=Path(ready['native_base_archive_path']);assert hashlib.sha256(native_archive.read_bytes()).hexdigest()==ready['native_base_archive_SHA256'];shutil.copyfile(native_archive,research/native_archive.name)
  scripts=research/'scripts';scripts.mkdir()
  for name in ['study_native_WaveShaper48_original_refinement03.py','confirm_WS48_ref03_latest_context_original.py','build_original_target_stereo_wip30.py','publish_full30_and_latest_context_proofs.py','adopt_and_check_full30_runtime.py','start_actual_full30_original_target_continuation.py','study_native_Chorus9_original.py']:shutil.copyfile(H/name,scripts/name)
  a=Path('/workspace/divalead-work/pc-stereo-20261024');runtime=research/'current-two-ZL-runtime';runtime.mkdir()
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py']:shutil.copyfile(a/name,runtime/name)
  intro='''# ZL30 WIP — следующий подтверждённый шаг прямо к оригиналу

- [Полный ZIP FL20/26](ZL-WIP30/Diva_ZL30_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → numeric264 с4.168с → ZL30 с8.336с](ZL-WIP30/AB_ORIGINAL_264_ZL30_WIP.mp3).
- [Lossless A/B](ZL-WIP30/AB_ORIGINAL_264_ZL30_WIP.flac).
- [Пошаговая инструкция FL Studio](ZL-WIP30/FL_STUDIO_RU.md).
- [Первые48WAV на исходном контексте](original-WS48-ref03-initial-context-proof/README_RU.md).
- [Последние48WAV на актуальном EQ264](original-WS48-ref03-latest264-base09/README_RU.md).

Полного совпадения нет. Две отдельные серии не объединялись для прохождения
порогов: сначала кривая прошла на исходном29, затем однократно на новомEQ264.
В latestfirst6 запас над3SEM невелик; latestfirst10 и обеcold положительны.
Все96validationWAV обеих серий сохранены lossless в ordinaryGit сmemberSHA и
partsmanifest. Результат не называется точным совпадением. Цель — только
исходный оригинальныйWAV на штатных Fruity и двух ZL, три длинныевходящиеноты.
НовыйFLP не открывался вWindowsGUI; actualLinux/WineDSP/состояния/ZIP проверены.

'''
  doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL30_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP30/','](../ZL-WIP30/').replace('](original-WS48-','](../original-WS48-'))
  p=PUBLIC/'README_RU.md';p.write_text('[ZL30: native09, PRIMARY264, полный трёхнотный WIP, A/B и инструкция](ZL30_CONTINUATION_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_ORIGINAL_WS48_REF03_ZL30_20261026
Latest supported fullkit ZL-WIP30/Diva_ZL30_STEREO_WIP_complete.zip SHA{build['ZIP_SHA256']}. ReadZL30_CONTINUATION_RU.md andFL_STUDIO_RU.md. TargetONLYuploadedoriginalWAV, neverv83/Finishproxy/effect. Nativebase09 new48controlWScurve, other11native/Diva281/incoming3longnotes41-37-36twice/ARP/ADSR/routesunchanged. PRIMARY264; POSTsame28/29:3SideAP+1StereoAP+LeftPeak1013.3Hz/Q4.786/gain-1.04dBslot4, TWOactualZLs noFinish. Relative264 WSonly, relativefull29 WSandPRIMARY.167actualnative/VST3cases, initial12passed(first10gain.004144567014,cold+.003638115617/+.005039594972); PRIMARYadvanced264, sooneSEPARATElatest12confirmation, no pooling. BOTHfirst6ANDfirst10>max(.0005,3SEM), all12stereoguards, cold2positive. Latestfirst6gain.004093436273 SEM.001353749775 threshold.004061249325 narrowmargin; first10gain.004505644493 SEM.000873692657 threshold.002621077970; cold+.003051600354/+.005135124591. First10loss1.298081008453. H24/ERB/wholebetter, upperoff/envelope/stereobalancetinyworse disclosed. FullmatchFALSE/noaudition/perceptualpercentageclaim. StrictfullZIP2actualcoldZLreplays0/0/componentsexact/native12DLL-FSTzeroDepth0at2e-7, ZLPDC0/impulse0notASIO; smallnativeblockdifferences disclosed. NewFLPnotWindowsGUItested/noGUIexport. Initial48WAV inoriginal-WS48-ref03-initial-context-proof, latest48inoriginal-WS48-ref03-latest264-base09; all96losslessGit. Native09 lives /workspace/divalead-work/native-low-latency-effects/validated-bases/FL20_NATIVE_ZL_REBASED_09, internalverifiednative09ZIPalsoinlatestresearchforrestorationonly, fullZL30foruser. GUItransfermustSOURCEWSandPRIMARY(orPRIMARYalready264); POSTsame28. NoMista/originalaudioinsynthesis. Alloldkits/PCGUI/privateoriginalsource48/refsretained. Userchangedbackupthresholdto15percentremaining; APIquotapercentageNOTobservable, completedusefulworkbackedimmediately. Continueactualworktomatch/actuallimit, do notendturnclaimingbackground. OldsingleZLstopsremainretired. GracefulSTOPownerWS48-ref03-latest-context-20261026 removedonlyafter30adoption andactualcoldruntimecheck.
END_ORIGINAL_WS48_REF03_ZL30_20261026

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');finish_manifest(h,research,parts);git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL30 native09 WIP and independent latest-context48 WAVs');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_264_ZL30_WIP.mp3',dest/'FL_STUDIO_RU.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  verify_and_offload(P,git,commit,parts,H/'full30-public-structural-cache')
  for p in local_archives:p.unlink()
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP30',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='09',initial48_and_latest48_WAVs_remote_Git_verified=True,ZIP_replay_max_abs_errors=[0.,0.],native_ZIP_FST_zero_depth_error=0.,HTTP_checks=checks,all_old_kits_and_PC_GUI_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(H/'ZL30_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
