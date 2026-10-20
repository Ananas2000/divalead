"""Describe remaining original-reference errors; never substitute for full proof."""
from pathlib import Path
import datetime, hashlib, json, os, sys
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parent
P=Path('/workspace/divalead')
research=P/'diva-lead/research/repository-selection'
sys.path.insert(0,str(research))
import compare_all as common
reference,rate=sf.read(P/'diva-lead/v82-wip/Diva_original_lead_reference.wav')
assert rate==48000 and reference.shape==(176064,2)
assert hashlib.sha256(reference.tobytes()).hexdigest()=='450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c'
bands=[(120,300),(300,800),(800,2000),(2000,3500),(3500,6500),(6500,10000),(10000,14000)]
frequency=np.fft.rfftfreq(len(reference),1/rate)
window=np.hanning(len(reference))[:,None]
def features(wave):
    powers=abs(np.fft.rfft(wave*window,axis=0))**2
    mid=(wave[:,0]+wave[:,1])*.5
    side=(wave[:,0]-wave[:,1])*.5
    return np.asarray([powers[(frequency>=a)&(frequency<b)].sum(axis=0) for a,b in bands]),20*np.log10(np.sqrt(np.mean(side*side)/np.mean(mid*mid))),20*np.log10(np.sqrt(np.mean(wave[:,0]**2)/np.mean(wave[:,1]**2)))
target,target_width,target_balance=features(reference)
rows=[]
for version in ['v81','v82']:
    path=P/('diva-lead/'+version+'-wip/Diva_Lead_'+version+'_REFERENCE_EDIT.wav')
    wave,sr=sf.read(path);assert sr==rate and wave.shape==reference.shape
    wave*=np.sqrt(np.mean(reference*reference)/np.mean(wave*wave))
    powers,width,balance=features(wave)
    harmonic=common.h.harmonic_errors(wave)
    errors=np.asarray(harmonic['harmonic_errors_db'])
    order_error=np.mean(abs(errors),axis=tuple(i for i in range(errors.ndim) if i!=1))
    rows.append(dict(version=version,band_total_excess_dB=(10*np.log10(powers.sum(axis=1)/target.sum(axis=1))).tolist(),band_L_minus_R_excess_vs_original_dB=(10*np.log10(powers[:,0]/powers[:,1])-10*np.log10(target[:,0]/target[:,1])).tolist(),side_to_mid_RMS_dB=float(width),side_to_mid_difference_vs_original_dB=float(width-target_width),L_minus_R_RMS_dB=float(balance),L_minus_R_difference_vs_original_dB=float(balance-target_balance),harmonic_error_abs_mean_by_order_dB=order_error.tolist(),single_common_stereo_RMS_gain=True))
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Diagnostic Hann-windowed whole-fragment spectral bands and stereo RMS; canonical acceptance remains unchanged.',bands_Hz=bands,reference_side_to_mid_RMS_dB=float(target_width),reference_L_minus_R_RMS_dB=float(target_balance),results=rows,subjective_audition_performed=False,match_reached=False)
(R/'post82-residual-band-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
