from pathlib import Path
import json
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
ROOT=W/'Stereo-Shaper-actual-units-03';ROOT.mkdir(exist_ok=False)
a=np.zeros((12000,2),np.float32);a[1024]=[.1,.073];p=ROOT/'impulse.wav';sf.write(p,a,48000,subtype='FLOAT');rows=[]
with four_native_slots(ROOT):
 c=NativeChain(p,'Stereo-Shaper-actual-units',fl_graph=True,engine_override='fl_native_parameter_units_host.exe')
 try:
  for n in range(13):c.bypass(n,n!=8)
  for i,v in enumerate([1,0,1,1,0]):c.gain(i,v)
  for i,v in enumerate([0,12800,12800,0,0,0]):c.set(8,i,v)
  reference,_=c.render()
  for index in [4,5]:
   for raw in [-65536,-12800,-4000,-1000,-100,-1,0,1,100,1000,4000,12800,65536]:
    c.set(8,4,0);c.set(8,5,0);c.set(8,index,raw);actual=c.value_hint(8,index);y,status=c.render();nz=np.flatnonzero(abs(y).max(axis=1)>1e-9)
    rows.append(dict(index=index,requested=raw,actual=actual,native_status=status,first_nonzero=int(nz[0]) if len(nz) else None,max_abs_difference=float(abs(y-reference).max()),difference_RMS=float(np.sqrt(np.mean((y-reference).astype(float)**2)))))
 finally:c.close()
(ROOT/'MAPPING.json').write_text(json.dumps(rows,indent=2)+'\n');print('ACTUAL_STEREO_SHAPER_UNITS_COMPLETE')
