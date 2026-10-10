"""Per-note interchannel spectral phase, independent of common oscillator phase."""
import numpy as np

PITCHES=[41,41,53,37,37,49,36,36]
F=np.fft.rfftfreq(8192,1/48000)
WINDOWS=[(r*7/3+i/6+.055,r*7/3+i/6+.145,440*2**((p-69)/12))
         for r in range(2) for i,p in enumerate(PITCHES)]
MASKS=[[np.abs(F-f0*h)<max(7,h*.45) for h in range(1,13)] for _,_,f0 in WINDOWS]

def spatial_features(x):
    phases=[];balances=[];coherences=[];powers=[]
    for (a,b,_),masks in zip(WINDOWS,MASKS):
        z=x[int(a*48000):int(b*48000)]
        fft=np.fft.rfft(z*np.hanning(len(z))[:,None],8192,axis=0)
        ll=abs(fft[:,0])**2;rr=abs(fft[:,1])**2;lr=fft[:,0]*fft[:,1].conj()
        phase=[];balance=[];coherence=[];power=[]
        for mask in masks:
            cross=lr[mask].sum();left=ll[mask].sum();right=rr[mask].sum()
            phase.append(np.angle(cross));balance.append(10*np.log10(max(left,1e-12)/max(right,1e-12)))
            coherence.append(abs(cross)/np.sqrt(max(left*right,1e-24)));power.append(left+right)
        phases.append(phase);balances.append(balance);coherences.append(coherence);powers.append(power)
    return {'phase':np.asarray(phases),'balance':np.asarray(balances),
            'coherence':np.asarray(coherences),'power':np.asarray(powers)}

def compare(x,reference):
    target=spatial_features(reference)
    weights=np.maximum(target['power'],1e-6)**.65
    weights/=weights.sum()
    features=spatial_features(x)
    delta=np.angle(np.exp(1j*(features['phase']-target['phase'])))
    return {'phase_rms_degrees':float(np.sqrt(np.sum(delta**2*weights))*180/np.pi),
            'balance_rms_db':float(np.sqrt(np.sum((features['balance']-target['balance'])**2*weights))),
            'coherence_rms_error':float(np.sqrt(np.sum((features['coherence']-target['coherence'])**2*weights)))}
