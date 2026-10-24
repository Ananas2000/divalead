"""Preserve confirmed current audio, rejected finite study outcome and setup handoff."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
D=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='ZL23_EQ05_handoff_backup')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read']
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve current confirmed sound, rejected EQ05, signed residuals and reproducible setup'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
  h['fetch_main']();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');protected=h['protected']();pub=read(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json')
  assert pub['full_kit']=='ZL-WIP23'
  stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
  dest=PUBLIC/('ZL23-after-native-EQ05-signed-residuals-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  best=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert best['native_base_export_directory'].endswith('_06')
  h['copy_evidence'](Path(best['native_ZL_component_state']).parent,dest/'current-confirmed-component-and-all-renders',True)
  (dest/'CURRENT_CONFIRMED_CANDIDATE.json').write_text(json.dumps(best,indent=2)+'\n')
  h['copy_evidence'](D/'ZL-current23-signed-band-diagnostics-02',dest/'analysis-only-signed-band-residuals')
  for name in ['NATIVE_EQ76_CYCLE05_NEW_CONTEXT_RATIONALE.json','NATIVE_EQ76_CYCLE05_CONTROLLER.json','ZL_NATIVE_EQ76_CYCLE05_STUDY_STATE.json','NATIVE_EQ76_CYCLE05_MATCHER_RESTART.json','native-EQ76-current-native06-ZL23-cycle05-PUBLICATION.json','NATIVE_EQ76_CYCLE05_EXACT_REMOTE_PROOF_DUPLICATE_EVICTION.json','OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_SECOND_PASS_RECEIPT.json','OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_SECOND_PASS_DECISION_PROOFS.json.gz','ZL23_NORMAL_CACHE_SETUP111_CONTINUATION_PUBLICATION.json','ONBOARDING_ZL23_DRAFT_PERSISTENCE_VERIFIED.json','NATIVE_BASE06_ISOLATED_DATA_RESTORE_VALIDATION.json']:
   shutil.copyfile(N/name,dest/name)
  for name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','study_native_EQ_with_ZL_cycle05.py','run_native_EQ76_cycle05.py','adopt_native_EQ76_cycle05_and_export.py','backup_finite_ZL_study.py','evict_completed_EQ05_remote_exact_proof_duplicates.py','diagnose_current23_signed_band_residuals.py','finalize_ZL05_kit.py','prepare_latest_ZL_onboarding_delta.py','restore_verified_native_base_and_source.py','check_onboarding_actual_ZL23_component.py','backup_ZL23_after_EQ05_and_signed_diagnostics.py']:
   p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
  p=N/'prune_old_ZL_auxiliary_worse_0p010_second_pass_20261024.py';shutil.copyfile(p,scripts/p.name)
  for name in ['fl20_curve.py','export_fl20_checkpoint.py']:shutil.copyfile(D.parent/name,scripts/name)
  shutil.copyfile(S/'scripts/setup-current-ZL23.sh',scripts/'setup-current-ZL23.sh');shutil.copyfile(S/'start-ZL23-current.md',dest/'PREPARED_CURRENT_START_INSTRUCTIONS.md')
  active=[];states={}
  for name,script in [('FL20_ZL_CONTINUOUS_CONTROLLER.json','continue_ZL_matching.py'),('ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json','watch_ZL_useful_complete_backups.py')]:
   state=read(N/name);states[name]=state;identity=state.get('owner')if isinstance(state.get('owner'),dict)else state;pid=identity['PID']
   assert h['alive'](pid)and os.fsencode(str(D/script))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
   actual_start=Path(f'/proc/{pid}/stat').read_text().split()[21];assert actual_start==identity['starttime']
   active.append(dict(PID=pid,starttime=actual_start,script=script,phase=state['phase']))
  (dest/'ACTUAL_MAIN_AND_WATCHER_SNAPSHOT.json').write_text(json.dumps(dict(states=states,actual_live=active),indent=2)+'\n')
  summary=read(D/'ZL-native-EQ76-after-native06-ZL23-05/completion.json');assert summary['robust_improvement']is False
  doc=f'''# ZL23: дальнейшая проверка штатных EQ и анализ оставшихся различий

Последний полный пользовательский комплект: [ZIP FL Studio20](../ZL-WIP23/Diva_ZL_23_WIP_complete_WIP.zip),
[оригинал → ZL23](../ZL-WIP23/AB_REFERENCE_ZL23_WIP.mp3),
[инструкция и официальный бесплатный эквалайзер](../ZL-WIP23/FL_STUDIO_RU.md).
Полного совпадения ещё нет. Только три длинные ноты41→37→36 на фразу, дважды,
движение создаёт внутренний ARP Diva. MistaTowa не используется, исходный WAV
только для анализа/A-B. Diva281/ADSR/ARP/12MIDI неизменны; nativebase06/fine32
и новый хорус сохранены. Все прежние полные комплекты/история остаются в Git.

Новая EQ76проверка выполнена в другом контексте native06/newZL23, после
Chorus9adoption и измеренных диапазонов ZL. Это не повтор старого теста до
хоруса.1409настоящих DLL/VST3вариантов,3trainingвхода,2heldout,12новых полных пар.
Control1.322871926873→candidate1.321820570970; gain.001051355903,
SEM.000617747445,3SEM.001853242335. **Кандидат отклонён** прежним критерием
max(.0005,3SEM): его выигрыш недостаточно устойчив. All12nativebytesexact,
zeroDepth0 и неизменный ZLstate не заменяют требование устойчивого улучшения.
Весь training/24validationWAV/native12states/selectedWAV сохранён в
[полном checkpoint исследования](../native-EQ76-current-native06-ZL23-cycle05/README_RU.md).
Новая nativebase07 не принята, новый ZL24 из этого кандидата не создавался.

Основной поиск87настроек официального ZL уже возобновлён с подтверждённым
вариантом. Снимок актуального принятого mean={best['loss']:.12f}; полный его
контрольный архив, реальный компонент, selectedWAV и метаданные сохранены здесь.
Реально работают {active}. Проверять актуальные N/proc/PID/starttime, snapshot
не вечный. Четыре настоящих VST3host, paired6/cold2, fixedoriginalcriterion,
Qmax25/dynamicGainTarget[-30,30]. Требования к качеству/сохранению/latency прежние.

Отдельная диагностика с прежним819alignment/edit показывает остаток между
гармониками около3.5–6.5кГц, при другом знаке ошибки в6.5–14кГц. Это анализ
публичного23 и одного подтверждённого selectedWAV, а не проверка нового кандидата.
Between-harmonics включает модуляцию, утечку атак и реверберацию, поэтому его
нельзя объявлять чистым шумом или установленной причиной различия. Гармоники
и промежутки нужно оценивать отдельно; простой подъём всех верхов может
усилить нежелательные компоненты. Критерий/веса/пороги не менялись. Использовать
отчёт для следующих реальных проб, принимать только по свежим полным парам.

Второй проход ТОЙ ЖЕ pruningполитики>.010 освободил101204931bytes:4старых
хуже auxiliaryархива. Current/recent20/published/every10th защищены, все
mainWAV/компоненты/параметры оставлены. Удалённые privateauxrepeats не выдаются
за Gitbacked. Завершённый EQ05losslessархив51903348bytes сохранён публично;
его рабочие/privateдубликаты выгружены только после байтовой проверки Git.
Все24WAV доступны через записанный commit/path/SHA/restorecommand.

Исправленный normalGitcache workflow подтверждён настоящим commit/push
14d5a67092276266d63dbee7242884711259e5a5 без новых promisorpacks. Сохранять
ls-tree -r БЕЗ --long; старый --long вновь скачивает publicаудиокэш.
Все refs/история/fullkitTreeOIDs и privateoriginalsource48blob/ref сохранены.
Некоторые старые PUBLICblob намеренно отсутствуют локально и скачиваются
стандартным Git по требованию. Не восстанавливать все старые архивы разом.

Onboardingdraft111 для23/native06 сохранён с точным backendreadback;55native/source
файлов восстановлены отдельно, actualofficialZL23/PDC0/impulse0/statebytes пройдены.
Обновлённые startинструкции с отказом EQ05 подготовлены здесь; окончательное
сохранение draft фиксируется backendотдельно. Draft не применяется автоматически:
Review/Save/Publish в настройках среды. Работа не блокируется этим действием.
Новый GUIFL/полная установка новой машины/субъективное прослушивание/точное
совпадение не заявляются. APIquota5% недоступен, полезные этапы сохраняются сразу.
Продолжать фактический подбор с подтверждённого варианта до совпадения либо лимитов.
'''
  (dest/'README_RU.md').write_text(doc)
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text(f'[ZL23: отказ EQ05, оставшиеся спектральные различия и дальнейший принятый звук]({dest.name}/README_RU.md).\n\n'+p.read_text())
  p=PUBLIC/'ZL23-validated-continuation/README_RU.md';s=p.read_text();p.write_text(s.replace('](ZL-WIP','](../ZL-WIP').replace('](ZL05_CONTINUATION_RU.md)','](../ZL05_CONTINUATION_RU.md)'))
  header=f'''BEGIN_ZL23_AFTER_EQ05_SIGNED_RESIDUALS_{stamp}
Latest FULLUSERKIT remains ZL23/nativebase06/fine32/newChorus9/THREEheldnotes. NativeEQ76 cycle05 inNEWnative06/ZL23context1409cases REJECTED:12freshpairs1.322871926873->1.321820570970 gain.001051355903 <3SEM.001853242335 (SEM.000617747445), originalmax(.0005,3SEM)UNCHANGED. All24WAV/training/native12states/selected backed in native-EQ76-current-native06-ZL23-cycle05; no native07/ZL24adoption. Main/watch resumed confirmedbest mean{best['loss']:.12f}, currentcomponent/allvalidationWAV/example backed in {dest.name}. Read its README and actual N/FL20_ZL_CONTINUOUS_CONTROLLER.json/PID/starttime/hosts, not stale snapshot. Main87actualZLparams measuredQ25/dynamicGainTarget30, allsource281/ARP/ADSR/12MIDI unchanged. Analysis-only signedharmonic/interharmonic residuals identify3.5-6.5kHzexcess and different6.5-14kHzsignederrors; NOT pure noise/causal proof/acceptance of newcandidate. No objectiveweight/tolerancechanges. AllmainselectedWAV/presets retained; same>.010auxpruning secondpass4archives101204931bytes, current/recent20/published/every10th protected. EQ05proof exactduplicate copies evicted onlyafterGitbytescheck; all24WAV remainpublicGit withrestorecommands. NormalGitcache commit/push14d5a670 succeededwithoutnewpromisorpacks, KEEP correctedaggregate ls-tree -r WITHOUT --long; don'trestoreall oldpubliccache. All refs/history/fullkitTreeOIDs/privateoriginalsource48blob preserved. Setup111 savedUNPUBLISHED withactualcomponent/native06restorechecks; currentstartprepared withEQ05rejection, backendlatestrevisionauthoritative. No FLGUI/humanaudition/perceptualpercentage/perfectsoundclaim. Continue until convincing3noteoriginalmatch oractual limits, no pertrialquestions. APIquota5%unavailable, backupfinishedstages progressively.
END_ZL23_AFTER_EQ05_SIGNED_RESIDUALS_{stamp}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md')
  packs=set((P/'.git/objects/pack').glob('*.promisor'));h['aggregate']();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
  assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Preserve ZL23 continued matching, rejected EQ05 proof and signed residual diagnostics');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());h['push_and_confirm'](commit)
  assert set((P/'.git/objects/pack').glob('*.promisor'))==packs
  for p in [dest/'README_RU.md',*dest.glob('current-confirmed-component-and-all-renders/*WAVs.tar.gz')]:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  for p in(dest/'current-confirmed-component-and-all-renders').glob('*WAVs.tar.gz'):
   rel=p.relative_to(P).as_posix();assert subprocess.check_output(['git','-C',str(P),'show',commit+':'+rel])==p.read_bytes();git('update-index','--skip-worktree','--',rel);p.unlink()
  assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),native_EQ05_rejected=True,latest_complete_user_kit='ZL23',current_confirmed_mean=best['loss'],actual_live=active,all_old_full_kit_tree_OIDs_preserved=True,normal_commit_and_push_no_promisor_refetch=True,reference_match_reached=False)
  (N/'ZL23_AFTER_EQ05_SIGNED_DIAGNOSTICS_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ZL23_EQ05_REJECTION_CURRENT_AUDIO_AND_CONTINUATION_PUSHED',json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
