"""Stationary single-note M/S powers with separately fitted carriers; offline diagnostic only."""
from pathlib import Path
import json
import numpy as np
import soundfile as sf
from scipy.optimize import minimize_scalar
V=Path(__file__).resolve().parent.parent;SR=48000
PITCHES=[41,41,53,37,37,49,36,36]
WINDOWS=[(r*7/3+i/6+.045,r*7/3+i/6+.130,440*2**((pitch-69)/12)) for r in range(2) for i,pitch in enumerate(PITCHES)]
BANDS=[(120,300),(300,800),(400,1600),(1600,2500)]
FREQ=np.fft.rfftfreq(65536,1/SR)
def measure(path):
 x,sr=sf.read(path);assert sr==SR and x.shape==(176064,2);rows=[];carriers=[]
 for a,b,nominal in WINDOWS:
  z=x[int(a*SR):int(b*SR)];tt=np.arange(len(z))/SR;win=np.hanning(len(z));orders=np.array([1,2,3])
  def energy(f0):
   basis=win[:,None]*np.exp(-2j*np.pi*tt[:,None]*f0*orders[None,:]);co=z.T@basis;return -float(np.sum(abs(co)**2/orders[None,:]**2))
  fit=minimize_scalar(energy,bounds=(nominal*.992,nominal*1.008),method='bounded',options={'xatol':1e-9});f0=float(fit.x)
  assert nominal*.992+1e-4<f0<nominal*1.008-1e-4,'Carrier fit reached bounds; window needs diagnosis'
  carriers.append(f0);ms=np.c_[z.mean(axis=1),(z[:,0]-z[:,1])/2];power=abs(np.fft.rfft(ms*win[:,None],65536,axis=0))**2;harm=abs(FREQ-np.rint(FREQ/f0)*f0)<.23*f0;unit=power[abs(FREQ-f0)<.23*f0].sum()
  rows.append([[float(power[(FREQ>=low)&(FREQ<high)&mask,ch].sum()/unit) for mask in [harm,~harm] for ch in [0,1]] for low,high in BANDS])
 return np.array(rows),carriers
if __name__=='__main__':
 files={'reference':'Diva_original_lead_reference.wav','v45':'Diva_v45_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav','v46':'Diva_v46_VIDEO_REFERENCE_EDIT.wav'};powers={};carriers={}
 for name,file in files.items():powers[name],carriers[name]=measure(V/file)
 results={}
 for name in ['v45','v46']:
  err=10*np.log10(np.maximum(powers[name],1e-15)/np.maximum(powers['reference'],1e-15));results[name]={'window_dB_RMS':np.sqrt(np.mean(err**2,axis=0)).tolist(),'mean_power_ratio_reference':(powers[name].mean(axis=0)/powers['reference'].mean(axis=0)).tolist(),'window_errors_db':err.tolist()}
 print(json.dumps({'definition':'16single-note stationary windows; separate3harmonic carrier fit per signal; hard nominal masks withradius.23*f0. Includes modulation/window leakage/transients/codec, not isolated hiss or perceived similarity. Fits do not establish exact pitch and are not runtime note tables.','windows':WINDOWS,'bands_Hz':BANDS,'component_order':['Mid_harm','Side_harm','Mid_off','Side_off'],'fitted_carriers_Hz':carriers,'results':results},indent=2))
