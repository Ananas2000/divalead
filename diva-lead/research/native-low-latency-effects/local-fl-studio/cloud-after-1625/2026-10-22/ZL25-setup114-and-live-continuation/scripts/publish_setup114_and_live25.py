"""Back up exact setup114 readback proof and a current actual-process snapshot."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');S=Path('/workspace/divalead-setup');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='setup114_live25_backup')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='back up exact setup114 full scripts and live actual25 continuation'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID'];assert h['alive'](pid)and Path(f'/proc/{pid}/stat').read_text().split()[21]==state['owner']['starttime'];assert str(A/'continue_stereo_ZL_matching.py').encode()in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
  for host in state['actual_VST3_hosts']:assert h['alive'](host['PID'])and Path(f"/proc/{host['PID']}/stat").read_text().split()[21]==host['starttime']
  dest=PUBLIC/'ZL25-setup114-and-live-continuation';dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  for p in [S/'scripts/setup-current-STEREO25.sh',S/'start-current-STEREO25.md',A/'verify_current_stereo_environment_runtime.py',H/'prepare_current_setup25.py',H/'publish_setup114_and_live25.py']:
   shutil.copyfile(p,scripts/p.name)
  for p in [H/'SETUP25_SAVED_READBACK_PROOF.json',H/'SETUP25_PREPARATION.json',H/'STEREO25_ACTUAL_STARTUP_RUNTIME_PROOF.json',N/'CURRENT_WORKSPACE_REPOSITORY_DISCOVERY.json']:shutil.copyfile(p,dest/p.name)
  (dest/'ACTUAL_LIVE_CONTROLLER.json').write_text(json.dumps(state,indent=2)+'\n');shutil.copyfile(A/'stereo-continuous87/BEST_CANDIDATE.json',dest/'CURRENT_BEST_SNAPSHOT.json')
  s=read(H/'SETUP25_SAVED_READBACK_PROOF.json')
  text=f'''# Setup114 сохранён; фактический двухступенчатый подбор продолжается

[Полный ZL25 WIP / WAV / A-B / инструкция FL20](../ZL25_CONTINUATION_RU.md).
[Двухступенчатый runtime и восстановление](../ZL25-runtime-handoff-20261025/README_RU.md).

Backendчерновик revision{s['revision']} подтверждён отдельным readback: полные
install/startточны, единственный project Ananas2000/divalead /workspace/divalead,
полный localHEAD{s['exact_repository_SHA']}. Полный обход17477каталогов безошибок;
четыре аудиоcodecdependencybuildcache явноклассифицированы и сохранены.
Сеть/secrets/runtime requirements прежние. Fullinstall113 сохранён какprefix,
добавлен реально проверенный genericstartupдвухZL25. Bashsyntaxпрошёл.
ColdZLstatebytes/PDC0/impulse0 реально проверены. Не заявляется повторный
полный bootstrap новой машины или открытие нового FLP вWindowsGUI.

requires_publish=true: сохранение черновика НЕ применило и НЕ опубликовало
конфигурацию. Для применения нужны Review/Save и Publish в настройках среды.
Это не блокирует текущую Linux/Wine работу. Черновик pin может быть старше
последующих automaticaudio commits; актуальные repoheaders/controller/BEST
важнее старых снимков. Никогда не откатывать новое PCGUI/cloudпродолжение.

На момент снимка реальный PID{pid}, phase{state['phase']},cohort{state.get('cohort')},
cases{state.get('cases')}; проверены четверо actualVST3host PID/starttime.
Это свидетельство конкретного момента, не обещание бесконечной работы.
Native06/actualDivasource/ARP/ADSR/3heldnotes41-37-36twice сохранены.
Фиксированный POST25 содержит SideAllPass10000Q2+2200Q4+895.8Q13.84.
Первый ZL меняется, oldoriginalobjective/fresh6/cold2/tolerances прежние,
upperstereo +новаяlowmidзащита добавочны. Полного совпадения пока нет.
Все полезные принятые cohorts autoGit ALL24WAV +полный playableFL20ZIP.
Прежние полные kits иPCGUI2026-10-24treeOID сохранены. APIquota% недоступен;
результаты бэкапятся по завершении, Root208MiB/tmp128MiB остаютсяguards.
'''
  (dest/'README_RU.md').write_text(text);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text('[ZL25: setup114 сохранён и прочитан обратно, текущая работа и инструкции](ZL25-setup114-and-live-continuation/README_RU.md).\n\n'+p.read_text())
  header='''BEGIN_SETUP114_ZL25_20261025
Setupdraft114 fullinstall/start/exactrepoSHA readbackverified, pinnedb0edd24e05b0709eddc00afe4bc1dc3f3bbd5e5d (neweraudioGitcommits mayexist). Publicbackup ZL25-setup114-and-live-continuation/README_RU.md. requires_publishTRUE, NOTapplied/published, onlyReviewSavePublishactivates; doesnotblockcurrentwork. NewactualgenericZL25startup/exactstate/PDC0/impulse0 andbashsyntaxchecked, no newfullmachinerestoreclaim. Latestfull25 andactualTWOZLruntime inprecedingheaders; preserve3SideAPPOST/currentBEST andalloriginalsciencegates. Thissetupinfo doesnotreplace newest acceptedcandidate/controller. Allpreviouskits/PCGUIretained, fullsoundmatchFALSE. Keepactualmatchingrunninguntillimits/userstop; no pertrialquestions.
END_SETUP114_ZL25_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Save verified setup114 recovery and current real two-ZL WIP25 continuation');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),actual_main_PID=pid,exact_setup_revision=114,requires_publish=True,config_not_applied=True,reference_match_reached=False)
  (H/'SETUP114_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
