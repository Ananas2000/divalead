"""Resume current full39 against the original after complete publication and replay."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,time
T=Path(__file__).resolve().parent;A=T.parent/'pc-stereo-20261024';N=T.parent/'native-low-latency-effects';script=A/'continue_stereo_ZL_matching.py'
def read(p):return json.loads(p.read_text())
assert max(read(T/'ADOPTED_FULL39_RUNTIME_CHECK.json')['actual_new_runtime_two_cold_two_ZL_chain_errors'])<=2e-7
best=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert best['accepted_full_public_kit']=='ZL39'and not best['not_adopted_until_publication']
from fl20_curve import native_dsp_settings_SHA256
assert best['native_base']['native_saved_state_bundle']['settings_SHA256']==native_dsp_settings_SHA256(best['native_base']['x'],best['native_base'])
assert not(N/'zl-stereo-numerical.pause').exists()and not(N/'zl-stereo-continuation.stop').exists()
for name in ['zl-continuation.stop','zl-useful-full-backup.stop']:assert read(N/name)['owner']=='two-ZL-stereo24-retired-single-stage'
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  if str(script).encode()in p.read_bytes().split(b'\0'):assert(p.parent/'stat').read_text().split()[2]=='Z','An actual matcher is already live'
 except(FileNotFoundError,ProcessLookupError):pass
assert shutil.disk_usage('/workspace').free>=208*2**20 and shutil.disk_usage('/tmp').free>=128*2**20
env=dict(os.environ,PYTHONPATH=str(A)+':/tmp/divalead-local-1625/internet-plugins-20261023:/tmp/divalead-native-effects:/tmp/divalead-local-1625',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
with(T/'ACTUAL_FULL39_CONTINUATION.log').open('ab',buffering=0)as log:child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(script)],env=env,stdout=log,stderr=log,stdin=subprocess.DEVNULL,start_new_session=True)
deadline=time.monotonic()+20
while time.monotonic()<deadline:
 assert child.poll()is None,'Actual matcher exited; inspect the log';s=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json')
 if s.get('owner',{}).get('PID')==child.pid and 'running'in s['phase']:break
 time.sleep(.2)
else:raise TimeoutError('Actual main controller not yet confirmed')
assert len(s['actual_VST3_hosts'])==4 and len(s['actual_native_post_trim_hosts'])==2
for row in [s['owner'],*s['actual_VST3_hosts'],*s['actual_native_post_trim_hosts']]:
 stat=(Path('/proc')/str(row['PID'])/'stat').read_text().split();assert stat[2]!='Z'and stat[21]==row['starttime']
r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_main_PID=child.pid,actual_cohort=s['cohort'],actual_phase=s['phase'],actual_four_ZL_and_two_native_trim_hosts_verified=True,full_base_kit='ZL-WIP39',fixed_POST_SHA256=s['fixed_post_SHA256'],original_is_only_target=True,all_existing_numeric_quality_gates_retained=True,only_three_incoming_held_notes=True,reference_match_reached=False);(T/'ACTUAL_FULL39_CONTINUATION_START.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
