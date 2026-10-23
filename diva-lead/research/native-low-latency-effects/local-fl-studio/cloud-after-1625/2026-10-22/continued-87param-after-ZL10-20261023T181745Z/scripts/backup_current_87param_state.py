"""Recoverable checkpoint: current accepted native+ZL, fresh Diva audit, cleanup."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,shutil,subprocess,urllib.request
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');prefix=(D/'watch_ZL_useful_complete_backups.py').read_text().split("if __name__=='__main__':")[0];exec(compile(prefix,'scoped-ZL-backup-helpers','exec'),globals())
pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve current87-param actual DSP and all fresh Diva/cleanup proofs before resource limits'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True);before=git('rev-parse','HEAD');old=protected()
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('continued-87param-after-ZL10-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  best=read(D/'ZL-continuous65/BEST_CANDIDATE.json');component=Path(best['native_ZL_component_state']);assert read(component.parent/'completion.json')['robust_improvement'];copy_evidence(component.parent,dest/'current-accepted-private-best',True);(dest/'BEST_CANDIDATE_COMPONENT_AUTHORITATIVE.json').write_text(json.dumps(best,indent=2)+'\n')
  fresh=D/'ZL09-fresh-Diva-to-final-render-01';copy_evidence(fresh,dest/'fresh-actual-Diva-through-whole-chain',True)
  for label in ['h2p','FLP_chunk']:copy_evidence(fresh/label,dest/'fresh-actual-Diva-through-whole-chain'/label,True)
  copy_evidence(D/'ZL-high-band-dynamics-response-audit',dest/'actual-high-band-unit-response-proof',True);copy_evidence(D/'ZL-high-band-dynamics-confirmed-merge-01',dest/'high-band-current-control-revalidation',True)
  for p in sorted(D.glob('*.py')):
   if p.name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','study_ZL_high_band_dynamics.py','probe_real_ZL_upward_band.py','merge_confirmed_ZL_high_band_dynamics.py','verify_fresh_Diva_and_ZL09_full_chain.py','prepare_native_base_for_combined_ZL.py','package_verified_native_base.py','backup_finite_ZL_study.py','backup_current_87param_state.py']:
    compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  for name in ['cleanup_completed_native_study_duplicates.py','prune_only_rejected_old_auxiliary_renders.py']:shutil.copyfile(N/name,scripts/name)
  names=['COMPLETED_NATIVE_STUDY_DUPLICATE_CLEANUP.json','REJECTED_OLD_AUXILIARY_RENDER_PRUNING_RECEIPT.json','REJECTED_OLD_AUXILIARY_RENDER_PRUNING_DECISION_PROOFS.json.gz','ZL10_POST_CACHE_PRUNING_RESTART.json','NATIVE_EQ_WS_REBASE_ADOPTION_AND_RESTART.json','ZL_POST_HIGH_BAND_DYNAMIC_MERGE_RESTART.json']
  for name in names:
   p=N/name;data=p.read_bytes()
   if p.suffix=='.json'and len(data)>150000:(dest/(name+'.gz')).write_bytes(gzip.compress(data,mtime=0))
   else:shutil.copyfile(p,dest/name)
  main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');watch=read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json');assert alive(main['owner']['PID'])and alive(watch['PID']);(dest/'ACTUAL_CONTROLLERS_SNAPSHOT.json').write_text(json.dumps(dict(main=main,full_kit_backup=watch),indent=2)+'\n')
  doc=f'''# Текущее продолжение87params после ZL10

Полного совпадения с оригиналом пока нет. [Полный ZL10 с FLP/WAV/Diva/MIDI/FST/инструкцией](ZL-WIP10/Diva_ZL_10_WIP_complete_WIP.zip)
и [A/B: оригинал0с → ZL10 с4,168с](ZL-WIP10/AB_REFERENCE_ZL10_WIP.mp3).
Полный экспорт6 mean1.411652354, отдельная распаковка/ещё6 actualrenders
mean1.410393589. Числа — прежний полный original-reference критерий, не процент.
Штатная эквализация и поддерживаемая WaveShaper2+4+8форма перенастроены в
контексте настоящего ZL. Потом добавлены две дополнительные динамические
MidPeak полосы:21около5.3kHz (тихий уровень приглушён),22около8.4kHz.
Их реальная работа сначала подтверждена синтетическим тестом официального VST3:
−6dB на тихом синусе и почти0dB на громком. Затем actual6paired на оригинальном
трёхнотном источнике:1.436448947→1.423234635, SEM0.000184997. После совместного
87param refit получен полный ZL10. MinimumPhase/lookahead0/PDC0/impulse0;
это не измерение ASIO/целойDAW. Новый GUIэкспорт FL20 ещё не выполнен.

Свежая фактическая Diva отдельно запущена из H2P и из chunk, извлечённого
из FLP09. Обе:all281/12MIDI/rawfloat32/effGetChunk совпали точно с исходником.
Затем весь actualnative+officialVST3 тракт выполнен из этого нового источника,
loss1.441275041 для тех настроек ZL09. Полный отчёт/WAV/обе sourceпроверки
сохранены в этом checkpoint. Это подтверждение источника и исполненияDSP,
не замена отсутствующему GUI FLэкспорту. Три внешние heldnotes41→37→36 дважды,
ARP/ADSR/Diva source неизменны; оригинал только analysis/A-B, MistaTowa не используется.

Текущий принятый частный mean{best['loss']:.9f}, фактический компонент и все
его independentvalidationWAV также сохранены. В MAIN актуальны реальные
componentXML/610readbacks: унаследованные массивы параметров могут устаревать.
Сейчас12staticPeak+4AllPass+6dynamicPeak; у каждой dynamic настраивается также
baseGain:36+8+42+OutputGain=87. На каждой итерации joint48proposals,
coordinate87,2heldouts,paired6, actualstatebytes и2NEWcoldinstances проверка.
SnapshotactualmainPID{main['owner']['PID']}, snapshotbackupPID{watch['PID']}.
Проверять actualPID/starttime, не считать snapshot постоянным доказательством.

База stockFX теперь FL20_NATIVE_ZL_REBASED_01; брать старую Native17 по умолчанию
нельзя. Её полный проверенный архив сохранён в rebased-native-bases/
FL20_NATIVE_ZL_REBASED_01-verified-base.zip, SHA256
f13ae339bc0c6655d356db417888af71354e5061a18036789074979f4c4e86c3.
Будущий экспорт читает native_base_export_directory и этот архив. Stock-only
mean может быть хуже, важна вся связка native+ZL. Native16 остаётся прежним
самостоятельным stock-only комплектом. Все прежние completekit/treeOID сохранены.

Место дополнительно освобождено строго в127завершённых старых отклонённых
подборах: удалены1016auxiliaryprefix/fresh-check WAV, каждый основной bestWAV,
recordedWAV, все параметры/состояния/метаданные сохранены; принятые варианты,
исходники, runtime и Gitверсии не затронуты. Журнал содержитSHA/решения;
randomChorus trainingrealization при перегенерации может отличаться, основной
WAV каждого старого варианта оставлен. Снято~2.4GiB именно дублей проверок.
Плюс ранее181MB закрытого studyIO/remote-backedduplicatedproof освобождены.
После фактического порога места matcher завершил finitecohort, затем после
очистки был снова запущен. Сейчас вычисления/полные backups реально работают.
Пользователь просит сохранять всё до5%остатка; процентAPIнедоступен, поэтому
проверенные этапы и полные комплекты публикуются по мере готовности.
'''
  (PUBLIC/'CURRENT_87PARAM_AFTER_ZL10_RU.md').write_text(doc,encoding='utf-8');(dest/'README_RU.md').write_text(doc,encoding='utf-8');p=PUBLIC/'README_RU.md';p.write_text('[Актуальное продолжение87params, ZL10, свежая Diva и журналы места](CURRENT_87PARAM_AFTER_ZL10_RU.md).\n\n'+p.read_text(),encoding='utf-8')
  header=f'''BEGIN_CURRENT_87PARAM_AFTER_ZL10
LATEST COMPLETE PUBLIC KIT ZL10, export6mean1.411652354/NEWZIPreplay6mean1.410393589, exactwholezero-depth replay/statecontainers/native12bytes. Read CURRENT_87PARAM_AFTER_ZL10_RU.md first. NativeEQ76 thenWS16 successfullyrefitted inCURRENTrealZLcontext; NEWnativebase FL20_NATIVE_ZL_REBASED_01 mustbe used, not oldNative17. VerifiedbaseZIP in rebased-native-bases/FL20_NATIVE_ZL_REBASED_01-verified-base.zip SHA256f13ae339bc0c6655d356db417888af71354e5061a18036789074979f4c4e86c3; extracttoB forfuturebuilder. FullZL10containsFLP/WAV/Diva/MIDI/17FST/VSTpreset/proofs/FL20guide; officialfreeZL1.4.1 installedseparately. Native16 remainsbestpreviousstandaloneSTOCK-only; don't selectnewbase bystockonlyloss.

CURRENTMAIN87params =12staticPeak(36)+4AP(8)+6dynamicPeak(eachGain/Freq/Q/Target/Threshold/Attack/Release=42)+OutputGain1. DynamicUIbands15/16/17/18/21/22; last2 peakMid~5.3k/8.4k, lowlevelcut/loudlevelcorrection actualVST3syntheticunitverified. Separatecurrentcontrolpaired6gain1.436448947->1.423234635/SEM.000184997; componentstatebytesexact/2NEWcoldinstancesbitexact/PDC0/impulse0, originalcriteriaunchanged. MainactualD/continue_ZL_matching.py, N/FL20_ZL_CONTINUOUS_CONTROLLER.json andD/ZL-continuous65/BEST_CANDIDATE.json (directorynamehistorical). CheckactualPID/starttime; snapshotmain{main['owner']['PID']}, backup{watch['PID']}; bothaliveatbackup. Joint48proposals/coordinate87/2heldouts/paired6/robust>.0005or3SEM, actualall12WAVlossless+SHA; realcomponentXML authoritative overstaleinheritedarrays. Canonicalfreezer dynamicallyenumerates allactiveAP/dynamicbands andphysicalbaseGains. Templates/editor must preserveall2+4+8WSmetadata/newnativebase/currentDivaChunk/noextraMIDInotes. Threeincomingheld41->37->36 perphrase twice/internalARP/ADSR same. ActualfreshDivaH2P andFLPchunkrun all281/12MIDI/rawfloat32/chunkbyteexact, freshsource fullnative+ZL09replayloss1.441275041 backedhere. No GUIFLexport/humanaudition/exactreference/perceptualpercentage/ASIOlatencyclaim.

Userexplicitlyrequestsworkuntilreal limits andbackupat5%remaining; APIpercentunavailable, commitallcompletedstudies/completekits progressively. Lastprivateacceptedmean{best['loss']:.9f} andallvalidationaudio backedunder {dest.name}. Mainendedatrealstorageguard thenrestarted after1016oldrejectedauxiliaryWAVs prunedacross127trials, whileEVERYmainselectedWAV/allparams/states/metadata, allacceptedtrials/currentresearch/originals/publicGitversions preserved. Explicitdecisionproofs/SHA logged. Another181MBcompletedIO andremote-backedstudyduplicatepruned withreceipts. AllGitversions/treeOIDs/historypreserved. Mainreserve root64/tmp112MiB; fullbackup192/180. Oldnative/Finishcontrollersretired; don'trestart. Futurefinitehandoffs own stop/pause andfinishcurrentcohort, neverremoveanotherowner. Currentownednumericpauseexternal-ZL-continuous65-refinement. Draftsavedearlierisunpublished, notcurrentruntimeorPublishclaim/blocker.
END_CURRENT_87PARAM_AFTER_ZL10

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md');aggregate();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(x.startswith('diva-lead/research/native-low-latency-effects/')for x in git('diff','--cached','--name-only').splitlines());git('commit','-m','Preserve current87-parameter ZL10 continuation, real fresh Diva renders and selective rejected render cleanup');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+x)==oid for x,oid in old.items());subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  receipt=dict(commit=commit,previous_HEAD=before,current_private_mean=best['loss'],last_complete_kit='ZL10',all_old_kit_tree_OIDs_preserved=True,main_PID=main['owner']['PID'],backup_PID=watch['PID'],reference_match_reached=False);(N/'CURRENT_87PARAM_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
