from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-direct-original580-AB-20261104');h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_direct_original580_AB');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish direct original to exact WAV in accepted580 FL20 ZIP, instructions and proof'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/'original-accepted580-direct-AB-20261104';dest.mkdir();proof=json.loads((R/'PROOF.json').read_text());assert proof['actual_exact_working_WAV_inside_published_FL20_ZIP']
  for name in ['AB_ORIGINAL_580_WIP.mp3','AB_ORIGINAL_580_WIP.flac','PROOF.json']:shutil.copyfile(R/name,dest/name)
  for name in ['build_direct_AB_original580.py','publish_direct_AB580.py']:shutil.copyfile(V/name,dest/name)
  (dest/'README_RU.md').write_text('''# Оригинал →580: прямое сравнение с WAV из FL20 ZIP

[MP3](AB_ORIGINAL_580_WIP.mp3), [FLAC](AB_ORIGINAL_580_WIP.flac). Сначала оригинал,580 начинается с4.168с. Здесь использован ТОТ ЖЕ рабочий WAV, который лежит в полном ZIP580; равенство байтов проверено. Только в A/B применены одна stereoRMS-поправка и общая защита от пиков. L/R отдельно не нормировались. Исходный рабочий WAV и пресеты не менялись.

[Полный580 ZIP](../stereo-cascade87-cohort-0580/cohort-0580_complete_FL20_STEREO_WIP.zip), [инструкция](../stereo-cascade87-cohort-0580/README_RU.md). Распаковать в новую папку, открыть Diva_STEREO_CONTINUED_WIP.flp;180BPM/48kHz/Pattern. Нужны Diva, штатные Fruity и бесплатный ZL Equalizer2v1.4.1. Три длинные входящие ноты41→37→36 на фразу; верхние скачки создаёт внутренний ARP. Если Diva запросит пресет — Diva_NATIVE_WIP_THREE_HELD.h2p из ZIP.

Самостоятельный трёхнотный комплект580 принят по своей проверке6warm+2cold; это A/B не новая приёмка и не процент сходства. Полного совпадения с оригиналом пока нет. Native12/13native+2ZL, минимум фазы/lookahead0/AutoGainOff, прежний Finish/свёртка отсутствует. Новый WindowsFLGUI/ASIO не проверен. Референс в синтез не подмешан, MistaTowa не используется.
''')
  p=PUBLIC/'LATEST_THREE_NOTE_RU.md';p.write_text('''# Проверенный трёхнотный комплект580

[Полный ZIP для FL Studio20](stereo-cascade87-cohort-0580/cohort-0580_complete_FL20_STEREO_WIP.zip), [инструкция](stereo-cascade87-cohort-0580/README_RU.md), [прямое A/B оригинал →580](original-accepted580-direct-AB-20261104/AB_ORIGINAL_580_WIP.mp3).580 начинается с4.168с. Звук580 в A/B взят из WAV полного ZIP, а не нового дубля.

Полного совпадения нет. База native12/WIP40 с13native и2ZL; Diva/триheld/ARP/ADSR/WS/POST/finaltrim сохранены, изменён PRIMARY. [Подробности](original-accepted580-direct-AB-20261104/README_RU.md). [Исходный полный40](ZL40_CONTINUATION_RU.md) и все старые комплекты сохранены. Свежие последующие опубликованные numericalветки видны в основном README; эта страница фиксирует комплект580 и не обещает активность процессов.
''');p=PUBLIC/'README_RU.md';p.write_text('[Прямое A/B оригинал →580 и полный FL20 комплект](original-accepted580-direct-AB-20261104/README_RU.md).\n\n'+p.read_text());(dest/'FILE_SHA256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.iterdir()if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish direct original to accepted580 A/B using the exact WAV in its complete FL20 ZIP');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==v for p,v in protected.items());assert git('rev-parse','HEAD:'+pc)==oid;h['push_and_confirm'](commit)
  for p in [dest/'AB_ORIGINAL_580_WIP.mp3',dest/'README_RU.md',dest/'PROOF.json']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),HTTP_byte_exact=True,actual_exact_WAV_in_published580_ZIP=True,reference_match_reached=False);(V/'DIRECT580_AB_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
