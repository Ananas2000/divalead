"""Checkpoint actual accepted runtime, tested restoration and persisted setup draft."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
V=Path(__file__).resolve().parent;A=V.parent/'pc-stereo-20261024';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='full40_runtime_setup_checkpoint');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='checkpoint accepted full40, tested restored runtime, saved draft132 and genuine continued matching'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher owns pause')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);best=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['full_public_kit_directory']=='ZL-WIP40';state=json.loads((N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json').read_text());live=[]
  for row in[state['owner'],*state['actual_VST3_hosts'],*state['actual_native_post_trim_hosts']]:
   stat=(Path('/proc')/str(row['PID'])/'stat').read_text().split();assert stat[2]!='Z'and stat[21]==row['starttime'];live.append(dict(PID=row['PID'],starttime=stat[21]))
  dest=PUBLIC/'original-OSstep1-local17-full40/actual-runtime-20261104';dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for name in ['ADOPTED_FULL40_RUNTIME_CHECK.json','ZL40_FULL_PUBLICATION.json','ACTUAL_FULL40_CONTINUATION_START.json','CURRENT40_READINESS_PROOF.json','CURRENT565_READINESS_PROOF.json','ONBOARDING_DRAFT40_READBACK.json','ACTUAL_DIVA_SOURCE_RECHECK.json','TMP_RUNTIME_RESTORATION_PROVENANCE.json','INTERRUPTED_OS_LOCAL17_DATA_RESTORED.json','OLD30_38_MEDIA_CACHE_RELEASE.json','CLOSED_ZIP_DUPLICATE_CACHE_RELEASE.json','CURRENT40_KNOWN_LOOSE_AUDIO_OFFLOAD.json','DIVA15_SOURCE_REPLAY_FAILURE_DIAGNOSIS.json','OLD25_38_MEDIA_CACHE_RELEASE.json','ACTUAL_WS_OSSTEP2_GUI_PROOF.json']:shutil.copyfile(V/name,dest/name)
  shutil.copyfile(PUBLIC/'original-OSstep1-local17-full40/TMP_RUNTIME_RESTORATION_PROVENANCE.json',dest/'INITIAL_FRESH_TMP_RESTORATION_PROVENANCE.json')
  for p in V.glob('*.py'):shutil.copyfile(p,scripts/p.name)
  for name in ['continue_stereo_ZL_matching.py','backup_stereo_numeric_checkpoint.py','stereo_cascade_runtime.py','native_post_trim.py']:shutil.copyfile(A/name,scripts/name)
  for name in ['RESTORE_AUDIO_RUNTIME_FIXED.log','RESTORE_RUNTIME_FULL40_CHECK.log','CURRENT40_AUDIO_READINESS.log','ACTUAL_DIVA_RECHECK.log','NATIVE12_MIGRATION.log','BUILD40_HEADER_PARSER_DIAGNOSIS.log','BUILD40_HOT_COLD_SCOPE_DIAGNOSIS.log']:shutil.copyfile(V/name,dest/name)
  (dest/'BEST_SNAPSHOT.json').write_text(json.dumps(best,indent=2)+'\n');(dest/'MAIN_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n');(dest/'LIVE_PID_SNAPSHOT.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),live=live,liveness_point_in_time_only=True),indent=2)+'\n')
  startup=(V/'start_skill_full40.md').read_text();(dest/'CLOUD_START_CURRENT.md').write_text(startup);(C/'start_skill_current.md').write_text(startup);(h['BASE']/'start_skill_current.md').write_text(startup)
  doc='''# Принятие WIP40 и проверка среды, 4ноября

[Полный FL20 ZIP, A/B и инструкция](../../ZL40_CONTINUATION_RU.md). Полного совпадения с оригиналом нет.

WIP40 принят после12 новых пар, независимой распаковки ZIP и реального рендера. Supported native12 генератор без cachedbundle создаёт точное WaveShaper-состояние; all12state resave и два zeroDepth0/0. Два coldкаскада runtime0/0 с каноническим WAV. Источник Diva реально запущен снова:281параметр/12MIDI/исходный WAV точные. Другие11native/триheld/ARP/ADSR сохранены.

/tmp была очищена между задачами: среда восстановлена с проверкой исходных DLL и официального ZL. Исправлен устаревший путь проверки Xvfb. Fullfresh-/tmp и последующая ready-проверка native12 явно разделены. Подготовленный Wine/MinGW/Python/private uploads являются предусловиями; это не установщик с пустого образа.

Черновик инструкций132 сохранён и прочитан обратно точно. Installscript, сетевые правила, репозитории, секреты и runtime requirements не менялись. Черновик не применён/не опубликован. Для активации нужно сохранить изменения в настройках среды и опубликовать среду; работа по звуку от этого не ожидала подтверждения.

Реально запущен подбор от40 с4ZL+2nativeTrim. PID/starttime снимок доказывает активность только на время снимка. Численные продолжения требуют собственных6+2 проверок и не наследуют строгий first10/nonincreasingAir40. Малые Shape2пробы отсеяны: параметр менялся, фактический DivaWAV оставался тем же, поэтому видимый выигрыш на отдельных Chorusреализациях не принят. Состояния/рендеры/диагноз сохранены отдельно.

Освобождены только удалённо проверенные дубликаты кеша. Старые версии/PCGUI/оригинал/частные загрузки сохранены. Новый FLP в WindowsGUI/ASIO не проверен; субъективное прослушивание ассистентом не заявляется.
''';(dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Checkpoint adopted WIP40 runtime, actual Diva replay, safe cache cleanup and verified onboarding draft132');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in [dest/'CLOUD_START_CURRENT.md',dest/'ADOPTED_FULL40_RUNTIME_CHECK.json',dest/'ONBOARDING_DRAFT40_READBACK.json',scripts/'restore_tmp_audio_runtime_full40.py']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,actual_full40_runtime_and_setup_checkpoint=True,draft_revision=132,HTTP_checks_byte_exact=True,older_kits_and_PC_GUI_preserved=True,reference_match_reached=False);(V/'FULL40_RUNTIME_SETUP_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
