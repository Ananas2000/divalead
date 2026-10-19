from pathlib import Path
import json,os,subprocess,sys,time,datetime
R=Path(__file__).resolve().parent
while True:
 p=R/'source-pw5190-coupled135-control/paused-balance-power.json'
 d=json.loads(p.read_text()) if p.exists() else {}
 if 'resumed_UTC' in d:break
 time.sleep(5)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase='build_best_fully_proved_v66_after_joint_search',prior_coordinator_finished=True,match_reached=False)
(R/'v66-build-start.json').write_text(json.dumps(report,indent=2)+'\n')
with (R/'v66-build.log').open('w') as log:
 subprocess.run([sys.executable,'-B',str(R/'run_full_v66_build.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True,timeout=1500)
print('V66_BEST_FULLY_PROVED_KIT_FINISHED',flush=True)
