"""Preserve actual normal-EQ original-reference screen without adopting it."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;ROOT=Path('/tmp/divalead-original-target-post-EQ6-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='normal_post_EQ6_original_target_evidence')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];s=read(ROOT/'completion.json');assert s['training_cases']==74 and not s['sufficient_screen']
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='back up74realnormalpostEQtrials andtrainingWAV whileoriginal-onlycontinuationruns'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'original-target-normal-post-EQ6-study01';h['copy_evidence'](ROOT,dest,True);scripts=dest/'scripts';scripts.mkdir()
  for name in ['study_post_EQ_original_normal_processing.py','publish_post_EQ6_rejected_screen.py','evict_verified_full26_build_duplicates.py']:shutil.copyfile(H/name,scripts/name)
  shutil.copyfile(H/'FULL26_VERIFIED_BUILD_DUPLICATE_EVICTION.json',dest/'FULL26_VERIFIED_BUILD_DUPLICATE_EVICTION.json')
  state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID'];assert state['original_is_the_only_target']
  assert Path(f'/proc/{pid}/stat').read_text().split()[21]==state['owner']['starttime']and Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
  (dest/'LIVE_MAIN_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n')
  doc='''# Шесть обычных полос EQ после нелинейной обработки —74реальных пробы

Цель — исключительно загруженный оригинал, неv83/Finish. Проверялась новая
гипотеза распределения частотной коррекции после имеющейся nativeцепи иZL.
Во втором официальном ZL включались6обычных статических Stereopeakingполос,
безlookahead/линейнойфазы. Настоящие nativeDLL дали3новых входа PRIMARY,
два оставлены дляheldout. Два настоящих ZLVST3worker отрендерили74пробы.

Контроль с включёнными нулевымиgainполосами воспроизвёл оценку исходника
с прежним допуском. Подбор gain/frequency/Q не дал допустимого улучшения:
лучший вариант остался безкоррекции, heldoutgain0/0. Fresh6/cold2/export
не запускались, потомучтоscreenнепрошёл. Никакие настройки этогофайла
RESEARCH_ONLY не приняты в рабочийпроект. Полный26 остаётся лучшей принятойбазой.
Дальнейший непрерывный PRIMARYподбор к оригиналу работал отдельно и не остановлен.

Сохранены все74настройки/оценки,3trainingPRIMARY WAV и1выбранныйконтрольный
WAV, сохранённые компоненты/параметры искрипт. Это неархив каждогоtrialWAV.
Три длинные ноты41→37→36дважды/ARP/ADSR/native06/Diva281 неизменны.
Дополнительныестереоguards/исходныйscore/веса/819alignment/пороги прежние.
GUIэкспорт/субъективное прослушивание/полное совпадение не заявляются.
После exactSHA/CRC/GitHTTPпроверок удалены только лишние build/ZIPrestoreкопии
уже опубликованного26, освобождено43810816байт/tmp. Текущий public26полностью
сохранён, как иисточники/валидационныеWAV/старыеверсии/PCGUI. Cacheвосстановим.

[Последний полный WIP26 и A/B/FLинструкция](../ZL26_CONTINUATION_RU.md).
[Текущий original-onlyruntime и продолжение](../ZL26-original-target-runtime-and-WS51/README_RU.md).
Оригинал толькоанализ/A-B, не подмешивается в синтез; MistaTowa не используется.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Record74 actual normal post-EQ trials against original without adopting unconfirmed changes');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),screen_accepted=False,actual_main_PID_at_snapshot=pid,original_is_the_only_target=True,reference_match_reached=False);(H/'POST_EQ6_SCREEN_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
