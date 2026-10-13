"""Reproduce the general v17 FIRs from fixed coefficients, without audio."""
import json,re
from pathlib import Path
import numpy as np
from scipy.fft import rfft,irfft
from v15_fir_design import make_v15_kernels
N=16384;HALF=N//2;SR=48000
def make_v17_kernels(root):
 h0=make_v15_kernels(root);s=json.loads((root/'v17_filter_settings.json').read_text());grid=np.fft.rfftfreq(N,1/SR);centers=np.array(s['relative_phase_centers_Hz']);B=np.exp(-.5*(np.log2(np.maximum(grid,1)[:,None]/centers[None,:])/s['relative_phase_width_octaves'])**2);phase=B@np.array(s['relative_phase_coefficients_radians']);phase[0]=phase[-1]=0;H=rfft(np.roll(h0[:2],-HALF,axis=2),axis=2);M=H*np.exp(.5j*np.array([1,-1])[:,None,None]*phase[None,None,:]);hn=np.roll(irfft(M,n=N,axis=2),HALF,axis=2);h=h0.copy();h[:2]=h0[:2]+(hn-h0[:2])*np.hanning(N)[None,None,:];return h
if __name__=='__main__':
 root=Path(__file__).resolve().parent;h=make_v17_kernels(root);body=(root/'fir_kernels.h').read_text().split(' = {',1)[1];header=np.array([float(q) for q in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',body)]).reshape(h.shape);np.testing.assert_array_equal(h,header);print('PASS: all',h.size,'general FIR coefficients reproduced bit-exact without audio; shape',h.shape)
