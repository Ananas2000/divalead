"""Publish independently replayed WIP39; preserve older kits and PC work."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zipfile
U=Path(__file__).resolve().parent;A=U.parent/'pc-stereo-20261024';N=U.parent/'native-low-latency-effects';O=U.parent/'stereo-refinement-20261025';Q=U/'BIPOLAR_FINALIST1_AIR_MARGIN_REPAIR'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_verified_full39');P,C,PUBLIC=[h[k]for k in ['P','R','PUBLIC']];git=h['git'];build=read(U/'ZL39_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);s=read(Q/'completion.json');priorproof=read(O/'original-bipolar-even8-Mid20-Side22-margin39-new12-passed-20261031_PUBLICATION.json');assert s['robust_improvement']and priorproof['all_retained_study_files_and_WAVs_remote_Git_verified'];assert build['actual_two_cold_ZL_replay_errors']==[0.,0.]and max(build['actual_two_cold_full_native_trim_chain_errors'])<=2e-7;assert sha(archive)==build['ZIP_SHA256'];assert not(N/'zl-stereo-numerical.pause').exists()
pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish complete native11 bipolar even8 WIP39 after strict12 and independent ZIP replay'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  latest=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert latest['source_accepted_cohort']==556;assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
  dest=PUBLIC/'ZL-WIP39';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-bipolar-even8-full39';research.mkdir();scripts=research/'scripts';scripts.mkdir();runtime=research/'current-runtime';runtime.mkdir()
  for name in ['ZL39_BUILD_COMPLETION.json','NATIVE11_SUPPORTED_RUNTIME_PROOF.json','SUPPORTED_NATIVE11_CANDIDATE.json','BUILD39_FLOAT_REPLAY_DIAGNOSIS.json']:shutil.copyfile(U/name,research/name)
  shutil.copyfile(O/'original-bipolar-even8-Mid20-Side22-margin39-new12-passed-20261031_PUBLICATION.json',research/'ALL60_REAL_WAV_PUBLICATION.json')
  for name in ['build_complete_original_wip39.py','finalize_full39_metadata.py','publish_complete_wip39.py','prepare_supported_bipolar_native11.py','repair_bipolar_finalist1_air_margin.py','bipolar_finalist1_air_margin_support.py','check_bipolar_WS_added_delay.py']:shutil.copyfile(U/name,scripts/name)
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
  shutil.copyfile(U/'bipolar-runtime/fl20_curve.py',runtime/'fl20_curve.py');shutil.copyfile(U/'bipolar-runtime/fl20_curve_legacy_snapshot.py',runtime/'fl20_curve_legacy_snapshot.py')
  delay=U/'BIPOLAR_WS_IMPULSE_DELAY'
  assert read(delay/'PROOF.json')['new_WS_added_delay_samples']==0;shutil.copytree(delay,research/'isolated-WS-delay-proof')
  # Native11 is reusable separately from the full two-ZL project.
  base=N/'validated-bases/FL20_NATIVE_ZL_REBASED_11';base_zip=research/'FL20_NATIVE_ZL_REBASED_11_verified_base.zip'
  with zipfile.ZipFile(base_zip,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for p in sorted(base.rglob('*')):
    if p.is_file():z.write(p,base.name+'/'+p.relative_to(base).as_posix())
  with zipfile.ZipFile(base_zip)as z:
   assert z.testzip()is None
   for p in base.rglob('*'):
    if p.is_file():assert z.read(base.name+'/'+p.relative_to(base).as_posix())==p.read_bytes()
  (research/'NATIVE11_ARCHIVE_PROOF.json').write_text(json.dumps(dict(path=base_zip.name,bytes=base_zip.stat().st_size,SHA256=sha(base_zip),CRC_and_every_member_byte_verified=True,native_only_base_not_full_ZL_output=True),indent=2)+'\n')
  doc='''# WIP39: новый проверенный трёхнотный комплект

- [Полный ZIP для FL Studio20](ZL-WIP39/Diva_ZL39_STEREO_WIP_complete.zip).
- [A/B оригинал →556→39](ZL-WIP39/AB_ORIGINAL_556_ZL39_WIP.mp3), [FLAC](ZL-WIP39/AB_ORIGINAL_556_ZL39_WIP.flac).
- [Инструкция FL Studio](ZL-WIP39/FL_STUDIO_RU.md).
- [Все60 проверочных WAV и состояния](original-bipolar-even8-Mid20-Side22-margin39-new12-passed-20261031/README_RU.md).

Полного совпадения пока нет. Изменены WaveShaper на SOURCE и MID20/SIDE22 в первом ZL. Три длинные входящие ноты, источник Diva, ARP/ADSR, остальные11native, POST и финальный StereoShaper сохранены. Проверены12 новых пар и полный ZIP настоящими DLL/VST3 под Wine. Новый FLP ещё не открыт в WindowsGUI; задержка ASIO не измерялась.

'''+(kit/'FL_STUDIO_RU.md').read_text()
  (PUBLIC/'ZL39_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP39/','](../ZL-WIP39/').replace('](original-bipolar-even8-Mid20-Side22-margin39-new12-passed-20261031/','](../original-bipolar-even8-Mid20-Side22-margin39-new12-passed-20261031/'))
  (PUBLIC/'LATEST_THREE_NOTE_RU.md').write_text('''# Текущий полный трёхнотный комплект WIP39

[ZIP для FL Studio20](ZL-WIP39/Diva_ZL39_STEREO_WIP_complete.zip), [инструкция](ZL-WIP39/FL_STUDIO_RU.md), [A/B оригинал →556→39](ZL-WIP39/AB_ORIGINAL_556_ZL39_WIP.mp3). WIP39 начинается с8.336с. В свою копию556/38 перенесите SOURCE WaveShaper И первый ZL PRIMARY; POST и последний StereoShaper прежние. Надёжнее открыть полный FLP из ZIP.

Полного совпадения пока нет. [Проверки](ZL39_CONTINUATION_RU.md). [Предыдущая556](stereo-cascade87-cohort-0556/README_RU.md) сохранена. Дальнейшую активность определяет фактический контроллер; страница не обещает работу процессов.
''')
  p=PUBLIC/'README_RU.md';p.write_text('[WIP39: новый полный FL20 комплект, A/B с оригиналом и инструкция](ZL39_CONTINUATION_RU.md). Полного совпадения нет.\n\n'+p.read_text());(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():sha(p)for p in research.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete WIP39: native bipolar WaveShaper, strict12 original comparison and full cold ZIP replay');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_556_ZL39_WIP.mp3',dest/'FL_STUDIO_RU.md',runtime/'fl20_curve.py',base_zip]:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP39',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],all60_training_and_validation_WAVs_remote_verified=True,prior_backup_commit=priorproof['commit'],two_cold_actual_full_chain_replay_errors=build['actual_two_cold_full_native_trim_chain_errors'],HTTP_checks=checks,all_old_kits_PC_GUI_original_and_private_refs_preserved=True,original_is_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (U/'ZL39_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
