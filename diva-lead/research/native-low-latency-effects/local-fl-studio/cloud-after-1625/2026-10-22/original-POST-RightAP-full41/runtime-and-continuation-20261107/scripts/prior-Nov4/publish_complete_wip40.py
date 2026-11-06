"""Publish verified full WIP40; preserve every older kit and PC GUI tree."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zipfile
V=Path(__file__).resolve().parent;A=V.parent/'pc-stereo-20261024';N=V.parent/'native-low-latency-effects';O=V.parent/'stereo-refinement-20261025';Q=Path('/tmp/divalead-recovered-OS17-point-new12-20261104')
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_verified_full40');P,C,PUBLIC=[h[k]for k in ['P','R','PUBLIC']];git=h['git'];build=read(V/'ZL40_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);s=read(Q/'completion.json');priorproof=read(O/'original-recovered-OS17-point-new12-passed-20261104_PUBLICATION.json');assert s['robust_improvement']and priorproof['all_retained_study_files_and_WAVs_remote_Git_verified'];assert build['actual_two_cold_ZL_replay_errors']==build['actual_two_cold_vs_canonical_full_errors']==[0.,0.]and max(build['actual_two_cold_full_native_trim_chain_errors'])<=2e-7;assert sha(archive)==build['ZIP_SHA256'];assert not(N/'zl-stereo-numerical.pause').exists();assert read(N/'zl-stereo-continuation.stop')['owner']=='full40-supported-export-20261104'
pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish native12 OSstep1 local17 full40 after NEW12 and independent ZIP cold replay'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  latest=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert latest['source_accepted_cohort']==565;assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes();assert latest['native_base']['native_saved_state_bundle']['settings_SHA256']==read(Q/'PRIOR_COMBINED_CANDIDATE.json')['native_base']['native_saved_state_bundle']['settings_SHA256']
  dest=PUBLIC/'ZL-WIP40';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-OSstep1-local17-full40';research.mkdir();scripts=research/'scripts';scripts.mkdir();runtime=research/'current-runtime';runtime.mkdir()
  for name in ['ZL40_BUILD_COMPLETION.json','NATIVE12_SUPPORTED_RUNTIME_PROOF.json','SUPPORTED_NATIVE12_CANDIDATE.json','BUILD40_COLD_REPLAY_DIAGNOSIS.json','BUILD40_HEADER_PARSER_DIAGNOSIS.json','ACTUAL_DIVA_SOURCE_RECHECK.json','INTERRUPTED_OS_LOCAL17_DATA_RESTORED.json','TMP_RUNTIME_RESTORATION_PROVENANCE.json','OLD30_38_MEDIA_CACHE_RELEASE.json']:shutil.copyfile(V/name,research/name)
  shutil.copyfile(O/'original-recovered-OS17-point-new12-passed-20261104_PUBLICATION.json',research/'ALL60_REAL_WAV_PUBLICATION.json')
  for p in V.glob('*.py'):shutil.copyfile(p,scripts/p.name)
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
  shutil.copyfile(V/'fl20_curve.py',runtime/'fl20_curve.py')
  base=N/'validated-bases/FL20_NATIVE_ZL_REBASED_12';base_zip=research/'FL20_NATIVE_ZL_REBASED_12_verified_base.zip'
  with zipfile.ZipFile(base_zip,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for p in sorted(base.rglob('*')):
    if p.is_file():z.write(p,base.name+'/'+p.relative_to(base).as_posix())
  with zipfile.ZipFile(base_zip)as z:
   assert z.testzip()is None
   for p in base.rglob('*'):
    if p.is_file():assert z.read(base.name+'/'+p.relative_to(base).as_posix())==p.read_bytes()
  (research/'NATIVE12_ARCHIVE_PROOF.json').write_text(json.dumps(dict(path=base_zip.name,bytes=base_zip.stat().st_size,SHA256=sha(base_zip),CRC_and_every_member_byte_verified=True,native_only_base_not_full_ZL_output=True),indent=2)+'\n')
  doc='''# WIP40: новый проверенный трёхнотный комплект

- [Полный ZIP для FL Studio20](ZL-WIP40/Diva_ZL40_STEREO_WIP_complete.zip).
- [A/B оригинал →565→40](ZL-WIP40/AB_ORIGINAL_565_ZL40_WIP.mp3), [FLAC](ZL-WIP40/AB_ORIGINAL_565_ZL40_WIP.flac).
- [Инструкция FL Studio](ZL-WIP40/FL_STUDIO_RU.md).
- [Все60 новых проверочных WAV и состояния](original-recovered-OS17-point-new12-passed-20261104/README_RU.md).

Полного совпадения пока нет. Новая обработка прошла12 новых пар относительно565 и полного39, независимый холодный ZIP и проверку supportedгенератора. Изменены только SOURCE WaveShaper, оба ZL и финальный StereoShaper; остальные11native, Diva/MIDI/ARP/ADSR и маршруты сохранены. Новый FLP пока не открыт в WindowsGUI; ASIO не измерялась.

'''+(kit/'FL_STUDIO_RU.md').read_text()
  (PUBLIC/'ZL40_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP40/','](../ZL-WIP40/').replace('](original-recovered-OS17-point-new12-passed-20261104/','](../original-recovered-OS17-point-new12-passed-20261104/'))
  (PUBLIC/'LATEST_THREE_NOTE_RU.md').write_text('''# Текущий полный трёхнотный комплект WIP40

[ZIP для FL Studio20](ZL-WIP40/Diva_ZL40_STEREO_WIP_complete.zip), [инструкция](ZL-WIP40/FL_STUDIO_RU.md), [A/B оригинал →565→40](ZL-WIP40/AB_ORIGINAL_565_ZL40_WIP.mp3). WIP40 начинается с8.336с. Из565/39 нужны SOURCE WaveShaper, ОБА ZL и последний StereoShaper. Предпочтителен полный FLP из нового ZIP.

Полного совпадения пока нет. [Проверки](ZL40_CONTINUATION_RU.md). [Предыдущая565](stereo-cascade87-cohort-0565/README_RU.md) сохранена. Дальнейшую активность определяет фактический контроллер; страница не обещает работу процессов.
''')
  p=PUBLIC/'README_RU.md';p.write_text('[WIP40: полный FL20 комплект, A/B с оригиналом и инструкция](ZL40_CONTINUATION_RU.md). Полного совпадения нет.\n\n'+p.read_text());(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():sha(p)for p in research.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish full WIP40: recovered canonical OS local17, strict NEW12 original comparison and cold FL20 ZIP');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_565_ZL40_WIP.mp3',dest/'FL_STUDIO_RU.md',runtime/'fl20_curve.py',base_zip]:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP40',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],all60_new_validation_WAVs_remote_verified=True,prior_backup_commit=priorproof['commit'],two_cold_actual_full_vs_canonical_errors=build['actual_two_cold_vs_canonical_full_errors'],cold_vs_warm_validation_absolute_error=build['actual_two_cold_full_native_trim_chain_errors'],HTTP_checks=checks,all_old_kits_PC_GUI_original_and_private_refs_preserved=True,latest_comparator_rechecked_565=True,original_is_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (V/'ZL40_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
