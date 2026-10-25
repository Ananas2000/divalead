"""Publish current real-process evidence, generalized cascade and safe recovery notes."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo25_live_runtime_backup')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='save real active WIP25 cascade, generalized publisher and recovery notes'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID']
  assert h['alive'](pid)and str(A/'continue_stereo_ZL_matching.py').encode()in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0');assert Path(f'/proc/{pid}/stat').read_text().split()[21]==state['owner']['starttime']
  assert state['full_base_kit']=='ZL-WIP25'and state['fixed_post_SHA256']=='51dd979271b5fbfda5cffbd8cb71796009a5b3cc305289bbf9c472c672a7a96e'
  for host in state['actual_VST3_hosts']:assert h['alive'](host['PID'])and Path(f"/proc/{host['PID']}/stat").read_text().split()[21]==host['starttime']
  dest=PUBLIC/'ZL25-runtime-handoff-20261025';dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','verify_current_stereo_environment_runtime.py']:
   p=A/name;compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  tools=dest/'research_tools';tools.mkdir()
  for p in H.glob('*.py'):compile(p.read_text(),p.name,'exec');shutil.copyfile(p,tools/p.name)
  for name in ['ZL25_FULL_PUBLICATION.json','ZL25_BUILD_COMPLETION.json','LOWMID_RESEARCH_PUBLICATION.json','ADOPTED_FULL25_RUNTIME_CHECK.json','STEREO25_ACTUAL_STARTUP_RUNTIME_PROOF.json','ACTUAL_WIP25_CONTINUATION_START.json','OLD_PUBLIC_AUDIO_WORKTREE_CACHE_EVICTION.json','RUNTIME_UPGRADE_SYNTAX_PROOF.json']:
   shutil.copyfile(H/name,dest/name)
  shutil.copyfile(A/'stereo-continuous87/BEST_CANDIDATE.json',dest/'CURRENT_BEST_AT_HANDOFF.json');(dest/'ACTUAL_LIVE_TWO_STAGE_CONTROLLER.json').write_text(json.dumps(state,indent=2)+'\n')
  doc=f'''# ZL25: работающий поиск, два реальных ZL, восстановление

[Полный комплект ZL25, A/B и FLинструкция](../ZL25_CONTINUATION_RU.md).
В момент снимка PID{pid}, phase{state['phase']}, cohort{state.get('cohort')},
cases{state.get('cases')}. Проверены PID/starttime/cmdline главного процесса
и четырёх настоящих официальных VST3host. Снимок не доказывает будущую работу.

Текущий процесс: A/continue_stereo_ZL_matching.py,
A=/workspace/divalead-work/pc-stereo-20261024,
N=/workspace/divalead-work/native-low-latency-effects,
N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json и
A/stereo-continuous87/BEST_CANDIDATE.json — актуальные контроллер/кандидат.
D=/tmp/divalead-local-1625/internet-plugins-20261023,
W=/tmp/divalead-native-effects,B=/tmp/divalead-local-1625,
PYTHONPATH=A:D:W:B. Python /workspace/.venvs/divalead/bin/python -B,
OPENBLAS_NUM_THREADS=1,OMP_NUM_THREADS=1,PYTHONDONTWRITEBYTECODE=1.

Два worker по два реальных ZL. PRIMARY87параметров ищется, POST фиксируется
при старте из актуального BEST, SHA51dd979271b5fbfda5cffbd8cb71796009a5b3cc305289bbf9c472c672a7a96e.
POST содержит три Side AllPass10000Hz/Q2+2200Hz/Q4+895.8Hz/Q13.84.
Это два экземпляраZL, не три. Нельзя восстановить старый hardcodedPOST24.
Новый runtime и две его холодные цепочки проверены: replay0/0, exactbytes.
Новая generic startupпроверка verify_current_stereo_environment_runtime.py
--kit ZL-WIP25 --receipt /workspace/divalead-setup/STEREO25_ENV_STARTUP_PROOF.json
реально исполнялась: combinedZLPDC0/impulse0. Не ASIO/новыйGUI/всяDAW.

Прежний originalobjective, выравнивание819, tolerances и fresh6порог
max(.0005,3SEM), cold2positive сохранены. Дополнительная защита стерео:
upperRMSerror<=1.5dB,max|LR|<=1.6dB в2–5/5–10/10–14kHz;
после ZL25 ещё |LR300–800−original|<=3.35dB. Это extra preservation gate,
не изменение прежнего score. Низкая середина пока~4.2dBLeft vsoriginal~1dB.
Источник actualDiva281/native06/fine32/ADSR/ARP/3longnotes41→37→36twice
не меняется. Новые nativeDLLреализации используют сохранённый реальный
Divaисточник; новыеDivaэкземпляры/GUIэкспорты не заявляются. SoundmatchFALSE.

После принятого этапа автоматический publisher сохраняет все24WAVinput/
control/candidate lossless, оба компонента и полный небольшой playableZIP
FLP/FST/WAV/h2p/MIDI/инструкция. Он теперь читает artifact_layout.json
и full_public_kit_directory, сохраняет post25/его три полосы. Прежний singleZL
publisher это делать не умеет. Старые N/zl-continuation.stop и
zl-useful-full-backup.stop сowner two-ZL-stereo24-retired-single-stage
оставлены. Новый stop zl-stereo-continuation.stop, pause zl-stereo-numerical.pause;
не снимать чужой pause/stop. Root208MiB/tmp128MiB guards защищают backup.

На новом восстановлении сначала сверить актуальный start_skill_current.md
и живые PID/cmdline; не плодить процессы. Если A отсутствует, создать его и
скопировать пять scripts/*.py. Если BEST отсутствует, восстановить приложенный
CURRENT_BEST_AT_HANDOFF.json в A/stereo-continuous87/BEST_CANDIDATE.json,
проверить paths и соответствие primary/post сохранённому acceptedstage.
Не перезаписывать более новое существующее состояние. Нужны уже подготовленные
runtimehost/nativebase06/actualDivasource из сохранённого setup. На чистой новой
машине весь bootstrap этой стадии отдельно не исполнялся; это не fresh-taskproof.
Запускать только после реальных startup/statechecks. Не запускать старую
continue_ZL_matching.py/watcher. Исторический setup55 — readinessfixture,
его FinishVST с задержкой не является рабочей цепью.

В этой стадии освобождены только byte-verified локальные publicaudioкопии
и закрытые старые regenerableVSTscratch. Старые Gitверсии/refs/полныеZIP/PCGUI
не удалены. В рабочем publiccheckout могут отсутствовать WAV/ZIP сskipworktree;
это ожидаемый cache, восстанавливать выбранный файл через gitshow нужногоref.
Publicpromisorobjectcache тоже содержит ожидаемые старые holes. Избегать bulk
two-treegitdiff и ls-tree--long. Privateoriginalsource48/blob41e9bf7d7adba68226614297644c9661181bff6d
и его refs/archive/unpublished-pre-split-f3ed5c50 сохранены. No forcepush.
APIquotaпроцент недоступен; готовые полезные этапы сохраняются сразу.
До совпадения остаются различия. Продолжать, без вопросов по каждой пробе.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text('[ZL25: фактически запущенный поиск, защита стерео и восстановление](ZL25-runtime-handoff-20261025/README_RU.md).\n\n'+p.read_text())
  header='''BEGIN_ZL25_ACTUAL_TWO_STAGE_RUNTIME_20261025
Latest fullkit ZL25; runtime/recovery ZL25-runtime-handoff-20261025/README_RU.md. Current A=/workspace/divalead-work/pc-stereo-20261024, A/continue_stereo_ZL_matching.py, N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json, A/stereo-continuous87/BEST_CANDIDATE.json. TWOactualZL runtime nowfreezespostfromcurrentBEST, neverhardcodedpost24; current3SideAP10000Q2+2200Q4+895.8Q13.84. Primary87fit, postimmutable. UpperRMS<=1.5/maxLR<=1.6dB unchanged plus EXTRA lowmid300-800LRerror<=3.35dB. Originalobjective/819alignment/tolerances/fresh6max(.0005,3SEM)/cold2positiveunchanged. AutoacceptedcohortbackupALL24WAV+playableFL20ZIP generalizedfull_public_kit_directory/artifact_layout.json; no lostpost. Actual2newcoldruntime replay0/0 andgenericstartupbothcomponentsPDC0/impulse0, notGUI/ASIO. SourceDiva281/native06/fine32/3longincomingnotes/ARP/ADSRunchanged. Actual4hostPID snapshotnotperpetualclaim; checklivecontroller. Legacy-singleZL stopfilesremain, onlynewzl-stereo controlsapply. PublicoldaudioWAV/ZIPworktreecopiesbyteverifiedandskipworktreeoffloaded719714320logicalbytes, allGitversions/refspreserved. Current25audio/presets/nativebase/privatecapturessurvive. Standardpublicpromisorcacheoldholesexpected, fetchspecificfilesonly; nobulk2treegitdiff/ls-tree--long. Snapshotsetuprestorationnotfreshmachineverified. FullmatchFALSE, noMistaTowa/pertrialquestions, APIquotapercentageunknown, backfinishedstagesprogressively.
END_ZL25_ACTUAL_TWO_STAGE_RUNTIME_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve actual WIP25 continuation with fixed three-band post and generalized complete backups');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),actual_main_PID=pid,actual_four_ZL_hosts_verified_at_snapshot=True,all_previous_kits_and_PC_GUI_tree_preserved=True,reference_match_reached=False)
  (H/'STEREO25_RUNTIME_HANDOFF_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
