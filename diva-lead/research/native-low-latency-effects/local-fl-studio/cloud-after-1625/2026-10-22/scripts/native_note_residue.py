"""Independent note-residue diagnostic; never modifies the matching objective."""
from pathlib import Path
import numpy as np
import soundfile as sf
SR=48000
REFERENCE=Path('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav')
WINDOWS=[(.3783333333333333,.4633333333333333,174.61411571650194),(.8783333333333334,.9633333333333334,138.59131548843604),(2.711666666666667,2.796666666666667,174.61411571650194),(3.211666666666667,3.296666666666667,138.59131548843604)]
def edit(y):
 z=np.pad(y,((819,0),(0,0)));out=np.zeros((176064,2));out[1:64041]=z[1:64041];out[112022:176064]=z[128007:192049];return out
def ratios(y):
 rows=[]
 for a,b,f in WINDOWS:
  v=y[round(a*SR):round(b*SR)];t=np.arange(len(v))/SR;w=np.hanning(len(v))
  power=lambda freq:float(np.sum(abs(np.exp(-2j*np.pi*freq*t)@(v*w[:,None]))**2))
  rows.append(float(10*np.log10((power(f/2)+1e-30)/(power(f)+1e-30))))
 return np.asarray(rows)
ref,rate=sf.read(REFERENCE,dtype='float64');assert rate==SR and ref.shape==(176064,2)
REFERENCE_DB=ratios(ref)
def measure_native_raw(y):
 measured=ratios(edit(y));delta=measured-REFERENCE_DB
 return dict(definition='Fixed nominal-carrier Hann complex projection summed L/R power: half-carrier/carrier. Diagnostic, not perceptual hiss or original objective.',
  windows_seconds_Hz=WINDOWS,original_dB=REFERENCE_DB.tolist(),actual_dB=measured.tolist(),signed_error_dB=delta.tolist(),
  RMS_error_dB=float(np.sqrt(np.mean(delta**2))),RMS_excess_dB=float(np.sqrt(np.mean(np.maximum(delta,0)**2))),
  original_matching_objective_unchanged=True)
