"""Publish exact native diagnostics, rejected studies and active EQ04 handoff."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,time
D=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='ZL20_native_diagnostics_scoped_backup')
P=h['P'];N=h['N'];R=h['R'];PUBLIC=h['PUBLIC'];git=h['git'];read=h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
deadline=time.monotonic()+180
while True:
    try:
        with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve full20 native diagnostics/setup delta/rejected studies and active current EQ04'),f)
        break
    except FileExistsError:
        if time.monotonic()>deadline:raise TimeoutError('Existing Git writer still owns pause')
        time.sleep(.2)
try:
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True);before=git('rev-parse','HEAD');old=h['protected']();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('ZL20-native-diagnostics-setup-continuation-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
        proof=D/'ZL20-native-state-controls-proof-archive-01';h['copy_evidence'](proof,dest/'lossless-actual-native-diagnostics',True)
        h['copy_evidence'](D/'ZL-actual-free-slot22-filter-type-enum-01',dest/'actual-ZL-filter-type-enumeration')
        h['copy_evidence'](D/'static-slot-supported-migration-proposal-01',dest/'UNINSTALLED-static-slot-migration-proposal')
        for name in ['ONBOARDING_ZL19_DRAFT_PERSISTENCE_VERIFIED.json','NATIVE_BASE04_ISOLATED_DATA_RESTORE_VALIDATION.json','CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json','OLD_CLEARLY_WORSE_ZL_AUX_ARCHIVE_PRUNING_RECEIPT.json','OLD_CLEARLY_WORSE_ZL_AUX_ARCHIVE_PRUNING_DECISION_PROOFS.json.gz','REDUNDANT_UNPUBLISHED_BUNDLE_EVICTION.json','RETIRED_UNUSED_WINE_PREFIX_CACHE_EVICTION.json','RETIRED_UNUSED_WINE_PREFIX_GENERATED_FILE_MANIFEST.json.gz','OLD_COMPLETED_STUDY_WORKTREE_PROOF_EVICTION.json','COMPLETED_PRIVATE_VALIDATION_ARCHIVE_DUPLICATE_EVICTION.json','OBSOLETE_PRIVATE_AUX_AB_CACHE_PRUNING_RECEIPT.json','OBSOLETE_PRIVATE_AUX_AB_CACHE_PRUNING_DECISION_PROOFS.json.gz','OLDER_ZL_LOCAL_ZIP_COPIES_EVICTION.json','NATIVE_CONTEXT03_NEW_DIVA_FULL_KIT_ADOPTION.json','ZL20_MANUAL_FULL_EXPORT_CONTROLLER.json']:
            p=N/name
            if p.exists():shutil.copyfile(p,dest/name)
        shutil.copyfile(D/'ZL-runtime-bootstrap-validation/STARTUP_ACTUAL_ZL_PROOF.json',dest/'ACTUAL_ONBOARDING_ZL20_COMPONENT_PROOF.json')
        for name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','build_ZL05_kit.py','finalize_ZL05_kit.py','build_ZL20_kit.py','finalize_ZL20_kit.py','backup_finite_ZL_study.py','backup_ZL20_native_diagnostics_setup_and_continuation.py','probe_actual_WaveShaper_transfer.py','probe_actual_WaveShaper_controls.py','check_native_WaveShaper_control_metadata.py','check_native_saved_bundle_actual_behavior.py','diagnose_ZL20_native_cold_and_wet_history.py','export_confirmed_current_ZL20.py','study_actual_Diva_PWM_sync_in_native04.py','recover_actual_Diva_PWM_sync_in_native04.py','run_recovered_Diva_PWM_sync_sequentially.py','study_actual_Diva_Drift_Plate_in_native04.py','run_actual_Diva_Drift_Plate_study.py','package_actual_Diva_source_study_evidence.py','study_native_WS19_controls_with_ZL.py','run_native_WS19_controls_study.py','study_ZL_two_free_static_slots.py','study_native_EQ_with_ZL_cycle04.py','run_native_EQ76_cycle04.py','adopt_native_EQ76_cycle04_and_export.py','check_onboarding_actual_ZL20_component.py','restore_verified_native_base_and_source.py']:
            p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
        for name in ['fl20_curve.py','export_fl20_checkpoint.py']:
            p=D.parent/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
        for name in ['prune_only_clearly_worse_old_ZL_auxiliary_validation_archives.py','evict_Git_exact_private_completed_validation_archives.py','evict_origin_verified_old_study_archive_worktree.py','evict_origin_verified_older_ZL_complete_ZIP_copies.py','prune_obsolete_private_auxiliary_AB_cache_only.py','discover_current_workspace_repositories.py']:
            p=N/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
        shutil.copyfile(S/'scripts/setup-current-ZL20.sh',scripts/'setup-current-ZL20.sh');shutil.copyfile(S/'start-ZL20.md',dest/'ONBOARDING_ZL20_START_INSTRUCTIONS.md')
        names=['FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json','WS19_SEQUENTIAL_STUDY_CONTROLLER.json','ZL_NATIVE_WS19_CONTROLS_STUDY_STATE.json','DIVA_DRIFT_PLATE_SEQUENTIAL_CONTROLLER.json','ACTUAL_DIVA_DRIFT_PLATE_NATIVE04_STUDY_STATE.json','ZL_TWO_FREE_STATIC_SLOTS_STUDY_STATE.json','NATIVE_EQ76_CYCLE04_CONTROLLER.json','ZL_NATIVE_EQ76_CYCLE04_STUDY_STATE.json']
        states={name:read(N/name)for name in names if(N/name).exists()};active=[]
        for name,state in states.items():
            identity=state.get('owner')if isinstance(state.get('owner'),dict)else None;pid=state.get('PID')or(identity or{}).get('PID')
            if pid and h['alive'](pid):active.append(dict(state=name,PID=pid,phase=state['phase'],actual_cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()))
        assert active;(dest/'ACTUAL_CURRENT_WORK_SNAPSHOT.json').write_text(json.dumps(dict(states=states,actual_alive_at_snapshot=active),indent=2)+'\n')
        doc='''# ZL20: фактические рендеры, проверки состояния и продолжение

Полного совпадения с оригиналом ещё нет. Последний полный проверенный комплект:
[ZIP ZL20 для FL20](../ZL-WIP20/Diva_ZL_20_WIP_complete_WIP.zip),
[A/B оригинал0с → ZL20 с4,168с](../ZL-WIP20/AB_REFERENCE_ZL20_WIP.mp3),
[инструкция FL20 и официальный бесплатный эквалайзер](../ZL-WIP20/FL_STUDIO_RU.md).
Три длинные входящие ноты41→37→36 на фразу, дважды; внутренний ARP сохранён.

ZL20: шесть полных рендеров mean1.330842108; независимая распаковка/ещё6 mean1.330934113.
Это улучшение относительно полного19 по прежнему критерию, не процент сходства.
Сохранены FLP/WAV/H2P/MIDI/17FST/VSTpreset. Источник actualDivaOscMix6.5 и
nativebase04 сохранены. Новый GUIэкспорт FL20 и субъективное прослушивание не заявляются.

При первой попытке упаковки20 строгая смешанная warm/cold проверка отказала:
native6.2584877e-7, whole1.4901161e-6. Все исходные файлы/ZIP/code сохранены в
lossless-архиве. Диагностика3новыхцепочек/8повторов дала exact0; причина не установлена.
Новый протокол сравнивает3независимых свежих native+ZL цепи из original/двухZIP.
Все12nativebytes и ПРЕЖНИЕ native2e-7/wholefloat32rtol8eps/atol1e-12 прошли,
целые холодные рендеры exact0. Wet-history результат отдельно диагностический.
Нет утверждения, что любые будущие nativehot/cold рендеры всегда byte/sampleexact.

Фактические тесты WaveShaper Preamp/Mix/Post, legacyfingerprint, changedtrials,
сохранение native12presets, прежняя SDK/FST диагностика и все20cold/failedraw
сохранены БЕЗ ПОТЕРЬ:127252241rawbytes→13079196tar.xz, все исходные файлы SHA
проверены чтением архива. Чужие DLL/EXE/MSI отсутствуют. Оригинал только analysis/A-B.
Поддержанная новая metadata waveshaper_native_controls не меняет старые defaults;
изменённые кривые/EQ/controls не могут перезаписываться старым savedstatebundle.

Отклонены после отдельных новых проверок:22DivaPWM/synccases,310WaveShapercases,
25DivaDrift/Platecases и1129комбинаций в двух свободных полосахZL. Все полные
training/state/control/candidate WAV доказательства уже в отдельных publicstudy
папках. Эти отрицательные результаты не выдаются за улучшения. Дополнительные
staticfilters и их предложенная миграция НЕ установлены. Продолжается nativeEQ76
cycle04 в контексте актуального20; main87/watcher могут быть намеренно остановлены
на завершённой границе. Сверять реальныеPID/phase из N и /proc, snapshot не вечный.
Положительный EQ04 требует paired12/heldouts/native12state/replay, новой базы05,
полного новогоFLP/ZIPповторного исполнения и обычного Gitpush до принятия.

Setup20delta: bashsyntax, official20actualVST3state/PDC0/impulse0, независимый
base04datarestore55files проверены. Сохраняемый backenddraft требует Publish;
это не применение среды и не полная установка новой машины. Штатные эффекты
плюс freeofficialZL заменяют старый Finish12416frames; ASIO/wholeDAW0 не заявляются.

Место освобождается локально: точные уже опубликованные proof/ZIP дубли выгружаются
с командами восстановления изGit. Вспомогательные старые stochasticrepeats и
derivedauxA/B явно прорежены; каждый выбранный основной WAV/параметры/метаданные
сохранены, все публичные версии и Gitobjects/history неизменны. Удалённые privateaux
байты не объявляются удалённо сохранёнными. Неиспользуемый Winecache был в основном
hardlinked и почти не освободил место; исправная wine2/nativeWine не менялась.
Servicequota%не доступен: по просьбе backupпри5% выполненные этапы сохраняются сразу.
'''
        (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n');p=PUBLIC/'README_RU.md';p.write_text(f'[ZL20: nativeпресеты, полные диагностики, setup и текущая работа]({dest.name}/README_RU.md).\n\n'+p.read_text())
        header=f'''BEGIN_ZL20_NATIVE_DIAGNOSTICS_SETUP_{stamp}
Latest fulluserkit ZL20, actual nativebase04/OscMix6.5, exactly3heldnotes. Read {dest.name}/README_RU.md and ZL20_CONTINUATION_RU.md. Export6mean1.330842108, actualZIPnew6mean1.330934113, not exactmatch/perceptualpercentage/FLGUI claim. Allold numbered/fullkits protected. Important20original mixedwarm/cold strictfailure preserved, causeunestablished;3newcold original/twoZIP protocol passes SAME native2e-7/whole8eps+1e-12 gates with exact0; never claim arbitraryhotcoldnativebitexact. Complete actualdiagnostics127MB losslessly13MBtar.xz+perfileSHA, originals safe to offload ONLY after exactGitarchive verification. WS19controls310, source22PWM/sync, source25DriftPlate and freeZLslots1129 allREJECTED, statesWAVtraining public, nofailedcandidate adopted. Static-slot migration PROPOSAL ONLY/notinstalled. Current actual nativeEQ76cycle04 has owned stops native-EQ76-cycle04-finite-refit-20261023; check N/NATIVE_EQ76_CYCLE04_CONTROLLER.json and N/ZL_NATIVE_EQ76_CYCLE04_STUDY_STATE.json plusactualhosts, notold stoppedmain87snapshot. On positive: newbase05/fullkit/actualZIP/publicpush beforeadoption; wrapper resumesactualmain/watcher aftercompletion/failure. Templates/scripts/state snapshots preservedhere. Continue actualwork, no pertrialquestions. Runtimequota%unavailable so backupfinishedstages immediately. setup20script/start delta retained with actual20startup andbase04restore evidence; nofullfreshmachine/applieddraftclaim. Exactpublicarchives/ZIPcopies can be restored fromGit; don't restoreall skipworktree largefiles. Explicitoldauxrepeat/derivedABpruning keptallmainpresetsWAVmetadata andallpublichistory; deletedauxbytes NOT claimedremotelybacked.
END_ZL20_NATIVE_DIAGNOSTICS_SETUP_{stamp}

'''
        p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines());git('commit','-m','Preserve ZL20 native state diagnostics, rejected tone studies, setup delta and active EQ76 continuation');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items());h['push_and_confirm'](commit)
        for p in [dest/'README_RU.md',dest/'lossless-actual-native-diagnostics/ACTUAL_NATIVE_STATE_CONTROL_AND_ZIP_DIAGNOSTICS.tar.xz']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
        assert not git('status','--porcelain');receipt=dict(commit=commit,previous_HEAD=before,full_user_kit='ZL20',public_path=dest.relative_to(P).as_posix(),actual_alive_at_snapshot=active,all_old_complete_kit_tree_OIDs_preserved=True,reference_match_reached=False);(N/'ZL20_NATIVE_DIAGNOSTICS_SETUP_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ZL20_NATIVE_DIAGNOSTICS_CONTINUATION_PUSHED',json.dumps(receipt),flush=True)
finally:
    if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
