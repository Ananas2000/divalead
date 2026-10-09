"""Recompute spectral distances from the delivered audio, without Diva.

These are measurements of power distributions, not perceptual percentages.
Run: python analysis/compare.py
"""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft
from scipy.ndimage import gaussian_filter1d

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

old=read('Diva_v3_DRY_previous.wav')
old_aligned=np.concatenate([np.zeros((960,2)),old])[:len(old)]
result={'reference':measure(reference),'v3_raw':measure(old),'v3_aligned_20ms':measure(old_aligned),
        'v4_raw':measure(read('Diva_v4_DRY.wav')),
        'v4_aligned':measure(read('Diva_v4_DRY_ALIGNED.wav'))}
print(json.dumps(result,indent=2))
