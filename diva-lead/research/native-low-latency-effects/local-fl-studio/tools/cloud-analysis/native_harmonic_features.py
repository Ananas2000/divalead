"""v83 transfer objective resolving harmonics, off-harmonic power and phase.

All analysis kernels are derived from the migration target, never used as audio.
The same original-reference edit and timing are applied to both compared signals.
"""
import numpy as np
from scipy.optimize import minimize_scalar
import scipy.fft as fft
from native_features import Features,channels,target,sr

def edit(y):
    x=np.pad(y,((819,0),(0,0)))
    z=np.zeros((176064,2),np.float32)
    z[1:64041]=x[1:64041];z[112022:176064]=x[128007:192049]
    return z

class MigrationFeatures:
    def __init__(self,y):
        self.coarse=Features(y);self.windows=[];self.orders=np.arange(1,25)
        z=edit(y);nfft=8192;hz=np.fft.rfftfreq(nfft,1/sr)
        self.banks=[];wanted=[];off=[]
        for rep in range(2):
            for i,p in enumerate([41,41,53,37,37,49,36,36]):
                a=rep*7/3+i/6+.045;b=rep*7/3+i/6+.130
                lo,hi=int(a*sr),int(b*sr);w=np.hanning(hi-lo).astype(np.float32)
                t=np.arange(hi-lo)/sr;nom=440*2**((p-69)/12)
                mid=z[lo:hi].mean(axis=1)
                f=minimize_scalar(lambda f:-abs(np.sum(mid*w*np.exp(-2j*np.pi*f*t)))**2,bounds=(nom*.995,nom*1.005),method='bounded').x
                kernel=(w[:,None]*np.exp(-2j*np.pi*t[:,None]*f*self.orders[None,:])).astype(np.complex64)
                self.windows.append((lo,hi,w,kernel))
                masks=[];isoff=abs(hz-np.rint(hz/f)*f)>.23*f
                for l,h in [(120,300),(300,800),(800,1600),(1600,2500),(2500,4500),(4500,6500),(6500,10000),(10000,16000)]:
                    m=((hz>=l)&(hz<h)&isoff).astype(np.float32);m/=max(1,m.sum());masks.append(m)
                self.banks.append(np.stack(masks))
        self.cc,self.off=self.analyze(y)
        self.p=abs(self.cc)**2;self.pfloor=self.p[:,:,0:1]*1e-5+np.max(self.p)*1e-9
        self.logp=np.log1p(self.p/self.pfloor)
        self.phase=self.phases(self.cc)
        weight=np.maximum(self.p/np.maximum(self.p[:,:,0:1],1e-20),1e-7)**.6
        weight[:,:,0]=0;weight*=np.array([1.,.6,.25,.25])[None,:,None]
        self.phaseweight=np.sqrt(.24*weight/(weight.sum()+1e-20))
        self.ow=np.sqrt(np.array([1.,.6,.2,.2])[None,:,None]/self.off.size)
        self.ofloor=self.off*.03+np.max(self.off)*1e-7
        self.offlog=np.log1p(self.off/self.ofloor)
        self.pw=np.sqrt(np.array([1.,.6,.2,.2])[None,:,None]/self.p.size)

    def analyze(self,y):
        z=channels(edit(y));cc=[];off=[]
        for (lo,hi,w,kernel),bank in zip(self.windows,self.banks):
            x=z[lo:hi];cc.append(x.T@kernel)
            f=fft.rfft(x*w[:,None],8192,axis=0,workers=1)
            power=(f.real*f.real+f.imag*f.imag).T
            off.append(power@bank.T)
        return np.stack(cc),np.stack(off)

    def phases(self,c):return np.exp(1j*(np.angle(c)-self.orders[None,None,:]*np.angle(c[:,:,0:1])))
    def residual(self,y):
        cc,off=self.analyze(y);p=abs(cc)**2
        phase=(self.phases(cc)-self.phase)*self.phaseweight
        return np.r_[self.coarse.residual(y)*.4,
                     ((np.log1p(p/self.pfloor)-self.logp)*self.pw).ravel(),
                     ((np.log1p(off/self.ofloor)-self.offlog)*self.ow*.6).ravel(),
                     phase.real.ravel(),phase.imag.ravel()]
