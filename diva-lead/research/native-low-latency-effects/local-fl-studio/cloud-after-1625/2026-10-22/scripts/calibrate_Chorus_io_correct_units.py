"""Actual native Chorus dry/wet and buffer-alias diagnostic, not a lead candidate."""
from pathlib import Path
import json,sys
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625');ROOT=BASE/'Chorus-io-calibration-02';ROOT.mkdir(exist_ok=False)
KIT=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')
sys.path.insert(0,'/tmp/divalead-native-effects');from native_chain import NativeChain
src=np.random.default_rng(1625).normal(0,.03,(32768,2)).astype(np.float32);src[0]=[.8,.4];sf.write(ROOT/'diagnostic-input.wav',src,48000,subtype='FLOAT')
c=NativeChain(ROOT/'diagnostic-input.wav','Chorus-isolated-io',fl_graph=True,phase_pair=True,engine_override='fl_native_host_context_diag.exe');captures={};states=[]
try:
    c.load_state(3,KIT/'verification/SOURCE_Chorus.bin')
    for node in range(15):c.bypass(node,node!=3)
    for k,v in enumerate([0,1,1,1,0]):c.gain(k,v)
    wet_on=c.mapped(3,11,65536);assert wet_on>1;wet_off=c.mapped(3,11,0);assert wet_off==0
    c.set(3,1,0);c.pending.extend(['C 128 -1 0 0','F 0'])
    for mode in [0,1,2]:
        c.pending.append(f'U {mode}')
        for wetonly in [0,1]:
            c.set(3,11,wet_on if wetonly else wet_off);assert c.value_hint(3,11)==(wet_on if wetonly else wet_off);y,status=c.render();path=ROOT/f'mode{mode}-wetonly{wetonly}.wav';sf.write(path,y,48000,subtype='FLOAT');captures[(mode,wetonly)]=y
            states.append(dict(buffer_mode=mode,wet_only=wetonly,native_status=status,initial_L=float(y[0,0]),initial_R=float(y[0,1])))
finally:c.close()
dry=src.astype(float).ravel();wet=captures[0,1].astype(float).ravel();full=captures[0,0].astype(float).ravel();matrix=np.c_[dry,wet]
coef=np.linalg.lstsq(matrix,full,rcond=None)[0];err=full-matrix@coef
aliases=[dict(buffer_mode=m,wet_only=w,max_abs_error_to_default=float(abs(captures[m,w]-captures[0,w]).max()))for m in [1,2]for w in [0,1]]
report=dict(actual_native_DLL_audio=True,zero_Chorus_depth_control=True,native_WetOnly_on_raw=wet_on,native_WetOnly_off_raw=wet_off,parameters_loaded_from_current_Chorus_bin=True,
    no_lead_or_original_reference_audio_used_as_input=True,diagnostic_input_is_seeded_noise_plus_impulse=True,
    isolated_plugin_mixing_coefficients=dict(dry=float(coef[0]),wet_only_output=float(coef[1]),max_residual=float(abs(err).max()),RMS_residual=float(np.sqrt(np.mean(err*err)))),
    buffer_alias_tests=aliases,native_captures=states,FL_GUI_slot_mix_law_not_measured=True,not_a_timbre_candidate=True,reference_match_reached=False)
(ROOT/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
