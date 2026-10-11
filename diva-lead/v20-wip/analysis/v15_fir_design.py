"""Reproduce general v15 audible and detector FIRs without reading audio."""
import json,re
from pathlib import Path
import numpy as np
from v14_fir_design import make_v14_kernels
from v12_fir_design import side_response
N=16384;HALF=N//2;SR=48000
def make_v15_kernels(root):
 h13=make_v14_kernels(root);h0=h13[:2];s=json.loads((root/'v15_filter_settings.json').read_text());grid=np.fft.rfftfreq(N,1/SR);H0=np.fft.rfft(np.roll(h0,-HALF,axis=2),axis=2);centres=np.array(s['eq_centres_Hz']);B=np.exp(-.5*(np.log2(np.maximum(grid,1)[None,:]/centres[:,None])/s['eq_width_octaves'])**2);B[:,0]=B[:,-1]=0
 hn=np.roll(np.fft.irfft(H0*10**((np.array(s['eq_db'])@B)[None,None,:]/20),n=N,axis=2),HALF,axis=2);base=h0+(hn-h0)*np.hanning(N)[None,None,:];Hbase=np.fft.rfft(np.roll(base,-HALF,axis=2),axis=2);G=side_response(s['side_centres_Hz'],s['side_gains_db'],s['side_Q'],grid);M=np.empty_like(Hbase);M[0]=(1+G)[None,:]/2*Hbase[0]+(1-G)[None,:]/2*Hbase[1];M[1]=(1-G)[None,:]/2*Hbase[0]+(1+G)[None,:]/2*Hbase[1];hn=np.roll(np.fft.irfft(M,n=N,axis=2),HALF,axis=2);audible=base+(hn-base)*np.hanning(N)[None,None,:]
 return np.concatenate([audible,h13[2:]],axis=0)
if __name__=='__main__':
 root=Path(__file__).resolve().parent;h=make_v15_kernels(root);body=(root/'fir_kernels.h').read_text().split(' = {',1)[1];header=np.array([float(z) for z in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',body)]).reshape(h.shape);np.testing.assert_array_equal(h,header);print('PASS: all',h.size,'general FIR coefficients reproduced bit-exact without audio; shape',h.shape)
