"""Wait for an actual proved improvement, then build/test/publish a full kit once."""
from pathlib import Path
import datetime,fcntl,json,os,subprocess,sys,time,traceback,shutil
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead')
lock=(R/'v83-preparation-controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def state(phase,**extra):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,match_reached=False,**extra)
 p=R/'v83-preparation-controller-state.tmp';p.write_text(json.dumps(d,indent=2)+'\n');p.replace(R/'v83-preparation-controller-state.json')
baseline=json.loads((P/'diva-lead/v82-wip/verification/selected_validation.json').read_text())['tone_score']
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
try:
 while True:
  rows=[]
  for p in list(R.glob('pw5190-verified-*/validation.json'))+list(R.glob('post74joint-verified-*/validation.json'))+list(R.glob('post80plate68-verified-*/validation.json'))+[R/'source-post74joint-basis/validation.json',R/'source-post80plate68-basis/validation.json']:
   try:d=json.loads(p.read_text())
   except json.JSONDecodeError:continue
   rows.append((d['tone_score'],p))
  tone,path=min(rows)
  if tone<baseline-1e-4 and shutil.disk_usage(R).free>=384*1048576:break
  state('waiting_for_new_fully_proved_improvement',best_tone=tone,required_strict_improvement=1e-4,full_kit_minimum_free_MiB=384);time.sleep(15)
 state('building_and_testing_full_v83',selected_validation=str(path),tone_score=tone)
 subprocess.run([sys.executable,'-B',str(R/'run_full_v83_build.py')],env=env,check=True)
 subprocess.run([sys.executable,'-B',str(R/'verify_full_kit_documentation.py'),'/tmp/divalead-v83-build/v83-wip',str(P/'diva-lead/v82-wip')],env=env,check=True)
 state('publishing_tested_full_v83')
 subprocess.run([sys.executable,'-B',str(R/'publish_full_v83.py')],env=env,check=True)
 state('full_v83_published_other_audio_controllers_continue')
except Exception:
 state('failed_preserve_results_and_diagnose',error=traceback.format_exc());raise
