"""Three directions within existing HF coefficients, using full fresh-carrier scoring."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
s=(R/'probe_cleaner_offharmonic_hf.py').read_text().split('\nrows=[];best=None')[0]
s=s.replace("'pw5190-verified-live-main-0005-hf'","'pw5190-verified-live-balance-0005-balance42'").replace('/tmp/divalead-cleaner-offharmonic-hf','/tmp/divalead-cleaner-coupled-optimization')
exec(compile(s,'coupled_optimization_capture','exec'),globals())
from scipy.optimize import minimize
rows=[];best=None;cached={};crest_cap=choice['fixed_crest_cap_dB']
def compute(p):
 global best
 key=tuple(p)
 if key in cached:return cached[key]
 hf=base.copy();hf[0]+=p[0]*shape;hf[1]+=p[1]*shape
 for k in [6,7]:hf[k]+=p[2]*shape
 y=render(hf);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=12416));path=V/'probe-edit.wav';sf.write(path,edit,48000,subtype='DOUBLE')
 measured=a.score(dict(id='center-'+str(len(rows)),canonical_path=str(path),aliases=[]));m=measured['metrics'];tone=sum(W[k]*m[k]/scales[k] for k in W);std=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS);crest=measured['diagnostics']['crest_RMS_db'];peak=float(np.max(abs(y)))
 con=np.r_[[limit-m[k]/anchor['metrics'][k] for k,limit in choice['guard_limits'].items()],.99-peak,1-crest/crest_cap,1.0001-std/anchor['score'],1-m['upper_off']/report['metrics']['upper_off']]
 row=dict(offsets=list(p),tone_score=tone,standard_score=std,metrics=m,crest_RMS_dB=crest,minimum_constraint=float(np.min(con)),all_original_numeric_guards_passed=bool(np.min(con)>=-1e-12),fresh_carriers_refitted=True,accepted=False,requires_full_actual_proof=True,match_reached=False);rows.append(row)
 if np.min(con)>=-1e-12 and tone<report['tone_score']-1e-6 and m['upper_off']<report['metrics']['upper_off'] and (best is None or tone<best['weighted_score']):best=dict(choice,hf_matrix_parameters=hf.ravel().tolist(),HF_offsets=(hf-base).ravel().tolist(),weighted_score=tone,metrics=m,standard_weighted_score=std,feasible_search_guards=True,cleaner_existing_HF_three_direction_search=True,fresh_carriers_refitted=True)
 value=tone+.05*m['upper_off']/scales['upper_off'];cached[key]=(value,con);print('FRESH_CARRIER_CLEANER_CENTER',len(rows),tone,m['upper_off'],float(np.min(con)),flush=True);return value,con
fit=minimize(lambda p:compute(p)[0],np.zeros(3),method='SLSQP',bounds=[(-.06,.06)]*3,constraints=[dict(type='ineq',fun=lambda p:compute(p)[1])],options=dict(maxiter=18,ftol=1e-10,eps=2e-5))
out=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_validation=str(S/'validation.json'),independent_zero_actual_max_error=error,unchanged_original_quality_limits=True,extra_noise_constraint=True,objective='Original tone error plus0.05 normalized upper-off error; acceptance still requires original tone improvement and lower upper-off error.',solver=dict(status=int(fit.status),message=str(fit.message),nit=int(fit.nit)),all_trials=rows,accepted=False,match_reached=False)
(R/'cleaner-coupled-optimization-result.json').write_text(json.dumps(out,indent=2)+'\n')
if best is not None:
 F=R/'cleaner-coupled-optimization-numeric';F.mkdir(exist_ok=False);(F/'best.json').write_text(json.dumps(best,indent=2)+'\n');(F/'history.json').write_text(json.dumps([dict(weighted_score=report['tone_score']),best],indent=2)+'\n');print('NUMERIC_IMPROVEMENT_REQUIRES_FULL_FRESH_PROOF',F,flush=True)
else:print('NO_STRICTLY_BETTER_CLEANER_OPTIMIZED_POINT; KEEP_PROVED_BEST',flush=True)
