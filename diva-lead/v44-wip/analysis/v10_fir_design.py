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


def common_correction(kernels,centres,width,values,phase=False):
    length=kernels.shape[1];half=length//2
    grid=np.fft.rfftfreq(length,1/48000)
    basis=np.exp(-.5*(np.log2(np.maximum(grid,1)[None,:]/np.asarray(centres)[:,None])/width)**2)
    basis[:,0]=0;basis[:,-1]=0;curve=np.asarray(values)@basis
    H=np.fft.rfft(np.roll(kernels,-half,axis=1),axis=1)
    factor=np.exp(1j*curve) if phase else 10**(curve/20)
    corrected=np.roll(np.fft.irfft(H*factor[None,:],n=length,axis=1),half,axis=1)
    return kernels+(corrected-kernels)*np.hanning(length)[None,:]

def make_v10_kernels(curve,settings):
    h=make_kernels(curve,settings['phase_amount'],settings['balance_amount'],settings['common_amount'])
    h=common_correction(h,settings['common_phase_centres_Hz'],settings['common_phase_width_octaves'],settings['common_phase_radians'],phase=True)
    return common_correction(h,settings['common_eq_centres_Hz'],settings['common_eq_width_octaves'],settings['common_eq_db'])

if __name__=='__main__':
    import json
    from pathlib import Path
    base=Path(__file__).resolve().parent
    settings=json.loads((base.parent/'Finish_settings.json').read_text())['fir']
    curve=json.loads((base/'fir_target_curve.json').read_text())
    h=make_v10_kernels(curve,settings)
    print('Length:',h.shape[1],'; latency:',settings['reported_latency_frames_48000'])
    # Print only metadata; coefficient export can be done with np.save.
