"""Relative harmonic phase and peak/RMS; neither is an audition or hiss score."""
import json
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize_scalar
V=Path(__file__).resolve().parent.parent;SR=48000
WINDOWS=[(r*7/3+i/6+.045,r*7/3+i/6+.130,440*2**((p-69)/12)) for r in range(2) for i,p in enumerate([41,41,53,37,37,49,36,36])];ORDERS=np.arange(1,13)
def features(x):
 coefficients=[];crests=[];frequencies=[]
 for a,b,nom in WINDOWS:
  z=x[int(a*SR):int(b*SR)];mid=z.mean(axis=1);t=np.arange(len(z))/SR;w=np.hanning(len(z));f=minimize_scalar(lambda f:-abs(np.sum(mid*w*np.exp(-2j*np.pi*f*t)))**2,bounds=(nom*.995,nom*1.005),method='bounded').x
  cc=mid@(w[:,None]*np.exp(-2j*np.pi*t[:,None]*f*ORDERS[None]));coefficients.append(cc);crests.append(20*np.log10(np.max(abs(z))/np.sqrt(np.mean(z*z))));frequencies.append(f)
 cc=np.asarray(coefficients);return np.exp(1j*(np.angle(cc)-ORDERS*np.angle(cc[:,0])[:,None])),abs(cc)**2/abs(cc[:,0,None])**2,np.asarray(crests),frequencies
if __name__=='__main__':
 files={'reference':'Diva_original_lead_reference.wav','v51':'Diva_v51_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav','v52':'Diva_v52_VIDEO_REFERENCE_EDIT.wav'};data={}
 for label,file in files.items():
  x,sr=sf.read(V/file);assert sr==SR and x.shape==(176064,2);data[label]=features(x)
 target,weight,tc,_=data['reference'];weight=np.maximum(weight,1e-8)**.65;weight[:,0]=0;weight/=weight.sum();branches=[target,target*np.exp(1j*np.pi*(1-ORDERS))[None]];branch=min(range(2),key=lambda i:np.sum(abs(data['v51'][0]-branches[i])**2*weight));target=branches[branch];results={}
 for label,(shape,_,crest,freq) in data.items():
  if label=='reference':shape=target
  difference=abs(shape-target)**2;folds=[]
  for rep in range(2):
   sl=slice(rep*8,(rep+1)*8);w=weight[sl]/weight[sl].sum();folds.append({'repetition':rep+1,'relative_phase_complex_error':float(np.sqrt(np.sum(difference[sl]*w))),'crest_RMS_error_dB':float(np.sqrt(np.mean((crest[sl]-tc[sl])**2)))})
  results[label]={'relative_phase_complex_error':float(np.sqrt(np.sum(difference*weight))),'crest_RMS_error_dB':float(np.sqrt(np.mean((crest-tc)**2))),'stationary_peak_over_RMS_dB':crest.tolist(),'fitted_fundamentals_Hz':freq,'repetitions':folds}
 print(json.dumps({'definition':'16single-note stationary windows, independently fitted fundamentals and12relative Mid-harmonic phases. Shared polarity branch chosen using49only. Phase/amplitude are separate; these are not perceptual match, compression or hiss scores. Same fitting windows, not heldout.','polarity_branch':branch,'windows_seconds':WINDOWS,'results':results},indent=2))
