"""Back up the actual running two-ZL continuation and recovery instructions."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
A=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo24_runtime_handoff')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve actual two-instance running matcher and recovery scripts'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID'];assert h['alive'](pid)and str(A/'continue_stereo_ZL_matching.py').encode()in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0');assert Path(f'/proc/{pid}/stat').read_text().split()[21]==state['owner']['starttime']
  for host in state['actual_VST3_hosts']:assert h['alive'](host['PID'])and Path(f"/proc/{host['PID']}/stat").read_text().split()[21]==host['starttime']
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('ZL24-runtime-handoff-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  names=['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','verify_stereo24_environment_runtime.py','evict_only_verified_published_local_copies.py','evict_only_verified_published_local_copies_second_pass.py','cleanup_closed_trial_scratch.py','publish_stereo24_runtime_handoff.py']
  for name in names:compile((A/name).read_text(),name,'exec');shutil.copyfile(A/name,scripts/name)
  for name in ['ZL24_FULL_PUBLICATION.json','STEREO24_MATCHING_START.json','STEREO24_MATCHING_RESTART_AFTER_CACHE_EVICTION.json','PUBLISHED_LOCAL_KIT_COPY_EVICTION.json','PUBLISHED_LOCAL_KIT_COPY_EVICTION_SECOND_PASS.json','FINAL_ZIP_CACHE_ONLY_EVICTION.json','STEREO24_ENVIRONMENT_RUNTIME_PROOF.json']:
   p=A/name
   if p.exists():shutil.copyfile(p,dest/name)
  (dest/'ACTUAL_LIVE_TWO_INSTANCE_CONTROLLER.json').write_text(json.dumps(state,indent=2)+'\n');shutil.copyfile(A/'stereo-continuous87/BEST_CANDIDATE.json',dest/'CURRENT_BEST_AT_HANDOFF.json')
  doc=f'''# Продолжение ZL24: настоящий двухступенчатый поиск работает

Последний полный проверенный комплект и A/B: [ZL24](../ZL24_CONTINUATION_RU.md).
Четыре настоящих ZL VST3процесса:2worker, каждый основной ZL + фиксированный
Side-only post2200Гц/Q4 и10000Гц/Q2. На момент снимка главный PID{pid},
phase{state['phase']},cohort{state.get('cohort')},cases{state.get('cases')}.
Проверять актуальный N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json и реальные
PID/starttime/cmdline; snapshot не доказывает вечную работу процесса.

ROOT=/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87.
Actual script /workspace/divalead-work/pc-stereo-20261024/continue_stereo_ZL_matching.py.
Не перезапускать устаревшие singleZL continue_ZL_matching.py/watcher:
N/zl-continuation.stop и zl-useful-full-backup.stop оставлены с owner
two-ZL-stereo24-retired-single-stage. Новый stop — N/zl-stereo-continuation.stop,
новый numericalpause — N/zl-stereo-numerical.pause; не снимать чужие ownedстопы.

Поиск меняет87физических параметров только основного ZL, postфиксирован.
Тот же originalFeatures score/weights/819alignment/thresholds/coldrtol8eps
иatol1e-12. Дополнительная защита исправленного стерео: upperbandRMSerror<=1.5дБ,
|LR|<=1.6дБ по2–5/5–10/10–14кГц. Это отдельный gate, не подмена исходногоscore.
Три nativetrainingвхода,2heldout,6новых nativeпар на сохранённом Divaисточнике,
2положительных coldnativeвхода, два coldVSTкаскада и statebytes roundtrip.
Источник/Diva281/native06/fine32/ARP/ADSR/три длинные входящие ноты не меняются.

Каждый устойчивый принятый этап автоматически сохраняется в GitHub: все24
native-input/control/candidate WAV lossless+SHA, компонентprimary+точныйpost,
полный небольшой playable FL20/26 ZIP (FLP/WAV/h2p/MIDI/всеpresets/инструкция).
Эти numerical checkpoints не обозначают новое GUIподтверждение или полное
совпадение. Прежний полный base24 и старые GUI/полные комплекты защищены OID.
Все предыдущие52WAV исходного исследования сохранены в Git.

Перед остановкой Root208MiB/tmp128MiB резервируются для безопасного backup.
Большой archive в рабочем checkout жёстко ссылается на завершённый privateархив,
не копируется зря. После push обе рабочие копии выгружаются только при exactGit
проверке; publicstructuralpromisorgraph сохраняется, blobcache может быть удалён.
Git скачивает архив по требованию. Все refs и privateoriginalsource48 сохранены.
Не выполнять bulk two-treegitdiff/ls-tree--long: они повторно тянут старый кэш.
APIquota% недоступен; законченные полезные этапы сохраняются сразу.

Первая попытка запуска корректно остановилась на Root207.6MiB, поэтому были
выгружены только проверенные опубликованные локальные копии. Не удалены текущие
presets/components/WAV/native06/GUIinputs. Отдельно удалён ТОЛЬКО собственный
unreachable ZIP неудачного stagingдо TSV-formatfix; он никогда не публиковался.
Текущий ZIP16MB доступен на GitHub SHA368fc6eaa7d9b1d8effbcfb5bebe1f2e7530f98904718f510ae0e783180ad9da,
его рабочий cache skipworktree может отсутствовать. Восстанавливать выборочно.

CloudLinux/Wine; новое открытие/экспорт24 в Windows GUI не выполнялось. На ПК
предыдущий GUI ZL23 остаётся отдельным сохранённым файлом. Для загрузки нового
см. инструкцию полного24, два ZL не сводить в один. Полного совпадения пока нет;
продолжать с сохранением улучшенного баланса до совпадения либо фактических лимитов.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text(f'[ZL24: текущий работающий TWO-ZL поиск, автоматические полные backups и восстановление]({dest.name}/README_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_ZL24_ACTUAL_TWO_INSTANCE_RUNTIME_{stamp}
Latest complete kit remains ZL24, actual cascade runtime backup {dest.name}/README_RU.md and scripts. CURRENT matcher A/continue_stereo_ZL_matching.py, N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json, A/stereo-continuous87/BEST_CANDIDATE.json, A=/workspace/divalead-work/pc-stereo-20261024.2workers*2actualVST3=4processes, primary87params/postSide2200Q4+10000Q2 FIXED. New stereo gate RMS<=1.5dB andmax|LR|<=1.6dB bands2-5/5-10/10-14kHz, originalscore andtolerancesUNCHANGED. Freshnative6+positivecold2, whole2ZLcoldreplay andbytes. Acceptedstages autoGit ALL24WAV/rawinputs + fullplayableFLP/FST/WAV/h2p/MIDI ZIP. No newGUI/nativeDiva-source-instance claim or fullsoundmatch. OldsingleZLmatcher/watcher retired viaowned legacySTOPs; newstop N/zl-stereo-continuation.stop,newpause zl-stereo-numerical.pause. Read actualPID/starttime/cmdline, not stale snapshots. Root208MiB/tmp128MiB guards. Largepublicproof archives on-demandGitcache expectedholes; preserveallrefs/privateoriginalsource48, avoidbulk two-treegitdiff/ls-tree--long. Useraskscontinue/no pertrialquestions. APIquota5/10% unavailable, backfinishedstages progressively. Current setupneedsTWO-ZL-aware startup/runtime, oldsingleZL builder cannot preservepost. Allsource281/native06/fine32/threeincomingnotes/ARP/ADSR unchanged.
END_ZL24_ACTUAL_TWO_INSTANCE_RUNTIME_{stamp}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve live two-instance ZL24 continuation, stereo guards and automatic complete WIP backups');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),actual_main_PID=pid,old_kits_PC_GUI_and_private_data_preserved=True,reference_match_reached=False);(A/'STEREO24_RUNTIME_HANDOFF_PUBLICATION.json').write_text(json.dumps(r,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(r),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
