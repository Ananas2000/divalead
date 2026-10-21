"""Apply measured stock-effect settings. No audio is synthesized in Python."""
import struct
import numpy as np
from native_chain import W

FREQS=np.array([40,65,100,160,250,400,630,1000,1600,2500,4000,6300,10000,16000],float)
def curve_bytes(c3,c5):
    template=(W/'Fruity_WaveShaper_x64-default-state.bin').read_bytes()
    header=bytearray(template[:34]);struct.pack_into('<I',header,30,129);data=bytearray(header)
    for i,u in enumerate(np.linspace(0,1,129)):
        data.extend(struct.pack('<ddfI',0 if i==0 else 1/128,float(np.clip(u+c3*u**3+c5*u**5,0,1)),0.,0 if i==0 else 0x02000000))
    return bytes(data)+template[82:]

def apply(c,x):
    x=np.asarray(x,float)
    assert len(x) in [78,80]
    for n in [1,2,3,9]:c.bypass(n,True)
    for k,v in enumerate([1,0,1,1,1]):c.gain(k,v)
    path=W/(c.output.stem+'-curve.bin');path.write_bytes(curve_bytes(*x[76:78]));c.load_state(0,path)
    for node,offset in [(4,0),(5,7),(6,14),(7,21)]:
        f=FREQS[offset%14:offset%14+7]*2**x[34+offset:34+offset+7]
        raw=np.rint(np.log(np.clip(f,20,20000)/20)/np.log(1000)*65536).astype(int)
        for band in range(7):
            c.set(node,band,int(round(x[offset+band]*100)))
            c.set(node,7+band,int(raw[band]))
            c.set(node,14+band,int(round(x[62+(offset+band)%14]*65536)))
            c.set(node,21+band,6);c.set(node,28+band,0)
        c.set(node,35,int(round(x[28+(offset>=14)]*100)))
    for i in range(4):c.set(8,i,int(round(x[30+i]*12800)))
    c.set(8,4,int(round(x[78]*1000)) if len(x)>78 else 0)
    c.set(8,5,int(round(x[79]*1000)) if len(x)>79 else 0)
