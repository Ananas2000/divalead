"""Publish real404 shared-input A/B and correct the invalid earlier experiment."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_actual404_and_correction')
P,N,C,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+600
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish actual404 shared-native A/B and technical correction; no kit DSP changes'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Existing publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  old=PUBLIC/'original-real-DSP-Jacobian-primary-current';correction=json.loads((H/'GN_FIRST_ATTEMPT_TECHNICAL_CORRECTION.json').read_text());(old/'TECHNICAL_INVALID_FIRST_ATTEMPT.json').write_text(json.dumps(correction,indent=2)+'\n')
  old_readme=old/'README_RU.md';old_readme.write_text('''# Технически некорректный первый тест — не использовать как вывод о звуке

Второй параллельный PRIMARY-хост не загрузил исходный component перед измерениями. Часть проб поэтому использовала исходную топологию плагина. Кроме того, первоначальный residual был одним sqrt(loss), а не подробным спектральным вектором. Тест ничего не принял; состояния и результаты 372/403/404 не затронуты. Исходный архив оставлен без изменений для аудита. Это ошибка организации теста, а не доказательство неэффективности совместной настройки.

Исправленная серия отдельно проверяет загрузку обоих хостов и нейтральный рендер 0/0 перед матрицей 1188×94; норма нового подробного residual в каждом измерении равна прежней функции ошибки. Исправленный и последующий ограниченный тесты не дали достаточного улучшения и не приняты. Их отдельные архивы: [fixed-base](../original-real-DSP-Jacobian-fixed-base-negative/README_RU.md), [constrained](../original-real-DSP-Jacobian-constrained-negative/README_RU.md).

Ниже сохранено первоначальное описание до обнаружения ошибки.

'''+old_readme.read_text())
  sums=old/'FILE_SHA256.json';data=json.loads(sums.read_text())
  for name in ['README_RU.md','TECHNICAL_INVALID_FIRST_ATTEMPT.json']:data[name]=hashlib.sha256((old/name).read_bytes()).hexdigest()
  sums.write_text(json.dumps(data,indent=2)+'\n')
  dest=PUBLIC/'original-three-sweep-404-checkpoint';dest.mkdir();ab=dest/'shared-input-AB37-404';ab.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for p in(H/'AB_FULL37_LATEST404_SHARED_INPUT').iterdir():
   if p.is_file():shutil.copyfile(p,ab/p.name)
  for name in ['render_AB_full37_latest404_shared_input.py','publish_three_sweep404_AB_and_GN_correction.py','restart_current372_three_sweep_20261028.py','release_verified_public_blob_cache_20261028_1706.py']:shutil.copyfile(H/name,scripts/name)
  for name in ['MAIN_THREE_SWEEP_REFINEMENT_20261028.json','ACTUAL_CURRENT372_THREE_SWEEP_20261028_START.json','CURRENT_VERIFIED_PUBLIC_BLOB_CACHE_RELEASE_20261028_1706.json','GN_FIRST_ATTEMPT_TECHNICAL_CORRECTION.json']:shutil.copyfile(H/name,dest/name)
  A=H.parent/'pc-stereo-20261024'
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,scripts/name)
  for cohort in [403,404]:shutil.copyfile(A/f'stereo-continuous87/cohort-{cohort:04}/REMOTE_BACKUP.json',dest/f'ACCEPTED{cohort}_REMOTE_BACKUP.json')
  (dest/'README_RU.md').write_text('''# Трёхнотный вариант: проверенные продолжения 403 и 404

Цель — исходный загруженный референс. Приняты небольшие численные улучшения PRIMARY на полном комплекте 37. Три длинные входящие ноты, внутренний ARP, весь источник Diva, native12/base10, POST37 и последний native Stereo Shaper сохранены. Обработка без Finish/convolution. Самостоятельного полного совпадения или слышимого процента сходства эти метрики не доказывают.

Оптимизатор теперь делает три последовательных прохода по параметрам на одном записанном входе, затем проверяет результат на новых входах. Порог и исходные веса не смягчались. Обучающий Air ограничен исходным уровнем; свежие проверки сохраняют прежний допуск +0.02 dB. Небольшие допустимые приращения Air между принятыми версиями могут накапливаться; суммарное сохранение относительно 37 не утверждается.

Последняя на момент этого снимка принятая 404: [полный ZIP для FL20](../stereo-cascade87-cohort-0404/cohort-0404_complete_FL20_STEREO_WIP.zip), [инструкция установки](../stereo-cascade87-cohort-0404/README_RU.md). ZIP содержит проект FLP, обычные FST, Diva h2p, MIDI и WAV. Плагины устанавливаются отдельно по инструкции. Для сравнения: 48000 Hz и 180 BPM. Проверка новых FLP в Windows GUI/ASIO не выполнялась в этой облачной среде.

[A/B: оригинал → 37 → 404](shared-input-AB37-404/AB_ORIGINAL_FULL37_LATEST404_WIP.mp3), [FLAC](shared-input-AB37-404/AB_ORIGINAL_FULL37_LATEST404_WIP.flac). Начала: 0 / 4.168 / 8.336 с. Обе синтетические версии обработали ОДИН сохранённый реальный native input. Рабочие WAV не нормированы; только для A/B выровнена общая stereo RMS. Каналы L/R по отдельности не нормировались. Состояния, WAV и оценки этого одного входа сохранены рядом. Это не замена независимым проверкам.

403 прошла новые 6 warm + 2 cold: среднее уменьшение ошибки первых шести 0.0005423, SEM 0.0001212; оба cold положительные. 404 отдельно прошла тот же неизменный критерий: среднее уменьшение 0.0005942, оба cold положительные. Все 24 native/control/candidate WAV для каждой точки и точные состояния сохранены в соответствующих каталогах. Номер 404 — номер серии подбора, не новая крупная версия полного комплекта.

Первый Jacobian-тест оказался технически некорректным; [исправление опубликовано явно](../original-real-DSP-Jacobian-primary-current/README_RU.md). Исправленный и ограниченный тесты ничего не приняли. Основные принятые варианты и архивы прежних версий сохранены.
''')
  guide=PUBLIC/'LATEST_THREE_NOTE_RU.md';guide.write_text('''# Текущий проверенный трёхнотный вариант

Снимок 28 октября: [404 — полный ZIP](stereo-cascade87-cohort-0404/cohort-0404_complete_FL20_STEREO_WIP.zip), [как загрузить в FL Studio 20](stereo-cascade87-cohort-0404/README_RU.md), [A/B оригинал → 37 → 404](original-three-sweep-404-checkpoint/shared-input-AB37-404/AB_ORIGINAL_FULL37_LATEST404_WIP.mp3).

В A/B 404 начинается с 8.336 с. Для собственного сравнения используйте 48000 Hz и 180 BPM. Три длинные ноты, обычные native FL + два официальных ZL, без Finish. Небольшие улучшения подтверждены новыми парными и холодными рендерами; полного совпадения пока нет. [Проверки и ограничения](original-three-sweep-404-checkpoint/README_RU.md). Если позднее появился новый полностью опубликованный принятый checkpoint, этот снимок не должен перезаписывать его.
''')
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n')
  main=PUBLIC/'README_RU.md';main.write_text('[Текущий трёхнотный вариант 404, FL20 ZIP/инструкция и A/B с оригиналом](LATEST_THREE_NOTE_RU.md). Полного совпадения пока нет.\n\n'+main.read_text());h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish three-held404 original A-B and correct invalid initial Jacobian experiment');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[guide,dest/'README_RU.md',ab/'AB_ORIGINAL_FULL37_LATEST404_WIP.mp3',old/'TECHNICAL_INVALID_FIRST_ATTEMPT.json']
  for p in checks:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,AB_same_actual_native_input=True,invalid_first_Jacobian_explicitly_corrected=True,old_kit_DSP_and_PC_GUI_trees_preserved=True,reference_match_reached=False);(H/'THREE_SWEEP404_AB_AND_GN_CORRECTION_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
