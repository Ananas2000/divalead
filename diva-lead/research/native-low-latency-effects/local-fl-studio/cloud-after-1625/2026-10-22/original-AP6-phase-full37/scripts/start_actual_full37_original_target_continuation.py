"""Continue actual current three-note normal-FX matching against original only."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,time
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');script=A/'continue_stereo_ZL_matching.py'
def read(p):return json.loads(p.read_text())
assert read(H/'ADOPTED_FULL37_RUNTIME_CHECK.json')['actual_new_runtime_two_cold_two_ZL_chain_errors']==[0.,0.]
assert not(N/'zl-stereo-numerical.pause').exists();stop=N/'zl-stereo-continuation.stop';assert read(stop)['owner']=='complete-WIP37-AP6-phase-20261028'
from fl20_curve import native_dsp_settings_SHA256
best=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert best['native_base']['native_saved_state_bundle']['settings_SHA256']==native_dsp_settings_SHA256(best['native_base']['x'],best['native_base']);assert best['native_base_export_directory'].endswith('_10');assert best['accepted_full_public_kit']=='ZL37'and best['original_is_the_only_target']and not best['not_adopted_until_publication']
for filename in ['zl-continuation.stop','zl-useful-full-backup.stop']:assert read(N/filename)['owner']=='two-ZL-stereo24-retired-single-stage'
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  if str(script).encode()in p.read_bytes().split(b'\0'):assert(p.parent/'stat').read_text().split()[2]=='Z',('already live',p)
 except(FileNotFoundError,ProcessLookupError,PermissionError):pass
assert shutil.disk_usage('/workspace').free/2**20>=208 and shutil.disk_usage('/tmp').free/2**20>=128
stop.unlink();env=dict(os.environ,PYTHONPATH=str(A)+':/tmp/divalead-local-1625/internet-plugins-20261023:/tmp/divalead-native-effects:/tmp/divalead-local-1625',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
with(H/'ACTUAL_FULL37_ORIGINAL_TARGET_CONTINUATION.log').open('ab',buffering=0)as log:child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(script)],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
deadline=time.monotonic()+20
while time.monotonic()<deadline:
 assert child.poll()is None,'Actual matcher failed; inspect its log'
 s=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json')
 if s['owner']['PID']==child.pid and s.get('cohort',0)>=310:break
 time.sleep(.2)
else:raise TimeoutError('Started but running controller not yet confirmed')
assert len(s['actual_native_post_trim_hosts'])==2 and s['requires_post_native_trim'];assert len(s['actual_VST3_hosts'])==4 and 'running'in s['phase']and s['original_is_the_only_target']
assert s['fixed_post_SHA256']=='6597c11fe806b4d58243f8742eb0b358b02dbb86da63e007526025ba2f8c901f'
for row in [s['owner'],*s['actual_VST3_hosts'],*s['actual_native_post_trim_hosts']]:
 p=Path('/proc')/str(row['PID']);stat=(p/'stat').read_text().split();assert stat[2]!='Z'and stat[21]==row['starttime']
r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_main_PID=child.pid,actual_phase=s['phase'],actual_cohort=s['cohort'],four_actual_ZL_hosts_verified=True,two_actual_native_post_trim_hosts_verified=True,adopted_base='ZL-WIP37',three_Side_two_Stereo_one_Mid_AllPass_plus_LeftEQ4_active=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,all_previous_quality_gates_unchanged=True,reference_match_reached=False)
(H/'ACTUAL_FULL37_ORIGINAL_TARGET_START.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
