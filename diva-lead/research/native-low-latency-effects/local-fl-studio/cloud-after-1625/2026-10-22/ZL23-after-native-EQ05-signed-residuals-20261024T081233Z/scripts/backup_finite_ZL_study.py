"""Back up a completed finite actual-DSP study and all retained proof audio."""
from pathlib import Path
import argparse,datetime,fcntl,gzip,hashlib,json,shutil,subprocess,time,urllib.request
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
args_parser=argparse.ArgumentParser();args_parser.add_argument('--study',required=True);args_parser.add_argument('--label',required=True);args=args_parser.parse_args();study=Path(args.study)
prefix=(D/'watch_ZL_useful_complete_backups.py').read_text().split("if __name__=='__main__':")[0];exec(compile(prefix,'shared-scoped-ZL-publication-helpers','exec'),globals())
OWNER_FINITE='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause';completion=read(study/'completion.json');pair_count=len(completion.get('captures',[]));assert completion['only_three_held_notes']and not completion['reference_match_reached']
actual_finite_owner=read(N/'zl-continuation.stop').get('owner','unknown')if(N/'zl-continuation.stop').exists()else'no current owned stop'
source_changed=bool(completion.get('source_Diva_tone_parameters_tested')or completion.get('source_Diva_tone_changed'))
source_note='Источник Diva изменён только по явно проверенным тембровым параметрам; все281 параметр и12MIDI аудированы, исходный chunk повторно загружен с тем же rawWAV.'if source_changed else'Исходный Diva source не менялся.'
with pause.open('x')as p:json.dump(dict(owner=OWNER_FINITE,PID=os.getpid(),reason='full backup of completed real native+ZL DSP study with original criterion'),p)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');fetch_main();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/args.label;copy_evidence(study,dest,True)
  if(study/'actual-native-states').is_dir():copy_evidence(study/'actual-native-states',dest/'actual-native-states')
  if(study/'actual-source').is_dir():copy_evidence(study/'actual-source',dest/'actual-source',True)
  scripts=dest/'scripts';scripts.mkdir()
  for name in ['study_native_EQ_with_ZL.py','study_native_WS_with_ZL.py','prepare_native_base_for_combined_ZL.py','backup_finite_ZL_study.py','build_ZL05_kit.py','continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','study_ZL_high_band_dynamics.py','probe_real_ZL_upward_band.py','verify_fresh_Diva_and_ZL09_full_chain.py','package_verified_native_base.py']:
   p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
  for p in sorted(D.glob('*cycle0[23].py')):
   compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  for name in ['study_native_Chorus9_with_ZL.py','diagnose_current_signed_band_residuals.py','study_actual_Diva_tone_in_current_ZL_context.py','prepare_audited_Diva_OscMix6p5.py','adopt_Diva_source_OscMix6p5.py','confirm48_Diva_OscMix6p5_and_adopt_if_robust.py','restore_verified_native_base_and_source.py','study_actual_Diva_PWM_sync_in_native04.py','recover_actual_Diva_PWM_sync_in_native04.py','run_recovered_Diva_PWM_sync_sequentially.py','study_native_WS19_controls_with_ZL.py','run_native_WS19_controls_study.py','probe_actual_WaveShaper_controls.py','probe_actual_WaveShaper_transfer.py','check_native_WaveShaper_control_metadata.py','check_native_saved_bundle_actual_behavior.py','study_actual_Diva_Drift_Plate_in_native04.py','run_actual_Diva_Drift_Plate_study.py','package_actual_Diva_source_study_evidence.py','diagnose_ZL20_native_cold_and_wet_history.py','export_confirmed_current_ZL20.py','study_ZL_two_free_static_slots.py','study_native_EQ_with_ZL_cycle04.py','run_native_EQ76_cycle04.py','adopt_native_EQ76_cycle04_and_export.py','check_native_WaveShaper_fine32_metadata.py','study_native_WS_fine32_with_ZL.py','run_native_WS_fine32_study.py','adopt_native_WS_fine32_and_export.py','study_measured_ZL_boundary_expansion.py','run_measured_ZL_boundary_study.py','adopt_measured_ZL_boundaries_and_export.py','study_native_Chorus9_current22.py','run_native_Chorus9_current22.py','adopt_native_Chorus9_current22_and_export.py','study_native_EQ_with_ZL_cycle05.py','run_native_EQ76_cycle05.py','adopt_native_EQ76_cycle05_and_export.py']:
   p=D/name
   if p.exists():compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
  for name in ['fl20_curve.py','export_fl20_checkpoint.py']:
   p=D.parent/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
  snapshot={}
  for name in ['ZL_NATIVE_EQ76_STUDY_STATE.json','ZL_NATIVE_WS16_STUDY_STATE.json','ZL_HIGH_BAND_DYNAMIC_STUDY_STATE.json','FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json','NATIVE_EQ76_CYCLE05_CONTROLLER.json','ZL_NATIVE_EQ76_CYCLE05_STUDY_STATE.json']:
   p=N/name
   if p.exists():snapshot[name]=read(p)
  rationale=N/'NATIVE_EQ76_CYCLE05_NEW_CONTEXT_RATIONALE.json'
  if 'cycle05'in args.label and rationale.exists():shutil.copyfile(rationale,dest/rationale.name)
  (dest/'ACTUAL_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2)+'\n')
  latest=read(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json');code=latest['full_kit'][-2:]
  doc=f'''# {args.label}: завершённая проверка реальных nativeFX плюс ZL

Это checkpoint исследования, не новый полный FLP и не заявление о совпадении.
Актуальный полный пользовательский комплект остаётся [ZL{code}](../ZL{code}_CONTINUATION_RU.md)
до отдельной новой сборки/распаковки/фактического повторного рендера.

Кандидат проверен настоящими DLL штатных эффектов и официальным WindowsVST3
ZL Equalizer2. Только три входящие ноты41→37→36 на фразу, дважды; внутренний
ARP/ADSR и входящие ноты не менялись. {source_note} Оригинал служит только для анализа.
Тот же полный критерий по исходному WAV. Старый Finish не используется.

Независимые{pair_count} пар: контроль mean{completion['current_control_mean']:.9f},
кандидат mean{completion['candidate_mean']:.9f}, pairedSEM{completion['paired_difference_SEM']:.9f},
robust_improvement={completion['robust_improvement']}. Это не процент сходства.
Состояние фактически изменённых плагинов проверено повторной загрузкой.
Для native-этапов проверены все12states и численный остаток с нулевой глубиной
Chorus; для нового ZL-этапа проверены два свежих экземпляра ZL. Обычные wet WAV меняются между запусками.
Сохранены весь trainingJSON.gz, фактические component/native state bytes,
selectedWAV и lossless-архив всех{2*pair_count}контрольных/кандидатских WAV с SHA256.
Кэш оценивания исключён, исходные trainingprefixWAV сохранены, если были.
Новый GUIэкспорт FL Studio пока не выполнен.

Исходные stock-only настройки выбирались до добавления ZL, поэтому теперь
настройки штатных эффектов проверяются по звучанию ВСЕГО тракта. Снижение
stock-only критерия не требуется: native-кандидат может быть хуже без ZL,
при этом весь native+ZL тракт становится ближе к оригиналу. Именно combined
heldout/freshpaired проверки допускают новый вариант к последующей упаковке.

Работа продолжается последовательными реальными finite-fit/validation.
Снимки PID/phase в ACTUAL_CONTROLLER_SNAPSHOT проверять по фактическим процессам;
старый continuous-matcher может быть намеренно остановлен на время finite-fit,
это не признак отсутствия текущих вычислений. Остановочные файлы принадлежат
{actual_finite_owner}; снимать только после безопасной передачи.
Дальнейший экспорт обязан учитывать новый native_base_export_directory,
реальные12savedstates, все2+4+8WS metadata, реальныеZL610readbacks и компонент.
Обычный x95 exporter не подходит для полной цепи с ZL.

Пользователь просит работать до лимитов и сохранить всё при5%остатка.
Процент лимита сервисом не предоставлен; конечные проверенные этапы сразу
публикуются в Git, чтобы не зависеть от момента исчерпания лимита.
'''
  (dest/'README_RU.md').write_text(doc,encoding='utf-8');(dest/'FILE_SHA256.json').write_text(json.dumps({str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text(f'[Новый завершённый finiteDSP этап: {args.label}]({args.label}/README_RU.md).\n\n'+p.read_text(),encoding='utf-8')
  header=f'''BEGIN_FINITE_NATIVE_ZL_{args.label}
LATEST COMPLETE PUBLIC KIT REMAINS ZL{code} UNTIL NEXT COMPLETE EXPORT. New completed finite actual-DSP study {args.label}: currentcontrolmean{completion['current_control_mean']:.9f}, candidatemean{completion['candidate_mean']:.9f}, paired{pair_count}SEM{completion['paired_difference_SEM']:.9f}, robust={completion['robust_improvement']}. Fulltraining/all{2*pair_count}WAVlossless/native12states/ZLstate/selectedWAV backedunder {args.label}; no fullFLP or exactmatchclaim for this researchcheckpoint. Native12 controls are now fitted in CURRENT ZL context; stockonly loss can worsen while combinedloss improves. Don't select by oldstockonlyobjective. Diva_source_changed_in_this_study={source_changed}; internalARP/ADSR/exact3heldnotes remainunchanged; originalonlyanalysis/AB; noMistaTowa/noFinish. Current finite scientificwork mayrunwhile oldcontinuous andfullkitwatcher gracefully stopped by owner{actual_finite_owner}; read N/ZL_NATIVE_EQ76_STUDY_STATE.json andN/ZL_NATIVE_WS16_STUDY_STATE.json andactualPID/hosts, not oldcontinuoussnapshot. For newfullkit build a NEW native base with prepare_native_base_for_combined_ZL.py, actualnativeexport/FLPpreservednotesroutes andlatency/statechecks; mainZLbuilder must select explicit choice.native_base_export_directory ratherthan assumingoldbase17. Existingoldbase17 andallGitversionspreserved. DeriveZLvaluesfromrealcomponentXML/610dump, preserveall2+4+8WSmetadata, useextendedZLexporter. Native12 plus1ZL stillsame plugin topology, onlysettings change. No GUI FLexport/humanaudition/perceptualpercentage claim. User asksworkuntilactual limits andGitbackupat5%remaining; API percentunavailable, so commitcompletedstages immediately. Resume actual validatedmatching afterfinitehandoff and testedexport; no per-trialquestions.
END_FINITE_NATIVE_ZL_{args.label}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md')
  aggregate();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Back up completed '+args.label+' actual native plus ZL renders and full paired validation');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
  push_and_confirm(commit)
  for p in [dest/'README_RU.md',*dest.glob('*FRESH_CONTROL_CANDIDATE_WAVs.tar.gz')]:
   data=read_public_bytes('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())
   assert data==p.read_bytes()
  receipt=dict(commit=commit,previous_HEAD=before,study=str(study),public_path=str(dest.relative_to(P)),all_old_full_kit_tree_OIDs_preserved=True,robust_improvement=completion['robust_improvement'],candidate_mean=completion['candidate_mean'],reference_match_reached=False)
  (N/(args.label+'-PUBLICATION.json')).write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print('FINITE_ACTUAL_DSP_STUDY_PUSHED',json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER_FINITE:pause.unlink()
