"""Save actual current accepted state, native context handoff and diagnostics."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,runpy,shutil,subprocess
D=Path(__file__).resolve().parent
s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='joint_checkpoint_helpers')
P=s['P'];N=s['N'];R=s['R'];PUBLIC=s['PUBLIC'];BASE=s['BASE'];git=s['git'];read=s['read']
pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve latest actual native-context handoff and accepted real ZL renders'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');s['fetch_main']();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True);before=git('rev-parse','HEAD');old=s['protected']()
  latest=read(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json');code=latest['full_kit'][-2:];best=read(D/'ZL-continuous65/BEST_CANDIDATE.json');component=Path(best['native_ZL_component_state']);completion=read(component.parent/'completion.json');assert completion['robust_improvement']
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('joint-native-ZL-continuation-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  s['copy_evidence'](component.parent,dest/'current-accepted-private-best',True);(dest/'BEST_CANDIDATE_COMPONENT_AUTHORITATIVE.json').write_text(json.dumps(best,indent=2)+'\n')
  s['copy_evidence'](D/'ZL-current-signed-band-diagnostics-01',dest/'signed-original-band-diagnostics')
  handoff=dest/'native-context-cycle02-final-handoff';handoff.mkdir()
  for p in (D/'ZL-native-base-rebase-adoption-02').iterdir():
   if p.is_file()and p.suffix in ['.json','.bin']:shutil.copyfile(p,handoff/p.name)
  (handoff/'PREVIOUS_FULL_PAIRED_WAV_BACKUP.json').write_text(json.dumps(dict(already_published_all24_validation_WAVs='native-final-context02-current-main-revalidation/TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz',original_reference_match_reached=False),indent=2)+'\n')
  for name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','backup_current_joint_ZL_checkpoint.py','backup_finite_ZL_study.py','study_native_Chorus9_with_ZL.py','diagnose_current_signed_band_residuals.py','prepare_native_base_for_combined_ZL.py','package_verified_native_base.py','study_native_EQ_with_ZL_cycle02.py','study_native_WS_with_ZL_cycle02.py','run_native_ZL_context_cycle02.py','adopt_native_ZL_context_cycle02.py']:
   p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
  for name in ['evict_origin_verified_old_study_archive_worktree.py','pack_current_audio_objects_in_small_verified_batches.py','discover_current_workspace_repositories.py']:shutil.copyfile(N/name,scripts/name)
  receipts=['NATIVE_CONTEXT02_MATCHER_AND_FULL_BACKUP_RESTART.json','CONTEXT02_FULL_BACKUP_STARTUP_RACE_FIXED.json','ZL14_TRANSIENT_PUSH_RECOVERY.json','OLD_COMPLETED_STUDY_WORKTREE_PROOF_EVICTION.json','CURRENT_BOUNDED_LOSSLESS_AUDIO_GIT_PACKING.json','CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json']
  for name in receipts:
   p=N/name
   if p.exists():shutil.copyfile(p,dest/name)
  states={name:read(N/name)for name in ['FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json','ZL_NATIVE_CHORUS9_CONTEXT_STUDY_STATE.json','NATIVE_ZL_CONTEXT_CYCLE02_STATE.json','NATIVE_ZL_CONTEXT_CYCLE02_ADOPTION_STATE.json']};main=states['FL20_ZL_CONTINUOUS_CONTROLLER.json'];watch=states['ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json'];assert s['alive'](main['owner']['PID'])and s['alive'](watch['PID']);(dest/'ACTUAL_CONTROLLER_SNAPSHOTS.json').write_text(json.dumps(states,indent=2)+'\n')
  doc=f'''# Совместный native + ZL: текущее продолжение

Полного совпадения с исходным WAV пока нет. Три длинные входящие ноты
41→37→36 на фразу, дважды; высотное движение делает ARP Diva.

Полный пользовательский комплект на момент этого сохранения —
[ZL{code}: ZIP с FLP/WAV/Diva/MIDI/17FST/VSTpreset/проверками](ZL-WIP{code}/Diva_ZL_{code}_WIP_complete_WIP.zip),
[A/B: оригинал0с → ZL{code} с4,168с](ZL-WIP{code}/AB_REFERENCE_ZL{code}_WIP.mp3),
[инструкция FL Studio20 и официальный бесплатный эквалайзер](ZL-WIP{code}/FL_STUDIO_RU.md).
Экспорт6 mean{latest['original_objective_export_mean']:.9f}; независимая
распаковка и ещё6 фактических рендеров mean{latest['ZIP_replay_mean']:.9f}.
Это прежний критерий по полному оригиналу, не процент сходства.

Второй совместный подбор штатного EQ76 и WaveShaper16 подтвердился на
12 новых полных парах против актуального main:1.372868212→1.356668817,
SEM0.000460035. Принят только после отдельного nativeэкспорта, сохранения
новой базы FL20_NATIVE_ZL_REBASED_02, сборки полного ZL15, независимого
разбора контейнеров/распаковки/ещё6 реальных рендеров и Gitpush.
Обязательна именно choice.native_base_export_directory, также архив базы
в rebased-native-bases/. Нельзя возвращаться к старой Native17/base01.
Сохранять все2+4+8 поправок кривой WaveShaper, настоящий Diva effGetChunk,
native12state bytes и ZL component/610physicalreadbacks. Источник Diva не менялся.

После этого продолжается подбор87 реальных параметров ZL:
12staticPeak+4AllPass+6dynamicPeak+OutputGain. Новые входные рендеры,
2heldout,6 свежих пар, robust>max(0.0005,3SEM), реальные componentroundtrip
и2 новых coldinstances. Все12 контрольных/кандидатских WAV каждого принятого
этапа сохраняются lossless с SHA256. Текущий принятый private mean
{best['loss']:.9f}; его фактический компонент/полные проверки также сохранены здесь.
Случайный Chorus меняет отдельные WAV, поэтому нельзя выбирать по одному дублю.

Дополнительное исследование Chorus9:205 actualcases,12 новых пар,
1.349682597→1.348760460, SEM0.000698212. robust=False: кандидат НЕ принят.
Все проверки сохранены в native-Chorus9-current-ZL-context-study/.
Signedbanddiagnostics показывают избыток межгармонической энергии3.5–6.5kHz,
дефицит выше6.5kHz при близких самих гармониках; простой общий highcut не
устранит обе разницы. Межгармоническая энергия включает модуляцию/хвосты/
спектральную утечку, это не измерение только шума.

Заявленная ZL PDC0/импульсный первый отклик0 проверены реальным VST3.
Nativeтракт:первый отклик2samples, blockvariants имеют небольшой записанный
ненулевой остаток. Это не ASIO/всяDAW задержка. GUIFL20 на ПК здесь недоступен,
нового FLGUIоткрытия/экспорта, субъективного прослушивания и точного совпадения
не заявляется. Исходный WAV используется только для анализа/A-B, не для синтеза.

Запуск автосохранения после handoff исправлен: watcher теперь ждёт новый
фактический matcher при ещё старом stoppedcontroller. Сетевые503 повторяются
ограниченным числом обычных fetch/push/HTTP, без forcepush. ZL14push восстановлен,
HTTPbytes подтверждены. SnapshotPIDmain{main['owner']['PID']}/backup{watch['PID']}
проверять по /proc/starttime; снимок не доказывает работу после остановки среды.

Локальные копии опубликованных старых proofархивов выгружены после побайтного
сравнения с origin; git restore --ignore-skip-worktree-bits -- path возвращает
нужный файл. Все версии/история/Gitобъекты/selectedWAV/полные комплекты сохранены.
Дополнительно Gitобъекты lossless упакованы небольшими проверенными пакетами,
connectivity и неизменность release-tree OID подтверждены. Журналы приложены.
Процент сервисного лимита API не показывает; пользователь просит backup при5%
остатка, поэтому все проверенные этапы публикуются сразу по готовности.
'''
  (dest/'README_RU.md').write_text(doc);(PUBLIC/'CURRENT_JOINT_ZL_CONTEXT_RU.md').write_text(doc);p=PUBLIC/'README_RU.md';p.write_text('[Текущий совместный подбор, новая база02 и сохранённые проверки](CURRENT_JOINT_ZL_CONTEXT_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_CURRENT_JOINT_ZL_CONTEXT_{stamp}
Read CURRENT_JOINT_ZL_CONTEXT_RU.md first. Latest complete public kit at snapshot ZL{code}, export6mean{latest['original_objective_export_mean']:.9f}, independentZIP6mean{latest['ZIP_replay_mean']:.9f}; not an exact match. Native base MUST be FL20_NATIVE_ZL_REBASED_02 from choice.native_base_export_directory and rebased-native-bases verified archive, not prior base01/Native17. Final full paired12 revalidation1.372868212->1.356668817 SEM.000460035, actual native/FLP/states/ZIP replay before adoption into main. Keep all2+4+8WS metadata/sourceDiva/current610actualZLcomponent, same three held41/37/36 twice/internalARP. NativeChorus9 study205cases final12pairs robustFALSE (1.349682597->1.348760460 SEM.000698212), DO NOTADOPT it; current main nativebase02 retained. Main87param actualmatcher running PID{main['owner']['PID']}, fullkitwatcher PID{watch['PID']} at snapshot, check realPID/starttime/phase. Startup watcher race fixed by actual new main process discovery before trusting stale stoppedcontroller; bounded normal fetch/push retries for transient503 added. Currentprivate{best['loss']:.9f}/all12pairedWAV/component backed in {dest.name}. Signedanalysis is analysis-only; offharmonic excess3.5-6.5k/deficitabove6.5k, not pure noise. Rootreserve64MiB/tmp112MiB main,192/180fullbackups; user wants until limits andGit at5% butAPIpercent unavailable, publish stages progressively. NoGUIFL/humanaudition/exactmatch/wholeDAWlatencyclaim. Oldpublicstudyproofworktreecopies now skip-worktree after exactorigincomparison; restore individually with --ignore-skip-worktree-bits, do not restoreeverything. Gitobjects/history/versions allretained, bounded verifiedaudio packs only redundantloosecopiesremoved/connectivitypassed. Prior snapshots may be obsolete; highest latest-current header/publication receipt takes priority. No per-trial questions.
END_CURRENT_JOINT_ZL_CONTEXT_{stamp}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md');s['aggregate']();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines());git('commit','-m','Preserve native base02 handoff, rejected Chorus9 proof, current87 matching and verified storage journals');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items());s['push_and_confirm'](commit);assert not git('status','--porcelain')
  receipt=dict(commit=commit,previous_HEAD=before,last_complete_kit='ZL'+code,current_private_mean=best['loss'],main_PID=main['owner']['PID'],backup_PID=watch['PID'],all_old_full_kit_tree_OIDs_preserved=True,public_path=dest.relative_to(P).as_posix(),reference_match_reached=False);(N/'CURRENT_JOINT_NATIVE_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
