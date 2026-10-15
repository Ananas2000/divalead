"""Analysis helpers using committed WAVs, without private histories or Diva binary."""
import importlib.util,os,sys
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize_scalar
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2];PUBLIC=REPO/'diva-lead/v55-wip'
ROOT=Path(os.environ.get('DIVALEAD_RESEARCH_WORK',str(Path.home()/'.cache/divalead-after-v56')));ROOT.mkdir(parents=True,exist_ok=True)
SR=48000;sys.path.insert(0,str(PUBLIC/'analysis'))
spec=importlib.util.spec_from_file_location('public55_compare',PUBLIC/'analysis/compare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REFERENCE=sf.read(PUBLIC/'Diva_original_lead_reference.wav')[0];BASE_SPATIAL=np.asarray(m.spatial(REFERENCE)['band_correlations'])
def measure(x):
 result={**m.measure(x),**m.dynamics(x),**m.spatial(x),**m.harmonic_stereo(x,m.reference)}
 result['width_error']=float(np.sqrt(np.mean((np.asarray(result['band_correlations'])-BASE_SPATIAL)**2)));return result
def align_with_pdc(x,settings,latency=8320):
 shift=int(round(settings.get('alignment_frames',843)))-latency
 return np.pad(x,((max(shift,0),0),(0,0)))[max(-shift,0):]
def edit_aligned(x):
 output=np.zeros_like(x);output[1:64041]=x[1:64041];output[112022:176064]=x[128007:192049];return output[:len(REFERENCE)]
PITCHES=[41,41,53,37,37,49,36,36]
def harmonics(x):
    rows=[]
    for rep in range(2):
        for i,pitch in enumerate(PITCHES):
            start=rep*7/3+i/6+.045;lo,hi=int(start*SR),int((start+.085)*SR);z=x[lo:hi];t=np.arange(len(z))/SR;win=np.hanning(len(z));f0=440*2**((pitch-69)/12)
            def energy(f):return -float(np.sum(abs(np.sum(z*win[:,None]*np.exp(-2j*np.pi*f*t)[:,None],axis=0))**2))
            f=minimize_scalar(energy,bounds=(f0*.995,f0*1.005),method='bounded').x
            coeff=np.sum(z[:,:,None]*win[:,None,None]*np.exp(-2j*np.pi*t[:,None,None]*f*np.arange(1,25)[None,None,:]),axis=0);power=np.mean(abs(coeff)**2,axis=0);rows.append(power/max(power[0],1e-15))
    return np.array(rows)
HT=harmonics(REFERENCE)
def harmonic_errors(x):
    h=harmonics(x);error=10*np.log10(np.maximum(h,1e-12)/np.maximum(HT,1e-12));weights=np.maximum(HT,1e-5)**.5;weights[:,0]=0;weights/=weights.sum()
    return {'weighted_harmonic_error_db':float(np.sqrt(np.sum(error*error*weights))),'h6_errors_db':error[:,5].tolist(),'h6_rms_error_db':float(np.sqrt(np.mean(error[:,5]**2))),'harmonic_errors_db':error.tolist()}
