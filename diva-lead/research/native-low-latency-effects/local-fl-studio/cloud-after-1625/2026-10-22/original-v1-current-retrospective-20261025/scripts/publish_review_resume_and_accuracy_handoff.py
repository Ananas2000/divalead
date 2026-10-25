"""Keep the honest accuracy comparison and actual continuation recovery in Git."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='retrospective_accuracy_recovery')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve retrospective accuracy finding and actual resume after closed scratch cleanup'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID'];assert h['alive'](pid)and Path(f'/proc/{pid}/stat').read_text().split()[21]==state['owner']['starttime']
  dest=PUBLIC/'original-v1-current-retrospective-20261025'
  for p in [H/'AFTER_REVIEW_ACTUAL_RESUME.json',H/'after-review-scratch-cleanup/EXPIRED_CLOSED_DEFAULT_VST3_BUFFER_CLEANUP.json']:shutil.copyfile(p,dest/p.name)
  for p in [H/'resume_best_after_retrospective.py',H/'after-review-scratch-cleanup/cleanup_closed_regenerable_vst3_buffers.py',H/'publish_review_resume_and_accuracy_handoff.py']:shutil.copyfile(p,dest/'scripts'/p.name)
  (dest/'ACTUAL_RESUMED_CONTROLLER_SNAPSHOT.json').write_text(json.dumps(state,indent=2)+'\n')
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n')
  header='''BEGIN_ORIGINAL_FIRST_CURRENT_ACCURACY_REVIEW_20261025
Read PUBLIC/original-v1-current-retrospective-20261025/README_RU.md andCOMPARISON.json (PUBLIC=local-fl-studio/cloud-after-1625/2026-10-22). User asked honest similarity vsfirstavailable: actualfirstv1preset exactbyteverified to controlledactualDiva render,12historical/currentstages rescoredsameoriginal/globalstereoRMS withunchangedmetricweights/scales. H24error v1=11.600,v2=3.704,v8=3.221,currentcohort155=1.685dB (8rendermean1.684). DoNOTclaim95percentperceivedmatch or subjectiveaudition. Important: older3notev83highlatencyFinish is STILLcloser ontimbre/H24=1.017/upper=1.165/ERB=.929 than currentnative/ZL H24=1.685/upper=1.714/ERB=1.193. So latestlowlatencykit isNOT globalbest-ever or equivalentoldfinal; transferlostsomeaccuracy andneedstorecoveritWITHOUToldPDCdelay. V57bettertotalindexbutdifferentmanynoteperformance/userexclusively3notes; neverreintroduce16notes. CurrentlowmidLR4.19 vsoriginal.97dB remains~3.23dBleftresidual. Currentbestaccepted155 afterstages70/155 allbackedGit, mainfinished223cohorts atobservedtmp126.86MiBguard, NOTsoundmatch. ClosedregenerableVSTscratchonly122705920bytescleared (allselected/source/GUI/presets retained), resumedfrombest155withsameobjective/tolerances/native06/twoZL3SideAPPOST; actualPID/controller snapshotinreviewdir andH/AFTER_REVIEW_ACTUAL_RESUME.json, H=/workspace/divalead-work/stereo-refinement-20261025. ChecklivecontrolleractualPID/starttime, neverassumeold snapshotalive. Legacy-singleZLstopsretained. Lowlatencyconstrainedacceptedpoints continueautomaticGit fullplayableZIP+ALL24validationWAV. NoMista/referenceaudioinsynthesis/pertrialquestions. PreservecurrentRUNTIME andfixedPOST25; noresettoolderbest/GUI overwrite. FullsoundmatchFALSE, APIquota%unknown, oldpublicGitcacheholesexpected.
END_ORIGINAL_FIRST_CURRENT_ACCURACY_REVIEW_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve honest old-vs-current accuracy findings and resume accepted low-latency matching');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert not git('status','--porcelain');print(json.dumps(dict(commit=commit,actual_main_PID_at_snapshot=pid,public_accuracy_report_and_resume_saved=True,reference_match_reached=False)),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
