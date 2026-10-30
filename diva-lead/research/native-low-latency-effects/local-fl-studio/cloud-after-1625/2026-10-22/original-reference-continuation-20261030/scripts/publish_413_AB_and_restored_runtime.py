"""Publish current playable413 comparison and reproducible restored-instance evidence."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
T=Path(__file__).resolve().parent;H=T.parent/'stereo-refinement-20261026';A=T.parent/'pc-stereo-20261024'
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_restored_current413')
P,N,C,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+600
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish actual413 A-B, restored native/VST runtime and live two-stage research snapshot; no DSP adoption'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/'original-reference-continuation-20261030';dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for name in ['restore_tmp_audio_runtime.py','joint_primary_post_fit.py','Joint_primary_post109_support.py','study_joint_primary_post109_current413.py','render_original_413_fresh_AB.py','publish_413_AB_and_restored_runtime.py']:shutil.copyfile(T/name,scripts/name)
  for name in ['TMP_RUNTIME_RESTORATION_PROVENANCE.json','STALE_MAIN_PAUSE_RELEASE.json','ACTUAL_LATEST413_RESTART.json','FRESH_PREFIX_STARTUP_PROBE.json','SAVED_RUNTIME_AND_CURRENT413_DRAFT_RECEIPT.json']:shutil.copyfile(T/name,dest/name)
  shutil.copyfile(H/'CURRENT_CHAIN_READINESS.json',dest/'ACTUAL_CURRENT413_CHAIN_READINESS.json');shutil.copytree(T/'AB_ORIGINAL_413_FRESH',dest/'original-to413-AB');live=T/'JOINT_PRIMARY_POST_109_CURRENT413'
  for name in ['PREDECLARED_PROTOCOL.json','EXACT109_PARAMETER_SPECS.json','BOTH_WORKERS_BOTH_ZLS_NEUTRAL_IDENTITY.json','CURRENT_DIVA_EXACT_SOURCE_PROOF.json','PRIOR_COMBINED_CANDIDATE.json']:shutil.copyfile(live/name,dest/name)
  shutil.copytree(live/'CURRENT_DIVA_REAL_RUN',dest/'actual-Diva-source-audit',ignore=shutil.ignore_patterns('*.wav'));shutil.copyfile(N/'ORIGINAL_JOINT_PRIMARY_POST_109_CURRENT413_STUDY.json',dest/'JOINT109_CONTROLLER_SNAPSHOT.json');shutil.copyfile(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json',dest/'MAIN_CONTROLLER_SNAPSHOT.json');shutil.copyfile(A/'stereo-continuous87/cohort-0413/REMOTE_BACKUP.json',dest/'ACCEPTED413_REMOTE_BACKUP.json')
  start=(T/'start_skill_current.md').read_text();(dest/'CLOUD_START_CURRENT.md').write_text(start);(C/'start_skill_current.md').write_text(start);(h['BASE']/'start_skill_current.md').write_text(start)
  (dest/'README_RU.md').write_text('''# Продолжение 30 октября: текущая 413 и новый совместный поиск

Лучший принятый вариант на момент этого снимка — 413 на полном комплекте37. [Полный ZIP для FL Studio20](../stereo-cascade87-cohort-0413/cohort-0413_complete_FL20_STEREO_WIP.zip), [как загрузить](../stereo-cascade87-cohort-0413/README_RU.md). Обычные native FL + два официальных ZL1.4.1, без Finish. Для сравнения48000Hz/180BPM. Три длинные входящие ноты41→37→36, повторённые дважды; верхние скачки создаёт внутренний ARP Diva.

[Свежий A/B: оригинал → 413](original-to413-AB/AB_ORIGINAL_413_WIP.mp3), [FLAC](original-to413-AB/AB_ORIGINAL_413_WIP.flac). 413 начинается с4.168с. Это новый рендер настоящих DLL/VST3. Рабочий WAV не нормирован; только для A/B выровнена общая stereo RMS. Каналы L/R отдельно не нормировались. Полного совпадения нет; численные небольшие улучшения не переводятся в слуховой процент.

После перезапуска среды исчезли /tmp и процессы. Runtime восстановлен из сохранённых исходников, пользовательских DLL и проверенных официальных файлов. Обнаруженные несовместимые старые помощники заменены: native95-аппликатор, актуальный generic-host с INPUT_LOADED и x64 zlib в новом Wine prefix. Официальный ZL проверен по SHA256, Xvfb — через подпись Debian InRelease и хеш пакета. Контрольная413 прошла все12 native state resaves, два независимых полных каскада0/0, ZL PDC0. Это проверка облачных DSP-хостов, не Windows GUI/ASIO. Новый отдельный Wine prefix также успешно инициализирован и удалён после проверки; активные префиксы не затронуты.

Основной подбор реально возобновлён с413/серии446. Параллельный новый тест109 совместно меняет PRIMARY94 и15 параметров существующего POST: частоты/Q шести allpass и частоту/Q/gain LeftEQ4. Источник Diva, native12, MIDI, ARP/ADSR и последний Stereo Shaper не меняются; новых эффектов нет. Перед подбором настоящая Diva повторила исходник побитово, все281 параметры и12 MIDI-событий совпали. Оба рабочих каскада дали neutral configure против load0/0. Три одинаковых записанных native-входа на каждое предложение, три прохода и два unseen; звук не усредняется. Финальное принятие потребует новых first6ANDfirst10/cold2, прежних stereo-гейтов, нерастущего Air, latest-context проверки, полного FL20 экспорта и независимого восстановления ZIP. Пока этот тест ничего не принял. Контроллеры — снимки активности, не обещание будущей работы.

Завершённый Divine+PRIMARY94 не прошёл экранный порог и не принят; [все исходные/обработанные WAV, состояния и код сохранены](../original-Diva-divine-primary-coadapt404-negative/README_RU.md). Старые106-detector и mean-three94 тоже отрицательные. Исходник great остаётся прежним.

Инструкции восстановления и запуска сохранены/прочитаны из черновика среды revision127; они не применены и не опубликованы автоматически. Для постоянного снимка их можно просмотреть, сохранить и опубликовать в настройках. Это не блокирует текущую аудиоработу. Старые комплекты, PC GUI-дерево, оригинал и текущая413 сохранены.
''')
  guide=PUBLIC/'LATEST_THREE_NOTE_RU.md';guide.write_text('''# Текущий проверенный трёхнотный вариант

Снимок30октября: [413 — полный ZIP](stereo-cascade87-cohort-0413/cohort-0413_complete_FL20_STEREO_WIP.zip), [инструкция FL Studio20](stereo-cascade87-cohort-0413/README_RU.md), [свежий A/B оригинал → 413](original-reference-continuation-20261030/original-to413-AB/AB_ORIGINAL_413_WIP.mp3). 413 начинается с4.168с. Для собственного сравнения48000Hz/180BPM.

Три длинные ноты на фразу, обычные native FL и два официальных ZL; без Finish. Полного совпадения пока нет. [Проверки, восстановленная среда и продолжающийся совместный тест](original-reference-continuation-20261030/README_RU.md). Более поздний полностью проверенный и опубликованный checkpoint имеет приоритет перед этим снимком. [Сохранённое уточнение проверки403/404](original-three-sweep-404-checkpoint/paired-stereo-correction-20261028T1736/README_RU.md).
''');p=PUBLIC/'README_RU.md';p.write_text('[413, свежий A/B с оригиналом и фактическое продолжение30октября](LATEST_THREE_NOTE_RU.md). Полного совпадения нет.\n\n'+p.read_text());(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Save fresh original-to413 A-B, verified restored runtime and actual joint109 continuation');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in [guide,dest/'README_RU.md',dest/'original-to413-AB/AB_ORIGINAL_413_WIP.mp3',dest/'CLOUD_START_CURRENT.md']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,actual413_AB_and_runtime_proof_HTTP_byte_exact=True,no_new_finite_point_adopted=True,all_old_kit_DSP_and_PC_GUI_trees_preserved=True,startup_draft127_saved_not_applied=True,reference_match_reached=False);(T/'413_AB_AND_RESTORED_RUNTIME_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
