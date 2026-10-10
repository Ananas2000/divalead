import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d

def make_kernels(curve,phase_amount,balance_amount,common_amount,sample_rate=48000,length=8192):
 curve=np.asarray(curve);grid=np.fft.rfftfreq(length,1/sample_rate);points=np.r_[0,curve[:,0],4000,sample_rate/2]
 phase=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,1],0,0])(grid),1.)
 balance=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,2],0,0])(grid),1.)
 common=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,3],0,0])(grid),1.)
 phase=np.clip(phase,-1.4,1.4);balance=np.clip(balance,-12,12);common=np.clip(common,-6,6);kernels=[]
 for sign in [-1,1]:
  H=np.exp((common_amount*common+sign*balance_amount*balance/2)*np.log(10)/20+1j*sign*phase_amount*phase/2);H[0]=H[0].real;H[-1]=H[-1].real
  kernels.append(np.roll(np.fft.irfft(H,n=length),length//2)*np.hanning(length))
 return np.array(kernels)
