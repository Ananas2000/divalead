"""Preserve adopted full38 runtime, setup restoration, and diagnostic evidence."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time,zipfile
T=Path(__file__).resolve().parent
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='full38_actual_runtime_checkpoint')
P,N,C,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git=h['git'];A=T.parent/'pc-stereo-20261024'
pause=C/'auto-backup.pause';deadline=time.monotonic()+240
def identity(pid):
 try:
  root=Path('/proc')/str(pid);stat=(root/'stat').read_text().split()
  if stat[2]=='Z':return None
  return dict(PID=pid,starttime=stat[21],cmdline=(root/'cmdline').read_bytes().replace(b'\0',b' ').decode())
 except FileNotFoundError:return None
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='checkpoint actual published/adopted38 runtime and tested ephemeral tooling restoration'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher remains active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main')
  protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  best=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['full_public_kit_directory']=='ZL-WIP38'
  state=json.loads((N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json').read_text());owner=identity(state['owner']['PID']);assert owner and owner['starttime']==state['owner']['starttime']
  actual=[identity(row['PID'])for row in state['actual_VST3_hosts']+state['actual_native_post_trim_hosts']]
  assert all(actual) and len(actual)==6
  dest=PUBLIC/'original-joint109-full38/actual-runtime-20261030';dest.mkdir(exist_ok=False);scripts=dest/'scripts';scripts.mkdir()
  names=['ADOPTED_FULL38_RUNTIME_CHECK.json','ZL38_FULL_PUBLICATION.json','ACTUAL_FULL38_CONTINUATION_START.json','FULL38_OWN_STOP_RELEASE.json','TMP_RUNTIME_RESTORATION_PROVENANCE.json','FRESH_PREFIX_STARTUP_PROBE.json','ONBOARDING_FULL38_DRAFT_READBACK.json','CURRENT_VERIFIED_PUBLIC_BLOB_CACHE_RELEASE_AFTER38_20261030.json','OLDER_NUMERIC_PUBLIC_CACHE_RELEASE.json']
  for name in names:shutil.copyfile(T/name,dest/name)
  for name in ['restore_tmp_audio_runtime.py','restart_current_full38_matching.py','adopt_and_check_full38_runtime.py','probe_native_waveshaper_transfer_axis.py','study_native_WS52_current_full38_screen.py','release_current_public_blob_cache_after38.py','release_older_numeric_public_audio_cache.py','publish_actual_full38_runtime_checkpoint.py']:shutil.copyfile(T/name,scripts/name)
  (dest/'BEST_SNAPSHOT.json').write_text(json.dumps(best,indent=2)+'\n');(dest/'MAIN_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n')
  snapshot=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_main=owner,actual_effect_hosts=actual,original_is_only_target=True,only_three_incoming_held_notes=True,full_base_kit='ZL-WIP38',POST_SHA256=state['fixed_post_SHA256'],liveness_is_point_in_time_only=True,reference_match_reached=False,FL_GUI_validation_pending=True)
  (dest/'ACTUAL_PROCESS_SNAPSHOT.json').write_text(json.dumps(snapshot,indent=2)+'\n')
  diag=T/'WAVESHAPER_AXIS_DIAGNOSTIC';shutil.copyfile(diag/'RESULT.json',dest/'WAVESHAPER_AXIS_DIAGNOSTIC_RESULT.json');archive=dest/'WAVESHAPER_AXIS_DIAGNOSTIC_ALL_RETAINED_DATA.zip'
  with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for p in sorted(diag.iterdir()):
    if p.is_file():z.write(p,p.name)
  with zipfile.ZipFile(archive)as z:
   for p in diag.iterdir():
    if p.is_file():assert z.read(p.name)==p.read_bytes()
  (dest/'WAVESHAPER_DIAGNOSTIC_ARCHIVE_MANIFEST.json').write_text(json.dumps(dict(archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),members={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in diag.iterdir()if p.is_file()},diagnostic_only_not_a_lead_candidate=True),indent=2)+'\n')
  startup=(T/'start_skill_current.md').read_text();(dest/'CLOUD_START_CURRENT.md').write_text(startup);(C/'start_skill_current.md').write_text(startup);(h['BASE']/'start_skill_current.md').write_text(startup)
  (dest/'README_RU.md').write_text('''# Фактическое продолжение после публикации38 — 30октября

WIP38 опубликован и принят в рабочий контур. После публикации два новых полных рендера текущего runtime совпали с комплектом0/0; текущие POST/trim пересохранены побайтно. Реально запущенный подбор от38 и шесть живых эффект-хостов проверены по PID/starttime на время снимка. Снимок не обещает будущую активность.

[Полный комплект38 и FL20 инструкция](../../ZL38_CONTINUATION_RU.md). Полного совпадения с оригиналом нет. Цель — исходный референс; только три длинные входящие ноты, верхние прыжки делает ARP Diva. WindowsGUI/ASIO здесь не проверялись.

Сохранены проверенное восстановление временной среды после сброса /tmp, реальный отдельный тест нового Wine prefix, текущие стартовые инструкции и прочитанный обратно draft128. Сохранение черновика само по себе не публикует настройки среды и не останавливает разрешённый подбор.

Также сохранены журналы безопасного удаления только проверенных публичных локальных копий и кеша Git. Все исходники, оригинал, приватные DLL, старые версии на GitHub и текущие комплекты сохранены.

Диагностика WaveShaper отдельно содержит все сохранённые WAV/состояния и код. Там остальные эффекты выключены только для проверки оси кривой; это НЕ новый вариант лида. Идущий новый WS52 screen использует полную обычную цепочку38 и отдельно сохраняет результаты. Его завершение/успех этот снимок не утверждает.
''')
  positive=PUBLIC/'original-joint109-Air-margin-positive/README_RU.md';positive.write_text('[Позже эта точка прошла полный экспорт и независимый повтор ZIP и стала WIP38](../ZL38_CONTINUATION_RU.md). Текст и архив исследования ниже сохраняют состояние до принятия.\n\n'+positive.read_text())
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n')
  h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Checkpoint adopted full38 runtime, tested cloud restoration and actual WaveShaper diagnostic');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in [dest/'ADOPTED_FULL38_RUNTIME_CHECK.json',dest/'CLOUD_START_CURRENT.md',archive,dest/'ONBOARDING_FULL38_DRAFT_READBACK.json']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,actual_adopted_full38_and_setup_checkpoint=True,HTTP_bytes_verified=True,all_old_kits_and_PC_GUI_tree_preserved=True,draft_revision=128,reference_match_reached=False);(T/'FULL38_ACTUAL_RUNTIME_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
