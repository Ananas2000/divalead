"""One-shot durable backup of the current finite job; never claims a match."""
from pathlib import Path
import json,os,subprocess,sys,time
H=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');s=json.loads((N/'ORIGINAL_POST_JOINT11_STUDY.json').read_text());pid=int(s['PID']);proc=Path('/proc')/str(pid);root=Path(s['root']);assert root==Path('/tmp/divalead-post-joint11-20261026-01')
try:start=(proc/'stat').read_text().split()[21]
except FileNotFoundError:start=None
deadline=time.monotonic()+7200
while start is not None:
 try:
  stat=(proc/'stat').read_text().split()
  if stat[21]!=start or stat[2]=='Z':break
 except FileNotFoundError:break
 if time.monotonic()>deadline:raise TimeoutError('Finite job still active; no false completed backup')
 time.sleep(.5)
if not(root/'completion.json').exists():
 (root/'INCOMPLETE_FINITE_STUDY_BACKUP.json').write_text(json.dumps(dict(job_ended_without_completion=True,last_state=json.loads((N/'ORIGINAL_POST_JOINT11_STUDY.json').read_text()),not_adopted=True),indent=2)+'\n')
note='Automatic snapshot of actual existingPOST11parameter jointretune. Noaddedfilters: same3SideAllPasses,1StereoAllPass,1LeftPeak; onlyfreq/Q for4AP andfreq/Q/gainLeftPeakvaried. Currentnative10/WS52/Diva281/3longincomingnotes/ARP/ADSR andfrozenPRIMARYunchanged. Samefulloriginalscore/stereoguards, BOTHfirst6ANDfirst10+2cold, andadditionalpairedlowmiderrornotworseover.02dB. Verdict incompletion.json, notadopteduntilmatchinglatestcontextandindependentfullkitreplay. Allretainedtraining/validationWAV/states/XMLchanges/data saved;localaudioretained. CurrentfullkitZL31 andanyacceptednumericaldescendantremainbaselineuntil separatelyverifiednewkit.'
subprocess.run([sys.executable,'-B','/workspace/divalead-work/stereo-refinement-20261025/backup_complete_finite_study.py','--root',str(root),'--label','original-existing-POST11-finite-result','--note',note,'--retain-local-audio'],check=True)
print('FINITE_JOB_AUTOMATIC_REMOTE_BACKUP_COMPLETE',flush=True)
