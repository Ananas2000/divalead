"""Persist actual35 adoption/startup proofs; preserve every kit's DSP tree."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;A=H.parent/'pc-stereo-20261024';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_full35_runtime_handoff');P,N,R,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];assert json.loads((H/'ADOPTED_FULL35_RUNTIME_CHECK.json').read_text())['actual_new_runtime_two_cold_two_ZL_chain_errors']==[0.,0.];pause=R/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish actual35 runtime proof and startup handoff'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Another publisher remains active')
  time.sleep(.5)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);research=PUBLIC/'original-Mid-AP5-stereo-full35'
  for name in ['ZL35_FULL_PUBLICATION.json','ADOPTED_FULL35_RUNTIME_CHECK.json','ACTUAL_FULL35_ORIGINAL_TARGET_START.json','CURRENT_CHAIN_READINESS.json','CURRENT35_CHAIN_READINESS_20261027.log','CLOUD_FULL35_DRAFT_RECEIPT_20261027.json','FULL35_INPUT_AND_COLD_PROOF.json','VERIFIED_MID_AP5_POSITIVE_AUXILIARY_WAV_RELEASE.json','VERIFIED_CLOSED_NEGATIVE_TRAINING_F32_RELEASE_20261027.json']:shutil.copyfile(H/name,research/name)
  for name in ['adopt_and_check_full35_runtime.py','start_actual_full35_original_target_continuation.py','check_current_original_chain_readiness.py','prepare_full35_inputs_and_cold_proof.py','publish_full35_runtime_handoff.py']:shutil.copyfile(H/name,research/'scripts'/name)
  startup=(H/'cloud_start_current.md').read_text();(R/'start_skill_current.md').write_text(startup);shutil.copyfile(R/'start_skill_current.md',h['BASE']/'start_skill_current.md');(research/'CLOUD_START_CURRENT.md').write_text(startup)
  (research/'HANDOFF_FULL35_RU.md').write_text('Полный35 опубликован71d33ef5c52b565921681fa7aa1144df055cfc90. НовыйPOST: только MidAllPass5/650Hz/Q9.6; sourceDiva281/ARP/ADSR/три длинные/native12base10WS52/PRIMARY34иnativeTrim34 прежние. Первый10пар gain.001975495283, SEM.000025221148, lowmidLRerror~3.03->1.38 на каждой из12пар, upperRMS1.48/abs1.6/lowmid3.25; небольшоеAir+.0044dB раскрыто. ПолныйFL20ZIP/WAV/A-B/инструкция лежат ZL-WIP35. Два cold восстановленияZIP0/0 и реального runtime0/0; readiness35 native12resaves/каскад0/0, PDC0. Main реально стартовалPID598785/cohort353:4VST3ZL+2nativeTrimhosts; позже мог продвинуться. Сверять controller и PID/starttime, не перезаписывать более новый BEST старымadopter. Продолжается существующая94параметроваянастройка; отдельнаяMid5refinement35 серия83частотыQ использует3новыхвхода и строгие first6AND10/cold2/stereo/air. Setup-инструкции saved draft, не опубликованы. Нет GUI/ASIO/процента/полного совпадения/слуховогоутверждения.\n')
  for p in [PUBLIC/'ZL35_CONTINUATION_RU.md',research/'README_RU.md']:
   s=p.read_text();s=s.replace('WS52/исходные12native и POST32.','WS52/исходные12native и настройки существующих полос POST32; добавлен только Mid AllPass5.');p.write_text(s)
  (research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Persist verified full35 adoption, actual continuation and original-reference startup');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);checks=[]
  for p in [research/'HANDOFF_FULL35_RU.md',research/'ADOPTED_FULL35_RUNTIME_CHECK.json',research/'CLOUD_START_CURRENT.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,full_kit='ZL-WIP35',actual_runtime_adopted_and_started=True,actual_two_cold_complete_runtime_errors=[0.,0.],all_kit_DSP_trees_and_PC_GUI_preserved=True,HTTP_checks=checks,reference_match_reached=False);(H/'ZL35_CURRENT_RUNTIME_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
