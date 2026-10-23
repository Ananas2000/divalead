"""Signed Mid/Side harmonic and between-harmonic errors, analysis only."""
from pathlib import Path
import datetime,hashlib,json,os
import numpy as np
import soundfile as sf
D=Path(__file__).resolve().parent;ROOT=D/'ZL-current-signed-band-diagnostics-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
import fl20_objective as objective
a=objective.a;best=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text())
sources=[('ZL15',D.parent/'FL20_ZL_15_WIP/NATIVE_FULL_180BPM_WIP.wav'),('ZL16',D.parent/'FL20_ZL_16_WIP/NATIVE_FULL_180BPM_WIP.wav'),('current_private_best',Path(best['recorded_audio']))]
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),definition='16 fixed stable note windows. Each window uses actual estimated fundamental. Energies normalized to total Mid+Side fundamental, not arbitrary per-band gains. Positive dB means excess relative to original; negative dB means deficit. Between-harmonic energy includes modulation, transient leakage and reverb; it is not a pure noise measurement.',original_reference_SHA256=hashlib.sha256(Path('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav').read_bytes()).hexdigest(),only_three_held_notes=True,reference_match_reached=False,candidates=[])
for label,path in sources:
 y,sr=sf.read(path,dtype='float64',always_2d=True);assert sr==48000
 edit=a.h.edit_aligned(a.h.align_with_pdc(y[:288000],dict(alignment_frames=819),latency=0));p,carriers,bounds=a.powers(edit);errors=10*np.log10(np.maximum(p,1e-15)/np.maximum(a.TP,1e-15));rows=[]
 for band,(lo,hi)in enumerate(a.BANDS):
  means=np.mean(errors[:,band],axis=0);rms=np.sqrt(np.mean(errors[:,band]**2,axis=0))
  rows.append(dict(band_Hz=[lo,hi],signed_mean_dB=dict(zip(['Mid_harmonic','Side_harmonic','Mid_between_harmonics','Side_between_harmonics'],map(float,means))),RMS_error_dB=dict(zip(['Mid_harmonic','Side_harmonic','Mid_between_harmonics','Side_between_harmonics'],map(float,rms)))))
 row=dict(label=label,path=str(path),audio_file_SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),carrier_at_bounds_windows=[i for i,b in enumerate(bounds)if b],bands=rows)
 report['candidates'].append(row)
 (ROOT/(label+'-signed-bands.json')).write_text(json.dumps(row,indent=2)+'\n')
 print(label,[(r['band_Hz'],{k:round(v,2)for k,v in r['signed_mean_dB'].items()})for r in rows[4:]],flush=True)
(ROOT/'SIGNED_ORIGINAL_REFERENCE_BAND_RESIDUALS.json').write_text(json.dumps(report,indent=2)+'\n')
