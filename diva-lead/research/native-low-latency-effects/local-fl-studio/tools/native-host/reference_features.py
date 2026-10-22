"""Fast original-reference analysis proxy; never used to synthesize audio."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.fft import rfft
from scipy.optimize import minimize_scalar
ROOT=Path(__file__).resolve().parents[2]
SR=48000
def edit(x):
    p=np.pad(x,((819,0),(0,0)));z=np.zeros((176064,2),np.float32)
    z[1:64041]=p[1:64041];z[112022:176064]=p[128007:192049]
    return z
def channels(x):return np.stack([x.mean(axis=1),.5*(x[:,0]-x[:,1]),x[:,0],x[:,1]],axis=1).astype(np.float32)
class ReferenceFeatures:
    def __init__(self):
        ref,sr=sf.read(ROOT/'sessions/2026-10-22/input/Diva_original_lead_reference.wav',dtype='float32',always_2d=True);assert sr==SR
        self.centers=np.arange(0,len(ref),2048);self.parts=[]
        for size in (1024,4096,16384):
            hz=np.fft.rfftfreq(size,1/SR);edges=np.geomspace(25,20000,50)
            bank=np.maximum(0,np.minimum((np.log(np.maximum(hz,1))[None,:]-np.log(edges[:-2,None]))/(np.log(edges[1:-1,None])-np.log(edges[:-2,None])),(np.log(edges[2:,None])-np.log(np.maximum(hz,1))[None,:])/(np.log(edges[2:,None])-np.log(edges[1:-1,None]))))
            bank=(bank/(bank.sum(axis=1,keepdims=True)+1e-30)).astype(np.float32);win=np.hanning(size).astype(np.float32)
            z=self.spectrum(ref,size,win);p=self.power(z,bank);floor=p.mean(axis=0,keepdims=True)*.03+p.max()*1e-5
            wanted=np.log1p(p/floor);energy=p.mean(axis=(1,2));activity=np.maximum(.04,(energy/(energy.max()+1e-20))**.3)
            weights=np.sqrt(activity[:,None,None]*np.array([1,.7,.3,.3])[None,None,:]/p.size)
            cross=(z[:,:,0]*z[:,:,1].conj())@bank.T;denom=p[:,:,0]+p[:,:,1]+floor[:,:,0]+floor[:,:,1]
            coherence=np.stack([cross.real/denom,cross.imag/denom],axis=-1);cw=np.sqrt(activity[:,None,None]*.15/coherence.size)
            self.parts.append((size,win,bank,floor,wanted,weights,coherence,cw))
        self.rms=float(np.sqrt(np.mean(ref.astype(float)**2)));self.windows=[];orders=np.arange(1,25)
        for rep in range(2):
            for i,pitch in enumerate([41,41,53,37,37,49,36,36]):
                a=rep*7/3+i/6+.045;b=rep*7/3+i/6+.130;lo,hi=int(a*SR),int(b*SR);w=np.hanning(hi-lo).astype(np.float32);t=np.arange(hi-lo)/SR;nom=440*2**((pitch-69)/12)
                mid=ref[lo:hi].mean(axis=1);freq=minimize_scalar(lambda f:-abs(np.sum(mid*w*np.exp(-2j*np.pi*f*t)))**2,bounds=(nom*.995,nom*1.005),method='bounded').x
                kernel=(w[:,None]*np.exp(-2j*np.pi*t[:,None]*freq*orders[None,:])).astype(np.complex64);self.windows.append((lo,hi,kernel))
        c=self.harmonics(ref);self.p=abs(c)**2;self.pfloor=self.p[:,:,0:1]*1e-5+self.p.max()*1e-9;self.logp=np.log1p(self.p/self.pfloor)
        self.pw=np.sqrt(np.array([1,.6,.25,.25])[None,:,None]/self.p.size)
        self.target_phase=self.phases(c);wt=np.maximum(self.p/np.maximum(self.p[:,:,0:1],1e-20),1e-7)**.6;wt[:,:,0]=0;wt*=np.array([1.,.6,.25,.25])[None,:,None];self.phaseweight=np.sqrt(.08*wt/(wt.sum()+1e-20))
    def spectrum(self,y,size,win):
        p=np.pad(channels(y),((size//2,size//2),(0,0)));x=np.stack([p[c:c+size]for c in self.centers]);return rfft(x*win[None,:,None],axis=1,workers=1)/np.sqrt(np.sum(win**2))
    @staticmethod
    def power(z,bank):return ((z.real*z.real+z.imag*z.imag).transpose(0,2,1)@bank.T).transpose(0,2,1)
    def harmonics(self,y):
        x=channels(y);return np.stack([x[lo:hi].T@kernel for lo,hi,kernel in self.windows])
    @staticmethod
    def phases(c):return np.exp(1j*(np.angle(c)-np.arange(1,25)[None,None,:]*np.angle(c[:,:,0:1])))
    def residual(self,full):
        y=edit(full);rms=float(np.sqrt(np.mean(y.astype(float)**2)));y=y*(self.rms/(rms+1e-20));out=[]
        for size,win,bank,floor,wanted,weight,coh,cw in self.parts:
            z=self.spectrum(y,size,win);p=self.power(z,bank);out.append(((np.log1p(p/floor)-wanted)*weight).ravel())
            cross=(z[:,:,0]*z[:,:,1].conj())@bank.T;denom=p[:,:,0]+p[:,:,1]+floor[:,:,0]+floor[:,:,1];out.append(((np.stack([cross.real/denom,cross.imag/denom],axis=-1)-coh)*cw).ravel())
        c=self.harmonics(y);out.append(((np.log1p(abs(c)**2/self.pfloor)-self.logp)*self.pw).ravel())
        phases=self.phases(c);branches=[self.target_phase,self.target_phase*np.exp(1j*np.pi*(1-np.arange(1,25)))[None,None,:]]
        choices=[(phases-t)*self.phaseweight for t in branches];phase=min(choices,key=lambda z:float(np.sum(abs(z)**2)))
        out.extend([phase.real.ravel(),phase.imag.ravel()]);out.append(np.array([.35*np.log((rms+1e-20)/self.rms),max(0,float(abs(full).max())-.94)*5]));return np.concatenate(out)
