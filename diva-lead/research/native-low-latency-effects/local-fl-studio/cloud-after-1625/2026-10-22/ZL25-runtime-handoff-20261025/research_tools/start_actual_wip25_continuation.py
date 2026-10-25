"""Start the persistent actual two-ZL job after the completed finite study."""
from pathlib import Path
import datetime,json,os,shutil,subprocess
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects')
assert json.loads((H/'ADOPTED_FULL25_RUNTIME_CHECK.json').read_text())['actual_new_runtime_two_cold_two_ZL_chain_errors']==[0.,0.]
assert not(N/'zl-stereo-numerical.pause').exists()
for filename in ['zl-continuation.stop','zl-useful-full-backup.stop']:assert json.loads((N/filename).read_text())['owner']=='two-ZL-stereo24-retired-single-stage'
stop=N/'zl-stereo-continuation.stop';assert json.loads(stop.read_text())['owner']=='stereo-lowmid-SideAP-finite-20261025'
assert shutil.disk_usage('/workspace').free/2**20>=208 and shutil.disk_usage('/tmp').free/2**20>=128
best=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['accepted_full_public_kit']=='ZL25'and not best['not_adopted_until_publication']
script=A/'continue_stereo_ZL_matching.py'
for proc in Path('/proc').iterdir():
 if proc.name.isdigit():
  try:
   argv=(proc/'cmdline').read_bytes().split(b'\0');assert str(script).encode()not in argv,('already running',proc.name)
  except(FileNotFoundError,ProcessLookupError,PermissionError):pass
env=dict(os.environ,PYTHONPATH=str(A)+':/tmp/divalead-local-1625/internet-plugins-20261023:/tmp/divalead-native-effects:/tmp/divalead-local-1625',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
stop.unlink()
with(H/'ACTUAL_WIP25_CONTINUATION.log').open('ab',buffering=0)as log:
 child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(script)],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
stat=Path('/proc')/str(child.pid)/'stat'
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=child.pid,starttime=stat.read_text().split()[21],script=str(script),published_base='ZL25',fixed_POST_SHA256='51dd979271b5fbfda5cffbd8cb71796009a5b3cc305289bbf9c472c672a7a96e',owner_stop_cleared='stereo-lowmid-SideAP-finite-20261025',legacy_single_stage_stops_retained=True,actual_runtime_check_passed=True,reference_match_reached=False)
(H/'ACTUAL_WIP25_CONTINUATION_START.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
