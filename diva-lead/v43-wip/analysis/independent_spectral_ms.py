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

def adaptive_harmonic_gain(out,f,f0,sr,hop,settings):
 strength=settings['strength'];tau=settings['tau_seconds']
 if strength<=0:return out
 target=np.array(settings['target_logpower_db_polynomial']);key=np.log2(f0/100);q=np.floor(f[:,None]/f0+.5).astype(int);h=np.exp(-.5*((f[:,None]-q*f0)/(.23*f0))**2);power=np.sum(abs(out)**2,axis=0);unit=np.sum(power*h*(q==1),axis=0)
 aa=np.array([np.sum(power*h**3*(q==o),axis=0) for o in range(2,25)]);bb=np.array([2*np.sum(power*h*h*(1-h)*(q==o),axis=0) for o in range(2,25)]);cc=np.array([np.sum(power*h*(1-h)**2*(q==o),axis=0) for o in range(2,25)])
 aa=np.divide(aa,unit,out=np.zeros_like(aa),where=unit>0);bb=np.divide(bb,unit,out=np.zeros_like(bb),where=unit>0);cc=np.divide(cc,unit,out=np.zeros_like(cc),where=unit>0);goal=10**((target[0,:,None]+target[1,:,None]*key+target[2,:,None]*key*key)/10);delta=goal-cc
 desired=np.maximum(np.where(delta>0,2*delta/np.maximum(bb+np.sqrt(np.maximum(bb*bb+4*aa*delta,0)),1e-30),1e-6),1e-6);lg=np.log(desired);lg[:,unit<=0]=0;lim=settings['limit_db']*np.log(10)/20;wanted=strength*np.clip(lg,-lim,lim);alpha=np.exp(-(hop/sr)/tau) if tau else 0;gain=np.exp(lfilter([1-alpha],[1,-alpha],wanted,axis=1))
 curve=1+sum((q==order)*h*(gain[order-2][None,:]-1) for order in range(2,25));return out*curve[None]

def spectral_ms(processed,dry,sr,base_latency,parameters,sigma=.23,key_slopes=None,phase_angles=None,hf_parameters=None,hf_anchors=None,upper_rolloff=None,harmonic_gain=None,gain_orders=None,hf_sigma=None,phase_key_slopes=None,core_anchors=None,key_quadratic=None,adaptive_dynamic=None):
 hop=round(sr*(4096/48000)/8);size=hop*8;fft=1
 while fft<size:fft*=2
 ms=np.stack([processed.mean(axis=1),.5*(processed[:,0]-processed[:,1])])
 f,t,Z=stft(ms,fs=sr,nperseg=size,noverlap=size-hop,nfft=fft,boundary='zeros',padded=True)
 series=frequency_series(dry,sr)
 idx=np.clip(np.rint(t*sr-base_latency+round(.05*sr)).astype(int),0,len(series)-1)
 f0=np.clip(series[idx],45,220);d=f[:,None]-np.rint(f[:,None]/f0)*f0
 mask=np.exp(-.5*(d/(sigma*f0))**2);off=1-mask
 anchors=np.array([200,500,1400,3500,6000,8000] if core_anchors is None else core_anchors);p=np.asarray(parameters).reshape(7,len(anchors)-2)
 curves=np.array([np.interp(np.log(np.maximum(f,1)),np.log(anchors),np.r_[0,row,0]) for row in p])[:,:,None]
 if key_slopes is not None:
  slopes=np.asarray(key_slopes).reshape(7,len(anchors)-2)
  sc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(anchors),np.r_[0,row,0]) for row in slopes])[:,:,None]
  curves=curves+sc*np.log2(f0/100)[None,None,:]
 if key_quadratic is not None:
  qp=np.asarray(key_quadratic).reshape(7,len(anchors)-2)
  qc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(anchors),np.r_[0,row,0]) for row in qp])[:,:,None]
  curves=curves+qc*np.log2(f0/100)[None,None,:]**2
 m=Z[0];s=Z[1];out=Z.copy()
 out[0]=(1+mask*curves[0]+off*curves[1])*m+off*curves[6]*s
 out[1]=(1+mask*curves[2]+off*curves[3])*s+mask*(curves[5]+1j*curves[4])*m
 if phase_angles is not None:
  orders=np.array([1,2,3,4,6,10,20,40])
  phi=np.interp(np.log(np.maximum(f[:,None]/f0,1)),np.log(orders),np.r_[0,phase_angles,0])
  if phase_key_slopes is not None:phi+=np.interp(np.log(np.maximum(f[:,None]/f0,1)),np.log(orders),np.r_[0,phase_key_slopes,0])*np.log2(f0/100)
  out=out*np.exp(1j*phi)[None]
 if hf_parameters is not None:
  ha=np.asarray(hf_anchors);hp=np.asarray(hf_parameters).reshape(-1,len(ha)-2)
  hc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(ha),np.r_[0,row,0]) for row in hp])[:,:,None]
  hmask=mask if hf_sigma is None else np.exp(-.5*(d/(hf_sigma*f0))**2);hoff=1-hmask
  hm=out[0];hs=out[1]
  mr=hoff*hc[4];mi=hoff*hc[5]
  if len(hp)>8:mr+=hmask*hc[8];mi+=hmask*hc[9]
  out=np.stack([(1+hoff*hc[0]+hmask*hc[6])*hm+hoff*(hc[2]+1j*hc[3])*hs,(1+hoff*hc[1]+hmask*hc[7])*hs+(mr+1j*mi)*hm])
 if upper_rolloff is not None:
  lo,hi=upper_rolloff;lp=np.ones(len(f));roll=(f>lo)&(f<hi);lp[roll]=(.5+.5*np.cos(np.pi*(f[roll]-lo)/(hi-lo)))**2;lp[f>=hi]=0;out*=lp[None,:,None]
 if harmonic_gain is not None:
  gp=np.asarray(harmonic_gain).reshape(3,len(gain_orders)-2);key=np.log2(f0/100);ratio=f[:,None]/f0
  gc=np.array([np.interp(np.log(np.maximum(ratio,1)),np.log(gain_orders),np.r_[0,row,0]) for row in gp])
  gain=1+mask*(gc[0]+key*gc[1]+key*key*gc[2]);out*=gain[None]
 if adaptive_dynamic is not None:out=adaptive_harmonic_gain(out,f,f0,sr,hop,adaptive_dynamic)
 out[:,0]=out[:,0].real;out[:,-1]=out[:,-1].real
 _,y=istft(out,fs=sr,nperseg=size,noverlap=size-hop,nfft=fft);y=y[:,:len(processed)]
 return np.stack([y[0]+y[1],y[0]-y[1]],axis=1),size
