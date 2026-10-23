from pathlib import Path
import csv,json
import numpy as np
from win_vst3 import D,WinVST3
ROOT=D/'ZL-high-band-dynamics-response-audit';ROOT.mkdir(exist_ok=False);ids={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
c=WinVST3('ZL-high-band-gate-unit-probe')
try:
 c.set(ids['Auto Gain'],0);c.set(ids['Lookahead'],0);c.set(ids['Filter Structure'],0);c.set(ids['Filter Status20'],1);c.set(ids['Filter Type20'],0);c.set(ids['Order20'],1/6);c.set(ids['Dynamic ON20'],1);c.set(ids['Dynamic Learn20'],0);c.set(ids['Dynamic Relative20'],0)
 for title,value in [('Freq20',1000),('Q20',.7),('Side Freq20',1000),('Side Q20',.7),('Gain20',-6),('Target Gain20',0),('Threshold (dB)20',-24),('Attack20',1),('Release20',30)]:c.text(ids[title],str(value))
 c.save(ROOT/'ACTUAL_PROBE_COMPONENT.bin');results=[]
 for level in [-60,-48,-36,-24,-12,-6]:
  t=np.arange(48000)/48000;s=np.sin(2*np.pi*1000*t)*10**(level/20);x=np.c_[s,s].astype('float32');y,status=c.render(x);ratio=float(20*np.log10(np.sqrt(np.mean(y[-12000:]**2))/np.sqrt(np.mean(x[-12000:]**2))));results.append(dict(input_peak_dBFS=level,measured_gain_dB=ratio,status=status))
 assert results[0]['measured_gain_dB']<-5 and results[-1]['measured_gain_dB']>-1,results;assert c.latency()==0
 proof=dict(actual_official_Windows_VST3=True,static_gain_dB=-6,target_gain_dB=0,threshold_dB=-24,low_level_band_attenuated_high_level_band_restored=True,declared_PDC_frames=0,measurements=results)
 (ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:c.close()
