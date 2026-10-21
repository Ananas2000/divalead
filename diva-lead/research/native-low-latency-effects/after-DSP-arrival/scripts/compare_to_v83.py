"""Compare rendered audio to v83 without gain matching or time warping.

The candidate must include its entire declared latency and enough tail.
This script measures data; it does not certify that a file was rendered by FL.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import soundfile as sf

p=argparse.ArgumentParser()
p.add_argument('rendered_wav',type=Path)
p.add_argument('--latency-frames',type=int,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--label',required=True)
a=p.parse_args()
target=Path('/workspace/divalead/diva-lead/v83-wip/Diva_Lead_v83_FULL_180BPM.wav')
x,sr=sf.read(a.rendered_wav,dtype='float32',always_2d=True)
y,tr=sf.read(target,dtype='float32',always_2d=True)
assert sr==tr==48000 and x.shape[1]==y.shape[1]==2
assert np.isfinite(x).all() and a.latency_frames>=0
assert len(x)>=len(y)+a.latency_frames,'Render must include declared latency and a complete tail'
x=x[a.latency_frames:a.latency_frames+len(y)]
difference=x.astype('float64')-y.astype('float64')
rms=float(np.sqrt(np.mean(difference**2)))
report=dict(label=a.label,candidate_WAV=str(a.rendered_wav),target_WAV=str(target),
 candidate_file_SHA256=hashlib.sha256(a.rendered_wav.read_bytes()).hexdigest(),
 target_file_SHA256=hashlib.sha256(target.read_bytes()).hexdigest(),
 rate=sr,frames=len(y),channels=2,declared_latency_frames=a.latency_frames,
 automatic_alignment_used=False,gain_normalization_used=False,time_warp_used=False,
 decoded_float32_bit_exact=bool(np.array_equal(x,y)),max_abs_error=float(abs(difference).max()),
 null_RMS=rms,null_relative_RMS=rms/float(np.sqrt(np.mean(y.astype('float64')**2))),
 channel_null_RMS=np.sqrt(np.mean(difference**2,axis=0)).tolist(),
 native_plugin_render_provenance_not_checked_by_this_script=True,
 subjective_equivalence_not_certified=True)
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
