"""An isolated actual Fruity Stereo Shaper after the two actual ZL effects."""
from pathlib import Path
import math,os
import numpy as np,soundfile as sf
from native_chain import NativeChain
class NativePostTrim:
 def __init__(self,root,tag,cleanup_on_close=False):
  self.cleanup_on_close=cleanup_on_close;self.closed=False;self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.input=self.root/(tag+'-input.wav');sf.write(self.input,np.zeros((32768,2),np.float32),48000,subtype='FLOAT');self.chain=NativeChain(self.input,tag,fl_graph=False,engine_override='fl_native_chain_host.exe')
  for k in range(10):self.chain.bypass(k,k!=8)
  for k,v in enumerate([1.,0.,1.,1.,1.]):self.chain.gain(k,v)
  self.configure(12800,12800)
 @staticmethod
 def raw_from_dB(db):return int(round(12800*math.log(1+2*10**(db/20))/math.log(3)))
 def configure(self,left_raw,right_raw):
  assert 0<left_raw<=14000 and 0<right_raw<=14000
  # Fruity's parameter order is R->L, L->L, R->R, L->R, delayL, delayR.
  for k,v in enumerate([0,left_raw,right_raw,0,0,0]):self.chain.set(8,k,int(v))
 def load(self,path):self.chain.load_state(8,path)
 def save(self,path):self.chain.save_state(8,path)
 def render(self,y):
  sf.write(self.input,np.asarray(y,np.float32),48000,subtype='FLOAT');self.chain.load_input(self.input);return self.chain.render()[0]
 def close(self):
  if self.closed:return
  self.chain.close();self.closed=True
  if self.cleanup_on_close:
   for p in[self.input,self.chain.output]:
    if p.exists():p.unlink()
