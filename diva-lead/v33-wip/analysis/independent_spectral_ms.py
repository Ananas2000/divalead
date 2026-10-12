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

def spectral_ms(processed,dry,sr,base_latency,parameters,sigma=.23,key_slopes=None,phase_angles=None,hf_parameters=None,hf_anchors=None,upper_rolloff=None,harmonic_gain=None,gain_orders=None,hf_sigma=None,phase_key_slopes=None):
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
 if key_slopes is not None:
  slopes=np.asarray(key_slopes).reshape(7,4)
  sc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(anchors),np.r_[0,row,0]) for row in slopes])[:,:,None]
  curves=curves+sc*np.log2(f0/100)[None,None,:]
 m=Z[0];s=Z[1];out=Z.copy()
 out[0]=(1+mask*curves[0]+off*curves[1])*m+off*curves[6]*s
 out[1]=(1+mask*curves[2]+off*curves[3])*s+mask*(curves[5]+1j*curves[4])*m
 if phase_angles is not None:
  orders=np.array([1,2,3,4,6,10,20,40])
  phi=np.interp(np.log(np.maximum(f[:,None]/f0,1)),np.log(orders),np.r_[0,phase_angles,0])
  if phase_key_slopes is not None:phi+=np.interp(np.log(np.maximum(f[:,None]/f0,1)),np.log(orders),np.r_[0,phase_key_slopes,0])*np.log2(f0/100)
  out=out*np.exp(1j*phi)[None]
 if hf_parameters is not None:
  ha=np.asarray(hf_anchors);hp=np.asarray(hf_parameters).reshape(8,len(ha)-2)
  hc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(ha),np.r_[0,row,0]) for row in hp])[:,:,None]
  hmask=mask if hf_sigma is None else np.exp(-.5*(d/(hf_sigma*f0))**2);hoff=1-hmask
  hm=out[0];hs=out[1]
  out=np.stack([(1+hoff*hc[0]+hmask*hc[6])*hm+hoff*(hc[2]+1j*hc[3])*hs,(1+hoff*hc[1]+hmask*hc[7])*hs+hoff*(hc[4]+1j*hc[5])*hm])
 if upper_rolloff is not None:
  lo,hi=upper_rolloff;lp=np.ones(len(f));roll=(f>lo)&(f<hi);lp[roll]=(.5+.5*np.cos(np.pi*(f[roll]-lo)/(hi-lo)))**2;lp[f>=hi]=0;out*=lp[None,:,None]
 if harmonic_gain is not None:
  gp=np.asarray(harmonic_gain).reshape(3,len(gain_orders)-2);key=np.log2(f0/100);ratio=f[:,None]/f0
  gc=np.array([np.interp(np.log(np.maximum(ratio,1)),np.log(gain_orders),np.r_[0,row,0]) for row in gp])
  gain=1+mask*(gc[0]+key*gc[1]+key*key*gc[2]);out*=gain[None]
 out[:,0]=out[:,0].real;out[:,-1]=out[:,-1].real
 _,y=istft(out,fs=sr,nperseg=size,noverlap=size-hop,nfft=fft);y=y[:,:len(processed)]
 return np.stack([y[0]+y[1],y[0]-y[1]],axis=1),size
