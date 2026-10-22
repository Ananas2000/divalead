"""Signed harmonic and stereo residuals from actual exported audio, assessment only."""
from pathlib import Path
import json,os,sys
import numpy as np
import soundfile as sf

root=Path(sys.argv[2]);root.mkdir(parents=True,exist_ok=True)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(root/'assessment')
from fl20_objective import FeaturesOriginal,a

candidate=json.loads(Path(sys.argv[1]).read_text())
audio=Path(candidate['recorded_audio']);raw,sr=sf.read(audio)
assert sr==48000 and raw.ndim==2 and raw.shape[1]==2
edit=a.h.edit_aligned(a.h.align_with_pdc(raw,dict(alignment_frames=819),latency=0))
harmonics=a.h.harmonics(edit);reference=a.h.HT
power,carriers,bounds=a.powers(edit)
errors=10*np.log10(np.maximum(power,1e-15)/np.maximum(a.TP,1e-15))
signed=10*np.log10(np.maximum(harmonics,1e-12)/np.maximum(reference,1e-12))
features=FeaturesOriginal();r=features.residual(raw[:288000])
active=np.r_[np.arange(1,64041),np.arange(112022,176064)]

def spatial(x):
    z=x[active];mid=z.mean(axis=1);side=(z[:,0]-z[:,1])/2
    return dict(left_right_RMS_dB=float(10*np.log10(np.mean(z[:,0]**2)/np.mean(z[:,1]**2))),
                side_to_mid_RMS_dB=float(10*np.log10(np.mean(side**2)/np.mean(mid**2))),
                correlation=float(np.corrcoef(z.T)[0,1]))

report=dict(candidate=str(Path(sys.argv[1])),actual_audio=str(audio),
            only_three_held_notes=True,original_reference_match_reached=False,
            definition='Signed physical residuals; neither percentage similarity nor a listening judgement.',
            mean_harmonic_error_dB=np.mean(signed,axis=0).tolist(),
            harmonic_error_by_window_dB=signed.tolist(),
            band_signed_mean_dB=np.mean(errors,axis=0).tolist(),bands_Hz=a.BANDS,
            band_signed_columns=['harmonic_mid','harmonic_side','off_harmonic_mid','off_harmonic_side'],
            spatial=dict(reference=spatial(a.REF),candidate=spatial(edit)),
            assessment=features.local.last)
(root/'SIGNED_RESIDUALS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(spatial=report['spatial'],mean_harmonic_error_dB=report['mean_harmonic_error_dB'],
                     band_signed_mean_dB=report['band_signed_mean_dB']),indent=2))
