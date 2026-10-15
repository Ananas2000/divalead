"""Frequency-band energy diagnostics on the sixteen fitted note windows.

This analysis is not a listening judgment, held-out test or similarity score.
It is not included in the audio effect and does not measure isolated hiss.
"""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
V=Path(__file__).resolve().parent.parent
SR=48000;NFFT=16384
windows=[]
for repetition in range(2):
 for i in range(8):
  start=repetition*7/3+i/6+.045
  windows.append((int(start*SR),int((start+.085)*SR)))
F=np.fft.rfftfreq(NFFT,1/SR)
def erb(f):return 21.4*np.log10(1+.00437*np.asarray(f))
centers=np.linspace(erb(40),erb(16000),40)
bank=np.exp(-.5*((erb(F)[None]-centers[:,None])/.5)**2)
band=(F>=40)&(F<=16000);bank[:,~band]=0
def power(audio):
 rows=[]
 for lo,hi in windows:
  x=audio[lo:hi]
  p=np.sum(abs(np.fft.rfft(x*np.hanning(len(x))[:,None],NFFT,axis=0))**2,axis=1)
  rows.append(bank@p/max(float(p[band].sum()),1e-30))
 return np.asarray(rows)
reference,rate=sf.read(V/'Diva_original_lead_reference.wav');assert rate==SR and reference.shape==(176064,2)
target=power(reference);weight=np.maximum(target,1e-6)**.2;weight/=weight.sum()
results={}
for label,name in [('v55','Diva_v55_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav'),('v56','Diva_v56_VIDEO_REFERENCE_EDIT.wav')]:
 audio,rate=sf.read(V/name);assert rate==SR and audio.shape==reference.shape
 error=10*np.log10(np.maximum(power(audio),1e-12)/np.maximum(target,1e-12))
 results[label]=dict(weighted_RMS_error_db=float(np.sqrt(np.sum(error*error*weight))),mean_error_by_center_db=error.mean(axis=0).tolist(),RMS_error_by_center_db=np.sqrt(np.mean(error*error,axis=0)).tolist(),error_by_window_and_center_db=error.tolist())
print(json.dumps(dict(centers_Hz=((10**(centers/21.4)-1)/.00437).tolist(),ERB_width=.5,FFT_size=NFFT,windows_frames=windows,power_normalization='sum of L+R FFT power from40..16000Hz within each window',weights='(reference_relative_band_power floor1e-6)^.2, globally normalized',results=results,fitted_windows_not_held_out=True,not_listening_or_similarity_percentage=True,not_isolated_hiss_measurement=True,match_reached=False),indent=2))
