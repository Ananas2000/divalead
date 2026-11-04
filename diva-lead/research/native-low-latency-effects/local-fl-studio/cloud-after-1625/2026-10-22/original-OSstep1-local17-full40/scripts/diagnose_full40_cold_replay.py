from pathlib import Path
import json
import numpy as np,soundfile as sf
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-recovered-OS17-point-new12-20261104');T=Path('/tmp/divalead-full40-cold-diagnostic');T.mkdir();raw,sr=sf.read(R/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);want,_=sf.read(R/'CANDIDATE_00.wav',dtype='float32',always_2d=True);pre0=out0=None;errors=[]
for k in range(3):
 p=WinVST3('W40diag-P-'+str(k));z=WinVST3('W40diag-Z-'+str(k));c=NativePostTrim(T/'buffers','W40diag-T-'+str(k),cleanup_on_close=True)
 try:
  p.load(R/'CANDIDATE_PRIMARY.bin');z.load(R/'CANDIDATE_POST.bin');c.load(R/'CANDIDATE_NATIVE_TRIM.bin');mid,_=p.render(raw);pre,_=z.render(mid);out=c.render(pre)
  if k==0:pre0=pre.copy();out0=out.copy();sf.write(T/'COLD_BEFORE_TRIM.wav',pre,sr,subtype='FLOAT');sf.write(T/'COLD_FULL.wav',out,sr,subtype='FLOAT')
  np.testing.assert_allclose(pre,pre0,rtol=8*np.finfo(np.float32).eps,atol=1e-12);np.testing.assert_allclose(out,out0,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
  e=float(abs(out-want).max());assert e<=2e-7;errors.append(dict(before_trim_vs_first_cold=float(abs(pre-pre0).max()),full_vs_first_cold=float(abs(out-out0).max()),full_vs_warm_validation=e,warm_validation_samplewise_relative_gate_passed=bool(np.all(abs(out-want)<=8*np.finfo(np.float32).eps*abs(want)+1e-12)),actual_ZL_PDC=p.latency()+z.latency()))
 finally:p.close();z.close();c.close()
d=dict(three_independent_actual_cold_cascades=errors,unchanged_ZL_relative_tolerance_eps=8,unchanged_ZL_absolute_tolerance=1e-12,unchanged_native_full_absolute_tolerance=2e-7,hot_vs_cold_diagnostic_not_cold_reproducibility_gate=True,reference_quality_gates_unchanged=True,not_adopted=True);(V/'BUILD40_COLD_REPLAY_DIAGNOSIS.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d),flush=True)
