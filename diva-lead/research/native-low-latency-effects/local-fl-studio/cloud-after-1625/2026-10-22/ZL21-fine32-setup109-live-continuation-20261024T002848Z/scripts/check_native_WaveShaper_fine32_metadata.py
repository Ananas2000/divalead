"""Actual-DLL cold replay and legacy fingerprint check for optional fine curve."""
from pathlib import Path
import datetime,json,struct
import numpy as np
from native_chain import NativeChain
from fl20_curve import apply_candidate,extended_curve_bytes,FINE_FORMAT,native_dsp_settings_SHA256
from win_vst3 import D
ROOT=D/'native-WaveShaper-fine32-metadata-01';ROOT.mkdir(exist_ok=False)
seed=json.loads((D.parent/'FL20_NATIVE_ZL_REBASED_04/verification/candidate.json').read_text())
defaults=dict(seed,waveshaper_fine_bump_format=FINE_FORMAT,waveshaper_fine_bump_adjustment=[0.]*32)
assert native_dsp_settings_SHA256(seed['x'],defaults)==seed['native_saved_state_bundle']['settings_SHA256']
values=[0.]*32;values[16]=.0001
changed=dict(defaults,waveshaper_fine_bump_adjustment=values)
assert native_dsp_settings_SHA256(seed['x'],changed)!=native_dsp_settings_SHA256(seed['x'],seed)
blob=extended_curve_bytes(np.array(seed['x']),seed['waveshaper_curve_adjustment'],seed['waveshaper_local_bump_adjustment'],seed['waveshaper_detail_bump_adjustment'],values)
y=np.array([struct.unpack_from('<d',blob,34+24*j+8)[0]for j in range(129)]);assert np.min(np.diff(y))>=-1e-10
clients=[]
def make(tag,candidate):
    c=NativeChain(seed['source_manifest']['native_input'],'fine32-metadata-'+tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');clients.append(c);apply_candidate(c,np.array(candidate['x']),candidate)
    for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
    c.set(3,1,0);return c
try:
    a=make('legacy-default',seed);baseline,_=a.render()
    b=make('changed',changed);actual,_=b.render();delta=float(abs(actual-baseline).max());assert delta>1e-7
    state=ROOT/'changed-WaveShaper.bin';b.save_state(0,state)
    c=make('independent-cold',changed);cold,_=c.render();cold_error=float(abs(actual-cold).max());assert cold_error<=2e-7
    c.load_state(0,state);c.save_state(0,ROOT/'resaved-WaveShaper.bin');assert state.read_bytes()==(ROOT/'resaved-WaveShaper.bin').read_bytes()
    replay,_=c.render();replay_error=float(abs(actual-replay).max());assert replay_error<=2e-7
    report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_DLLs_executed=True,unchanged_legacy_and_zero_fine32_fingerprints=True,new_fine_curve_not_overwritten_by_old_bundle=True,minimum_monotone_point_difference=float(np.min(np.diff(y))),actual_audio_delta_from_default=delta,two_fresh_native_instances_max_abs_error=cold_error,actual_saved_state_audio_max_abs_error=replay_error,WaveShaper_saved_state_byte_exact=True,unchanged_absolute_gate=2e-7,only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
    (ROOT/'ACTUAL_FINE32_METADATA_AND_PRESET_PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print('ACTUAL_FINE32_METADATA_PASS',json.dumps(report),flush=True)
finally:
    for c in clients:c.close()
