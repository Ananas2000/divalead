"""Separate harmonic and off-harmonic Mid/Side contributions, auxiliary only."""
import json,importlib.util,sys
sys.dont_write_bytecode=True
import numpy as np
import soundfile as sf
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SR=48000
V=ROOT.parent
spec=importlib.util.spec_from_file_location('roughness',V/'analysis/roughness_compare.py');rough=importlib.util.module_from_spec(spec);spec.loader.exec_module(rough)
results={}
for name,path in [('reference',V/'Diva_original_lead_reference.wav'),('v29',V/'Diva_v29_VIDEO_REFERENCE_EDIT_previous_CORRECT_ALIGNMENT.wav'),('v30',V/'Diva_v30_VIDEO_REFERENCE_EDIT.wav')]:
 x=sf.read(path)[0];rows=[]
 for a,b,f0 in rough.WINDOWS:
  z=x[int(a*SR):int(b*SR)];mid=np.mean(z,axis=1);side=.5*(z[:,0]-z[:,1]);P=abs(np.fft.rfft(np.stack([mid,side],axis=1)*np.hanning(len(z))[:,None],65536,axis=0))**2
  F=rough.FREQ;off=abs(F-np.rint(F/f0)*f0)>f0*.23;row={};fund=P[abs(F-f0)<f0*.23].sum()
  for lo,hi in [(400,1600),(1600,4000),(4000,6500),(6500,10000),(10000,14000),(14000,16000),(16000,17000),(17000,20000)]:
   mask=(F>=lo)&(F<hi);energy=P[mask].sum();harm=P[mask&~off].sum(axis=0);noise=P[mask&off].sum(axis=0)
   row[str(lo)+'_'+str(hi)]={'mid_off_fraction_of_band':float(noise[0]/energy),'side_off_fraction_of_band':float(noise[1]/energy),'mid_off_power_relative_to_fundamental':float(noise[0]/fund),'side_off_power_relative_to_fundamental':float(noise[1]/fund),'mid_harmonic_power_relative_to_fundamental':float(harm[0]/fund),'side_harmonic_power_relative_to_fundamental':float(harm[1]/fund),'harmonic_side_mid_power_db':float(10*np.log10(harm[1]/harm[0])),'off_side_mid_power_db':float(10*np.log10(noise[1]/noise[0]))}
  rows.append(row)
 results[name]={band:{key:float(np.mean([row[band][key] for row in rows])) for key in rows[0][band]} for band in rows[0]}
print(json.dumps({'description':'Nominal-mask auxiliary analysis; modulation/drift/transition/codec contamination included, not a hiss or similarity score.','results':results},indent=2),flush=True)
