from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
U=Path(__file__).resolve().parent;R=Path('/tmp/divalead-AB-original-39-559-20261031');h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_AB_actual39_559');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish actual same-input original39_559 A/B and WAV proof'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/'original-full39-accepted559-common-input-20261031';dest.mkdir();proof=json.loads((R/'PROOF.json').read_text());assert proof['two_fresh_actual559_cold_full_chain_replay_errors']==[0.]
  for name in['AB_ORIGINAL_ZL39_559_WIP.mp3','AB_ORIGINAL_ZL39_559_WIP.flac','ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip','PROOF.json']:shutil.copyfile(R/name,dest/name)
  scripts=dest/'scripts';scripts.mkdir()
  for name in['build_AB_original_39_559.py','publish_AB_original_39_559.py']:shutil.copyfile(U/name,scripts/name)
  doc='''# A/B: оригинал → полный39 → принятая559

[MP3](AB_ORIGINAL_ZL39_559_WIP.mp3), [FLAC](AB_ORIGINAL_ZL39_559_WIP.flac): оригинал0с →39с4.168с →559с8.336с. Оба варианта обработали один и тот же реальный native11WAV, поэтому различие вызвано первым ZL, а не разными стартовыми фазами Chorus. Это отдельное удобное сравнение, не новое правило принятия кандидата.

[Полный559 ZIP и FLStudioинструкция](../stereo-cascade87-cohort-0559/README_RU.md). [Полная базовая39 и подробная инструкция](../ZL39_CONTINUATION_RU.md). По сравнению с более старыми версиями обязательны SOURCE WaveShaper из39 и обаZL плюс финальный StereoShaper. Источник Diva/три длинные ноты/ARP/ADSR/native11/POST/trim между39 и559 не менялись. В559 меняется только PRIMARY.

559 прошла отдельные fresh6+2cold: first6gain.000843705932/SEM.000145936143, cold+.000867264180/+.001013158403; все stereo/pairedlowmid/Airгейты пройдены. Airfirst6−.009964848016dB, обаcold также снизились. Дополнительные10пар для numeric559 не выполнялись; утверждение first10/nonincrease полного39 на559 не переносится.

Рабочие WAV и все сохранённые состояния доступны в ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip. Рабочее аудио без нормировки. Только A/B общая stereoRMS и общая защита от пиков, L/R отдельно не нормировались. На этом одном входе критерий39=1.266038782076/559=1.263041000697; это не процент сходства. Два новых холодных559 повторились0/0, обаZL PDC0; не WindowsGUI/ASIO.

Полного совпадения пока нет. Цель — исходный оригинал; старый Finish и MistaTowa не используются. Идущий отдельный совместный подбор изменённого источника Diva и PRIMARY не принят и в этот A/B не входит. Текущую активность подтверждают только реальные процессы/контроллеры.
'''
  (dest/'README_RU.md').write_text(doc);p=PUBLIC/'LATEST_THREE_NOTE_RU.md';p.write_text('[A/B оригинал →39→принятая559 на общем nativeвходе, полный559 комплект](original-full39-accepted559-common-input-20261031/README_RU.md). Полного совпадения нет.\n\n'+p.read_text());p=PUBLIC/'README_RU.md';p.write_text('[Свежее A/B оригинал →39→559 и полныйFL20 комплект559](original-full39-accepted559-common-input-20261031/README_RU.md).\n\n'+p.read_text());(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish same-input original to WIP39 to accepted559 A/B with actual WAV and cold replay proof');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in[dest/'AB_ORIGINAL_ZL39_559_WIP.mp3',dest/'ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip',dest/'README_RU.md']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),AB_and_actual_WAV_ZIP_HTTP_byte_exact=True,old_kits_PC_GUI_preserved=True,reference_match_reached=False);(U/'AB39_559_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
