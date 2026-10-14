"""Level, correlation and quadrature are separate stereo measurements."""
import json
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt,hilbert
V=Path(__file__).resolve().parent.parent
BANDS=[(40,300),(300,800),(800,1600),(1600,2500),(2500,4000),(4000,6500),(6500,10000),(10000,14000),(14000,16000)]
def profile(x,sr=48000):
 analytic=hilbert(np.pad(x,((8192,8192),(0,0))),axis=0)[8192:-8192];rows=[]
 for low,high in BANDS:
  sos=butter(3,[low,high],fs=sr,btype='bandpass',output='sos');z=sosfilt(sos,x,axis=0);hz=sosfilt(sos,analytic.imag,axis=0);p=np.mean(z*z,axis=0);unit=np.sqrt(p.prod());rows.append({'band_Hz':[low,high],'right_over_left_dB':float(10*np.log10(p[1]/p[0])),'correlation':float(np.mean(z[:,0]*z[:,1])/unit),'quadrature':float(.5*np.mean(hz[:,0]*z[:,1]-z[:,0]*hz[:,1])/unit)})
 p=np.mean(x*x,axis=0);return {'whole_right_over_left_dB':float(10*np.log10(p[1]/p[0])),'bands':rows}
if __name__=='__main__':
 files={'reference':'Diva_original_lead_reference.wav','v50':'Diva_v50_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav','v51':'Diva_v51_VIDEO_REFERENCE_EDIT.wav'};results={}
 for name,file in files.items():
  x,sr=sf.read(V/file);assert sr==48000 and x.shape==(176064,2);results[name]=profile(x,sr)
 print(json.dumps({'definition':'Third-order bandpass, whole-fragment R/L power dB, normalized real correlation, signed analytic quadrature. Level balance is not established by correlation alone. Not a listening similarity score.','results':results},indent=2))
