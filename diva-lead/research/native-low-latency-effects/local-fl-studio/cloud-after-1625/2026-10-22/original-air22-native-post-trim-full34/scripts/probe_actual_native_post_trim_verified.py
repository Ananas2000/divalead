"""Calibrate isolated native Stereo Shaper; no synthetic DSP substitutes."""
from pathlib import Path
import hashlib,json,os
import numpy as np,soundfile as sf
from native_post_trim import NativePostTrim
H=Path(__file__).resolve().parent;R=H/'ACTUAL_NATIVE_POST_TRIM_PROBE_VERIFIED';R.mkdir();source=H/'RELATIVE_AIR_PRIMARY_JOINT_RETRY2/CANDIDATE_00.wav';y,sr=sf.read(source,dtype='float32',always_2d=True);assert sr==48000
c=NativePostTrim(R,'ActualPostTrim-probe-'+str(os.getpid()));rows=[]
try:
 unity=c.render(y);error=float(abs(unity-y).max());assert error<=2e-7,error;sf.write(R/'ACTUAL_UNITY.wav',unity,48000,subtype='FLOAT')
 for db in[-.02,-.05,-.1,-.2,.05,.1]:
  left=c.raw_from_dB(db);c.configure(left,12800);out=c.render(y);wanted=np.column_stack([y[:,0]*((3**(left/12800)-1)/2),y[:,1]]);err=float(abs(out-wanted).max());assert err<=2e-7,err;state=R/('left-'+str(db)+'.bin');c.save(state);rows.append(dict(left_requested_dB=db,left_raw=left,right_raw=12800,measured_L_gain=float(np.sum(out[:,0].astype(float)*y[:,0])/np.sum(y[:,0].astype(float)**2)),ordinary_matrix_formula_max_abs_error=err,state_SHA256=hashlib.sha256(state.read_bytes()).hexdigest()))
 c.configure(c.raw_from_dB(-.05),12800);impulse=np.zeros((32768,2),np.float32);impulse[4096,0]=.1;impulse[8192,1]=.073;out=c.render(impulse);assert not np.any(out[:4096]);assert np.flatnonzero(abs(out[:,0])>1e-9).tolist()==[4096];assert np.flatnonzero(abs(out[:,1])>1e-9).tolist()==[8192]
 c.save(R/'CANDIDATE_TRIM.bin');fresh=NativePostTrim(R,'ActualPostTrim-cold-'+str(os.getpid()))
 try:fresh.load(R/'CANDIDATE_TRIM.bin');again=fresh.render(impulse);cold_error=float(abs(again-out).max());assert cold_error<=2e-7;fresh.save(R/'COLD_RESAVED_TRIM.bin');assert(R/'COLD_RESAVED_TRIM.bin').read_bytes()==(R/'CANDIDATE_TRIM.bin').read_bytes()
 finally:fresh.close()
 result=dict(actual_original_Fruity_Stereo_Shaper_DLL_used=True,all_other_host_plugins_bypassed=True,unchanged_identity_max_abs_error=error,ordinary_diagonal_gain_formula_actual_DSP_comparisons=rows,impulse_added_delay_samples=0,no_cross_channel_leakage_for_separate_impulses=True,cold_native_saved_state_replay_error=cold_error,cold_state_resave_byte_exact=True,absolute_native_tolerance=2e-7,user_FL_needs_one_standard_Stereo_Shaper_after_two_ZLs=True,no_custom_Finish_or_convolution=True,reference_match_reached=False);(R/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:c.close()
