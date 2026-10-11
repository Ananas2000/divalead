"""Reproduce a general fixed stereo FIR from saved filter parameters, without audio."""
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d
from scipy.signal import sosfreqz
from v11_fir_design import make_v11_kernels
N=16384;HALF=N//2;SR=48000
def peak(fc,g,q):
 A=10**(g/40);w=2*np.pi*fc/SR;a=np.sin(w)/(2*q);c=np.cos(w);den=1+a/A
 return np.array([1+a*A,-2*c,1-a*A,den,-2*c,1-a/A])/den
def correction(curve,phase_amount,balance_amount,grid):
 curve=np.array(curve);points=np.r_[0,curve[:,0],4000,24000]
 phase=gaussian_filter1d(PchipInterpolator(points,np.r_[0,np.unwrap(curve[:,1]),0,0])(grid),.5)
 balance=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,2],0,0])(grid),.5)
 input_balance=gaussian_filter1d(PchipInterpolator(points,np.r_[0,curve[:,3],0,0])(grid),.5);ratio=10**(input_balance/10)
 left=10**(-balance_amount*balance/40);right=10**(balance_amount*balance/40);common=np.sqrt((ratio+1)/(left*left*ratio+right*right))
 return np.array([common*left*np.exp(-.5j*phase_amount*phase),common*right*np.exp(.5j*phase_amount*phase)])
def side_response(centres,gains,q,grid):
 return sosfreqz(np.array([peak(f,g,q) for f,g in zip(centres,gains)]),worN=grid,fs=SR)[1]
def make_v12_kernels(base_curve,base_settings,v11_settings,residual_settings,matrix_settings):
 h0=make_v11_kernels(base_curve,base_settings,v11_settings);grid=np.fft.rfftfreq(N,1/SR);H0=np.fft.rfft(np.roll(h0,-HALF,axis=1),axis=1)
 D=correction(residual_settings['curve'],residual_settings['phase_amount'],residual_settings['balance_amount'],grid);h=[]
 for c in range(2):
  # Preserve the original residual-design truncation before composing with v11.
  hc=np.roll(np.fft.irfft(D[c],n=N),HALF)*np.hanning(N);HD=np.fft.rfft(np.roll(hc,-HALF));hn=np.roll(np.fft.irfft(H0[c]*HD,n=N),HALF);h.append(h0[c]+(hn-h0[c])*np.hanning(N))
 h=np.array(h);H=np.fft.rfft(np.roll(h,-HALF,axis=1),axis=1);G=side_response(residual_settings['post_side_centres_Hz'],residual_settings['post_side_gains_db'],residual_settings['post_side_Q'],grid)
 M=np.empty((2,2,len(grid)),dtype='complex128');M[0,0]=(1+G)/2*H[0];M[0,1]=(1-G)/2*H[1];M[1,0]=(1-G)/2*H[0];M[1,1]=(1+G)/2*H[1];hm=np.roll(np.fft.irfft(M,n=N,axis=2),HALF,axis=2)
 D=correction(matrix_settings['phase_curve'],matrix_settings['phase_amount'],matrix_settings['balance_amount'],grid);MD=M*D[:,None,:];G=side_response(matrix_settings['side_centres_Hz'],matrix_settings['side_gains_db'],matrix_settings['side_Q'],grid);out=np.empty_like(MD)
 out[0]=(1+G)[None,:]/2*MD[0]+(1-G)[None,:]/2*MD[1];out[1]=(1-G)[None,:]/2*MD[0]+(1+G)[None,:]/2*MD[1]
 hn=np.roll(np.fft.irfft(out,n=N,axis=2),HALF,axis=2)
 return hm+(hn-hm)*np.hanning(N)[None,None,:]
if __name__=='__main__':
 root=Path(__file__).resolve().parent;read=lambda name:json.loads((root/name).read_text())
 h=make_v12_kernels(read('base_v10_curve.json'),read('base_v10_settings.json')['fir'],read('v11_filter_settings.json'),read('residual_filter_settings.json'),read('matrix_filter_settings.json'))
 print('General fixed stereo FIR:',h.shape,'; latency at48000:',8320)
