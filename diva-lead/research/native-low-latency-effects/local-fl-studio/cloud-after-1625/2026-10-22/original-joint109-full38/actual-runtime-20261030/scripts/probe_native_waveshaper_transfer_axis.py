"""Diagnostic only: establish whether native curve coordinates are bipolar or |x|.

Uses the unchanged three-held-note Diva waveform through the real WaveShaper.
All other effects are bypassed for this measurement; this is NOT a lead variant.
"""
from pathlib import Path
import datetime,hashlib,json,struct
import numpy as np,soundfile as sf
from native_chain import NativeChain
T=Path(__file__).resolve().parent;R=T/'WAVESHAPER_AXIS_DIAGNOSTIC';R.mkdir();A=T.parent/'pc-stereo-20261024';bestfile=A/'stereo-continuous87/BEST_CANDIDATE.json';original_best=bestfile.read_bytes();best=json.loads(original_best);seed=best['native_base'];bundle=seed['native_saved_state_bundle'];row=next(v for v in bundle['manifest']if v['node']==0);state=Path(bundle['directory'])/row['state'];blob=state.read_bytes();assert hashlib.sha256(blob).hexdigest()==row['state_SHA256'];assert struct.unpack_from('<I',blob,30)[0]==129
flat=bytearray(blob)
for k in range(129):struct.pack_into('<d',flat,34+24*k+8,.5)
(R/'FLAT_HALF_DIAGNOSTIC.bin').write_bytes(flat);c=NativeChain(seed['source_manifest']['native_input'],'NativeAxisDiagnostic-'+str(__import__('os').getpid()),engine_override='fl_native_chain_host.exe')
try:
 for node in range(1,10):c.bypass(node,True)
 c.load_state(0,state);before,_=c.render();again,_=c.render();np.testing.assert_allclose(again,before,rtol=8*np.finfo(np.float32).eps,atol=1e-12);c.load_state(0,R/'FLAT_HALF_DIAGNOSTIC.bin');out,_=c.render()
finally:c.close()
sf.write(R/'CANONICAL_WAVESHAPER_DIAGNOSTIC.wav',before,48000,subtype='FLOAT');sf.write(R/'FLAT_HALF_WAVESHAPER_DIAGNOSTIC.wav',out,48000,subtype='FLOAT');rms=float(np.sqrt(np.mean(out[:288000].astype(float)**2)));peak=float(abs(out).max());axis='bipolar_x_to_01_and_y_from_01'if peak<1e-7 else'absolute_amplitude_or_other_unipolar_mapping';assert bestfile.read_bytes()==original_best
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_WaveShaper_DLL=True,source_Diva_waveform_MIDI_3held_unchanged=True,all_other_effects_bypassed_for_transfer_diagnostic_only=True,canonical_repeat_max_error=float(abs(again-before).max()),flat_half_output_RMS=rms,flat_half_output_peak=peak,inferred_axis=axis,source_lead_candidate=False,no_reference_comparison_or_match_claim=True,not_adopted=True,BEST_unchanged=True);(R/'RESULT.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
