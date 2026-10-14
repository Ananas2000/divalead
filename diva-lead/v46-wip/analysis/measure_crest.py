"""Stationary peak/RMS diagnostics; not a compression or listening score."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
V=Path(__file__).resolve().parent.parent;SR=48000
windows=[(rep*7/3+i/6+.045,rep*7/3+i/6+.130) for rep in range(2) for i in range(8)]
results={}
for name,file in [('reference','Diva_original_lead_reference.wav'),('v45','Diva_v45_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav'),('v46','Diva_v46_VIDEO_REFERENCE_EDIT.wav')]:
 x,sr=sf.read(V/file);assert sr==SR and x.shape==(176064,2)
 values=np.array([20*np.log10(np.max(abs(x[int(a*SR):int(b*SR)]))/np.sqrt(np.mean(x[int(a*SR):int(b*SR)]**2))) for a,b in windows])
 if name=='reference':target=values
 results[name]={'windows_peak_RMS_dB':values.tolist(),'mean_peak_RMS_dB':float(values.mean()),'peak_RMS_difference_from_reference_RMS_dB':float(np.sqrt(np.mean((values-target)**2)))}
print(json.dumps({'description':'16 stationary windows. Peaks depend on waveform phase, stereo mixing, modulation, envelope, saturation and codec context. This does not establish perceived openness or quality, and is not a similarity percentage.','windows_seconds':windows,'results':results},indent=2))
