from pathlib import Path
import sys,json,numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;A=R/'proof/analysis';sys.path.insert(0,str(A))
from independent_spectral_ms import spectral_ms
c=json.loads((A/'spectral_model.json').read_text());actual=sf.read(R/'proof/actual-Windows.wav')[0];raw=sf.read(R/'source-base/Diva_source.wav')[0]
kw=dict(sigma=c['mask_sigma'],key_quadratic=c['key_quadratic'],key_slopes=c['key_slopes'],phase_angles=c['common_phase_radians'],hf_parameters=c['hf_matrix_parameters'],hf_anchors=c['hf_matrix_anchors_Hz'],upper_rolloff=c['upper_rolloff_Hz'],harmonic_gain=c['harmonic_gain_parameters'],gain_orders=c['harmonic_gain_orders'],hf_sigma=c['hf_mask_sigma'],phase_key_slopes=c['common_phase_key_slopes'],phase_key_quadratic=c['common_phase_key_quadratic'],core_anchors=c['anchors_Hz'],adaptive_dynamic=c['dynamic_harmonic_parameters'],adaptive_stereo=c['stereo_harmonic_parameters'],final_stereo_balance=c['final_stereo_balance'],fine_phase=c['fine_phase_harmonic_parameters'])
errors={}
for n,tol in [('NEW-independent-base-pdc.wav',3e-7),('Diva_before_spectral.wav',2e-7)]:
 y,extra=spectral_ms(sf.read(R/'source-base'/n)[0],raw,48000,8320,c['parameters'],**kw);error=float(np.max(np.abs(actual[extra:]-y[:-extra])));assert error<tol;errors[n]=error
for line in (R/'SHA256SUMS.txt').read_text().splitlines():
 import hashlib
 sha,name=line.split('  ',1);assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
print(json.dumps(dict(full_matching_own_NEW_and_fixture_pass=True,errors=errors,match_reached=False)))
