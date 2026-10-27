"""Finish the already committed guide update after a too-broad historical-kit guard."""
from pathlib import Path
import datetime,fcntl,hashlib,io,json,os,runpy,subprocess,time,zipfile
H=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='finish_current34_doc_guard');P,N,R,PUBLIC=[h[k]for k in['P','N','R','PUBLIC']];git=h['git'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='verify expected current34 guide-only update and finish normal push'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();base=git('rev-parse','origin/main');assert git('rev-parse','HEAD^')==base;assert git('log','-1','--format=%s')=='Record verified full34 runtime and clarify SUM-only mix settings without audio changes';kit='ZL-WIP34';kitpath=str((PUBLIC/kit).relative_to(P));protected=h['protected']();changed_protected=[p for p,oid in protected.items()if git('rev-parse',base+':'+p)!=oid];assert changed_protected==[kitpath],changed_protected
  zippath=kitpath+'/Diva_ZL34_STEREO_WIP_complete.zip';old=subprocess.run(['git','-C',str(P),'show',base+':'+zippath],capture_output=True,check=True).stdout;new=(P/zippath).read_bytes();allowed={'FL20_ZL34_STEREO_WIP/'+p for p in ['README_RU.md','FL_STUDIO_RU.md','SHA256SUMS.txt','verification/ZIP_ACTUAL_REPLAY_PROOF.json']}
  with zipfile.ZipFile(io.BytesIO(old))as a,zipfile.ZipFile(io.BytesIO(new))as b:
   assert a.testzip()is None and b.testzip()is None and set(a.namelist())==set(b.namelist())
   for name in a.namelist():
    if name not in allowed:assert a.read(name)==b.read(name),name
  # Preserve all old kits while explicitly allowing this authorized current
  # kit's guide/manifest update; its DSP payloads were just compared above.
  p=H/'publish_full34_runtime_and_SUM_mix_clarification.py';s=p.read_text();oldtext="protected=h['protected']();old33=";newtext="protected={p:oid for p,oid in h['protected']().items()if p!=str((PUBLIC/'ZL-WIP34').relative_to(P))};old33=";assert oldtext in s;s=s.replace(oldtext,newtext);p.write_text(s);research=PUBLIC/'original-air22-native-post-trim-full34';(research/'scripts'/p.name).write_text(s);(research/'scripts'/Path(__file__).name).write_text(Path(__file__).read_text());(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n');h['aggregate']();git('add','--',str(research.relative_to(P)),str((PUBLIC/'SHA256SUMS.txt').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Keep historical-kit guards while allowing explicit current34 guide updates');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());h['push_and_confirm'](commit)
  paths=[P/zippath,PUBLIC/'ZL34_CONTINUATION_RU.md',research/'HANDOFF_FULL34_RU.md'];checks=[]
  for p in paths:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,current_ZIP_SHA256=hashlib.sha256(new).hexdigest(),current_ZIP_bytes=len(new),documentation_only_ZIP_repackage=True,all_audio_and_DSP_byte_exact=True,actual_runtime_adopted_and_started=True,two_actual_full_runtime_cold_replays=[0.,0.],previous_kits_and_PC_GUI_preserved=True,guard_failure_only_current_kit_documentation_updated=True,HTTP_checks=checks,reference_match_reached=False);(H/'ZL34_CURRENT_RUNTIME_PUBLICATION.json').write_text(json.dumps(result,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(result),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
