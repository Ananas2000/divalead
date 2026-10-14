"""Independent probes with only a previously skipped group enabled."""
import ctypes,copy,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
ROOT=Path('/tmp/divalead-group-check');ROOT.mkdir(exist_ok=True)
A=Path(__file__).resolve().parent;sys.path.insert(0,str(A))
from independent_spectral_ms import spectral_ms
cfg=json.loads((A/'spectral_model.json').read_text());rows=[]
with tempfile.TemporaryDirectory(prefix='divalead-group-') as d:
 B=Path(d);shutil.copytree(A,B,dirs_exist_ok=True)
 for selected in [8,22]:
  values=np.zeros(23);values[selected]=.5;dyn=copy.deepcopy(cfg['dynamic_harmonic_parameters']);dyn['group_strengths']=values.tolist()
  s=(A/'spectral_dynamic_settings.h').read_text();s,n=re.subn(r'SMS_DYNAMIC_GROUP_STRENGTH\[23\]=\{[^}]+\}','SMS_DYNAMIC_GROUP_STRENGTH[23]={'+','.join(map(str,values))+'}',s);assert n==1;(B/'spectral_dynamic_settings.h').write_text(s)
  so=B/('probe'+str(selected)+'.so');subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(so),str(B/'spectral_component.c'),'-lm'],check=True)
  lib=ctypes.CDLL(str(so));lib.spectral_component_render.argtypes=[ctypes.c_void_p]*3+[ctypes.c_int]*3
  rate=48000;n=rate*2;t=np.arange(n)/rate;phase=2*np.pi*110*t;raw=.22*np.sin(phase)+.07*np.sin(6*phase+.1)+.04*np.sin(23*phase+.2)
  dry=np.ascontiguousarray(np.stack([raw,raw*.93],axis=1));pd=8320;processed=np.ascontiguousarray(np.pad(dry,((pd,0),(0,0)))[:n]);actual=np.zeros_like(dry);assert lib.spectral_component_render(processed.ctypes.data,dry.ctypes.data,actual.ctypes.data,n,rate,pd)
  kw=dict(key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],core_anchors=cfg['anchors_Hz'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'])
  ind,extra=spectral_ms(processed,dry,rate,pd,cfg['parameters'],adaptive_dynamic=dyn,**kw);np.testing.assert_allclose(actual[extra:],ind[:-extra],rtol=0,atol=2e-10)
  disabled=copy.deepcopy(dyn);disabled['group_strengths']=[0.]*23;neutral,_=spectral_ms(processed,dry,rate,pd,cfg['parameters'],adaptive_dynamic=disabled,**kw);change=float(np.max(abs(ind-neutral)));assert change>1e-5
  rows.append({'only_group_index_enabled':selected,'independent_max_error':float(np.max(abs(actual[extra:]-ind[:-extra]))),'difference_from_all_disabled':change})
(ROOT/'v49-group-activation.json').write_text(json.dumps(rows,indent=2));print('GROUP48_ONLY_LATE_GROUPS_PASS',rows,flush=True)
