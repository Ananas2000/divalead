"""Slow energy envelopes, independent of the effect implementation."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d
V=Path(__file__).resolve().parent.parent;sr=48000
ref=sf.read(V/'Diva_original_lead_reference.wav')[0];result={}
for name,file in [('reference','Diva_original_lead_reference.wav'),('v32','Diva_v32_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav'),('v33','Diva_v33_VIDEO_REFERENCE_EDIT.wav')]:
 x,rate=sf.read(V/file);assert rate==sr and len(x)==len(ref);row={}
 for ms in [24,48,96]:
  n=round(ms*sr/1000);e=np.sqrt(np.maximum(uniform_filter1d(np.mean(x*x,axis=1),n,mode='nearest'),0));t=np.sqrt(np.maximum(uniform_filter1d(np.mean(ref*ref,axis=1),n,mode='nearest'),0));row[str(ms)]=float(np.sqrt(np.mean((e-t)**2))/np.sqrt(np.mean(t*t)))
 result[name]=row
print(json.dumps({'definition':'sqrt(mean LR squared, uniform_filter1d nearest boundary), relative RMS error; separate definition from canonical12/24ms metrics','results':result},indent=2))
