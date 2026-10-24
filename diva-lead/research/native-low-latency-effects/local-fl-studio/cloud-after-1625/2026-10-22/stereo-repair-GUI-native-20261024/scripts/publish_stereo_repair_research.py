"""Publish completed actual-DSP evidence; full kit/adoption are separate steps."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
A=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='PC_stereo_evidence_publication')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
validation=read(A/'frozen-stereo-validation01/completion.json')
assert all(validation[k]for k in ['archival_GUI_original_criterion_passed','new_native6_and_cold2_original_criterion_passed','all_archival_GUI_stereo_errors_improve','all_new_native_stereo_errors_improve'])
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve completed stereo repair and all actual validation audio before full kit'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main')
  old=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'stereo-repair-GUI-native-20261024';dest.mkdir(exist_ok=False);scripts=dest/'scripts';scripts.mkdir()
  folders=['stereo-assessment','phase-stereo-study01','post-stereo-study01','primary-phase-stereo-fit01','cloud476-GUI-recheck','pure-side-stereo-screen','cloud476-pure-side-recheck','second-side-midrange-screen','frozen-stereo-validation01']
  for name in folders:h['copy_evidence'](A/name,dest/name,True)
  cohort=Path(read(A/'cloud476-GUI-recheck/CLOUD476_PRIOR_VALIDATION.json')['native_ZL_component_state']).parent
  h['copy_evidence'](cohort,dest/'original-cloud476-confirmation',True)
  shutil.copyfile(A/'archival-GUI-validation/ARCHIVE_RESTORE_PROVENANCE.json',dest/'ARCHIVAL_GUI_INPUT_PROVENANCE.json')
  for file in A.glob('*.py'):compile(file.read_text(),file.name,'exec');shutil.copyfile(file,scripts/file.name)
  for name in ['PUBLIC_ZIP_RESTORE_RECEIPT.json','OLD_PC_AUDIT_CACHE_ONLY_EVICTION.json','CLOSED_TRIAL_SCRATCH_CLEANUP.json','RESTORED_PC_ZIP_BLOB_CACHE_EVICTION.json']:
   p=A/name
   if p.exists():shutil.copyfile(p,dest/name)
  for name in ['PC_HANDOFF_DIFF_PREFETCH_CACHE_EVICTION.json','LATEST_PC_METADATA_FAST_FORWARD.json','EXPIRED_CLOSED_VST3_INPUT_SCRATCH_BEFORE_PC_HANDOFF_RESTORE.json','OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_THIRD_PASS_RECEIPT.json','OLD_WORSE_010_ZL_AUX_ARCHIVE_PRUNING_THIRD_PASS_DECISION_PROOFS.json.gz']:
   shutil.copyfile(N/name,dest/name)
  for name in ['win_vst3.py','fl20_vst3_state.py']:shutil.copyfile(D/name,scripts/name)
  for name in ['native_chain.py','native_fst.py']:shutil.copyfile(Path('/tmp/divalead-native-effects')/name,scripts/name)
  for name in ['fl20_curve.py','fl20_objective.py']:shutil.copyfile(D.parent/name,scripts/name)
  gui=read(A/'frozen-stereo-validation01/ARCHIVAL_GUI_SUMMARY.json');fresh=read(A/'frozen-stereo-validation01/NEW_NATIVE_SUMMARY.json')
  doc=f'''# Исправление перекоса влево после локальной FL26, 24 октября

Это завершённое исследование, **ещё не новый полный комплект и не полное
совпадение с оригиналом**. Прежний локальный ZL23 и все его файлы сохранены:
[контрольный GUI проект и отчёты](../../../../2026-10-24/README_RU.md).
Исторические комментарии не выравнивать L/R уступают новому прямому запросу
пользователя исправить перекос. Простая независимая RMS-нормализация каналов
не использовалась: в оригинале бас и верх имеют разный баланс.

Реальный последний FL26 export в5–10кГц имел около+5.4дБ слева; оригинал около
нуля. Предыдущий GUI export немного лучше в2–5кГц, но тоже около+5.3дБ вверху.
Общий RMS не отражает проблему: оригинал в целом сам сильнее слева из-за баса.
См. полный частотный отчёт stereo-assessment/ORIGINAL_AND_ACTUAL_FL26_CHANNEL_BALANCE.json.

Первый175вариантов с внутренними extraфильтрами не дал достаточного выигрыша.
Post153варианта дали сильный stereoэффект, но первый Mid+Side вариант ухудшил
общий критерий;225поправок основных AllPass не вернули общий выигрыш. Они не
приняты. Затем проверены8чистоSide фазовых фильтров и14дополнительных Sideфильтров.
**Зафиксирован другой кандидат:** ранее подтверждённый облачный primarycohort476
вместе с отдельным вторым ZL на SUM ПОСЛЕ основного. Во втором ZL только два
Side AllPass:10000Гц/Q2 и2200Гц/Q4, остальные полосы OFF. Ноты/Diva281/native06,
fine32/ARP/ADSR/source не менялись. Оба настоящих официальных VST3, тот же PE.
Side-only поправка сохраняет моно с максимумом остатка1.1920928955078125e-7.

В первом GUI trainingвходе новый баланс по2–5/5–10/10–14кГц примерно
+.29/+.89/+1.24дБ вместо примерно+3.2/+5.4/+5дБ. Общий исходный критерий также
стал лучше, а не заменён отдельной stereoоценкой. Stereoдиагностика добавлена
явно по новой жалобе; веса исходного objective,819alignment/edit и пороги прежние.
Нормирование громкости допустимо только в A/B, не в самих рабочих WAV.

Кандидат с обоими сохранёнными компонентами зафиксирован ДО проверки8других
записанных GUIвходов. Это архив предыдущей локальной проверки другого кандидата,
**не новые GUIэкспорты и не совершенно нетронутый finalholdout**. Первая6:
mean gain{gui['first6_mean_improvement']:.12f},SEM{gui['first6_SEM']:.12f},
порог{gui['required_improvement']:.12f}; две холодные GUIреализации дали
{gui['last2_cold_input_improvements']}. Во всех8 общий критерий и stereoошибка лучше.

Отдельно получены6 НОВЫХ настоящих рендеров штатной цепи из сохранённых12native
пресетов на прежнем реальном Divaисточнике и2новых холодных nativeэкземпляра.
Новые Diva VST/GUIзапуски не заявляются. Mean gain{fresh['first6_mean_improvement']:.12f},
SEM{fresh['first6_SEM']:.12f},порог{fresh['required_improvement']:.12f}; cold2
{fresh['last2_cold_input_improvements']}. Тот же input внутри каждой пары.
Все8 проверок положительны. Все610параметров обоих компонентов берутся из
реальных состояний; bytes roundtripexact, два холодных полных ZLтракта bitexact0.
Суммарный ZL PDC0, первый импульсный отклик0. Не ASIO/wholeDAW тест.

Сохранены все16новых GUIпарных выходов,24native/input/парных WAV и12проверочных
WAV исходного cloud476 в losslessархивах, каждый член SHA256проверен. Все параметры,
trainingJSON и исходники также сохранены. Невыбранные тренировочные DSP scratch
были перезаписываемыми буферами, их нельзя объявлять полным архивом всех опытов.
Никакие DLL/лицензии не добавлены. Схема требует ДВА ZL, не одного; старый
singleZLbuilder/main нельзя запускать поверх нового кандидата без поддержки
каскада. До отдельного fullFLP/FST/ZIP replay и push он не заменяет текущую базу.

Освобождались только проверенные публичные Gitcache и закрытые регенерируемые
DSPscratch. Git diff между двумя деревьями неожиданно подтянул большой кэш;
структурные объекты сохранены отдельно, публичные blob снова выгружены с proof.
Для сравнения metadata использовать ls-tree без --long и сравнение OIDкарт,
не двухдеревный git diff. Все refs/история/privateoriginalsource48 сохранены.
Последний GUIFLP/старые полные комплекты защищены treeOID. Продолжать подбор
после безопасной новой сборки. Полное совпадение ещё не достигнуто.
'''
  (dest/'README_RU.md').write_text(doc)
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text('[Новая проверенная поправка стерео после GUI FL26](stereo-repair-GUI-native-20261024/README_RU.md).\n\n'+p.read_text())
  header='''BEGIN_STEREO_REPAIR_VALIDATED_NOT_YET_FULL_KIT_20261024
Read local-fl-studio/cloud-after-1625/2026-10-22/stereo-repair-GUI-native-20261024/README_RU.md. User NEW explicit complaint asks fix left dominance, overrides earlier no-LR-rebalance handoff preference. Frequency-dependent issue: GUI5-10kHz~+5.4dBLeft vs originalnear0, bassoriginalLeftstrong. New frozen candidate PRIMARY actualcloudcohort476 + SECOND ZL POST onSUM with TWO Side-only AllPass10000Hz/Q2+2200Hz/Q4, source/Diva281/native06/fine32/ARP/exact3heldnotes unchanged. Do not collapse tooneZL: internal routing/order isn't proven equivalent. Primary bettertone plusSidephase repair passed ARCHIVALGUI8 (notnewGUI/notuntouchedfinalholdout) and NEWnative6+2cold onpreservedDiva source underoriginalfloor/3SEM, exactstates/cold2completeZLchain0/PDC0/impulse0. All52validationWAV/nativeinputs preserved inverifiedlosslessarchives. First175/internal extra,153/postMidSide,225/primaryphasefit aren't accepted; use actualFROZEN_BEFORE_VALIDATION for correct candidate. Not yet adopted: requires new fullFLP/FST/ZIP actualreplay/push. GUIcandidate opening/export stillpending; no completeoriginalsoundmatch. Need TWO-ZL-aware builder/main, never restart oldsingle65matcher/publisher on this state. KeepalloldversionsandcurrentPCGUI6f2ae405tree. Git diff two-tree canbulkrefillpromisorcache; compare ls-tree OIDmaps instead. No APIquotapercentage available, backupfinishedstages progressively.
END_STEREO_REPAIR_VALIDATED_NOT_YET_FULL_KIT_20261024

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md')
  packs=set((P/'.git/objects/pack').glob('*.promisor'));h['aggregate']();git('add','--',str(dest.relative_to(P)),str((PUBLIC/'README_RU.md').relative_to(P)),str((PUBLIC/'SHA256SUMS.txt').relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve validated frequency-dependent stereo repair after actual FL26 handoff');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert set((P/'.git/objects/pack').glob('*.promisor'))==packs
  assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+(dest/'README_RU.md').relative_to(P).as_posix())==(dest/'README_RU.md').read_bytes()
  evicted=[]
  for p in dest.rglob('*WAVs.tar.gz'):
   relative=p.relative_to(P).as_posix();blob=subprocess.check_output(['git','-C',str(P),'show',commit+':'+relative]);assert blob==p.read_bytes();git('update-index','--skip-worktree','--',relative);p.unlink();evicted.append(relative)
   private=cohort/p.name if p.parent.name=='original-cloud476-confirmation'else A/p.parent.relative_to(dest)/p.name
   if private.exists()and private.read_bytes()==blob:private.unlink()
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=old,public_path=dest.relative_to(P).as_posix(),full_kit_not_yet_published=True,old_full_kit_and_PC_GUI_tree_OIDs_preserved=True,all_validation_audio_public_Git_verified=True,evicted_only_exact_backed_archive_duplicates=evicted,normal_commit_push_no_cache_refill=True,reference_match_reached=False)
  (A/'STEREO_RESEARCH_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
