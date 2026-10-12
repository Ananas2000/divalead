"""Auxiliary modulation measurement; not a perceptual noise or match score."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
BASE=Path(__file__).resolve().parent.parent
SR=48000
WINDOWS=[(.06,.30,87.307),(.39,.49,174.614),(.58,.8,69.296),(.89,.98,138.591),(1.1,1.28,65.406)]
WINDOWS+= [(a+7/3,b+7/3,f) for a,b,f in WINDOWS.copy()]
FREQ=np.fft.rfftfreq(65536,1/SR)
FILES={'reference':'Diva_original_lead_reference.wav','v32':'Diva_v32_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav','v33':'Diva_v33_VIDEO_REFERENCE_EDIT.wav'}
def measure(path):
    x,sr=sf.read(path,always_2d=True);assert sr==SR and x.shape==(176064,2)
    rows=[]
    for a,b,f0 in WINDOWS:
        z=x[int(a*SR):int(b*SR)];power=np.mean(abs(np.fft.rfft(z*np.hanning(len(z))[:,None],65536,axis=0))**2,axis=1)
        off=abs(FREQ-np.rint(FREQ/f0)*f0)>f0*.23
        d={}
        for lo,hi in [(400,1600),(1600,4000),(4000,6500),(6500,10000)]:
            band=(FREQ>=lo)&(FREQ<hi);d[f'off_harmonic_fraction_{lo}_{hi}']=float(power[band&off].sum()/power[band].sum())
        rows.append(d)
    return {'window_results':rows,'mean_off_harmonic_fraction':{k:float(np.mean([row[k] for row in rows])) for k in rows[0]}}
if __name__=='__main__':
    print(json.dumps({'description':'Finite Hann windows and a nominal harmonic exclusion mask. Off-harmonic energy includes modulation, drift, transitions and codec context. It is not a hiss detector or a perceptual noise score. Compare identically processed windows only.','windows':WINDOWS,'harmonic_exclusion_half_width_f0_fraction':.23,'renders':{name:measure(BASE/file) for name,file in FILES.items()}},indent=2))
