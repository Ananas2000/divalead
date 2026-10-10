"""Recompute spectral distances from the delivered audio, without plugins.

These are measurements of power distributions, not perceptual percentages.
Run: python analysis/compare.py
"""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft
from scipy.ndimage import gaussian_filter1d, uniform_filter1d
from harmonic_stereo import compare as harmonic_stereo

BASE=Path(__file__).resolve().parent.parent
FIRST=[(.06,.30,87.307),(.39,.49,174.614),(.58,.8,69.296),
       (.89,.98,138.591),(1.1,1.28,65.406)]
WINDOWS=FIRST+[(a+7/3,b+7/3,f) for a,b,f in FIRST]
FREQ=np.fft.rfftfreq(16384,1/48000)
SELECT=(FREQ>=35)&(FREQ<=6500)

def read(name):
    x,sr=sf.read(BASE/name,always_2d=True)
    assert sr==48000 and x.shape[1]==2 and np.all(np.isfinite(x))
    return x

def windows(x):
    rows=[];levels=[]
    for a,b,f in WINDOWS:
        z=x[int(a*48000):int(b*48000)]
        p=np.mean(abs(np.fft.rfft(z*np.hanning(len(z))[:,None],16384,axis=0))**2,axis=1)
        unit=max(float(p[np.abs(FREQ-f)<f*.28].sum()),1e-12)
        rows.append(gaussian_filter1d(p,1.2)[SELECT]/unit)
        levels.append(np.sqrt(np.mean(z*z)))
    return np.asarray(rows),np.asarray(levels)

def frames(x):
    _,t,z=stft(x,48000,window='hann',nperseg=4096,noverlap=3072,axis=0,padded=False)
    p=np.mean(abs(z)**2,axis=1);f=np.fft.rfftfreq(4096,1/48000)
    active=((t>.02)&(t<1.31))|((t>2.35)&(t<3.64))
    p=gaussian_filter1d(p,1,axis=0)[(f>=35)&(f<=16000)][:,active]
    return p/np.maximum(p.sum(axis=0,keepdims=True),1e-15)

reference=read('Diva_original_lead_reference.wav')
target,levels=windows(reference)
norm_target=target/target.sum(axis=1,keepdims=True)
weights=np.maximum(target,1e-8)**.6/(1+FREQ[SELECT][None,:]/250)**.3
weights/=weights.sum(axis=1,keepdims=True)
whole_target=frames(reference)

def measure(x):
    p,lev=windows(x);q=p/p.sum(axis=1,keepdims=True)
    h=float(np.sqrt(np.mean(np.sum((np.sqrt(norm_target)-np.sqrt(q))**2,axis=1))/2))
    er=10*np.log10(np.maximum(p,1e-8))-10*np.log10(np.maximum(target,1e-8))
    db=float(np.sqrt(np.mean(np.sum(er*er*weights,axis=1))))
    dynamics=float(np.std(20*np.log10(np.maximum(lev,1e-8)/levels)))
    fp=frames(x)
    whole=float(np.sqrt(np.mean(np.sum((np.sqrt(whole_target)-np.sqrt(fp))**2,axis=0))/2))
    return {'window_distance':h,'weighted_db_error':db,'window_level_error_db':dynamics,
            'whole_distance':whole}

def spatial(x):
    from scipy.signal import butter, sosfilt
    active=np.r_[np.arange(2400,62400),np.arange(114400,174000)]
    z=x[:len(reference)]
    bands=[(40,300),(300,800),(800,2000),(2000,5000),(5000,10000)]
    correlations=[]
    for lo,hi in bands:
        sos=butter(3,[lo,hi],btype='bandpass',fs=48000,output='sos')
        b=sosfilt(sos,z,axis=0)[active]
        correlations.append(float(np.corrcoef(b.T)[0,1]))
    return {'active_lr_correlation':float(np.corrcoef(z[active].T)[0,1]),
            'bands_Hz':bands,'band_correlations':correlations}

def dynamics(x):
    # Windows remain fixed across versions; no individual note normalization.
    rms=float(np.sqrt(np.mean(reference**2)))
    x=x*rms/np.sqrt(np.mean(x[:len(reference)]**2))
    grid=np.r_[np.arange(0,71000,120),np.arange(111800,176000,120)]
    def env(z,width):
        return np.sqrt(np.maximum(uniform_filter1d(np.mean(z*z,axis=1),width),1e-15))
    errors={}
    for width in [576,1152]:
        errors[f'envelope{round(width/48)}_error']=float(np.sqrt(np.mean(((env(x,width)[grid]-env(reference,width)[grid])/rms)**2)))
    bodies=[(r*7/3+i/6+.045,r*7/3+i/6+.12) for r in range(2) for i in range(8)]
    db=[]
    for a,b in bodies:
        lo,hi=int(a*48000),int(b*48000)
        db.append(float(10*np.log10(np.mean(x[lo:hi]**2)/np.mean(reference[lo:hi]**2))))
    errors['body_errors_db']=db
    errors['body_level_error_db']=float(np.sqrt(np.mean(np.asarray(db)**2)))
    errors['tail_error']=float(np.sqrt(np.mean(x[int(1.337*48000):int(1.45*48000)]**2)))/rms
    return errors

if __name__=='__main__':
    result={}
    for name,file in [('reference','Diva_original_lead_reference.wav'),('v14_reference_pattern_correct_alignment','Diva_v14_FINAL_ALIGNED_previous_CORRECT_ALIGNMENT.wav'),('v15_reference_pattern','Diva_v15_FINAL_ALIGNED.wav'),('v14_continuous_reference_edit_correct_alignment','Diva_v14_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav'),('v15_continuous_reference_edit','Diva_v15_VIDEO_REFERENCE_EDIT.wav')]:
        x=read(file);result[name]={**measure(x),**spatial(x),**dynamics(x),**harmonic_stereo(x,reference)}
        result[name]['width_error']=float(np.sqrt(np.mean((np.array(result[name]['band_correlations'])-np.array(spatial(reference)['band_correlations']))**2)))
    print(json.dumps(result,indent=2))
