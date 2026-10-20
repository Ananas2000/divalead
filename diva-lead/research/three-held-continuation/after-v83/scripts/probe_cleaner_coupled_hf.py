"""Coupled existing off-harmonic/harmonic HF proposals, fresh carrier scoring."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
s=(R/'probe_cleaner_offharmonic_hf.py').read_text().split('\nrows=[];best=None')[0]
s=s.replace("'pw5190-verified-live-main-0005-hf'","'pw5190-verified-live-balance-0005-balance42'").replace('/tmp/divalead-cleaner-offharmonic-hf','/tmp/divalead-cleaner-coupled-hf')
exec(compile(s,'coupled_HF_capture','exec'),globals())
rows=[];best=None
for attenuation in [.008,.025,.06]:
 for brightness in [-.003,.003,.008,.02]:
  hf=base.copy();hf[1]-=attenuation*shape
  for k in [6,7]:hf[k]+=brightness*shape
  y=render(hf);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=12416));path=V/'probe-edit.wav';sf.write(path,edit,48000,subtype='DOUBLE')
  measured=a.score(dict(id=str(attenuation)+'-'+str(brightness),canonical_path=str(path),aliases=[]));m=measured['metrics'];tone=sum(W[k]*m[k]/scales[k] for k in W);std=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS)
  feasible=all(m[k]<=anchor['metrics'][k]*limit for k,limit in choice['guard_limits'].items()) and measured['diagnostics']['crest_RMS_db']<=choice['fixed_crest_cap_dB'] and std<=anchor['score']*1.0001 and np.max(abs(y))<.99
  row=dict(off_side_attenuation=attenuation,harmonic_mid_side_brightness=brightness,tone_score=tone,standard_score=std,metrics=m,crest_RMS_dB=measured['diagnostics']['crest_RMS_db'],all_original_numeric_guards_passed=bool(feasible),fresh_carriers_refitted=True,accepted=False,requires_full_actual_proof=True,match_reached=False);rows.append(row);print('COUPLED_HF_GRID',attenuation,brightness,tone,m['upper_off'],bool(feasible),flush=True)
  if feasible and tone<report['tone_score']-1e-6 and m['upper_off']<report['metrics']['upper_off'] and (best is None or tone<best['weighted_score']):
   best=dict(choice,hf_matrix_parameters=hf.ravel().tolist(),HF_offsets=(hf-base).ravel().tolist(),weighted_score=tone,metrics=m,standard_weighted_score=std,feasible_search_guards=True,cleaner_existing_HF_coupled_grid=True,fresh_carriers_refitted=True)
out=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_validation=str(S/'validation.json'),independent_zero_actual_max_error=error,unchanged_original_quality_limits=True,all_trials=rows,accepted=False,match_reached=False)
(R/'cleaner-coupled-hf-grid-result.json').write_text(json.dumps(out,indent=2)+'\n')
if best is not None:
 F=R/'cleaner-coupled-hf-numeric';F.mkdir(exist_ok=False);(F/'best.json').write_text(json.dumps(best,indent=2)+'\n');(F/'history.json').write_text(json.dumps([dict(weighted_score=report['tone_score']),best],indent=2)+'\n');print('NUMERIC_IMPROVEMENT_REQUIRES_FULL_FRESH_PROOF',F,flush=True)
else:print('NO_STRICTLY_BETTER_CLEANER_COUPLED_POINT; KEEP_PROVED_BEST',flush=True)
