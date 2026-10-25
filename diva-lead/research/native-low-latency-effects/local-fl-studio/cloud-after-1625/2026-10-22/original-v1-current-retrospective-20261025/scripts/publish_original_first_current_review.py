"""Publish exact retrospective evidence and A/B without changing synth candidates."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;ROOT=H/'original-first-current-review';D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='original_v1_current_retrospective')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
report=read(ROOT/'COMPARISON.json');assert len(report['rows'])==12 and not report['subjective_listening_performed_by_assistant']
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish common-original retrospective v1 to current with exact scoring audio and AB'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'original-v1-current-retrospective-20261025';h['copy_evidence'](ROOT,dest,True);scores=dest/'scores';shutil.copytree(ROOT/'scores',scores);scripts=dest/'scripts';scripts.mkdir()
  for name in ['review_original_first_and_current.py','package_original_first_current_review.py','publish_original_first_current_review.py']:shutil.copyfile(H/name,scripts/name)
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text('[Сравнение с оригиналом: v1 → история → текущий вариант, A/B и честные ограничения](original-v1-current-retrospective-20261025/README_RU.md).\n\n'+p.read_text());h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Compare first Diva preset and historical stages with current low-latency lead against one original');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for p in [dest/'README_RU.md',dest/'AB_ORIGINAL_V1_V8_V83_CURRENT.mp3',dest/'EXACT_RMS_MATCHED_SCORING_WAVs.zip']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes()
  assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,public_path=dest.relative_to(P).as_posix(),same_original_12_key_stages_compared=True,exact_scoring_WAV_ZIP_and_AB_remote_verified=True,no_new_synth_preset_or_MIDI_changes=True,no_subjective_audition_claim=True,reference_match_reached=False)
  (H/'ORIGINAL_FIRST_CURRENT_REVIEW_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
