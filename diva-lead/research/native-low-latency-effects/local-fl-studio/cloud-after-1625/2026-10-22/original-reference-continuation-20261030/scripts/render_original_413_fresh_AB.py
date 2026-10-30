"""A new real413 render and an original-first comparison; no result adoption."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
import numpy as np,soundfile as sf
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
T=Path(__file__).resolve().parent;H=T.parent/'stereo-refinement-20261026';R=T/'AB_ORIGINAL_413_FRESH';R.mkdir()
best=json.loads((T/'JOINT_PRIMARY_POST_109_CURRENT413/PRIOR_COMBINED_CANDIDATE.json').read_text());assert best['source_accepted_cohort']==413
ready=json.loads((H/'CURRENT_CHAIN_READINESS.json').read_text());assert ready['current_source_cohort']==413 and ready['two_fresh_actual_two_ZL_replays_errors']==[0.,0.]
input_path=Path(ready['root'])/'ACTUAL_NATIVE_INPUT.wav';raw,sr=sf.read(input_path,dtype='float32',always_2d=True);assert sr==48000;os.link(input_path,R/'SAME_REAL_NATIVE_INPUT.wav')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment')
from fl20_objective import FeaturesOriginal,a
p=WinVST3('AB413-'+str(os.getpid())+'-primary');z=WinVST3('AB413-'+str(os.getpid())+'-post');trim=NativePostTrim(R/'buffers','AB413-'+str(os.getpid())+'-trim',cleanup_on_close=True)
try:
 for c,key,name in [(p,'native_ZL_component_state','PRIMARY413.bin'),(z,'post_ZL_component_state','POST413.bin')]:
  c.load(best[key]);c.save(R/name);assert(R/name).read_bytes()==Path(best[key]).read_bytes()
 trim.load(best['post_native_trim_state']);trim.save(R/'NATIVE_POST_TRIM.bin');assert(R/'NATIVE_POST_TRIM.bin').read_bytes()==Path(best['post_native_trim_state']).read_bytes()
 mid,_=p.render(raw);pre,_=z.render(mid);out=trim.render(pre);assert p.latency()+z.latency()==0
finally:p.close();z.close();trim.close()
sf.write(R/'ACTUAL_413_FULL_WIP_UNNORMALIZED.wav',out,48000,subtype='FLOAT');feature=FeaturesOriginal();score=feature.residual(out[:288000]);ref=np.asarray(a.REF);edit=a.h.edit_aligned(a.h.align_with_pdc(out,dict(alignment_frames=819),latency=0));rms=lambda y:float(np.sqrt(np.mean(y*y)));gain=rms(ref)/rms(edit);gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,edit*gain]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(R/'AB_ORIGINAL_413_WIP.flac',ab,48000,subtype='PCM_24')
if shutil.which('ffmpeg'):
 wav=R/'AB_WORKING.wav';sf.write(wav,ab,48000,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','320k',str(R/'AB_ORIGINAL_413_WIP.mp3')],check=True);wav.unlink()
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),order=['uploaded_original','accepted413'],starts_seconds=[0,4.168],actual_current_DSP_render=True,source_cohort=413,native_input_SHA256=hashlib.sha256(input_path.read_bytes()).hexdigest(),working_WAV_unnormalized=True,AB_only_common_stereo_RMS_gain=gain,common_AB_peak_safety_gain=safety,no_individual_LR_normalization=True,component_and_native_trim_resaves_byte_exact=True,ZL_PDC_frames=0,one_realization_original_objective_without_constant_native_regularizer=float(score@score),assessment=feature.local.last,reference_match_reached=False)
(R/'ACTUAL_RENDER_AND_AB_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='assessment'}),flush=True)
