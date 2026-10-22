"""Convenient original -> native A/B using the exact existing four-way gains."""
from pathlib import Path
import hashlib,json,subprocess,sys
import numpy as np
import soundfile as sf

kit=Path(sys.argv[1]);destination=Path(sys.argv[2]);destination.mkdir(parents=True,exist_ok=False)
label=sys.argv[3]
ref=kit/'Diva_original_lead_reference.wav'
if not ref.exists():ref=Path('/workspace/divalead/diva-lead/v55-wip/Diva_original_lead_reference.wav')
native=kit/'NATIVE_REFERENCE_EDIT_WIP.wav'
r,sr=sf.read(ref);y,ysr=sf.read(native);assert sr==ysr==48000 and r.shape==y.shape==(176064,2)
levels=json.loads((kit/'verification/AB_LEVELS.json').read_text())
gains=[levels['per_clip_RMS_gains'][0],levels['per_clip_RMS_gains'][3]]
safety=levels['common_peak_safety_gain']
audio=np.concatenate([r*gains[0],np.zeros((24000,2)),y*gains[1]])*safety
wave=destination/'working_AB.wav';sf.write(wave,audio,48000,subtype='FLOAT')
out=destination/('AB_REFERENCE_'+label+'.mp3')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wave),'-codec:a','libmp3lame','-b:a','320k',str(out)],check=True)
wave.unlink()
proof=dict(order=['original_reference',label],starts_seconds=[0,(len(r)+24000)/48000],
    same_RMS_gains_as_complete_four_way_AB=gains,same_common_peak_safety_gain=safety,
    source_reference_SHA256=hashlib.sha256(ref.read_bytes()).hexdigest(),
    source_native_edit_SHA256=hashlib.sha256(native.read_bytes()).hexdigest(),
    MP3_SHA256=hashlib.sha256(out.read_bytes()).hexdigest(),
    full_candidate_WAV_unscaled_and_not_modified=True,only_AB_level_normalized=True,
    original_never_used_as_candidate_audio_input=True,reference_match_reached=False)
(destination/'AB_LEVELS_AND_SOURCES.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof),flush=True)
