"""Preserve current real original-target continuation and the rejected WS51 screen."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');WS=Path('/tmp/divalead-original-target-native-WScontrols-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='full26_original_target_actual_runtime')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
assert read(WS/'completion.json')['training_cases']==51 and not read(WS/'completion.json')['robust_improvement'];deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='back up actualoriginal-onlyfull26continuation and51case rejectednativeWSscreen'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID'];assert state['original_is_the_only_target']and state['full_base_kit']=='ZL-WIP26'
  assert state['fixed_post_SHA256']=='195e46104902cd1d5140104e8d951c859ee9ec8b1e2bb9890ce68e0597538688'
  assert str(A/'continue_stereo_ZL_matching.py').encode()in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
  for row in [state['owner'],*state['actual_VST3_hosts']]:
   p=Path('/proc')/str(row['PID']);stat=(p/'stat').read_text().split();assert stat[2]!='Z'and stat[21]==row['starttime']
  dest=PUBLIC/'ZL26-original-target-runtime-and-WS51';dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','verify_current_stereo_environment_runtime.py']:
   p=A/name;compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  for name in ['study_native_WS_controls_original_two_ZL.py','adopt_and_check_full26_runtime.py','start_actual_full26_original_target_continuation.py','publish_full26_original_target_runtime_and_WS51.py']:shutil.copyfile(H/name,scripts/name)
  for name in ['completion.json','FROZEN_BEFORE_FRESH_VALIDATION.json','TRAINING_RESULTS.json.gz']:shutil.copyfile(WS/name,dest/('WS51_'+name))
  for name in ['ADOPTED_FULL26_RUNTIME_CHECK.json','ACTUAL_FULL26_ORIGINAL_TARGET_START.json','STEREO26_ACTUAL_STARTUP_RUNTIME_PROOF.json','ZL26_FULL_PUBLICATION.json']:shutil.copyfile(H/name,dest/name)
  (dest/'ACTUAL_LIVE_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n');shutil.copyfile(A/'stereo-continuous87/BEST_CANDIDATE.json',dest/'CURRENT_BEST_AT_HANDOFF.json')
  doc=f'''# ZL26: подбор к оригиналу на нормальной обработке продолжается

[Полный WIP26, A/B и инструкция FLStudio](../ZL26_CONTINUATION_RU.md).
Цель — загруженный оригинальный WAV. v83/Finish только историческая диагностика;
они не служат целью/прокси или эффектом. В actualcontroller это записано явно,
а исходный referenceSHA2567617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f
проверяется при запуске. Все прежние веса/fresh6/cold2/819alignment/tolerances
и дополнительные stereo-guards сохранены.

На момент снимка главный PID{pid}, phase{state['phase']},cohort{state.get('cohort')},
cases{state.get('cases')}. Реально проверены PID/starttime/cmdline и четыре ZLVST3host.
Это снимок момента, не утверждение вечнойработы. A=/workspace/divalead-work/pc-stereo-20261024;
актуальны A/continue_stereo_ZL_matching.py, N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json
и A/stereo-continuous87/BEST_CANDIDATE.json, N=/workspace/divalead-work/native-low-latency-effects.

Два worker по два настоящих ZL: PRIMARY подбирается, POST фиксируется изBEST.
POST26: три SideAP10000Hz/Q2+2200Hz/Q4+895.8Hz/Q13.84 и один StereoAP783.2Hz/Q19.422.
ЕгоSHA195e46104902cd1d5140104e8d951c859ee9ec8b1e2bb9890ce68e0597538688.
Это два экземпляраZL,не4. Native06/fine32/Diva281/ARP/ADSR/три длинные входящие
ноты41→37→36дважды/маршруты прежние. Оба компонента exactbytesroundtrip,
два coldкаскада нового runtime replay0/0; actualstartup PDC0/impulse0 проверен.
Полный26ZIP отдельно прошёл CRC/SHA/два новых coldactualcascade0/0.
Это не открытие новогоFLPвWindowsGUI/ASIO/полная новаямашина. FullmatchFALSE.

После26 проверен51настоящий вариант Preamp/Mix/Post штатного FruityWaveShaper.
Для каждой пробы загружается исходный canonicalWSstate с точной кривойfine32,
меняются только3rawконтроля; остальные11native иобаZL фиксированы. Четыре
nativeреализации на пробу,контроль8; три лучших повторно по8. Подтверждённого
выигрыша нет, ни одна настройка не принята. Fresh6/cold2/exportне запускались,
посколькуscreenнепрошёл. Все51настройка/оценки иfrozenproof здесь; это не архив
всехtrialWAV. Рендеры действительно выполнялись, scratch перезаписывался.
Исходники/h2p/новаяполнаяDivaэкспортаэтим исследованием не заявляются.

Автоматический checkpointpublisher сохраняет каждый принятый этап: все24
native-input/control/candidateWAVlossless, оба состояния, полный playableFL20ZIP
сFLP/WAV/MIDI/h2p/FST/инструкцией. Он читает full_public_kit_directory/layout и
сохраняет все4полосыPOST; описание теперь учитывает иSide,иStereo. Старый
singleZLmatcher/watcher оставлены выключенными черезownedlegacySTOP.
Root208MiB/tmp128MiB резервы защищаютbackup; APIquota%недоступен.

Восстановление: сначала проверить актуальный start_skill_current.md иlivePID,
не создавать дубль. ЕслиA отсутствует,скопировать5runtime scripts/*.py, BEST
изCURRENT_BEST_AT_HANDOFF.json толькоеслион отсутствует ипослепроверки путей.
Не перезаписывать более новое work. D=/tmp/divalead-local-1625/internet-plugins-20261023,
W=/tmp/divalead-native-effects,B=/tmp/divalead-local-1625, PYTHONPATH=A:D:W:B,
OPENBLAS_NUM_THREADS=1,OMP_NUM_THREADS=1,/workspace/.venvs/divalead/bin/python -B.
Нужен уже подготовленный native06/source/WinVST3runtime. Полный fresh-machine
bootstrapэтойстадии отдельно не заявляется. Genericstartuphelper default26,
для25/старыхfixtures явно передавать --kitZL-WIP25 с пробелом после --kit.
Новый stopN/zl-stereo-continuation.stop, pausezl-stereo-numerical.pause;
не снимать чужиеownedфайлы. LegacyN/zl-continuation.stop и
zl-useful-full-backup.stop сownertwo-ZL-stereo24-retired-single-stage сохраняются.

Все старыеfullkits/PCGUI/privateoriginalsource48иrefsсохранены. Publicarchive
cacheможет бытьoffloaded(skipworktree/promisorholes), все байты остаютсяGit;
восстанавливать выборочно. Не использоватьbulk2treegitdiff/ls-tree--long.
Оригинал только дляанализа/A-B, безподмешивания; MistaTowaнеиспользуется.
Продолжать к оригиналу, не к старому Finish и не выдавать WIPза совпадение.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text('[ZL26: текущий original-only подбор, runtime, автоматические backups и WS51проверка](ZL26-original-target-runtime-and-WS51/README_RU.md).\n\n'+p.read_text())
  header='''BEGIN_ZL26_ORIGINAL_TARGET_LIVE_RUNTIME_20261025
Usertarget ORIGINAL WAVwithnormal lowlatencyFX, NOTv83/Finish. Latestfull26, readZL26_CONTINUATION_RU.md and ZL26-original-target-runtime-and-WS51/README_RU.md. CurrentA/continue_stereo_ZL_matching.py ORIGINALonlyflag+uploadedrefSHAchecked; A=/workspace/divalead-work/pc-stereo-20261024,N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json,BEST=A/stereo-continuous87/BEST_CANDIDATE.json. Actualmainresumedafterallfinitechecks, snapshotcheckrealPID/starttime, NOTeternalclaim. TWOworkers*TWOactualofficialZL=4hosts. NewPOST26SHA195e46104902cd1d5140104e8d951c859ee9ec8b1e2bb9890ce68e0597538688 contains3SideAP+StereoAP783.2Q19.422, notsingleZL or4instances. FrozenfromcurrentBEST. Actualruntimecold2replay0/0 andstartupstate/PDC0/impulse0 verified; noGUI/ASIO/newmachineclaim. SourceDiva281/native06/fine32/ARP/ADSR/3incominglongnotesunchanged. Subsequent51actualnativeWSPreMixPostvariants no confirmedoriginalgain, rejected/noexport. Originalobjective/fresh6max(.0005,3SEM)/cold2positive/strict8eps/1e-12 andnative2e-7 unchanged. Upper1.5RMS/1.6absLR pluslowmid3.35error extra guards unchanged. Autoacceptedcheckpointpublisher generalizedlayout/full_public_kit_directory andbothSide/StereoPOSTmetadata, all24WAV+playableFL20ZIPGit. RetiredsingleZLstopsstay; originalfiniteownedSTOPclearedafteractualfull26adoptionchecks. CurrentstartscriptH/start_actual_full26_original_target_continuation.py is historicalfinishedfinitehandoff, doNOTrerununcheckedagainstnewerBEST; H=/workspace/divalead-work/stereo-refinement-20261025. FullmatchFALSE/APIquota%unknown/backupfinishedstagesprogressively/noMista/referenceinsynthesis/pertrialquestions. Preserveoldkits/PCGUI/privateoriginalsource48/allrefs, oldpublicpromisorholesexpected, nobulk2treegitdiff/ls-tree--long.
END_ZL26_ORIGINAL_TARGET_LIVE_RUNTIME_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve actual ZL26 original-only matching, four-band POST runtime and rejected WS51 screen');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),actual_main_PID_at_snapshot=pid,original_is_the_only_target=True,WS51_not_adopted=True,reference_match_reached=False)
  (H/'ZL26_ORIGINAL_TARGET_RUNTIME_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
