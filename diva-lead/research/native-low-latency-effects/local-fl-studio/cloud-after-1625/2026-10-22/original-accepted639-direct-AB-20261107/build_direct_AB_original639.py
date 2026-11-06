"""Make A/B from the EXACT already-published working WAV in complete FL20 kit639."""
from pathlib import Path
import hashlib,json,os,subprocess,urllib.request,zipfile
import numpy as np,soundfile as sf
J=Path(__file__).resolve().parent;R=Path('/tmp/divalead-direct-original639-AB-20261107');R.mkdir();P=Path('/workspace/divalead')
public=Path('diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');kit=P/public/'stereo-cascade87-cohort-0639';audio=kit/'SELECTED_CANDIDATE_WIP.wav';name='cohort-0639_complete_FL20_STEREO_WIP.zip';archive=R/name;commit='bdb408e062020fce32d5b32d6c5bd8aa9f1687e3'
manifest=json.loads((kit/'FILE_SHA256.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+(public/'stereo-cascade87-cohort-0639'/name).as_posix()
with urllib.request.urlopen(url,timeout=60)as response,archive.open('wb')as out:
 while block:=response.read(1024*1024):out.write(block)
assert sha(archive)==manifest[name];assert sha(audio)==manifest[audio.name]
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 assert z.read('FL20_STEREO_WIP/STEREO_CONTINUED_FULL_WIP.wav')==audio.read_bytes()
raw,sr=sf.read(audio,dtype='float32',always_2d=True);os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment');from fl20_objective import a
refpath=P/'diva-lead/v83-wip/Diva_original_lead_reference.wav';ref,rate=sf.read(refpath,always_2d=True);assert sr==rate==48000
assert sha(refpath)=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF)
edit=a.h.edit_aligned(a.h.align_with_pdc(raw,dict(alignment_frames=819),latency=0));rms=lambda y:float(np.sqrt(np.mean(y*y)));gain=rms(ref)/rms(edit);ab=np.concatenate([ref,np.zeros((24000,2)),edit*gain]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(R/'AB_ORIGINAL_639_WIP.flac',ab,48000,subtype='PCM_24');tmp=R/'working.wav';sf.write(tmp,ab,48000,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(R/'AB_ORIGINAL_639_WIP.mp3')],check=True);tmp.unlink()
proof=dict(order=['original','accepted639'],starts_seconds=[0,4.168],actual_exact_working_WAV_inside_published_FL20_ZIP=True,working_WAV_path=audio.relative_to(P).as_posix(),working_WAV_SHA256=sha(audio),complete_FL20_ZIP_path=(public/'stereo-cascade87-cohort-0639'/name).as_posix(),complete_FL20_ZIP_SHA256=sha(archive),complete_FL20_ZIP_downloaded_from_immutable_commit=commit,ZIP_CRC_all_passed=True,AB_only_global_stereo_RMS_gain=gain,common_peak_safety_gain=safety,no_independent_channel_normalization=True,source_only_three_held_notes_internal_ARP=True,no_new_DSP_audio_or_acceptance_claim=True,reference_not_mixed_into_synth=True,reference_match_reached=False)
(R/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(J/'DIRECT639_AB_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
