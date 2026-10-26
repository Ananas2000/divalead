"""One-shot durable backup of the current finite job; never claims a match."""
from pathlib import Path
import json,os,subprocess,sys,time
H=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');s=json.loads((N/'ORIGINAL_WS52_PRIMARY_JOINT_STUDY.json').read_text());pid=int(s['PID']);proc=Path('/proc')/str(pid);root=Path(s['root']);assert root==H/'WS52_PRIMARY_JOINT_RESEARCH'
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
 (root/'INCOMPLETE_FINITE_STUDY_BACKUP.json').write_text(json.dumps(dict(job_ended_without_completion=True,last_state=json.loads((N/'ORIGINAL_WS52_PRIMARY_JOINT_STUDY.json').read_text()),not_adopted=True),indent=2)+'\n')
note='Automatic one-shot snapshot after actualfiniteWS52+PRIMARYjoint job closes. Isolated52curve failedfirst6 and was NOTadopted. This is a genuinelynewDSPpoint with mandatory changedPRIMARY and new first6ANDfirst10+2cold gates. Verdict in completion.json; if incomplete, seeINCOMPLETE_FINITE_STUDY_BACKUP.json. All retained actualnative/control/candidateWAV, frozenmetadata andcomponentstates saved. This snapshot does not adopt a preset or claim reference match. Current supported fullkit remainsZL30 until separately verified full export. Local audio retained for independent export/replay. User requestsbackupat15percentremaining, percentageunavailable, so completedwork isbackedimmediately.'
subprocess.run([sys.executable,'-B','/workspace/divalead-work/stereo-refinement-20261025/backup_complete_finite_study.py','--root',str(root),'--label','original-WS52-primary-joint-finite-result','--note',note,'--retain-local-audio'],check=True)
print('FINITE_JOB_AUTOMATIC_REMOTE_BACKUP_COMPLETE',flush=True)
