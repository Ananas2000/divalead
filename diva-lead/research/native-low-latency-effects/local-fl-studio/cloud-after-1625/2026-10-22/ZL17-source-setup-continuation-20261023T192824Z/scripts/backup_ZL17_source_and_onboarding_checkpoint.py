"""Back up accepted ZL17/fresh Diva, current research and verified setup delta."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,runpy,shutil,subprocess
D=Path(__file__).resolve().parent;s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='ZL17_scoped_backup_helpers');P=s['P'];N=s['N'];R=s['R'];PUBLIC=s['PUBLIC'];BASE=s['BASE'];git=s['git'];read=s['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve actual source17 full-chain replay, setup draft/readback, storage proofs and active cycle03 before service limits'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');s['fetch_main']();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True);before=git('rev-parse','HEAD');old=s['protected']();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('ZL17-source-setup-continuation-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  best=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert best['source_tone_changed_since_ZL16'];s['copy_evidence'](Path(best['native_ZL_component_state']).parent,dest/'current-accepted-private-best',True);(dest/'BEST_CANDIDATE_COMPONENT_AUTHORITATIVE.json').write_text(json.dumps(best,indent=2)+'\n')
  fresh=D/'ZL17-fresh-Diva-to-final-render-01';assert read(fresh/'PROOF.json')['full_actual_native_plus_ZL_render_from_fresh_Diva_source'];s['copy_evidence'](fresh,dest/'fresh-actual-Diva17-whole-chain',True)
  for label in ['h2p','FLP_chunk']:
   target=dest/'fresh-actual-Diva17-whole-chain'/label;s['copy_evidence'](fresh/label,target,True);(target/'Diva.log.gz').write_bytes(gzip.compress((fresh/label/'Diva.log').read_bytes(),mtime=0))
  names=['SOURCE48_NEW_DIVA_FULL_KIT_ADOPTION.json','SOURCE48_POST_ADOPTION_STATUS_AND_BACKUP_REPAIR.json','SOURCE48_SPLIT_BACKUP_RECOVERY.json','SOURCE48_LOSSLESS_FOUR_OBJECT_PACKING.json','SOURCE48_PRIVATE_ARCHIVE_REMOTE_BACKED_EVICTION.json','SOURCE48_PROOF_PART_WORKTREE_DUPLICATE_EVICTION.json','OLDER_ZL_LOCAL_ZIP_COPIES_EVICTION.json','OLD_REJECTED_ARCHIVE_AUX_PRUNING_RECEIPT.json','OLD_REJECTED_ARCHIVE_AUX_PRUNING_DECISION_PROOFS.json.gz','ONBOARDING_ZL17_DRAFT_PERSISTENCE_VERIFIED.json','CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json','NATIVE_BASE03_ISOLATED_DATA_RESTORE_VALIDATION.json','OSCMIX6P5_FIXED_INDEPENDENT48_PREDECLARED_PLAN.json']
  for name in names:shutil.copyfile(N/name,dest/name)
  shutil.copyfile(D/'ZL-runtime-bootstrap-validation/STARTUP_ACTUAL_ZL_PROOF.json',dest/'ONBOARDING_ACTUAL_ZL17_STARTUP_COMPONENT_PROOF.json')
  script_names=['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','backup_finite_ZL_study.py','prepare_native_base_for_combined_ZL.py','restore_verified_native_base_and_source.py','check_onboarding_actual_ZL17_component.py','verify_fresh_Diva_and_ZL17_full_chain.py','confirm48_Diva_OscMix6p5_and_adopt_if_robust.py','recover_split_large_unpublished_research_commit.py','finish_confirmed_source48_full_export.py','backup_ZL17_source_and_onboarding_checkpoint.py','study_native_EQ_with_ZL_cycle03.py','study_native_WS_with_ZL_cycle03.py','run_native_ZL_context_cycle03.py','adopt_native_ZL_context_cycle03.py']
  for name in script_names:compile((D/name).read_text(),name,'exec');shutil.copyfile(D/name,scripts/name)
  for name in ['prune_auxiliary_members_in_old_rejected_native_archives.py','pack_source48_duplicate_objects_losslessly.py','evict_verified_source48_proof_part_worktree_copies.py','evict_origin_verified_older_ZL_complete_ZIP_copies.py','discover_current_workspace_repositories.py']:shutil.copyfile(N/name,scripts/name)
  shutil.copyfile('/workspace/divalead-setup/scripts/setup-current-ZL17.sh',scripts/'setup-current-ZL17.sh');shutil.copyfile('/workspace/divalead-setup/start-ZL17.md',dest/'ONBOARDING_ZL17_START_INSTRUCTIONS.md')
  states={name:read(N/name)for name in ['FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json','NATIVE_ZL_CONTEXT_CYCLE03_STATE.json','ZL_NATIVE_EQ76_STUDY_STATE.json','ZL_NATIVE_WS16_STUDY_STATE.json']};active=[]
  for name,o in states.items():
   pid=o.get('PID',o.get('owner',{}).get('PID')if isinstance(o.get('owner'),dict)else None)
   if pid and s['alive'](pid):active.append(dict(state=name,PID=pid,phase=o['phase']))
  assert active;(dest/'ACTUAL_WORK_SNAPSHOT.json').write_text(json.dumps(dict(states=states,actual_alive=active),indent=2)+'\n')
  doc=f'''# ZL17: новый источник, фактический полный рендер и продолжение

Полного совпадения с оригиналом ещё нет. [Полный ZIP для FL20](../ZL-WIP17/Diva_ZL_17_WIP_complete_WIP.zip),
[A/B: оригинал0с → ZL17 с4,168с](../ZL-WIP17/AB_REFERENCE_ZL17_WIP.mp3),
[инструкция и официальный бесплатный эквалайзер](../ZL-WIP17/FL_STUDIO_RU.md).
Три длинные ноты41→37→36 на фразу, дважды, внутренний ARP; MIDI/ADSR не меняются.

Diva OscMix6.3→6.5 принят после отдельной заранее фиксированной48pair проверки:
mean1.347429927→1.344884890, SEM0.000404493. Остальные280 параметров и12MIDI точны.
Предшествующая12pair проверка была неуверенной и НЕ принята. Все96 WAV новой48
сохранены lossless в трёх64MiB частях с SHA, поскольку единый191MiB архив был
отклонён GitHub. Только собственный неопубликованный commit исправлен после
проверенного preservationbundle; remoteистория не переписывалась. Части проверены HTTP.

ZL17 export6 mean1.344694005, независимая распаковка/ещё6actual mean1.345885435.
После этого ещё раз фактически запущена Diva из H2P и из chunk самого новогоFLP:
all281/12MIDI/rawfloat32/effGetChunk точны, полный native+officialZL из нового raw
дал1.344075286. Отчёт, actualDiva raw/dumps/logs/chunks и свежий финальный WAV здесь.
Новый GUI FL20 экспорт, субъективное прослушивание и точное совпадение не заявляются.

ОБЯЗАТЕЛЬНА новая nativeбаза FL20_NATIVE_ZL_REBASED_03 с источником6.5;
архив в rebased-native-bases/, SHA86643bdb02077aa494de329a174d4510e623de5704440fb0003302f31862251d.
Сохранять native12states, все2+4+8WSmetadata, настоящий Diva chunk, реальные610
параметров ZL. Текущий acceptedprivate mean{best['loss']:.9f} также сохранён здесь.

Сейчас идёт cycle03: штатный EQ76/WaveShaper16 заново согласуются с принятым
источником6.5 и текущим ZL. Main87/watcher намеренно могут быть остановлены на
границе finitecohort; актуальные fitterPID/phase в ACTUAL_WORK_SNAPSHOT.json и N.
Они снова запускаются после полного экспорта/проверки либо сохранения старого
варианта при отказе. Проверять /procPID/starttime/cmdline: snapshot не доказывает
будущую работу. Actual живые процессы на момент snapshot: {active}.

Onboardingdraft106 сохранён и прочитан обратно точно; repoSHA95477a7e…,
обновлены startupпроверка реального компонента17 и восстановление base03/source.
Изолированное datarestore55files и actualVST3 PDC0/impulse0/statebytes прошли,
bashsyntax проверен. Это не полная установка с нуля. Draft НЕ применён/опубликован;
для будущих запусков нужны Save/Publish в настройках среды. Работа сейчас не блокируется.

Место:58старых явно отклонённых архивов лишились только auxiliaryprefix/freshcheck
WAV, каждый основной/training/recordedWAV и все метаданные/пресеты сохранены.
Освобождено654602241bytes; решения/полные SHA manifests приложены. Старые localZIP
и proofpart дубли выгружены только после точной origin/HTTP проверки, версииGitHub
сохранены. Исходный191MiB архив и три части дополнительно lossless упакованы вGit:
все4 объекта/история сохранены, освобождено ещё~200MBroot; privateдубль можно вернуть
из Gitblob41e9bf7d… или трёх удалённых частей, все96WAVdata сохранены.
Gitconnectivity и все прежние completekit treeOID проверены. Restoreкоманды в receipt.

Процент APIлимита не предоставлен. По просьбе о backup при5% этапы публикуются
сразу после проверки. Оригинал — только analysis/A-B, не источник подмешанного звука.
'''
  (dest/'README_RU.md').write_text(doc);p=PUBLIC/'README_RU.md';p.write_text(f'[ZL17: новый источник, свежая actualDiva, настройка среды и текущий цикл]({dest.name}/README_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_ZL17_SOURCE_SETUP_CONTINUATION_{stamp}
Latest complete kit ZL17/new actual OscMix6.5, nativebase03 mandatory. Read {dest.name}/README_RU.md and ZL17_CONTINUATION_RU.md. Fixed48passed1.347429927->1.344884890 SEM.000404493 after earlier inconclusive12; all96WAVlossless in3remoteSHAverifiedparts. No remote history rewrite: only overlarge unpublished commit amended after bundle. FreshactualDiva17 H2P/FLPchunk all281/12MIDI/raw/chunk exact, freshfullactualnative+ZL1.344075286, not GUI/humanaudition/exactmatch. Currentacceptedprivate{best['loss']:.9f} backedhere. NativeEQ76/WS16cycle03 ACTIVE, main87/watcher may be owned-finite stopped; check realfitterPID/cmdline/source6.5, then finalpaired/newbase04/fullkit gating before adoption; no need ask user. Gitobjects/history/allversions retained; rejectedoldarchive pruning keptEVERYmain/training/recordedWAV. Original source48privatearchive nowoffloadedtoverifiedGitblob/remote3parts; original4Gitobjects losslesslypacked andallretained, receiptrestorecommands. Oldproofpart/ZIPworktree copies skipped onlyafteroriginexactcheck; restoreindividually, aggregateincludesGitblobs. Onboardingdraft106 SAVED/readbackexact, repo95477a7e…, installactualstate17/nativebase03datarestore/bashsyntax validated; requiresPublishTRUE/notapplied/notfreshfullinstallclaim. API5%unavailable, backupstagesprogressively; continueactualwork.
END_ZL17_SOURCE_SETUP_CONTINUATION_{stamp}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md');s['aggregate']();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines());git('commit','-m','Preserve accepted Diva6.5/ZL17 fresh full-chain proof, verified setup draft and active native cycle03');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items());s['push_and_confirm'](commit);assert not git('status','--porcelain');receipt=dict(commit=commit,previous_HEAD=before,complete_user_kit='ZL17',current_private_mean=best['loss'],public_path=dest.relative_to(P).as_posix(),actual_work=active,all_old_complete_kit_tree_OIDs_preserved=True,reference_match_reached=False);(N/'ZL17_SOURCE_SETUP_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
