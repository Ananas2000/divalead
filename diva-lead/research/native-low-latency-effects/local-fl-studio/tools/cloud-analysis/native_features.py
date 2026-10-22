from pathlib import Path
import numpy as np
import scipy.fft as fft
import soundfile as sf
target,sr=sf.read("/workspace/divalead/diva-lead/v83-wip/Diva_Lead_v83_FULL_180BPM.wav",dtype="float32",always_2d=True)
centers=np.arange(0,len(target),4096)
def channels(y):
    l=y[:,0];r=y[:,1]
    return np.stack([.5*(l+r),.5*(l-r),l,r],axis=1).astype(np.float32)

class Features:
    def __init__(self,y):
        self.parts=[]
        for size in [1024,4096]:
            hz=np.fft.rfftfreq(size,1/sr)
            edges=np.geomspace(25,20000,50)
            bank=np.maximum(0,np.minimum((np.log(np.maximum(hz,1))[None,:]-np.log(edges[:-2,None]))/(np.log(edges[1:-1,None])-np.log(edges[:-2,None])),
                                        (np.log(edges[2:,None])-np.log(np.maximum(hz,1))[None,:])/(np.log(edges[2:,None])-np.log(edges[1:-1,None]))))
            bank=bank/(bank.sum(axis=1,keepdims=True)+1e-30)
            window=np.hanning(size).astype(np.float32);bank=bank.astype(np.float32)
            z=self.spectrum(y,size,window)
            p=self.power(z,bank)
            floor=np.mean(p,axis=0,keepdims=True)*.03+float(np.max(p))*1e-5
            wanted=np.log1p(p/floor)
            energy=np.mean(p,axis=(1,2));activity=np.maximum(.04,(energy/(energy.max()+1e-20))**.3)
            weights=np.sqrt(activity[:,None,None]*np.array([1,.7,.3,.3])[None,None,:]/p.size)
            cross=(z[:,:,0]*z[:,:,1].conj())@bank.T
            denom=p[:,:,0]+p[:,:,1]+floor[:,:,0]+floor[:,:,1]
            coherence=np.stack([cross.real/denom,cross.imag/denom],axis=-1)
            cw=np.sqrt(activity[:,None,None]*.15/coherence.size)
            self.parts.append((size,window,bank,floor,wanted,weights,coherence,cw))
        self.target_rms=float(np.sqrt(np.mean(y.astype(float)**2)))
    @staticmethod
    def spectrum(y,size,window):
        x=channels(y);pad=np.pad(x,((size//2,size//2),(0,0)))
        windows=np.stack([pad[c:c+size] for c in centers],axis=0)
        return fft.rfft(windows*window[None,:,None],axis=1,workers=1)/np.sqrt(np.sum(window**2))
    @staticmethod
    def power(z,bank):
        p=(z.real*z.real+z.imag*z.imag).transpose(0,2,1)@bank.T
        return p.transpose(0,2,1)
    def residual(self,y):
        out=[]
        for size,window,bank,floor,wanted,weights,coh,cw in self.parts:
            z=self.spectrum(y,size,window);p=self.power(z,bank)
            out.append(((np.log1p(p/floor)-wanted)*weights).ravel())
            cross=(z[:,:,0]*z[:,:,1].conj())@bank.T;denom=p[:,:,0]+p[:,:,1]+floor[:,:,0]+floor[:,:,1]
            got=np.stack([cross.real/denom,cross.imag/denom],axis=-1)
            out.append(((got-coh)*cw).ravel())
        rms=float(np.sqrt(np.mean(y.astype(float)**2)))
        out.append(np.array([.2*np.log((rms+1e-12)/self.target_rms),max(0,float(abs(y).max())-.95)*3]))
        return np.concatenate(out).astype(float)
