from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zipfile
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-AB-original40-578-20261104');h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_AB_actual40_578');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
arc=R/'ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip'
with zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(R.rglob('*')):
  if p.is_file()and p!=arc and p.suffix not in ['.f32','.exe','.dll','.log','.mp3','.flac']:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(arc)as z:assert z.testzip()is None
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish same real input original40/578 A/B and complete actual WAV/preset evidence'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/'original-full40-accepted578-common-input-20261104';dest.mkdir();proof=json.loads((R/'ACTUAL_AB_PROOF.json').read_text());assert proof['two_cold578_replay_error']==0
  for name in ['AB_ORIGINAL_ZL40_578_WIP.mp3','AB_ORIGINAL_ZL40_578_WIP.flac','ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip','ACTUAL_AB_PROOF.json']:shutil.copyfile(R/name,dest/name)
  scripts=dest/'scripts';scripts.mkdir()
  for name in ['build_AB_original40_578.py','publish_AB_original40_578.py']:shutil.copyfile(V/name,scripts/name)
  summary=json.loads((V.parent/'pc-stereo-20261024/stereo-continuous87/cohort-0578/completion.json').read_text());doc=f'''# A/B: оригинал → полный40 → принятая578

[MP3](AB_ORIGINAL_ZL40_578_WIP.mp3), [FLAC](AB_ORIGINAL_ZL40_578_WIP.flac): оригинал0с →40с4.168с →578с8.336с. Оба синтезированных варианта обработали ОДИН реальный native12WAV. Изменён только первый ZL; источник Diva, три длинные ноты/ARP/ADSR,12native, POST и финальный trim одинаковы. Полного совпадения пока нет.

[Полный578 ZIP и FLStudioинструкция](../stereo-cascade87-cohort-0578/README_RU.md). [Полная базовая40 и подробная инструкция](../ZL40_CONTINUATION_RU.md). В ZIP578 открыть Diva_STEREO_CONTINUED_WIP.flp,180BPM/48kHz/Pattern. Для старой565/39 нужны SOURCE WaveShaper из40, ОБА ZL и последний StereoShaper; предпочтителен полный FLP. Бесплатный ZL Equalizer2v1.4.1 тот же.

578 отдельно принята после6новых warm+2cold относительно576: first6gain{summary['first6_mean_improvement']:.12f}/SEM{summary['paired_difference_SEM']:.12f}, cold2{summary['cold_input_improvements']}. Все8stereo/pairedlowmid/Airгейты пройдены. Численный Aircap+.02dB; это не новая строгая first10/nonincreasingAirпроверка40. Все24native/control/candidateWAV этой проверки опубликованы с комплектом578.

Рабочие WAV и состояния в ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip, без нормировки. Только A/B общая stereoRMS и единая peakзащита; L/R отдельно не нормировались. На этом отдельном входе40={proof['single_draw_objectives_not_new_acceptance']['40']:.12f},578={proof['single_draw_objectives_not_new_acceptance']['578']:.12f}; это не процент сходства и не новая приёмка. Два холодных578 повторились точно0/0, savedstates точные, ZLPDC0. WindowsGUI/ASIO не проверены. Ассистент субъективное прослушивание не заявляет. Референс не подмешан в синтез, Finish/MistaTowa не используются.
'''
  (dest/'README_RU.md').write_text(doc);p=PUBLIC/'LATEST_THREE_NOTE_RU.md';p.write_text('[Принятая578: полный FL20 комплект и A/B оригинал →40→578 на общем входе](original-full40-accepted578-common-input-20261104/README_RU.md). Полного совпадения нет.\n\n'+p.read_text());p=PUBLIC/'README_RU.md';p.write_text('[A/B оригинал →40→578 и полный трёхнотный комплект578](original-full40-accepted578-common-input-20261104/README_RU.md).\n\n'+p.read_text());(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish same-input original to WIP40 to accepted578 A/B, actual WAVs and FL20 links');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in [dest/'AB_ORIGINAL_ZL40_578_WIP.mp3',dest/'ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip',dest/'README_RU.md']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),AB_and_actual_WAV_ZIP_HTTP_byte_exact=True,old_kits_PC_GUI_preserved=True,reference_match_reached=False);(V/'AB40_578_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
