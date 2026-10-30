"""Publish the strict12-qualified full38 and its independently restored FL20 kit."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
T=Path(__file__).resolve().parent;H=T.parent/'stereo-refinement-20261026';O=T.parent/'stereo-refinement-20261025';A=T.parent/'pc-stereo-20261024';Q=T/'JOINT109_AIR_MARGIN_REPAIR'
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_cold_verified_full38');P,N,C,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git=h['git'];build=json.loads((T/'ZL38_BUILD_COMPLETION.json').read_text());kit=Path(build['root']);archive=Path(build['ZIP']);s=json.loads((Q/'completion.json').read_text());priorproof=json.loads((O/'original-joint109-Air-margin-positive_PUBLICATION.json').read_text());assert s['robust_improvement']and priorproof['all_retained_study_files_and_WAVs_remote_Git_verified'];assert build['actual_two_cold_ZL_replay_errors']==[0.,0.]and build['actual_two_cold_full_native_trim_chain_errors']==[0.,0.];assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256'];assert json.loads((N/'zl-stereo-continuation.stop').read_text())['owner']=='complete-WIP38-joint109-20261030';pause=C/'auto-backup.pause';deadline=time.monotonic()+600
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish complete strict12/coldZIP-qualified native13/twoZL38 WIP'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);latest=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert latest['source_accepted_cohort']==413;assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
  dest=PUBLIC/'ZL-WIP38';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-joint109-full38';research.mkdir();scripts=research/'scripts';scripts.mkdir();runtime=research/'current-runtime';runtime.mkdir()
  for p in Q.iterdir():
   if p.is_file()and p.suffix in['.json','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for name in ['ZL38_BUILD_COMPLETION.json','FULL38_INPUT_AND_COLD_PROOF.json','CLOSED_VALIDATION_ARCHIVES_TEMPORARY_STAGING.json','413_AB_AND_RESTORED_RUNTIME_PUBLICATION.json']:shutil.copyfile(T/name,research/name)
  shutil.copyfile(O/'original-joint109-Air-margin-positive_PUBLICATION.json',research/'ALL_REPAIRED_REAL_WAV_PUBLICATION.json');shutil.copyfile(O/'original-primary-post109-extra-Air-not-adopted_PUBLICATION.json',research/'PARENT_REAL_WAV_PUBLICATION.json')
  for name in ['build_complete_original_wip38.py','prepare_full38_inputs_and_cold_proof.py','publish_complete_wip38.py','adopt_and_check_full38_runtime.py','restart_current_full38_matching.py','repair_joint109_air_margin.py','Joint109_air_margin_support.py','study_joint_primary_post109_current413.py','Joint_primary_post109_support.py','joint_primary_post_fit.py','restore_tmp_audio_runtime.py','backup_joint109_and_repaired_positive.py']:shutil.copyfile(T/name,scripts/name)
  for name in ['native_post_trim.py','check_current_original_chain_readiness.py','start_native_headless_display.py','normal_staged_primary_fit.py','checked_mean_three_real_primary_fit.py']:shutil.copyfile(H/name,scripts/name)
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
  for source in [Path('/tmp/divalead-local-1625/fl20_curve.py'),O/'backup_complete_finite_study.py',O/'bounded_git_audio_backup.py']:shutil.copyfile(source,runtime/source.name)
  intro='''# ZL38 WIP — проверенный совместный подбор двух ZL

- [Полный ZIP для FL Studio20](ZL-WIP38/Diva_ZL38_STEREO_WIP_complete.zip).
- [A/B: оригинал →413→38](ZL-WIP38/AB_ORIGINAL_413_ZL38_WIP.mp3).
- [FLAC](ZL-WIP38/AB_ORIGINAL_413_ZL38_WIP.flac).
- [Инструкция FL Studio](ZL-WIP38/FL_STUDIO_RU.md).
- [Все реальные WAV и проверочные данные](original-joint109-Air-margin-positive/README_RU.md).

Полного совпадения нет. Сохранены источник Diva, три длинные входящие ноты, ARP/ADSR/native12/WS52/маршруты и последний Stereo Shaper. Заново настроены ОБА ZL; новых фильтров и плагинов нет. Отдельная малая коррекция сохранила выигрыш и прошла строгий нерастущий Air,12новыхпар и оба cold. Полный ZIP независимо восстановлен и отрендерен0/0. Это проверка настоящих DSP-хостов, не WindowsGUI/ASIO или слуховой процент. Подробнее ниже.

''';doc=intro+(kit/'FL_STUDIO_RU.md').read_text();(PUBLIC/'ZL38_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP38/','](../ZL-WIP38/').replace('](original-joint109-Air-margin-positive/','](../original-joint109-Air-margin-positive/'))
  (PUBLIC/'LATEST_THREE_NOTE_RU.md').write_text('''# Следующий проверенный трёхнотный вариант — WIP38

[Полный ZIP](ZL-WIP38/Diva_ZL38_STEREO_WIP_complete.zip), [инструкция FL Studio20](ZL-WIP38/FL_STUDIO_RU.md), [A/B оригинал →413→38](ZL-WIP38/AB_ORIGINAL_413_ZL38_WIP.mp3). В A/B38 начинается с8.336с. Для сравнения48000Hz/180BPM. Загружаются оба новых ZL-пресета либо полный проект.

Источник и три длинные ноты прежние, только обычные эффекты. Полного совпадения пока нет. [Подробные проверки и ограничения](ZL38_CONTINUATION_RU.md). [Предыдущая413](stereo-cascade87-cohort-0413/README_RU.md) сохранена. Текущую активность подбора определяет фактический контроллер; эта страница не обещает будущую работу процессов.
''');p=PUBLIC/'README_RU.md';p.write_text('[WIP38: полный трёхнотный FL20 комплект, A/B с оригиналом и инструкция](ZL38_CONTINUATION_RU.md). Полного совпадения нет.\n\n'+p.read_text());startup=(T/'start_skill_full38_prepublication.md').read_text();(research/'CLOUD_START_PREPUBLICATION_SNAPSHOT.md').write_text(startup);(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL38 WIP, joint primary/post fit and nonincreasing-Air repair');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_413_ZL38_WIP.mp3',dest/'FL_STUDIO_RU.md',research/'FULL38_INPUT_AND_COLD_PROOF.json',runtime/'native_post_trim.py']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP38',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],all_training_and_validation_WAVs_remote_verified=True,prior_backup_commit=priorproof['commit'],two_cold_actual_full_chain_replays=[0.,0.],HTTP_checks=checks,all_old_kits_PC_GUI_original_and_private_refs_preserved=True,original_is_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(T/'ZL38_FULL_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
