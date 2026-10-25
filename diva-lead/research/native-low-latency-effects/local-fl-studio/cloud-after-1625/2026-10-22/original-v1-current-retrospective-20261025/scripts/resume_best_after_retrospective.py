"""Resume the accepted three-note two-ZL search after verified closed-buffer cleanup."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,time
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');script=A/'continue_stereo_ZL_matching.py'
def read(p):return json.loads(p.read_text())
state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');assert state['phase']=='stopped_at_observed_storage_reserve_after_completed_cohort'and state['completed_cohorts']==223
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  if str(script).encode()in p.read_bytes().split(b'\0'):assert p.parent.joinpath('stat').read_text().split()[2]=='Z',('already live',p)
 except(FileNotFoundError,PermissionError,ProcessLookupError):pass
assert not(N/'zl-stereo-numerical.pause').exists()and not(N/'zl-stereo-continuation.stop').exists()
for name in ['zl-continuation.stop','zl-useful-full-backup.stop']:assert read(N/name)['owner']=='two-ZL-stereo24-retired-single-stage'
cleanup=read(H/'after-review-scratch-cleanup/EXPIRED_CLOSED_DEFAULT_VST3_BUFFER_CLEANUP.json');assert cleanup['all_selected_WAVs_components_validation_archives_GUI_inputs_and_sources_retained']
best=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert best['source_accepted_cohort']==155
assert hashlib.sha256(Path(best['post_ZL_component_state']).read_bytes()).hexdigest()=='51dd979271b5fbfda5cffbd8cb71796009a5b3cc305289bbf9c472c672a7a96e'
assert shutil.disk_usage('/workspace').free/2**20>=208 and shutil.disk_usage('/tmp').free/2**20>=128
env=dict(os.environ,PYTHONPATH=str(A)+':/tmp/divalead-local-1625/internet-plugins-20261023:/tmp/divalead-native-effects:/tmp/divalead-local-1625',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
with(H/'AFTER_REVIEW_CONTINUATION.log').open('ab',buffering=0)as log:child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(script)],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
deadline=time.monotonic()+20
while time.monotonic()<deadline:
 assert child.poll()is None,'Matcher failed; inspect its actual log'
 new=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json')
 if new['owner']['PID']==child.pid and new.get('cohort',0)>=224:break
 time.sleep(.2)
else:raise TimeoutError('Process started but actual running controller not yet confirmed')
assert 'running'in new['phase']and len(new['actual_VST3_hosts'])==4
for host in [new['owner'],*new['actual_VST3_hosts']]:
 p=Path('/proc')/str(host['PID']);s=(p/'stat').read_text().split();assert s[2]!='Z'and s[21]==host['starttime']
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_new_PID=child.pid,actual_phase=new['phase'],actual_cohort=new['cohort'],actual_four_ZL_hosts_verified=True,continued_from_published_accepted_cohort=155,unchanged_primary_POST_native_and_MIDI_at_restart=True,only_closed_regenerable_scratch_cleared=True,original_objective_and_thresholds_unchanged=True,reference_match_reached=False)
(H/'AFTER_REVIEW_ACTUAL_RESUME.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
