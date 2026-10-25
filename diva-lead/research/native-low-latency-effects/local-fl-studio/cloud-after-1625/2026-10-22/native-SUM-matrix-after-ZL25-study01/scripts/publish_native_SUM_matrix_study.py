"""Preserve the completed rejected native SUM hypothesis without adopting it."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;ROOT=Path('/tmp/divalead-native-SUM-matrix-after25-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='SUM_matrix25_finite_evidence')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
s=read(ROOT/'completion.json');assert s['training_cases']==161 and not s['robust_improvement']and s['not_adopted']
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='save actual rejected161case nativeSUM hypothesis with all trainingWAV and routingproof'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'native-SUM-matrix-after-ZL25-study01';h['copy_evidence'](ROOT,dest,True);scripts=dest/'scripts';scripts.mkdir()
  for name in ['study_native_SUM_matrix_in_full25.py','publish_native_SUM_matrix_study.py']:shutil.copyfile(H/name,scripts/name)
  doc='''# Проверка четырёх коэффициентов native SUM после полного ZL25

161настоящая nativeDLL+дваZLVST3проба. Источник Diva/native06/ARP/ADSR/
три длинные входящие ноты на фразу и оба сохранённых ZL зафиксированы.
Менялись только четыре коэффициента штатного SUM Stereo Shaper.
Контекст primarycohort15 и POST25 с тремя SideAllPass сохранён вPRIMARY/POST.bin.

Три новых trainingprefix на сохранённом actualDivaисточнике, два heldout.
Реальное разбиение nativeцепи наprefix+SUM проверено при Chorusdepth0:
максимальная ошибка0, прежний допуск2e-7. Это не Pythonсимуляция эффектов.
Исходный originalobjective/веса/819alignment прежние; дополнительная защита
upperстерео и новой300–800Hzпоправки сохранена. Допустимый лучший training
вариант остался исходным; оба heldout не дали выигрыша. Fresh6/cold2
не запускались, поскольку training/heldoutэтап не прошёл. Нет принятия,
нового nativebase/FLP/полногоZIP или заявления полного совпадения.

Все161числа/настройки вTRAINING_RESULTS.json.gz. Три trainingprefix сохранены
lossless и проверены поSHA, отдельно есть4prefixWAV включаяzero-depthконтроль.
Sourcepresets/reference толькоанализ; оригинал не подмешан в синтез.
Новые DivaVST/WindowsGUIэкспорты не заявляются. Главный непрерывный поиск
PRIMARY с двумя ZL работал независимо и не остановлен этим исследованием.
Продолжать с [последней полной базой ZL25](../ZL25_CONTINUATION_RU.md) либо
более свежим действительно принятым и опубликованным numericalcohort.
Повторять этот же четырёхкоэффициентный поиск в том жеконтексте не нужно.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Record rejected real native SUM matrix search after ZL25 and all training audio');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  q=dest/'THREE_TRAINING_PREFIX_WAVs.tar.gz';assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+q.relative_to(P).as_posix())==q.read_bytes();assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),training_cases=161,accepted=False,all_training_audio_preserved=True,main_matcher_not_stopped=True,old_full_kits_and_PC_GUI_preserved=True,reference_match_reached=False)
  (H/'NATIVE_SUM_MATRIX_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
