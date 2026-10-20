"""Small existing-HF grid, scored with freshly refitted carriers, never accepted on prediction."""
from pathlib import Path
import datetime,json,os,sys
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;S=R/'pw5190-verified-live-main-0005-hf';B=R/'source-pw5190-basis'
V=Path('/tmp/divalead-cleaner-offharmonic-hf');V.mkdir(exist_ok=False);(V/'scores').mkdir()
sys.path.insert(0,str(Path('/workspace/divalead/diva-lead/research/repository-selection')));import compare_all as a
sys.path.insert(0,str(S/'analysis'));from independent_spectral_ms import spectral_ms
a.WORK=V;cfg=json.loads((S/'analysis/spectral_model.json').read_text());report=json.loads((S/'validation.json').read_text());choice=json.loads((S/'numeric-choice.json').read_text())
raw=sf.read(B/'Diva_source.wav')[0];before=sf.read(B/'Diva_before_spectral.wav')[0];actual=sf.read(S/'actual-Windows.wav')[0]
scales=json.loads(Path('/workspace/divalead/diva-lead/research/repository-selection/ranking.json').read_text())['normalizing_errors'];W=choice['tone_focused_weights'];anchor=json.loads((R/'baseline/validation.json').read_text())
def render(hf):
 kw=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=hf.ravel().tolist(),hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])
 y,extra=spectral_ms(before,raw,48000,8320,cfg['parameters'],**kw)
 return np.pad(y[:-extra],((extra,0),(0,0)))
base=np.asarray(cfg['hf_matrix_parameters']).reshape(10,10);neutral=render(base);error=float(np.max(abs(actual-neutral)));assert error<2e-7,error
freq=np.asarray(cfg['hf_matrix_anchors_Hz'][1:-1]);shape=np.interp(freq,[2500,3500,4500,6500,9000,11000,13500,16400],[0,0,.25,1,1,.5,0,0])
rows=[];best=None
for mode in ['mid-and-side','mid-only','side-only']:
 for depth in [.002,.008,.025,.06]:
  hf=base.copy()
  for row in ([0,1] if mode=='mid-and-side' else [0] if mode=='mid-only' else [1]):hf[row]-=depth*shape
  y=render(hf);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=12416));path=V/'probe-edit.wav';sf.write(path,edit,48000,subtype='DOUBLE')
  measured=a.score(dict(id=mode+'-'+str(depth),canonical_path=str(path),aliases=[]));m=measured['metrics'];tone=sum(W[k]*m[k]/scales[k] for k in W);std=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS)
  feasible=all(m[k]<=anchor['metrics'][k]*limit for k,limit in choice['guard_limits'].items()) and measured['diagnostics']['crest_RMS_db']<=choice['fixed_crest_cap_dB'] and std<=anchor['score']*1.0001 and np.max(abs(y))<.99
  row=dict(mode=mode,depth=depth,tone_score=tone,standard_score=std,metrics=m,crest_RMS_dB=measured['diagnostics']['crest_RMS_db'],all_original_numeric_guards_passed=bool(feasible),fresh_carriers_refitted=True,accepted=False,requires_fresh_Diva_Windows_own_NEW_and_all12_cases=True,match_reached=False);rows.append(row);print('CLEANER_HF_GRID',mode,depth,tone,m['upper_off'],bool(feasible),flush=True)
  if feasible and tone<report['tone_score']-1e-6 and m['upper_off']<report['metrics']['upper_off'] and (best is None or tone<best['weighted_score']):
   best=dict(choice,hf_matrix_parameters=hf.ravel().tolist(),weighted_score=tone,metrics=m,standard_weighted_score=std,feasible_search_guards=True,cleaner_existing_HF_grid=True,fresh_carriers_refitted=True)
out=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_validation=str(S/'validation.json'),independent_zero_actual_max_error=error,unchanged_original_quality_limits=True,all_trials=rows,accepted=False,match_reached=False)
(R/'cleaner-offharmonic-hf-grid-result.json').write_text(json.dumps(out,indent=2)+'\n')
if best is not None:
 F=R/'cleaner-offharmonic-hf-numeric';F.mkdir(exist_ok=False);(F/'best.json').write_text(json.dumps(best,indent=2)+'\n');(F/'history.json').write_text(json.dumps([dict(weighted_score=report['tone_score']),best],indent=2)+'\n');print('NUMERIC_IMPROVEMENT_REQUIRES_FULL_FRESH_PROOF',F,flush=True)
else:print('NO_STRICTLY_BETTER_CLEANER_GRID_POINT; KEEP_PROVED_BEST',flush=True)
