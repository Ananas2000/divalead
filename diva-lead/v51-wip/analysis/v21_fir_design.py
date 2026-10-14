"""Reproduce v21 fixed FIRs without audio or a MIDI schedule."""
import json,re
from pathlib import Path
import numpy as np
from scipy.fft import rfft,irfft
from v17_fir_design import make_v17_kernels
def make_v21_kernels(root):
 h0=make_v17_kernels(root);s=json.loads((root/'v21_filter_settings.json').read_text());n=16384;half=n//2;grid=np.fft.rfftfreq(n,1/48000);centers=np.array(s['common_eq_centres_Hz']);b=np.exp(-.5*(np.log2(np.maximum(grid,1)[:,None]/centers[None,:])/s['common_eq_width_octaves'])**2);b[0]=b[-1]=0;H=rfft(np.roll(h0,-half,axis=2),axis=2);shifted=np.roll(irfft(H*10**((b@np.array(s['common_eq_db']))[None,None,:]/20),n=n,axis=2),half,axis=2);h=h0.copy();h[:2]=h0[:2]+(shifted[:2]-h0[:2])*np.hanning(n)[None,None,:];return h
if __name__=='__main__':
 root=Path(__file__).resolve().parent;h=make_v21_kernels(root);body=(root/'fir_kernels.h').read_text().split(' = {',1)[1];header=np.array([float(v) for v in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',body)]).reshape(h.shape);np.testing.assert_array_equal(h,header);print('PASS:',h.size,'fixed FIR constants reproduced without audio')
