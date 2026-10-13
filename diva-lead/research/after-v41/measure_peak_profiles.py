"""Offline diagnostic for identically aligned 3.668s reference edits; no runtime audio processing."""
from pathlib import Path
import argparse,json
import numpy as np
import soundfile as sf
from scipy.optimize import minimize_scalar
SR=48000
PITCHES=[41,41,53,37,37,49,36,36]
WINDOWS=[(rep*7/3+i/6+.045,rep*7/3+i/6+.130,440*2**((p-69)/12)) for rep in range(2) for i,p in enumerate(PITCHES)]
BANDS=[(400,1600),(1600,2500),(2500,3500),(3500,4500),(4500,6500),(6500,10000),(10000,14000)]
FREQ=np.fft.rfftfreq(65536,1/SR)
def profile(path):
 x,sr=sf.read(path,always_2d=True)
 assert sr==SR and x.shape==(176064,2) and np.isfinite(x).all()
 result=[];carriers=[]
 for a,b,nom in WINDOWS:
  z=x[int(a*SR):int(b*SR)];tt=np.arange(len(z))/SR;win=np.hanning(len(z));orders=np.array([1,2,3])
  def energy(f0):
   coefficients=z.T@(win[:,None]*np.exp(-2j*np.pi*tt[:,None]*f0*orders))
   return -float(np.sum(abs(coefficients)**2/orders[None,:]**2))
  ff=float(minimize_scalar(energy,bounds=(nom*.992,nom*1.008),method='bounded',options={'xatol':1e-9}).x)
  assert nom*.992+1e-4<ff<nom*1.008-1e-4,'Carrier estimate reached a bound; inspect this window'
  carriers.append(ff);ms=np.c_[z.mean(axis=1),(z[:,0]-z[:,1])/2];power=abs(np.fft.rfft(ms*win[:,None],65536,axis=0))**2;delta=abs(FREQ-np.rint(FREQ/ff)*ff)
  result.append([[float(power[(FREQ>=lo)&(FREQ<hi)&(delta<.1*ff),ch].sum()/max(power[(FREQ>=lo)&(FREQ<hi)&(delta<.23*ff),ch].sum(),1e-30)) for ch in [0,1]] for lo,hi in BANDS])
 return np.array(result),carriers
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('reference',type=Path);parser.add_argument('candidate',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args();ref,rc=profile(args.reference);candidate,cc=profile(args.candidate)
 report={'definition':'16separate3harmonic-carrier stationary windows. Energy inside .1*f0 / energy inside .23*f0; finite85msHann windows; 65536FFT interpolates spectra. Includes modulation/drift/window leakage/codec; not isolatedhiss, actualpitch, or perceived similarity. No note schedule is used in the audio processor.','bands_Hz':BANDS,'channels':['Mid','Side'],'windows_seconds':[(a,b) for a,b,_ in WINDOWS],'reference_carriers_Hz':rc,'candidate_carriers_Hz':cc,'reference_mean_narrow_fraction':ref.mean(axis=0).tolist(),'candidate_mean_narrow_fraction':candidate.mean(axis=0).tolist(),'difference_reference_RMS':np.sqrt(np.mean((candidate-ref)**2,axis=0)).tolist()};text=json.dumps(report,indent=2)
 if args.output:args.output.write_text(text+'\n')
 else:print(text)
