"""Signed harmonic and Mid/Side band errors for choosing the next physical tests."""
from pathlib import Path
import json,os,sys
import numpy as np
import soundfile as sf
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(B/'native-signed-spectral-error-assessment')
from fl20_objective import a
candidate=json.loads(Path(sys.argv[1]).read_text());raw=Path(candidate['recorded_audio']);y,sr=sf.read(raw);assert sr==48000
x=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0))
power,carriers,_=a.powers(x);error=10*np.log10(np.maximum(power,1e-15)/np.maximum(a.TP,1e-15))
harmonics=a.h.harmonic_errors(x)['harmonic_errors_db'];weights=np.maximum(a.h.HT,1e-5)**.5;weights[:,0]=0;weights/=weights.sum()
contributions=np.asarray(harmonics)**2*weights;top=[]
for i,k in sorted(np.ndindex(contributions.shape),key=lambda index:contributions[index],reverse=True)[:24]:
 top.append(dict(window_index=i,seconds=list(a.WINDOWS[i][:2]),nominal_Hz=a.WINDOWS[i][2],harmonic_order=k+1,error_dB=harmonics[i][k],weighted_squared_error=contributions[i,k]))
report=dict(candidate_path=sys.argv[1],recorded_audio=str(raw),loss=candidate['loss'],error_sign='Positive = candidate has MORE relative power than original; negative = LESS. Fundamental normalized per window; not an absolute sound-level comparison.',
  band_limits_Hz=a.BANDS,band_error_axes=['window','band','harmonic_MID,harmonic_SIDE,offharmonic_MID,offharmonic_SIDE'],
  signed_band_errors_dB=error.tolist(),mean_signed_band_errors_dB=error.mean(axis=0).tolist(),
  harmonic_errors_dB=harmonics,top_weighted_harmonic_mismatches=top,
  actual_recorded_native_audio=True,reference_match_reached=False,not_a_perceptual_hiss_score=True)
out=Path(sys.argv[2]);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(mean_signed_band_errors_dB=report['mean_signed_band_errors_dB'],top_weighted_harmonic_mismatches=top[:12]),indent=2))
