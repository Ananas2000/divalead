"""Keep current setup, actual process evidence and reproducible research code."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;A=H.parent/'pc-stereo-20261024';O=H.parent/'stereo-refinement-20261025';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='actual404_dual_matcher_checkpoint');P,N,C,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+600
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='save actual404 main/finite-study evidence and startup draft125; no DSP adoption'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Existing publisher still owns Git coordination')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);parent=PUBLIC/'original-three-sweep-404-checkpoint';d=parent/'actual-main-and-mean3-20261028T1722';d.mkdir();scripts=d/'scripts';scripts.mkdir()
  for name in ['ACTUAL_DUAL_MAIN_AND_MEAN3_SNAPSHOT_20261028.json','ACTUAL_CURRENT372_THREE_SWEEP_20261028_START.json','CLOUD_ACTUAL_DUAL_MATCHER_DRAFT_RECEIPT_20261028.json','OLD_DERIVED_AB_REMOTE_VERIFIED_LOCAL_RELEASE_20261028.json','THREE_SWEEP404_AB_AND_GN_CORRECTION_PUBLICATION.json']:shutil.copyfile(H/name,d/name)
  for name in ['ORIGINAL_PRIMARY_MEAN3_THREE_SWEEPS_CURRENT404_STUDY.json','FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json']:shutil.copyfile(N/name,d/name)
  for name in ['study_PRIMARY_mean3_three_sweeps_current404.py','Primary_mean3_three_sweeps_current404_support.py','checked_mean_three_real_primary_fit.py','normal_staged_primary_fit.py','study_PRIMARY106_detector_joint_three_sweeps404.py','Primary106_detector_joint_three_sweeps404_support.py','checked_joint_detector_primary_fit.py','backup_and_release_old_derived_AB_batch.py','cleanup_closed_regenerable_vst3_buffers.py','publish_actual404_dual_matcher_checkpoint.py']:shutil.copyfile(H/name,scripts/name)
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,scripts/name)
  shutil.copyfile(A/'stereo-continuous87/BEST_CANDIDATE.json',d/'CURRENT_BEST_SNAPSHOT.json')
  for label in ['original-real-DSP-Jacobian-fixed-base-negative','original-real-DSP-Jacobian-constrained-negative']:shutil.copyfile(O/(label+'_PUBLICATION.json'),d/(label+'_PUBLICATION.json'))
  text=(H/'cloud_start_current.md').read_text();(C/'start_skill_current.md').write_text(text);(h['BASE']/'start_skill_current.md').write_text(text);(d/'CLOUD_START_CURRENT.md').write_text(text)
  (d/'README_RU.md').write_text('''# Фактический запуск после 404 и восстановление среды

Принятая 404 полностью сохранена: [ZIP и FL20-инструкция](../../LATEST_THREE_NOTE_RU.md). После копирования и проверки на GitHub старых производных A/B освобождено 67 409 124 байт локальных архивов. Их точные данные и исходные пути восстановления сохранены; actual candidate/source WAV и текущие состояния оставлены.

Основной реальный подбор возобновлён PID 687642 с серии 405. Отдельный реальный поиск PID 687430 проверяет три одинаковых native-входа на каждом из трёх проходов. Оба его PRIMARY-хоста прошли neutral configure против прямой загрузки: 0/0. Все основные веса, строгие fresh/cold допуски, три входящие ноты и source/native/POST/trim сохранены. Снимки процессов — свидетельство работы в указанное время, не обещание будущей активности. Контроллер и PID/starttime определяют текущую активность. Подготовленный поиск 106 параметров к моменту снимка ещё не запускался.

Полного совпадения нет. Исправленные Jacobian и constrained-тесты полностью архивированы и не приняты. Startup instructions сохранены и побитово прочитаны из черновика среды, revision 125; они не применены и не опубликованы. Для постоянного снимка среду можно просмотреть, сохранить и опубликовать в настройках. Это не требует приостанавливать уже разрешённую аудиоработу. Текущие пути и точные правила — в CLOUD_START_CURRENT.md.
''')
  (d/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(d).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in d.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');r=parent/'README_RU.md';r.write_text('[Фактический запуск 405, mean-three и сохранённый setup](actual-main-and-mean3-20261028T1722/README_RU.md).\n\n'+r.read_text());sums=parent/'FILE_SHA256.json';old=json.loads(sums.read_text());old.update({p.relative_to(parent).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in parent.rglob('*')if p.is_file()and p!=sums});sums.write_text(json.dumps(old,indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Save actual405 and three-input matching restart, draft125 and verified old A-B recovery');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in[d/'README_RU.md',d/'CLOUD_START_CURRENT.md',d/'ACTUAL_DUAL_MAIN_AND_MEAN3_SNAPSHOT_20261028.json']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,old_kit_DSP_and_PC_GUI_trees_preserved=True,actual_process_snapshot_HTTP_byte_exact=True,startup_draft125_saved_not_applied=True,reference_match_reached=False);(H/'ACTUAL404_DUAL_MATCHER_CHECKPOINT_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
