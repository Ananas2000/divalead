from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
U=Path(__file__).resolve().parent;A=U.parent/'pc-stereo-20261024';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='full39_adopted_runtime_checkpoint');P,N,C,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='checkpoint full39 adoption, supported restored runtime, saved draft130 and actual ongoing research'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Other publisher active')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);best=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['full_public_kit_directory']=='ZL-WIP39';state=json.loads((N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json').read_text());live=[]
  for row in[state['owner'],*state['actual_VST3_hosts'],*state['actual_native_post_trim_hosts']]:
   proc=Path('/proc')/str(row['PID']);s=(proc/'stat').read_text().split();assert s[2]!='Z'and s[21]==row['starttime'];live.append(dict(PID=row['PID'],starttime=s[21]))
  dest=PUBLIC/'original-bipolar-even8-full39/actual-runtime-20261031';dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for name in['ADOPTED_FULL39_RUNTIME_CHECK.json','ZL39_FULL_PUBLICATION.json','ACTUAL_FULL39_CONTINUATION_START.json','TMP_RUNTIME_RESTORATION_PROVENANCE.json','CURRENT39_READINESS_PROOF.json','ONBOARDING_DRAFT39_READBACK.json','BACKED_MARGIN39_TRAINING_WAV_RELEASE.json','PREVIOUS_COMPLETE_ZIP_WORKTREE_RELEASE.json']:shutil.copyfile(U/name,dest/name)
  for name in['restore_tmp_audio_runtime.py','restart_current_full39_matching.py','adopt_and_check_full39_runtime.py','publish_adopted_full39_runtime.py','study_native_odd_even17_current39.py','prepare_odd_even17_research.py','odd_even17_terminal.py.txt']:shutil.copyfile(U/name,scripts/name)
  for name in['continue_stereo_ZL_matching.py','backup_stereo_numeric_checkpoint.py','stereo_cascade_runtime.py','native_post_trim.py']:shutil.copyfile(A/name,scripts/name)
  (dest/'BEST_SNAPSHOT.json').write_text(json.dumps(best,indent=2)+'\n');(dest/'MAIN_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n');(dest/'LIVE_PID_SNAPSHOT.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),live=live,liveness_point_in_time_only=True),indent=2)+'\n')
  startup=(U/'start_skill_full39.md').read_text();(dest/'CLOUD_START_CURRENT.md').write_text(startup);(C/'start_skill_current.md').write_text(startup);(h['BASE']/'start_skill_current.md').write_text(startup)
  p=dest/'README_RU.md';p.write_text('''# Принятие WIP39 и проверка среды, 31октября

WIP39 опубликован и принят после12 новых пар и независимого ZIP. Новый supported native11 генератор и старая схема проверены реальными DLL. Два холодных каскада рабочего runtime совпали с WAV в пределах9.1×10⁻¹³; all12native пересохранены точно, два холодных повтора на новом фактическом nativeвходе0/0. Черновик стартовых инструкций130 сохранён и прочитан обратно; install_script/network/репозитории не менялись. Сохранение черновика не означает его применение или публикацию среды.

Реально запущены подбор первогоZL от39 и исследование17 локальных odd/evenконтролов WaveShaper. Снимки PID/starttime подтверждают активность только на момент снимка. Исследовательский17контрольный формат пока не поддерживается обычным экспортом и не принят. Каждый следующий результат требует своей проверки; first10/нерастущийAir39 не наследуются будущими numeric6+2cohort.

[Полный FL20 комплект и инструкция](../../ZL39_CONTINUATION_RU.md). Полного совпадения с оригиналом нет. Новый WindowsFLGUI/ASIO здесь не проверялся. Безопасно освобождены только подтверждённые удалённым Git дубликаты; старые версии/PCGUI/оригинал сохранены.
''');(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Checkpoint adopted native11 WIP39, actual runtime replay, restored cloud setup and matching continuation');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in[dest/'CLOUD_START_CURRENT.md',dest/'ADOPTED_FULL39_RUNTIME_CHECK.json',dest/'ONBOARDING_DRAFT39_READBACK.json',scripts/'restore_tmp_audio_runtime.py']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,actual_full39_runtime_and_setup_checkpoint=True,draft_revision=130,HTTP_checks_byte_exact=True,older_kits_and_PC_GUI_preserved=True,reference_match_reached=False);(U/'FULL39_ACTUAL_RUNTIME_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
