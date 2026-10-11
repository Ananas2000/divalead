"""Measure relative powers of24 harmonics in16 fixed, identical note windows.

The analysis uses the known score to locate stationary windows; the runtime
processor estimates frequency from audio alone. These errors are not match percentages.
"""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
from scipy.optimize import minimize_scalar
BASE=Path(__file__).resolve().parent.parent;SR=48000
PITCHES=[41,41,53,37,37,49,36,36]
def harmonics(x):
    rows=[]
    for rep in range(2):
        for i,pitch in enumerate(PITCHES):
            start=rep*7/3+i/6+.045;lo,hi=int(start*SR),int((start+.085)*SR);z=x[lo:hi];t=np.arange(len(z))/SR;win=np.hanning(len(z));f0=440*2**((pitch-69)/12)
            def energy(f):return -float(np.sum(abs(np.sum(z*win[:,None]*np.exp(-2j*np.pi*f*t)[:,None],axis=0))**2))
            f=minimize_scalar(energy,bounds=(f0*.995,f0*1.005),method='bounded').x
            coeff=np.sum(z[:,:,None]*win[:,None,None]*np.exp(-2j*np.pi*t[:,None,None]*f*np.arange(1,25)[None,None,:]),axis=0);power=np.mean(abs(coeff)**2,axis=0);rows.append(power/max(power[0],1e-15))
    return np.array(rows)

def read(name):
    x,sr=sf.read(BASE/name);assert sr==SR and x.shape==(176064,2);return x
HT=harmonics(read('Diva_original_lead_reference.wav'))
def errors(x):
    h=harmonics(x);error=10*np.log10(np.maximum(h,1e-12)/np.maximum(HT,1e-12))
    weights=np.maximum(HT,1e-5)**.5;weights[:,0]=0;weights/=weights.sum()
    return {'weighted_harmonic_error_db':float(np.sqrt(np.sum(error*error*weights))),'h6_rms_error_db':float(np.sqrt(np.mean(error[:,5]**2))),'harmonic_errors_db':error.tolist()}
if __name__=='__main__':
    result={name:errors(read(file)) for name,file in [('v24','Diva_v24_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav'),('v25','Diva_v25_VIDEO_REFERENCE_EDIT.wav')]}
    print(json.dumps(result,indent=2))
