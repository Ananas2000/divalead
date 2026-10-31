from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,zipfile
import numpy as np,soundfile as sf
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
U=Path(__file__).resolve().parent;P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22';BASE=PUBLIC/'ZL-WIP39';R=Path('/tmp/divalead-AB-original-39-559-20261031');R.mkdir();work=R/'actual-common-input-data';work.mkdir();A=U.parent/'pc-stereo-20261024';cohort=A/'stereo-continuous87/cohort-0559';receipt=json.loads((cohort/'REMOTE_BACKUP.json').read_text());summary=json.loads((cohort/'completion.json').read_text());assert summary['robust_improvement'];common=BASE/'verification/NATIVE12_BEFORE_ZL_WIP.wav';raw,sr=sf.read(common,dtype='float32',always_2d=True);assert sr==48000;shutil.copyfile(common,work/'NATIVE11_COMMON_INPUT.wav');states=[BASE/'verification/ZL39_PRIMARY_COMPONENT.bin',cohort/'candidate-component.bin'];post=BASE/'verification/ZL39_POST_COMPONENT.bin';trim=BASE/'verification/POST_NATIVE_STEREO_TRIM.bin';assert post.read_bytes()==(cohort/'fixed-post-component.bin').read_bytes();outs=[];errors=[]
for k,source in enumerate([states[0],states[1],states[1]]):
 p=WinVST3('AB39-559-P-'+str(k));z=WinVST3('AB39-559-Z-'+str(k));t=NativePostTrim(R/'buffers','AB39-559-T-'+str(k),cleanup_on_close=True)
 try:
  p.load(source);z.load(post);t.load(trim)
  for obj,state,name in[(p,source,'PRIMARY'),(z,post,'POST'),(t,trim,'TRIM')]:
   dst=work/(str(k)+'_'+name+'.bin');obj.save(dst);assert dst.read_bytes()==state.read_bytes()
  mid,_=p.render(raw);pre,_=z.render(mid);out=t.render(pre);assert p.latency()+z.latency()==0
  if k<2:outs.append(out);sf.write(work/(['FULL39_UNNORMALIZED.wav','FULL559_UNNORMALIZED.wav'][k]),out,48000,subtype='FLOAT')
  else:np.testing.assert_allclose(out,outs[1],rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-outs[1]).max()))
 finally:p.close();z.close();t.close()
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment');from fl20_objective import a,FeaturesOriginal
f=FeaturesOriginal();metrics=[]
for out in outs:r=f.residual(out[:288000]);metrics.append(dict(original_loss=float(r@r)+float(np.sum(np.array(json.loads((BASE/'verification/candidate.json').read_text())['native_base']['x'])[:28]**2))*.00000025,assessment=f.local.last))
reference=P/'diva-lead/v83-wip/Diva_original_lead_reference.wav';assert hashlib.sha256(reference.read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';ref,sr=sf.read(reference,always_2d=True);np.testing.assert_array_equal(ref,a.REF);edit=lambda out:a.h.edit_aligned(a.h.align_with_pdc(out,dict(alignment_frames=819),latency=0));edits=[edit(out)for out in outs];rms=lambda out:float(np.sqrt(np.mean(out*out)));gains=[1.,*[rms(ref)/rms(out)for out in edits]];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,edits[0]*gains[1],gap,edits[1]*gains[2]]);peak=min(1.,.95/float(abs(ab).max()));ab*=peak;sf.write(R/'AB_ORIGINAL_ZL39_559_WIP.flac',ab,48000,subtype='PCM_24');tmp=R/'AB-working.wav';sf.write(tmp,ab,48000,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(R/'AB_ORIGINAL_ZL39_559_WIP.mp3')],check=True);tmp.unlink()
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),order=['original','full39','accepted559'],starts_seconds=[0.,4.168,8.336],same_actual_native11_input_for_both_controls=True,reference_SHA256=hashlib.sha256(reference.read_bytes()).hexdigest(),reference_is_only_target=True,source_h2p_MIDI_ARP_ADSR_native11_POST_trim_unchanged=True,only_primary39_to_559_changed=True,two_fresh_actual559_cold_full_chain_replay_errors=errors,all_primary_POST_trim_resaves_exact=True,combined_ZL_PDC_frames=0,global_stereo_RMS_gains=gains,common_peak_safety_gain=peak,no_independent_channel_normalization=True,only_AB_normalized=True,actual_WAVs_unnormalized=True,single_common_input_objectives=metrics,not_new_acceptance_test=True,accepted559_publication=receipt,accepted559_first6_gain=summary['first6_mean_improvement'],accepted559_SEM=summary['paired_difference_SEM'],accepted559_cold2_gains=summary['cold_input_improvements'],fresh10_not_run_for_numeric559=True,Windows_FL_GUI_ASIO_not_tested=True,reference_match_reached=False);(R/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copyfile(R/'PROOF.json',work/'PROOF.json');shutil.copyfile(Path(__file__),work/Path(__file__).name);(work/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n'for p in sorted(work.iterdir())if p.is_file()and p.name!='SHA256SUMS.txt'));archive=R/'ALL_ACTUAL_COMMON_INPUT_WAV_AND_STATES.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(work.iterdir()):
  if p.is_file():z.write(p,p.name)
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in work.iterdir():
  if p.is_file():assert z.read(p.name)==p.read_bytes()
result=dict(root=str(R),same_native_input_WAV_states_ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),new559_cold_replay_error=errors,single_draw_loss39=metrics[0]['original_loss'],single_draw_loss559=metrics[1]['original_loss'],reference_match_reached=False);(U/'AB_ORIGINAL_39_559_BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
