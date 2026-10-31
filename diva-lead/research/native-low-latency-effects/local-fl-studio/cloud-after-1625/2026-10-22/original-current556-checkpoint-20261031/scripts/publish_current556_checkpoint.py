"""Publish current556 fresh A/B, measured readiness, setup and honest research status."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zipfile
U=Path(__file__).resolve().parent;T=U.parent/'continuation-20261030';O=U.parent/'stereo-refinement-20261025';A=U.parent/'pc-stereo-20261024'
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_current556_fresh_checkpoint');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+300
def identity(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split()
  if s[2]=='Z':return None
  return dict(PID=pid,starttime=s[21],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
 except FileNotFoundError:return None
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='fresh current556 A/B, readiness and honest pending original-reference research checkpoint'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);best=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['source_accepted_cohort']==556;ready=json.loads((U/'CURRENT556_READINESS_PROOF.json').read_text());assert ready['two_fresh_actual_two_ZL_replays_errors']==[0.,0.];tail=json.loads((O/'original-oct30-remaining-closed-and-interrupted-studies_PUBLICATION.json').read_text());assert tail['all_retained_study_files_and_WAVs_remote_Git_verified']
  dest=PUBLIC/'original-current556-checkpoint-20261031';dest.mkdir();scripts=dest/'scripts';scripts.mkdir();shutil.copytree(U/'AB_ORIGINAL_38_556',dest/'AB',ignore=shutil.ignore_patterns('buffers','assessment'));shutil.copyfile(U/'CURRENT556_READINESS_PROOF.json',dest/'CURRENT556_READINESS_PROOF.json');shutil.copyfile(U/'ONBOARDING_DRAFT129_READBACK.json',dest/'ONBOARDING_DRAFT129_READBACK.json');shutil.copyfile(U/'ACTUAL_JOINT109_START.json',dest/'ACTUAL_JOINT109_START.json');shutil.copyfile(U/'OLDER_CLOSED_ARCHIVE_CHECKOUT_CACHE_RELEASE.json',dest/'LOCAL_HTTP_VERIFIED_CACHE_RECOVERY.json');shutil.copyfile(O/'original-oct30-remaining-closed-and-interrupted-studies_PUBLICATION.json',dest/'OCT30_TAIL_COMPLETE_BACKUP_PROOF.json')
  study=U/'JOINT109_CURRENT556_AIR_ANCHOR38';snapshot=dest/'ACTIVE_STUDY_SNAPSHOT';snapshot.mkdir()
  for name in ['PREDECLARED_PROTOCOL.json','CURRENT_DIVA_EXACT_SOURCE_PROOF.json','SELECTED_FEASIBLE_SEED.json','CONTROL556_ASSESSMENTS.json','ANCHOR38_ASSESSMENTS.json','BOTH_WORKERS_BOTH_ZLS_NEUTRAL_IDENTITY.json','EXACT109_PARAMETER_SPECS.json']:
   shutil.copyfile(study/name,snapshot/name)
  state=json.loads((N/'ORIGINAL_JOINT109_CURRENT556_AIR_ANCHOR38_STUDY.json').read_text());owner=identity(state['PID']);assert owner and str(U/'study_joint109_current556_anchor38.py')in owner['cmdline'];(snapshot/'CONTROLLER_POINT_IN_TIME.json').write_text(json.dumps(state,indent=2)+'\n');(snapshot/'ACTUAL_PROCESS_IDENTITY.json').write_text(json.dumps(owner,indent=2)+'\n')
  for name in ['study_joint109_current556_anchor38.py','Joint109_current556_anchor38_support.py','render_original_full38_current556_AB.py','probe_actual_native_WS_bipolar_transfer.py','publish_current556_checkpoint.py','release_older_closed_archive_checkout_cache.py']:shutil.copyfile(U/name,scripts/name)
  for name in ['joint_primary_post_fit.py','restore_tmp_audio_runtime.py','fl_native_WS_editor_probe2.c','run_owned_native_editor2_diagnostic.py']:shutil.copyfile(T/name,scripts/name)
  for name in ['normal_staged_primary_fit.py','checked_mean_three_real_primary_fit.py','native_post_trim.py','check_current_original_chain_readiness.py']:shutil.copyfile(U.parent/'stereo-refinement-20261026'/name,scripts/name)
  diagnostics=dest/'NATIVE_GUI_AND_BIPOLAR_DIAGNOSTICS_ALL_RETAINED.zip'
  with zipfile.ZipFile(diagnostics,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for folder in ['WS_NATIVE_GUI_CONTROL_PROBE','WS_BIPOLAR_TRANSFER_DIAGNOSTIC']:
    for p in sorted((U/folder).rglob('*')):
     if p.is_file():z.write(p,folder+'/'+p.relative_to(U/folder).as_posix())
  with zipfile.ZipFile(diagnostics)as z:
   assert z.testzip()is None
   for folder in ['WS_NATIVE_GUI_CONTROL_PROBE','WS_BIPOLAR_TRANSFER_DIAGNOSTIC']:
    for p in(U/folder).rglob('*'):
     if p.is_file():assert z.read(folder+'/'+p.relative_to(U/folder).as_posix())==p.read_bytes()
  (dest/'GUI_BIPOLAR_TRANSFER_SUMMARY.json').write_bytes((U/'WS_BIPOLAR_TRANSFER_DIAGNOSTIC/RESULT.json').read_bytes());(dest/'BEST_CANDIDATE_SNAPSHOT.json').write_text(json.dumps(best,indent=2)+'\n');startup=(U/'start_skill_current.md').read_text();(dest/'CLOUD_START_DRAFT129.md').write_text(startup);(C/'start_skill_current.md').write_text(startup);(h['BASE']/'start_skill_current.md').write_text(startup)
  # Correct prose only. Raw measurements and all released complete ZIP bytes stay.
  old=PUBLIC/'original-WS52-current-full38-negative/README_RU.md';text=old.read_text();assert 'SEM0.00122532'in text;old.write_text(text.replace('SEM0.00122532','SEM0.0012530152448356196'))
  errata='''# Уточнение описательных полей WIP38 и производных535/556

В `verification/CASCADE_BUILD_PROOF.json` полного38 остался старый описательный ключ `PRIMARY36_unchanged_POST_StereoAP6_added_and_AP3_AP5_refitted=true`; старый текст `topology` также упоминает неизменныйPRIMARY36 и добавлениеAP6. Для38 это неверные исторические подписи: реально заново настроены ОБА ZL, новых полос не добавлено. Фактические заменённые payloads, сохранённые component и рендеры проверены. Источник/три длинные входящие ноты/ARP/ADSR/native12/последний nativeTrim сохранены.

535 и556 дальше меняют PRIMARY от38; POST38 и nativeTrim сохранены. Строка `EQ76-WS16-contextual-refit01` в старом README — историческое имя контекста, не указание загружать старую кривую: используйте реальные SOURCE/SUM FST текущего ZIP. Актуальная база native10/WS52, число native эффектов13 плюс2ZL. Состояния и звуковые файлы остаются прежними, выпущенные ZIP/SHA не переписываются. Этот документ исправляет только описание. Новый FLP в WindowsGUI этим не объявляется проверенным.
''';(PUBLIC/'FULL38_AND_NUMERIC_METADATA_ERRATA_RU.md').write_text(errata)
  doc='''# Актуальный численно принятый556 — 31октября

[Полный FL20/26 комплект556](../stereo-cascade87-cohort-0556/cohort-0556_complete_FL20_STEREO_WIP.zip), [инструкция FLStudio](../stereo-cascade87-cohort-0556/README_RU.md). [A/B оригинал→38→556](AB/AB_ORIGINAL_ZL38_556_WIP.mp3), [FLAC](AB/AB_ORIGINAL_ZL38_556_WIP.flac). 556 начинаетсяс8.336с. [Рабочий полный WAV без нормировки](AB/ACTUAL_556_FULL_UNNORMALIZED.wav).

Полного совпадения нет. Новый принятый556 сохранил три длинные ноты41→37→36 дважды, Diva/ARP/ADSR/native12/POST38/последнийStereoShaper. Только обычные13native+2ZL, безFinish/свёртки. В новом A/B оба варианта обработали один реальный nativeвход,556 повторил новый readinessWAV0/0. ТолькоA/B выровнен общейstereoRMS, L/R не нормировались отдельно.

556 прошёл стандартный fresh6+2cold: gain0.000799180452/SEM0.000074164635, cold+.000790857912/+.000669876432. Это не новый10warmтест и не процент слухового сходства. Допущенное правило локальногоAir+.02dB пройдено, но приростAir есть: first6+.00555166dB/cold+.00676435/+.00849780 относительно535. Поэтому новая совместная настройка109 от556 дополнительно удерживаетAir не выше полной38 и556, а общий выигрыш обязана подтвердить именно против текущей556. Её положительный исход этот снимок не утверждает.

Состояния текущей среды проверены31октября: all12native resave точный, два cold-повтора настоящих двухZL+nativeTrim0/0, ZLPDC0. Это не измерениеASIO/всейDAW и не открытиеFLP вWindowsGUI. Сохранены стартовые инструкции draft129, точное прочтение обратно, фактический старт/снимок процесса и код. Обзорный снимок не гарантирует будущую активность.

[Уточнение старых описательных полей](../FULL38_AND_NUMERIC_METADATA_ERRATA_RU.md). [Полный архив оставшихся старых закрытых/прерванных исследований](../original-oct30-remaining-closed-and-interrupted-studies/README_RU.md): незавершённый второйAPmodel не переобъявлен готовым/отрицательным. Старые версии и PCGUIпроекты сохранены. Исходный оригинал используется только для анализа/A-B, не подмешивается в синтез; MistaTowa не используется.

Отдельная nativeGUI/двусторонняякривая диагностика сохранена целиком: собственное окно WaveShaper, НЕ FLStudio. Она доказала новые степени свободы чётной нелинейности, но не совпадение лида. Такой режим пока несовместим со старым x95экспортом; без явной миграции/новых проверок он не принят.
''';(dest/'README_RU.md').write_text(doc)
  (PUBLIC/'CURRENT556_CONTINUATION_RU.md').write_text(doc.replace('](../','](').replace('](AB/','](original-current556-checkpoint-20261031/AB/'))
  (PUBLIC/'LATEST_THREE_NOTE_RU.md').write_text('''# Актуальный трёхнотный вариант — 556 на полной базе38

[Полный ZIP556](stereo-cascade87-cohort-0556/cohort-0556_complete_FL20_STEREO_WIP.zip), [инструкция](stereo-cascade87-cohort-0556/README_RU.md), [A/B оригинал→38→556](original-current556-checkpoint-20261031/AB/AB_ORIGINAL_ZL38_556_WIP.mp3). 556начинаетсяс8.336с.

Три длинные ноты, ordinarynative/twoZL; полного совпадения нет. [Фактическая проверка31октября, ограничения и продолжаемый поиск](CURRENT556_CONTINUATION_RU.md). [Описание сохранённых состояний](FULL38_AND_NUMERIC_METADATA_ERRATA_RU.md). Проверенная база38 и прежние версии сохранены.
''')
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Checkpoint current556 original A-B, actual readiness, anchored joint study and honest metadata corrections');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for path in[dest/'AB/AB_ORIGINAL_ZL38_556_WIP.mp3',dest/'CURRENT556_READINESS_PROOF.json',dest/'CLOUD_START_DRAFT129.md',diagnostics,PUBLIC/'stereo-cascade87-cohort-0556/cohort-0556_complete_FL20_STEREO_WIP.zip']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path.relative_to(P).as_posix())==path.read_bytes()
  result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,current_accepted_numeric=556,fresh_AB_and_readiness_HTTP_byte_verified=True,diagnostic_archive_HTTP_byte_verified=True,complete556_ZIP_HTTP_byte_verified=True,draft_revision=129,all_old_kits_PC_GUI_and_measured_data_preserved=True,reference_match_reached=False);(U/'CURRENT556_CHECKPOINT_PUBLICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
