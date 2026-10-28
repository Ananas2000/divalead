from pathlib import Path
import datetime,json,os,signal,subprocess,sys
H=Path(__file__).resolve().parent;proof=json.loads((H/'MAIN_TEMPORARY_SPACE_TRANSFER_PAUSE_20261028.json').read_text());pid=proof['PID']
try:subprocess.run([sys.executable,'-B',str(H/'backup_and_release_old_derived_AB_batch02.py')],check=True)
finally:
 p=Path('/proc')/str(pid)
 if p.exists():
  stat=(p/'stat').read_text().split()
  if stat[21]==proof['starttime']and stat[2]!='Z':os.kill(pid,signal.SIGCONT);proof['resumed_same_actual_main']=True
 proof['resume_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(H/'MAIN_AFTER_SPACE_TRANSFER_RESUME_20261028.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
