"""Independent SciPy rendering of the fixed spectral M/S correction."""
import json
import numpy as np
from scipy.signal import butter,sosfilt,lfilter,stft,istft

def frequency_series(dry,sr):
 z=sosfilt(butter(2,35,btype='highpass',fs=sr,output='sos'),dry.mean(axis=1))
 z=sosfilt(butter(4,200,fs=sr,output='sos'),z)
 crossings=np.flatnonzero((z[:-1]<=0)&(z[1:]>0))+1
 raw=np.full(len(z),100.);last=None;values=[]
 for frame in crossings:
  crossing=frame-1-z[frame-1]/(z[frame]-z[frame-1])
  if last is not None:
   f=sr/(crossing-last)
   if 45<f<220:
    values.append(f);values=values[-3:];raw[frame:]=np.median(values)
  last=crossing
 alpha=np.exp(-1/(sr*.005));return lfilter([1-alpha],[1,-alpha],raw,zi=[alpha*100])[0]

def spectral_ms(processed,dry,sr,base_latency,parameters,sigma=.23):
 hop=round(sr*(4096/48000)/8);size=hop*8;fft=1
 while fft<size:fft*=2
 ms=np.stack([processed.mean(axis=1),.5*(processed[:,0]-processed[:,1])])
 f,t,Z=stft(ms,fs=sr,nperseg=size,noverlap=size-hop,nfft=fft,boundary='zeros',padded=True)
 series=frequency_series(dry,sr)
 idx=np.clip(np.rint(t*sr-base_latency+round(.05*sr)).astype(int),0,len(series)-1)
 f0=np.clip(series[idx],45,220);d=f[:,None]-np.rint(f[:,None]/f0)*f0
 mask=np.exp(-.5*(d/(sigma*f0))**2);off=1-mask
 anchors=np.array([200,500,1400,3500,6000,8000]);p=np.asarray(parameters).reshape(7,4)
 curves=np.array([np.interp(np.log(np.maximum(f,1)),np.log(anchors),np.r_[0,row,0]) for row in p])[:,:,None]
 m=Z[0];s=Z[1];out=Z.copy()
 out[0]=(1+mask*curves[0]+off*curves[1])*m+off*curves[6]*s
 out[1]=(1+mask*curves[2]+off*curves[3])*s+mask*(curves[5]+1j*curves[4])*m
 out[:,0]=out[:,0].real;out[:,-1]=out[:,-1].real
 _,y=istft(out,fs=sr,nperseg=size,noverlap=size-hop,nfft=fft);y=y[:,:len(processed)]
 return np.stack([y[0]+y[1],y[0]-y[1]],axis=1),size
