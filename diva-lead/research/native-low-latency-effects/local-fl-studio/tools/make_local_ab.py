"""Listening comparison only: original, v83, actual FL04, actual FL05.
RMS matching is applied only to this AB file, never to synth/DSP candidates.
"""
from pathlib import Path
import json
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent.parent;S=ROOT/'sessions/2026-10-22'
kit=ROOT/'divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP'
ref,sr=sf.read(kit/'Diva_original_lead_reference.wav',always_2d=True)
old,sr2=sf.read(kit/'AB_ORIGINAL_V83_NATIVE_WIP.wav',always_2d=True);assert sr==sr2==48000
levels=json.loads((kit/'verification/AB_LEVELS.json').read_text());start=round(levels['starts_seconds'][1]*sr)
v83=old[start:start+len(ref)]/levels['common_peak_safety_gain']/levels['per_clip_RMS_gains'][1]
clips=[ref,v83]+[sf.read(S/'assessment'/(name+'_REFERENCE_EDIT.wav'),always_2d=True)[0]for name in ('FL_NATIVE_04_CALIBRATED','FL_NATIVE_05_MODDEPTH')]
assert all(x.shape==ref.shape for x in clips)
target=np.sqrt(np.mean(ref*ref));gains=[float(target/np.sqrt(np.mean(x*x)))for x in clips];matched=[x*g for x,g in zip(clips,gains)]
safety=min(1.,.98/max(float(abs(x).max())for x in matched));gap=np.zeros((24000,2));parts=[]
for k,x in enumerate(matched):
    if k:parts.append(gap)
    parts.append(x*safety)
y=np.concatenate(parts)
sf.write(S/'AB_ORIGINAL_V83_FL04_FL05.wav',y,sr,subtype='PCM_24')
pcm,_=sf.read(S/'AB_ORIGINAL_V83_FL04_FL05.wav',dtype='int32')
sf.write(S/'AB_ORIGINAL_V83_FL04_FL05.flac',pcm,sr,format='FLAC',subtype='PCM_24')
report=dict(order=['original','v83','FL04','FL05'],starts_seconds=[k*(len(ref)/sr+.5)for k in range(4)],per_clip_RMS_gains=gains,common_peak_safety_gain=safety,only_AB_is_gain_matched=True,flac_is_lossless=True,reference_used_in_candidate_synthesis=False)
(S/'AB_LEVELS_LOCAL.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
