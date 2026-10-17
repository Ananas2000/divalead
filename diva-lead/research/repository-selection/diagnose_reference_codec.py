"""Diagnostic HE-AACv2 roundtrips of a real Diva render, never a replacement preset.

Delay is calibrated with independent noise, not by matching the reference notes.
The verified original native/DSP model and searches remain unchanged.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.sched_setaffinity(0,{4})
from pathlib import Path
import sys,json,datetime,time,subprocess,hashlib,traceback
import numpy as np,soundfile as sf
from scipy.signal import resample_poly,correlate,butter,sosfilt
W=Path(os.environ.get('DIVALEAD_VALIDATION_WORK','/workspace/divalead-work/all-repository-selection'));P=Path(__file__).resolve().parent;ROOT=Path(os.environ.get('DIVALEAD_CODEC_WORK','/workspace/divalead-work/reference-codec-diagnostic'));STATE=W/'reference-codec-diagnostic-state.json'
def atomic(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2)+'\n');t.replace(p)
def state(phase,**kw):atomic(STATE,dict(time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_PID=os.getpid(),phase=phase,diagnostic_only_not_a_new_patch=True,match_reached=False,**kw))
try:
 ROOT.mkdir(exist_ok=False);state('waiting_for_optional_pinned_encoder_build');deadline=time.monotonic()+1800
 while True:
  assert time.monotonic()<deadline,'Optional encoder build not complete in30minutes'
  f=W/'optional-codec-build-state.json'
  if f.exists():
   build=json.loads(f.read_text());assert build['phase']!='failed',build
   if build['phase'].startswith('completed_'):break
  time.sleep(5)
 binary=build['binary'];sys.path.insert(0,str(P));import compare_all as a
 from search_global_guards import ORIGINAL53_LIMITS
 chosen=json.loads(Path('/workspace/divalead-work/best-new-source-hf/BEST_ACTUAL.json').read_text());validation=Path(chosen['validation']);r=json.loads(validation.read_text());fullpath=validation.parent/'actual-Windows.wav';full,sr=sf.read(fullpath);assert sr==48000 and full.shape==(288000,2);c=json.loads(Path(r['core_model']).with_name('selected_candidate.json').read_text());ranking=json.loads((P/'ranking.json').read_text());original=ranking['results'][0]['metrics'];scales=ranking['normalizing_errors'];a.WORK=ROOT;(ROOT/'scores').mkdir();rng=np.random.default_rng(20261017);noise=sosfilt(butter(5,4000,fs=44100,output='sos'),rng.normal(0,.15,88200));noise[:11025]=0;noise[-11025:]=0;cal=np.column_stack([noise,noise]);calpath=ROOT/'independent-delay-calibration.wav';sf.write(calpath,cal,44100,subtype='PCM_16');cal=sf.read(calpath)[0];calibrations={};rows=[]
 def roundtrip(inputpath,tag,bitrate):
  adts=ROOT/(tag+'.aac');out=ROOT/(tag+'-decoded.wav');proc=subprocess.run([binary,'-t','29','-r',str(bitrate),str(inputpath),str(adts)],stdin=subprocess.DEVNULL,capture_output=True,text=True,check=True,timeout=180);info=json.loads(proc.stdout);subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(adts),'-ar','44100','-c:a','pcm_f32le','-y',str(out)],stdin=subprocess.DEVNULL,check=True,timeout=180);profile=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=profile,sample_rate,channels','-of','json',str(adts)],text=True))['streams'][0];header=adts.read_bytes()[:7];core_rate=[96000,88200,64000,48000,44100,32000,24000,22050,16000,12000,11025,8000,7350][(header[2]>>2)&15];core_channels=((header[2]&1)<<2)|(header[3]>>6);assert core_rate==22050 and core_channels==1 and profile['sample_rate']=='44100' and profile['channels']==2 and info['frame_length']==2048,(core_rate,core_channels,profile,info);profile.update(requested_FDK_AOT=29,ADTS_core_rate=core_rate,ADTS_core_channels=core_channels,verified_SBR_double_rate_and_PS_stereo_output=True,ADTS_backward_compatible_header_may_report_LC=True);decoded,rate=sf.read(out);assert rate==44100;return decoded,info,profile
 for index,(bitrate,prefix) in enumerate([(32000,0),(32000,12163),(40000,12163),(48000,12163)]):
  state('HE_AACv2_real_render_diagnostic',case=index,bitrate=bitrate,prefix_frames_48000=prefix)
  if bitrate not in calibrations:
   decoded,info,profile=roundtrip(calpath,'delay-'+str(bitrate),bitrate);x=decoded.mean(axis=1);z=cal.mean(axis=1);dot=correlate(x,z,mode='valid',method='fft');cs=np.r_[0,np.cumsum(x*x)];corr=dot/np.sqrt(np.maximum(cs[len(z):]-cs[:-len(z)],1e-30)*np.sum(z*z));delay=int(np.argmax(corr));assert float(corr[delay])>.5 and abs(delay-int(info['codec_delay']))<4096;calibrations[bitrate]=dict(delay_frames_44100=delay,mono_correlation=float(corr[delay]),encoder_info=info,profile=profile,reference_audio_not_used=True);atomic(ROOT/'independent-delay-calibration.json',calibrations)
  input48=np.concatenate([np.zeros((prefix,2)),full]);input441=resample_poly(input48,147,160,axis=0);inputpath=ROOT/('case-'+str(index)+'-input.wav');sf.write(inputpath,input441,44100,subtype='PCM_16');decoded,info,profile=roundtrip(inputpath,'case-'+str(index),bitrate);delay=calibrations[bitrate]['delay_frames_44100'];assert info['codec_delay']==calibrations[bitrate]['encoder_info']['codec_delay'];decoded=decoded[delay:delay+len(input441)];assert len(decoded)==len(input441);output48=resample_poly(decoded,160,147,axis=0);output=output48[prefix:prefix+len(full)];assert len(output)==len(full);edit=a.h.edit_aligned(a.h.align_with_pdc(output,c['settings'],latency=12416));path=ROOT/('case-'+str(index)+'-REFERENCE_EDIT_DIAGNOSTIC.wav');sf.write(path,edit,48000,subtype='FLOAT');measured=a.score(dict(id='codec'+str(index),canonical_path=str(path),aliases=[]));m=measured['metrics'];score=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS);row=dict(case=index,profile=profile,bitrate_requested=bitrate,prefix_frames_48000=prefix,prefix_definition='0 or fixed23760video-reference-start minus11597knownDSP-alignment; no per-note alignment',delay_calibration=calibrations[bitrate],metrics=m,score=score,baseline_actual_score=r['score'],original_global_caps_passed=bool(all(m[k]<=original[k]*limit for k,limit in ORIGINAL53_LIMITS.items())),codec_after_real_Diva_and_verified_DSP=True,not_a_native_plugin_model=True,not_selected_as_a_new_patch=True,match_reached=False);rows.append(row);atomic(ROOT/'history.json',rows)
 state('completed_HE_AACv2_diagnostic',cases=len(rows),baseline_actual_validation=str(validation),baseline_actual_score=r['score'],input_DSP_WAV_SHA256=hashlib.sha256(fullpath.read_bytes()).hexdigest(),best_diagnostic_score=min(x['score'] for x in rows),no_patch_or_runtime_chain_replaced=True)
except Exception:
 state('failed',error=traceback.format_exc());raise
