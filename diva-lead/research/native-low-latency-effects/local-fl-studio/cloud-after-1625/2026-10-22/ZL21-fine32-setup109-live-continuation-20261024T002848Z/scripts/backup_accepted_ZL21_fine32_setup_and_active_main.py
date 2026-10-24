"""Preserve accepted full21, exact setup109 and actual continued main checkpoint."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,runpy,shutil,subprocess,time
D=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='accepted_ZL21_scoped_checkpoint');P=h['P'];N=h['N'];R=h['R'];PUBLIC=h['PUBLIC'];git=h['git'];read=h['read'];pause=R/'auto-backup.pause';OWNER='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='preserve accepted full21/fine32, exact saved setup109 and running actual current main before resource limits'),f)
try:
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True);before=git('rev-parse','HEAD');old=h['protected']();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('ZL21-fine32-setup109-live-continuation-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
        adoption=read(N/'NATIVE_WS_FINE32_FULL_KIT_ADOPTION.json');assert adoption['public_kit']=='ZL21';best=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert best['native_base_export_directory'].endswith('REBASED_05')
        h['copy_evidence'](Path(best['native_ZL_component_state']).parent,dest/'accepted-current-main',True);(dest/'BEST_CANDIDATE_COMPONENT_AUTHORITATIVE.json').write_text(json.dumps(best,indent=2)+'\n')
        h['copy_evidence'](D/'native-WaveShaper-fine32-metadata-01',dest/'actual-fine32-native-metadata-and-state-check')
        for name in ['NATIVE_WS_FINE32_FULL_KIT_ADOPTION.json','FINE32_PROVENANCE_RECOVERY_CONTROLLER.json','FINE32_PROVENANCE_RECOVERY_MATCHER_RESTART.json','WS_FINE32_SEQUENTIAL_CONTROLLER.json','ZL_NATIVE_WS_FINE32_STUDY_STATE.json','NATIVE_EQ76_CYCLE04_CONTROLLER.json','ZL_NATIVE_EQ76_CYCLE04_STUDY_STATE.json','ONBOARDING_ZL21_DRAFT_PERSISTENCE_VERIFIED.json','NATIVE_BASE05_ISOLATED_DATA_RESTORE_VALIDATION.json','CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json','MEASURED_SUCCESSFUL_FULL_KIT_STORAGE_RESERVE_UPDATE.json','OLD_NATIVE_REGISTRY_WORKTREE_DUPLICATE_EVICTION.json','OLD_SOURCE_STUDY_RAW_WORKTREE_DUPLICATE_EVICTION.json','EXACT_GIT_BACKED_NATIVE_DIAGNOSTIC_AUDIO_DUPLICATE_EVICTION.json','OLD_ZL_EXPANDED_STAGES_REMOTE_VERIFIED_EVICTION.json','OLD_COMPLETED_STUDY_WORKTREE_PROOF_EVICTION.json','COMPLETED_PRIVATE_VALIDATION_ARCHIVE_DUPLICATE_EVICTION.json']:
            p=N/name
            if p.exists():shutil.copyfile(p,dest/name)
        shutil.copyfile(D/'ZL-runtime-bootstrap-validation/STARTUP_ACTUAL_ZL_PROOF.json',dest/'ACTUAL_CURRENT21_ONBOARDING_COMPONENT_PROOF.json')
        for name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','build_ZL21_kit.py','finalize_ZL21_kit.py','build_ZL05_kit.py','finalize_ZL05_kit.py','check_native_WaveShaper_fine32_metadata.py','study_native_WS_fine32_with_ZL.py','run_native_WS_fine32_study.py','adopt_native_WS_fine32_and_export.py','finish_positive_fine32_after_provenance_fix.py','prepare_latest_ZL_onboarding_delta.py','use_measured_complete_kit_storage_reserve.py','check_onboarding_actual_ZL21_component.py','backup_finite_ZL_study.py','backup_accepted_ZL21_fine32_setup_and_active_main.py','restore_verified_native_base_and_source.py']:
            p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
        for name in ['fl20_curve.py','export_fl20_checkpoint.py']:
            p=D.parent/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
        for name in ['evict_exact_backed_native_diagnostic_audio_duplicates.py','evict_verified_old_ZL_expanded_stages.py','evict_origin_verified_old_study_archive_worktree.py','evict_origin_verified_older_ZL_complete_ZIP_copies.py','evict_Git_exact_private_completed_validation_archives.py']:
            shutil.copyfile(N/name,scripts/name)
        shutil.copyfile(S/'scripts/setup-current-ZL21.sh',scripts/'setup-current-ZL21.sh');shutil.copyfile(S/'start-ZL21-current.md',dest/'ONBOARDING_ZL21_EXACT_SAVED_START.md')
        states={name:read(N/name)for name in ['FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json']};active=[]
        for name,state in states.items():
            pid=state.get('PID',state.get('owner',{}).get('PID'));expected=D/('continue_ZL_matching.py'if name.startswith('FL20')else'watch_ZL_useful_complete_backups.py');assert h['alive'](pid)and os.fsencode(str(expected))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0');active.append(dict(state=name,PID=pid,starttime=Path(f'/proc/{pid}/stat').read_text().split()[21],phase=state['phase']))
        (dest/'ACTUAL_LIVE_MAIN_AND_WATCHER_SNAPSHOT.json').write_text(json.dumps(dict(states=states,actual_alive=active),indent=2)+'\n')
        doc=f'''# ZL21: принятая новая кривая и продолжение

Полного совпадения с оригиналом ещё нет. [Полный ZIP FL20](../ZL-WIP21/Diva_ZL_21_WIP_complete_WIP.zip),
[A/B: оригинал0с → ZL21 с4,168с](../ZL-WIP21/AB_REFERENCE_ZL21_WIP.mp3),
[инструкция и официальный бесплатный ZL](../ZL-WIP21/FL_STUDIO_RU.md).
Три входящие длинные ноты41→37→36 на фразу, дважды; ARP/ADSR/all281Diva сохранены.

После513реальных вариантов32fine-параметров монотонной кривой WaveShaper
прошли НОВЫЕ12пары:1.331061557834→1.328437636044,SEM.000751500573,
gain>.0005 и3SEM. Все12nativepresets сохраняются byteexact, zero-depth replay0.
Это изменение штатной129pointкривой, не дополнительные ноты и не новый буфер.
Остальные2+4+8WSкоэффициенты и nativePreamp/Mix/Post128/128/128 сохранены.

Новая ОБЯЗАТЕЛЬНАЯ база FL20_NATIVE_ZL_REBASED_05. Её архив в rebased-native-bases,
SHA256e91b631015b4c461106f473c93c633bcc18fccac754cf421db438d55f7a36ce3.
Полный21export6mean1.327198873018; независимая распаковка/new6mean1.328330461716.
Три свежие цепи original/twoZIP дали exact0 при ПРЕЖНИХ native2e-7 и
wholefloat32rtol8eps/atol1e-12. Небольшая NONZERO зависимость native от blocksize
измерена и сохранена; нет ASIO/wholeDAW0 или нового GUIFL20экспорта утверждений.

Первый freezer остановился из-за отсутствующего служебного номераcohort у
finiteисследования. Ошибка/partialсостояние сохранены. Исправлена ТОЛЬКО метка
происхождения; те же положительные12не повторялись и допуски не ослаблялись.
Текущий incumbent оставался тем же. Принято только ПОСЛЕ новой базы/полногоFLP/
actualZIPreplay и обычного Gitpush. Весь положительный finiteWAVarchive/training/
native12states уже в native-WS-fine32-current-ZL20-study01.

Реальная source6.5 не менялась. Отклонённый nativeEQ76cycle04/1409cases сохранён:
gain.000980<3SEM.001635. Старые source22/25,WS19 и unusedstatic1129 не приняты.
Fine32metadata/regression/stateproof и актуальные скрипты здесь; поддержанные
32fine коэффициента обязаны участвовать в fingerprint/export/replay.

Main87 уже продолжает с новой базой05, currentacceptedmean={best['loss']:.12f}.
Его компонент, примерWAV, все12pairedWAV lossless, training/heldout/completion
сохранены здесь. Это researchcheckpoint поверх полного21; новый полный kit
публикуется после отдельной полной actualFLP/FST/ZIP проверки. SnapshotPID не
доказывает будущую работу; сверять реальные /proc и N. На snapshot живы {active}.

Onboardingdraft109 сохранён/прочитан обратно ТОЧНО: repo41ce362e…,
actualofficial21VST3state/PDC0/impulse0, isolatednativebase05restore55files и
bashsyntax прошли. Setup устанавливает fine32-aware core из текущего21scripts,
старый embeddedbootstrap недостаточен. DraftrequiresPublishTRUE, не применён,
не является утверждением о полной установке новой машины. Работа не блокируется.

Известный успешный полный21экспорт прошёл с128MiBpreexportrootreserve; watcher
теперь использует этот проверенный128 вместо192, /tmp180 без изменений,
numericmainroot64/tmp112 без изменений. Все sound/paired/replay/latency gates
НЕ МЕНЯЛИСЬ. Только idlewatcher перезапущен; main не прерывался. Старые точные
Gitbacked ZIP/registry/proof/rawworktree дубли выгружены с restoreкомандами;
все Gitверсии/объекты и actualprivateосновныеWAV/пресеты сохранены. Старые
удалённые privateaux, в отличие от этих точных дублей, не объявляются Gitbacked.

Процент APIлимита не предоставлен. Выполненные этапы сразу публикуются по
просьбе о backupпри5%. Оригинал только analysis/A-B, MistaTowa не используется.
'''
        (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n');p=PUBLIC/'README_RU.md';p.write_text(f'[ZL21: принятая fine32кривая, точный setup109 и живое продолжение]({dest.name}/README_RU.md).\n\n'+p.read_text())
        header=f'''BEGIN_ACCEPTED_ZL21_FINE32_SETUP109_{stamp}
Latestfulluserkit ZL21, MANDATORYnativebase05 and supported32finecurve metadata. Read {dest.name}/README_RU.md plus ZL21_CONTINUATION_RU.md. Threeheldnotes41/37/36 only, DivaOscMix6.5/ARP/ADSR/all281/12MIDIunchanged. Fine32actual513cases/new12pairs passed1.331061558->1.328437636 SEM.000751501; native12bytes/zeroDepth0. Newbase05archiveSHAe91b631015b4c461106f473c93c633bcc18fccac754cf421db438d55f7a36ce3. Full21export6mean1.327198873, independentZIPnew6mean1.328330462, original/twoZIPcoldwhole0 atUNCHANGEDnative2e-7/whole8eps+1e-12. No fullmatch/perceptualpercentage/humanaudition/newFLGUI/ASIO0 claim. Firstfreeze21missingfinitecohort fixedPROVENANCEONLY; samepositive12notrerun andsameincumbent. Preserve2+4+8PLUS32finecoefficients,FINEFORMAT smooth_fine_bumps32_v1, centers.02..64,width.0125; currentfl20_curve.py andnativeexporter mandatory; oldcore silentlyomitsfine andiswrong. SavedbundleonlymatchingcompleteDSPfingerprint. Main87/actual4ZLworkers alreadyresumedusingbase05, currentbest{best['loss']:.12f} fullresearchWAV/component/all12paired/training backedhere. Check actualNcontrollers and /proc exactscript/starttime, don'tduplicatejobs or restartretiredstock/Finish. WatchermeasuredROOTreserve128MiB (successful21preexportguard),TMP180unchanged; main64/112unchanged; noaudio/objectivegate changed. NativeEQ04/1409rejected and priornegativecases remainnegative. Setupdraft109/readbackexact/repo41ce362e, actual21startup/base05datarestore55/bashsyntax passed, CURRENT21coreinstalled afterlegacybootstrap; requiresPublishTRUE/notapplied/notfreshmachineclaim. Gitversions/history/fullkitOIDs preserved; localoldZIP/registry/proof/sourceworktree duplicates exactGitbacked andrestorecommands. PrivateactualselectedWAVs kept. API%unavailable so completedstages backedprogressively. CONTINUE actualmatching untilconvincingreference match oractual observedlimits; no pertrialuserquestions.
END_ACCEPTED_ZL21_FINE32_SETUP109_{stamp}

'''
        p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines());git('commit','-m','Preserve accepted ZL21 fine32, exact setup109 and active actual native05 matching checkpoint');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+rel)==oid for rel,oid in old.items());h['push_and_confirm'](commit)
        for p in [dest/'README_RU.md',*dest.glob('accepted-current-main/*WAVs.tar.gz')]:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
        # Keep the verified full validation archive in Git and its original
        # private location, evict only the new duplicate worktree copy.
        offloaded=[]
        for p in(dest/'accepted-current-main').glob('*WAVs.tar.gz'):
            relative=p.relative_to(P).as_posix();blob=subprocess.check_output(['git','-C',str(P),'show',commit+':'+relative]);assert blob==p.read_bytes();offloaded.append(dict(path=relative,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest(),restore_command='git restore --ignore-skip-worktree-bits -- '+relative));git('update-index','--skip-worktree','--',relative);p.unlink()
        assert not git('status','--porcelain');receipt=dict(commit=commit,previous_HEAD=before,full_user_kit='ZL21',public_path=dest.relative_to(P).as_posix(),current_private_accepted_mean=best['loss'],actual_live_snapshot=active,all_old_full_kit_tree_OIDs_preserved=True,exact_new_proof_worktree_duplicates_offloaded=offloaded,reference_match_reached=False);(N/'ZL21_FINE32_SETUP109_LIVE_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ZL21_FINE32_SETUP109_AND_CURRENT_MAIN_PUSHED',json.dumps(receipt),flush=True)
finally:
    if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
