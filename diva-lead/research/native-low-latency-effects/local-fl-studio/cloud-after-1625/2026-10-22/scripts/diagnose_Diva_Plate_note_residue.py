"""Compare old-note residue on actual archived full native median captures."""
from pathlib import Path
import json,hashlib
import numpy as np
import soundfile as sf
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
D=B/'paired-physical-PlateWet-zero-and-0p1-direct-independent24-01'
reference=Path('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav')
ref,sr=sf.read(reference,dtype='float64');assert sr==48000
windows=json.loads((B/'DRY_DIVA_PLATE_RAW_NOTE_LEAKAGE_DIAGNOSTIC.json').read_text())['rows']
def edit(y):
 z=np.pad(y,((819,0),(0,0)));result=np.zeros((176064,2));result[1:64041]=z[1:64041];result[112022:176064]=z[128007:192049];return result
def ratio(y,start,end,carrier):
 v=y[round(start*48000):round(end*48000)];t=np.arange(len(v))/48000;w=np.hanning(len(v))
 power=lambda frequency:float(np.sum(abs(np.exp(-2j*np.pi*frequency*t)@(v*w[:,None]))**2))
 return float(10*np.log10((power(carrier/2)+1e-30)/(power(carrier)+1e-30)))
paths=[('current_native_control',D/'selection-control.json'),('PlateWet0_full_native',D/'selection-proposal-0.json'),('PlateWet0p1_full_native',D/'selection-proposal-1.json')]
rows=[]
for label,p in paths:
 c=json.loads(p.read_text());audio=Path(c['recorded_audio']);y,rate=sf.read(audio,dtype='float64');assert rate==48000;y=edit(y)
 rows.append(dict(label=label,full_native_mean_loss=c['loss'],recorded_audio=str(audio),WAV_SHA256=hashlib.sha256(audio.read_bytes()).hexdigest(),
   old_half_carrier_relative_dB=[dict(window_seconds=w['window_seconds'],original=ratio(ref,*w['window_seconds'],w['carrier']),actual_native=ratio(y,*w['window_seconds'],w['carrier']))for w in windows]))
report=dict(rows=rows,actual_native_DLL_audio=True,physical_Diva_only_parameter235_changed=True,three_held_notes_ARP_preserved=True,
  criterion='Hann complex projection summed L/R power: carrier/2 relative to nominal carrier; spectral residue diagnostic, not a perceptual hiss score',
  direct_complete_graph_comparison=D.joinpath('completion.json').as_posix(),own_source_specific_EQ_and_controls_refitting_still_required=True,reference_match_reached=False)
for p in [B/'DIVA_PLATE_FULL_NATIVE_NOTE_RESIDUE_DIAGNOSTIC.json',N/'DIVA_PLATE_FULL_NATIVE_NOTE_RESIDUE_DIAGNOSTIC.json']:p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
