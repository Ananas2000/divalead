"""Reproduce a general fixed FIR from saved filter settings, without audio."""
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d
from v10_fir_design import make_v10_kernels

def make_v11_kernels(base_curve,base_settings,settings):
 h10=make_v10_kernels(base_curve,base_settings);N=16384;half=N//2
 h0=np.pad(h10,((0,0),(4096,4096)));H0=np.fft.rfft(np.roll(h0,-half,axis=1),axis=1)
 curve=np.array(settings['curve']);grid=np.fft.rfftfreq(N,1/48000);points=np.r_[0,curve[:,0],4000,24000]
 phase=gaussian_filter1d(PchipInterpolator(points,np.r_[0,np.unwrap(curve[:,1]),0,0])(grid),.5)
 bal=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,2],0,0])(grid),.5)
 inputbal=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,3],0,0])(grid),.5);ratio=10**(inputbal/10)
 pa=settings['phase_amount'];ba=settings['balance_amount'];gL=10**(-ba*bal/40);gR=10**(ba*bal/40);common=np.sqrt((ratio+1)/(gL*gL*ratio+gR*gR));kernels=[]
 for c,sign,gain in zip(range(2),[-1,1],[gL,gR]):
  H=common*gain*np.exp(1j*sign*pa*phase/2);hc=np.roll(np.fft.irfft(H,n=N),half)*np.hanning(N);HD=np.fft.rfft(np.roll(hc,-half));hn=np.roll(np.fft.irfft(H0[c]*HD,n=N),half)
  kernels.append(h0[c]+(hn-h0[c])*np.hanning(N))
 h=np.array(kernels);centres=np.array(settings['eq_centres_Hz']);width=settings['eq_width_octaves'];B=np.exp(-.5*(np.log2(np.maximum(grid,1)[None,:]/centres[:,None])/width)**2);B[:,0]=0;B[:,-1]=0
 H=np.fft.rfft(np.roll(h,-half,axis=1),axis=1);hn=np.roll(np.fft.irfft(H*10**((np.array(settings['eq_db'])@B)[None,:]/20),n=N,axis=1),half,axis=1)
 return h+(hn-h)*np.hanning(N)[None,:]

if __name__=='__main__':
 root=Path(__file__).resolve().parent
 h=make_v11_kernels(json.loads((root/'base_v10_curve.json').read_text()),json.loads((root/'base_v10_settings.json').read_text())['fir'],json.loads((root/'selected_candidate.json').read_text()))
 print('Fixed stereo FIR:',h.shape,'; latency at 48000:',8320)
