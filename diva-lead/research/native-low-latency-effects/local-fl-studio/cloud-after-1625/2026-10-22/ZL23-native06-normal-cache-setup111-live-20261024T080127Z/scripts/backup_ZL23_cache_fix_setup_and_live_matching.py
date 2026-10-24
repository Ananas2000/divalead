"""Checkpoint current accepted audio, reproducible setup and normal Git cache fix."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
D=Path(__file__).resolve().parent
S=Path('/workspace/divalead-setup')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='current_ZL23_checkpoint')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']]
git,read=h['git'],h['read']
OWNER='authorized-local-backed-copy-cleanup-20261023'
pause=R/'auto-backup.pause'
if pause.exists():raise SystemExit('Another publisher owns the pause; no files changed. Retry when completed.')
with pause.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='preserve full23 adoption, corrected normal Git cache workflow, setup111 and actual matching'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert not git('status','--porcelain')
  h['fetch_main']()
  subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');protected=h['protected']()
  pub=read(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json');assert pub['full_kit']=='ZL-WIP23'
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
  dest=PUBLIC/('ZL23-native06-normal-cache-setup111-live-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  best=read(D/'ZL-continuous65/BEST_CANDIDATE.json')
  assert best['native_base_export_directory'].endswith('_06')
  h['copy_evidence'](Path(best['native_ZL_component_state']).parent,dest/'current-accepted-component-and-renders',True)
  (dest/'BEST_CANDIDATE_COMPONENT_AUTHORITATIVE.json').write_text(json.dumps(best,indent=2)+'\n')
  h['copy_evidence'](D/'actual-ZL-parameter-boundary-probe-20261024',dest/'actual-plugin-parameter-range-probe')
  names=['VERIFIED_GIT_PROMISOR_AUDIO_CACHE_PROBE.json','VERIFIED_REMOTE_GIT_AUDIO_BLOB_CACHE_EVICTION.json','REFETCHED_GIT_CACHE_FIX_AND_NORMAL_SAVE_VALIDATION.json','EXPIRED_CLOSED_VST3_INPUT_SCRATCH_CLEANUP_20261024.json','OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_RECEIPT.json','OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_DECISION_PROOFS.json.gz','MATCHING_AFTER_NORMAL_GIT_CACHE_SAVE_FIX_RESTART.json','ZL_MEASURED_BOUNDARIES_FULL_KIT_ADOPTION.json','NATIVE_CHORUS9_CURRENT22_FULL_KIT_ADOPTION.json','NATIVE_CHORUS9_CURRENT22_CONTROLLER.json','CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json','NATIVE_BASE06_ISOLATED_DATA_RESTORE_VALIDATION.json','ONBOARDING_ZL23_DRAFT_PERSISTENCE_VERIFIED.json','BOUNDARY_STUDY_DUPLICATE_ARCHIVE_EXACT_REMOTE_EVICTION.json','ZL21_ZL22_EXPANDED_STAGES_REMOTE_VERIFIED_EVICTION.json']
  for name in names:shutil.copyfile(N/name,dest/name)
  shutil.copyfile(D/'ZL-runtime-bootstrap-validation/STARTUP_ACTUAL_ZL_PROOF.json',dest/'ONBOARDING_ACTUAL_ZL23_COMPONENT_PROOF.json')
  for name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','build_ZL23_kit.py','finalize_ZL23_kit.py','finalize_ZL05_kit.py','study_measured_ZL_boundary_expansion.py','run_measured_ZL_boundary_study.py','adopt_measured_ZL_boundaries_and_export.py','study_native_Chorus9_current22.py','run_native_Chorus9_current22.py','adopt_native_Chorus9_current22_and_export.py','prepare_latest_ZL_onboarding_delta.py','check_onboarding_actual_ZL23_component.py','restore_verified_native_base_and_source.py','backup_finite_ZL_study.py','backup_ZL23_cache_fix_setup_and_live_matching.py']:
   p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
  for name in ['fl20_curve.py','export_fl20_checkpoint.py']:shutil.copyfile(D.parent/name,scripts/name)
  for name in ['probe_verified_Git_promisor_audio_cache.py','evict_verified_remote_Git_audio_blob_cache.py','evict_refetched_verified_promisor_audio_packs.py','prune_expired_closed_VST3_input_scratch.py','prune_old_ZL_auxiliary_worse_0p010_20261024.py','evict_exact_backed_ZL21_ZL22_expanded_copies.py','discover_current_workspace_repositories.py']:shutil.copyfile(N/name,scripts/name)
  shutil.copyfile(S/'scripts/setup-current-ZL23.sh',scripts/'setup-current-ZL23.sh')
  shutil.copyfile(S/'start-ZL23-current.md',dest/'ONBOARDING_CURRENT23_START.md')
  states={};active=[]
  for name,script in [('FL20_ZL_CONTINUOUS_CONTROLLER.json','continue_ZL_matching.py'),('ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json','watch_ZL_useful_complete_backups.py')]:
   state=read(N/name);states[name]=state;pid=state.get('PID',(state.get('owner')if isinstance(state.get('owner'),dict)else{}).get('PID'))
   assert pid and h['alive'](pid)and os.fsencode(str(D/script))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0'),(name,state)
   active.append(dict(state=name,PID=pid,phase=state['phase'],actual_cmdline=script))
  (dest/'ACTUAL_RUNNING_WORK_SNAPSHOT.json').write_text(json.dumps(dict(states=states,actual_live=active),indent=2)+'\n')
  doc=f'''# ZL23: native06, исправленный кэш Git, setup111 и продолжение

Полного совпадения с оригиналом ещё нет. [Полный ZIP FL20](../ZL-WIP23/Diva_ZL_23_WIP_complete_WIP.zip),
[A/B оригинал0с → ZL23 с4,168с](../ZL-WIP23/AB_REFERENCE_ZL23_WIP.mp3),
[инструкция и официальный бесплатный ZL](../ZL-WIP23/FL_STUDIO_RU.md).
Только три длинные ноты41→37→36 на фразу, дважды; движение делает ARP Diva.
Все281 параметр исходной Diva, ADSR, ARP и12MIDI сохранены. MistaTowa не используется.

В ZL22 настоящий VST3 подтвердил Qmax25 и Gain/Target[-30,30]. Поиск прежде
ограничивался Q8/Target15. Восемь параметров,271вариант; новые независимые12пар
1.328773611620→1.328177921526,SEM.000032400332 прошли прежний max(.0005,3SEM).
Девятипараметрическое предложение осталось UNRUN, за исполненное не выдаётся.

Затем Chorus9/phase/mix проверен в НОВОМ контексте22/fine32:229вариантов,
новые независимые12пар1.327703985454→1.324797664154,SEM.000627543546,
прежний max(.0005,3SEM) пройден. Старое отрицательное исследование хоруса в
другом контексте остаётся отрицательным. Новая nativebase06 принята только после
проверки всех12statebytes, zeroDepth0, полной FLP/FST/ZIP сборки, фактического
повторного рендера распакованного ZIP и нормального push. Fine32/остальныеFX
сохранены. Full23export6mean1.324406587131, ZIPnew6mean1.325045409550.
Это фиксированный критерий сравнения, не процент сходства. GUI FL не тестировался.
ZLMinimumPhase/lookahead0/PDC0/impulse0; nativeотклик2frames по фактическому отчёту,
wholeDAW/ASIO0 не заявляется. Текущий принятый mean={best['loss']:.12f}; пример
WAV/компонент/полные контрольные рендеры сохранены в этом checkpoint.

Основной87param поиск и полный-kit watcher реально работают: {active}.
Проверять актуальные N/PID/cmdline, snapshot не вечный. Критерий, tolerances,
pairedSEM/cold2/сохранение state и latency gates прежние. Поиск теперь допускает
физически измеренные Q25 и dynamicGain/Target[-30,30]. Это расширение допустимых
настроек, без изменения требований к улучшению. Продолжать до убедительного
совпадения либо фактических лимитов, без вопросов по каждому варианту.

Все publicrefs/история/полные комплекты сохранены. Git использует стандартный
promisor-кэш: старые PUBLIC proofblob могут отсутствовать локально, но Git
скачивает их по требованию. Реальный удалённый27MBblob повторно получен SHAexact.
Privateoriginalsource48blob/ref сохранены локально. Первая проверка lazyOFF
пропустила, что ls-tree --long запрашивает размеры и вновь скачивает архивы.
Ошибка обнаружена и исправлена: aggregate использует ls-tree -r БЕЗ --long.
NORMAL lazyON aggregate/gitadd/diff сохранили полный SHAmanifest byteexact,
новых packs не создали. Проверенные повторно скачанные только-кэш packs
выгружены,721440768Rootbytes освобождено. Этот новый commit/push дополнительно
проверяет NORMAL workflow без повторного скачивания. Новые/имеющиеся файлы
хешируются заново; хеш отсутствующего неизменённого архива берётся из
проверенного HEADmanifest. Не восстанавливать все старые архивы разом.
gc.auto0/maintenance.autofalse предотвращают неограниченную автоматическую
перепаковку при тесном диске. Все refs/неопубликованные privateданные сохранены.

Дополнительно удалены только старые явно худшие auxiliary repeatархивы и
просроченные закрытые hostINPUTscratch с защитой активных tags/fixtures.
Все mainselectedWAV/source/output/preset сохранены; удалённые старые scratch/
auxbytes не объявляются Gitbacked. Exactduplicate boundary53MB и старые
распакованные21/22комплекты выгружены только после байтовой проверки Git.
Несовпадающие с ZIP diagnosticWAV не удалялись. Текущий23/native06 защищены.

Setup111 сохранён с точным обратным чтением backend, native06/source55файлов
отдельно восстановлены и проверены, настоящий официальный VST3 загрузил
компонент23 byteexact/PDC0/impulse0. Bashsyntax пройден. Полная установка новой
машины не заявляется. Draft требует Review/Save/Publish в настройках среды;
он не применён автоматически и подбор не блокирует. APIquota% недоступен,
поэтому законченные полезные этапы сохраняются сразу.
'''
  (dest/'README_RU.md').write_text(doc)
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text(f'[ZL23/native06: NORMAL Gitcache fix, setup111 и актуальный принятый звук]({dest.name}/README_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_ZL23_NATIVE06_NORMAL_CACHE_SETUP111_{stamp}
LATEST FULL USERKIT ZL23/nativebase06/fine32/3heldnotes. Read {dest.name}/README_RU.md and ZL23_CONTINUATION_RU.md. Chorus9 NEW22context229cases passed NEW12pairs1.327703985454->1.324797664154 SEM.000627543546 atUNCHANGEDmax(.0005,3SEM), all12nativebytes/zeroDepth0/PDC0/impulse0/fullFLP/ZIP/new6/push passed BEFORE adoption. Old Chorusnegative staysnegative. Full23export6mean1.324406587131 ZIPnew6mean1.325045409550, not matchpercentage. Divaall281/ARP/ADSR/12MIDI unchanged. Current main87params actual4VST3hosts; currentbest{best['loss']:.12f} rendered/state/allpairedWAV archived here; current actualPID/cmdline andN authoritative. Actual ZL measuredQ25/dynamicGainTarget30 supported, no objective/tolerance/qualitygate changes. CRITICAL Gitpromisorcache: aggregate MUST use ls-tree -r WITHOUT --long; --long sizes caused fulloldarchive refetch. First lazyOFFtest missed it; NORMALlazyON aggregate/gitadd/diff proved byteexact/no newpacks. Verified refetchedcachepacksevicted721440768rootbytes. Current normalcommit/push checked no newpromisorpacks. gc.auto0/maintenancefalse; publicrefs/history/fullkitTreeOIDs and privateoriginalsource48blob/ref preserved, oldpublicblob fetchedondemand. Don't reinstall older ZL22watcher with --long or restoreall oldcache. Setup111 backendexactreadback savedUNPUBLISHED, isolatednative06restore55/source and actualofficialVST3component23/PDC0/impulse0 passed; no freshfullmachine/FLGUI/humanaudition/perfectmatch claim. Continue actual matching until convincing soundmatch or actualresources/limits, no pertrialquestions, noMistaTowa/referenceaudio in synthesis, APIquota5%unavailable so back up usefulfinishedstages progressively.
END_ZL23_NATIVE06_NORMAL_CACHE_SETUP111_{stamp}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md')
  packs_before=set((P/'.git/objects/pack').glob('*.promisor'))
  h['aggregate']();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
  assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Preserve ZL23 native06 audio, normal Git cache fix and verified setup111')
  commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items())
  h['push_and_confirm'](commit)
  assert set((P/'.git/objects/pack').glob('*.promisor'))==packs_before,'Normal commit/push refilled old promisor cache'
  for p in [dest/'README_RU.md',*dest.glob('current-accepted-component-and-renders/*WAVs.tar.gz')]:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  for p in(dest/'current-accepted-component-and-renders').glob('*WAVs.tar.gz'):
   rel=p.relative_to(P).as_posix();assert subprocess.check_output(['git','-C',str(P),'show',commit+':'+rel])==p.read_bytes();git('update-index','--skip-worktree','--',rel);p.unlink()
  assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),full_kit_at_snapshot='ZL23',active=active,normal_commit_and_push_no_promisor_refetch=True,root_free_after=shutil.disk_usage('/workspace').free,all_old_full_kit_tree_OIDs_preserved=True,reference_match_reached=False)
  (N/'ZL23_NORMAL_CACHE_SETUP111_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
  print('ZL23_NORMAL_CACHE_SETUP_AND_LIVE_AUDIO_PUSHED',json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
