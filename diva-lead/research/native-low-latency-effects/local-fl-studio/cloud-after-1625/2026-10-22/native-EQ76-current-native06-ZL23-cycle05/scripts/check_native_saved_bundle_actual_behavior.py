"""Real-DLL regression: unchanged presets replay, changed trials stay changed."""
from pathlib import Path
import copy,datetime,json,time
import numpy as np
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
B=Path('/tmp/divalead-local-1625');D=B/'internet-plugins-20261023';ROOT=D/'native-saved-bundle-actual-behavior-01';ROOT.mkdir(exist_ok=False);candidate=B/'FL20_NATIVE_ZL_REBASED_04/verification/candidate.json';deadline=time.monotonic()+120
while True:
 try:seed=json.loads(candidate.read_text());assert seed.get('native_saved_state_bundle');break
 except (FileNotFoundError,json.JSONDecodeError,AssertionError):
  if time.monotonic()>deadline:raise TimeoutError('New saved-state native base was not ready')
  time.sleep(.1)
clients=[]
def make(label,settings,manual=False):
 c=NativeChain(settings['source_manifest']['native_input'],'saved-native-bundle-test-'+label,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');clients.append(c);apply_candidate(c,np.array(settings['x']),dict(settings,native_saved_state_bundle=None)if manual else settings)
 for key,val in settings['chorus_overrides'].items():c.set(3,int(key),int(val))
 if manual:
  for row in settings['native_saved_state_bundle']['manifest']:c.load_state(row['node'],Path(settings['native_saved_state_bundle']['directory'])/row['state'])
 c.set(3,1,0);return c
try:
 unchanged=make('unchanged',seed);manual=make('independent-manual-FST',seed,True);a,_=unchanged.render();b,_=manual.render();error=float(abs(a-b).max());assert error<=2e-7,error
 oldEQ=ROOT/'original-EQ-node4.bin';oldWS=ROOT/'original-WaveShaper.bin';unchanged.save_state(4,oldEQ);unchanged.save_state(0,oldWS)
 changed_gain=copy.deepcopy(seed);changed_gain['x'][3]+=(-.01 if changed_gain['x'][3]>=17.99 else .01);g=make('changed-EQ-gain',changed_gain);gy,_=g.render();newEQ=ROOT/'changed-EQ-node4.bin';g.save_state(4,newEQ);assert newEQ.read_bytes()!=oldEQ.read_bytes();gain_delta=float(abs(gy-a).max());assert gain_delta>1e-7,gain_delta
 changed_curve=copy.deepcopy(seed);changed_curve['waveshaper_curve_adjustment'][0]+=.001;w=make('changed-curve-same-x95',changed_curve);wy,_=w.render();newWS=ROOT/'changed-WaveShaper.bin';w.save_state(0,newWS);assert newWS.read_bytes()!=oldWS.read_bytes();curve_delta=float(abs(wy-a).max());assert curve_delta>1e-7,curve_delta
 report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_DLLs_used=True,unchanged_bundle_matches_independent_explicit_FST_load_max_error=error,unchanged_bundle_audio_bit_exact=bool(error==0),original_FST_absolute_gate_unchanged=2e-7,changed_EQ_gain_kept_changed=True,changed_EQ_gain_actual_audio_delta=gain_delta,changed_curve_with_identical_x95_kept_changed=True,changed_curve_actual_audio_delta=curve_delta,stored_DSP_settings_fingerprint=seed['native_saved_state_bundle']['settings_SHA256'],changed_gain_fingerprint=native_dsp_settings_SHA256(changed_gain['x'],changed_gain),changed_curve_fingerprint=native_dsp_settings_SHA256(changed_curve['x'],changed_curve),actual_native_host_PIDs=[c.proc.pid for c in clients],reference_match_reached=False,actual_FL_GUI_validation_pending=True)
 (ROOT/'ACTUAL_DSP_PRESET_AND_CHANGED_TRIAL_BEHAVIOR.json').write_text(json.dumps(report,indent=2)+'\n');print('ACTUAL_PRESET_REPLAY_AND_CHANGED_TRIAL_TEST_PASS',json.dumps(report),flush=True)
finally:
 for c in clients:c.close()
