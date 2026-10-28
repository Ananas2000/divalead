from pathlib import Path
import datetime,json,os,signal,time
H=Path(__file__).resolve().parent;r=json.loads((H/'MAIN_SECOND_TEMPORARY_AUDIT_STAGING_PAUSE_20261028.json').read_text());deadline=time.monotonic()+1800
try:
 while not(H.parent/'stereo-refinement-20261025/original404-direct372-stricter-paired-stereo-audit_PUBLICATION.json').exists():
  if time.monotonic()>deadline:raise TimeoutError('Audit proof not yet remote; no false completion claim')
  time.sleep(.5)
finally:
 p=Path('/proc')/str(r['PID'])
 if p.exists():
  s=(p/'stat').read_text().split()
  if s[21]==r['starttime']and s[2]!='Z':os.kill(r['PID'],signal.SIGCONT);r['resumed_same_main_after_audit_staging']=True
 r['resume_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(H/'MAIN_SECOND_AUDIT_STAGING_RESUME_20261028.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
