"""Fit42 existing final-stereo coefficients of a complete verified model/source."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
if os.environ.get('DIVALEAD_CPU_SET'):os.sched_setaffinity(0,{int(v) for v in os.environ['DIVALEAD_CPU_SET'].split(',')})
import ast,json,time,sys,copy,hashlib,multiprocessing as mp
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
RESEARCH=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(RESEARCH))
import refine_selected53 as joint
W=RESEARCH;REPO=joint.REPO;SR=48000;current=W/'CURRENT_RESEARCH_MODEL.json';default_model=W/json.loads(current.read_text())['model_directory'];B=Path(os.environ.get('DIVALEAD_MODEL_BASE',str(default_model)));V=joint.analysis.WORK/('complete-balance42-'+B.name);V.mkdir(exist_ok=True)
manifest=json.loads((B/'source_manifest.json').read_text())
for k in ['source_preset','source_WAV','before_spectral_WAV']:assert hashlib.sha256((REPO/manifest[k]).read_bytes()).hexdigest()==manifest[k+'_SHA256']
source_fixture=sf.read(REPO/manifest['source_WAV'])[0];before_fixture=sf.read(REPO/manifest['before_spectral_WAV'])[0];frozen_cfg=json.loads((B/'analysis/spectral_model.json').read_text());frozen_actual=sf.read(B/'REFERENCE_EDIT_WIP.wav')[0];seed=frozen_cfg
from fine_phase_model import extend_prefix,spectral_source,fine_phase_curve,carry_fine_phase
tree=ast.parse((REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets)).replace('v55','v53')
prefix=prefix.replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')')
prefix=prefix.replace("cfg=json.loads((R/'analysis/spectral_model.json').read_text())",'cfg=copy.deepcopy(frozen_cfg)').replace("actual=sf.read(R/'Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0]",'actual=frozen_actual').replace("dry=sf.read(R/'Diva_v53_VIDEO_DIVA_ONLY.wav')[0]",'dry=source_fixture').replace("before=sf.read(R/'Diva_v53_BEFORE_SPECTRAL.wav')[0]",'before=before_fixture')
prefix=extend_prefix(prefix,RESEARCH)
ns={'__name__':'complete_HF_capture','Path':Path,'copy':copy,'frozen_cfg':frozen_cfg,'frozen_actual':frozen_actual,'source_fixture':source_fixture,'before_fixture':before_fixture};exec(compile(prefix,'complete_HF_capture','exec'),ns)
cfg=ns['cfg'];actual=frozen_actual
power_render=ns['render'];base_balance=copy.deepcopy(cfg['final_stereo_balance']);fields=['log_side_scale','mid_to_side_real','mid_to_side_imag'];base_coeff=np.array([base_balance[k] for k in fields]);active_indices=np.delete(np.arange(15),7);assert base_coeff.shape==(3,15) and np.all(base_coeff[:,7]==0)
def changed(p):
 balance=copy.deepcopy(base_balance);values=base_coeff.copy();values[:,active_indices]+=np.asarray(p).reshape(3,14)
 for k,row in zip(fields,values):balance[k]=row.tolist()
 return balance
def render(p):
 balance=changed(p);curves=[np.interp(np.log(np.maximum(ns['f'],1)),np.log(balance['anchors_Hz']),np.r_[0,balance[k],0])[:,None] for k in fields];ns['scale']=np.exp(curves[0]);ns['mix']=curves[1]+1j*curves[2]
 return power_render(np.zeros(69))
neutral_full,neutral=render(np.zeros(42));np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7)
fullns={'__name__':'selected53_stereo_full_independent'};exec(compile(spectral_source(RESEARCH),'selected53_stereo_full_independent','exec'),fullns)
checks=[]
for sign in [-1,1]:
 p=np.random.default_rng(419+sign).uniform(-.005,.005,42);args=dict(ns['kw'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],fine_phase=cfg['fine_phase_harmonic_parameters'],final_stereo_balance=changed(p));direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],48000,8320,cfg['parameters'],**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);checks.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-actual))),two_nonzero_full_SciPy_errors=checks,baseline=str(B),only_existing42_final_balance_values_changed=True,match_reached=False),indent=2));print('THREE_BALANCE42_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS',checks,flush=True)
from compare_all import wave as crest_definition, TC as target_crest
ANCHOR=json.loads(Path('/workspace/divalead-work/three-held-continuation/baseline/validation.json').read_text())
FIXED_CREST_CAP=ANCHOR['crest_RMS_dB']*1.001
NUMERICAL_CREST_CAP=FIXED_CREST_CAP-1e-5
crest_windows=[(int(a*48000),int(b*48000)) for a,b,_ in crest_definition.WINDOWS]
def crest_values(edit):
 return np.asarray([20*np.log10(np.max(abs(edit[a:b]))/np.sqrt(np.mean(edit[a:b]*edit[a:b]))) for a,b in crest_windows])
def crest_error(edit):return float(np.sqrt(np.mean((crest_values(edit)-target_crest)**2)))
for label,edit in [('zero',neutral),('nonzero',render(np.random.default_rng(1781).uniform(-.005,.005,42))[1])]:
 np.testing.assert_array_equal(crest_values(edit),crest_definition.features(edit)[2])
print('EXACT_CANONICAL_CREST_PARITY_ZERO_AND_NONZERO_PASS',crest_error(neutral),flush=True)
fresh_powers,joint.carriers,boundaries=joint.analysis.powers(neutral)
assert not any(boundaries)
np.testing.assert_array_equal(joint.fixed_powers(neutral),fresh_powers)
actual_baseline=json.loads(Path(os.environ.get('DIVALEAD_BASELINE_REPORT',str(B/'validation.json'))).read_text())
assert abs(joint.score(joint.metrics(neutral))-actual_baseline['score'])<1e-6
TONE_WEIGHTS=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
base=joint.metrics(neutral);score=lambda m:sum(TONE_WEIGHTS[k]*m[k]/joint.scales[k] for k in TONE_WEIGHTS)
lower=np.full(42,-.03);upper=-lower
guards=dict(H24=1.001,upper_harm=1.001,upper_off=1.001,low_harm=1.002,ERB=1.001,relative_phase=1.002,whole=1.001,envelope=1.001,body=1.002,stereo_phase=1.002,stereo_balance=1.002)
from search_global_guards import repair_near_feasible_rows
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));con=np.r_[[limit-m[k]/ANCHOR['metrics'][k] for k,limit in guards.items()],.99-peak,1-crest_error(e)/NUMERICAL_CREST_CAP,1.0001-joint.score(m)/ANCHOR['score']]
 keys=['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','parameters','key_slopes','key_quadratic','dynamic_harmonic_parameters','stereo_harmonic_parameters']
 row=dict(metrics=m,weighted_score=score(m),peak=peak,feasible_search_guards=bool(np.min(con)>=-1e-12),stereo_balance_offsets=p.tolist(),fine_phase_harmonic_parameters=cfg['fine_phase_harmonic_parameters'],final_stereo_balance=changed(p),**{k:cfg[k] for k in keys},baseline_model_SHA256=baseline_hash,source_manifest=manifest,guard_limits=guards,only_existing42_final_stereo_values=True,original_common_weights_unchanged=False,tone_focused_weights=TONE_WEIGHTS,standard_weighted_score=joint.score(m),user_selected_three_baseline=True,crest_RMS_dB=crest_error(e),fixed_crest_cap_dB=FIXED_CREST_CAP,all_DSP_tolerances_unchanged=True,match_reached=False)
 return score(m)+.0001*float(np.mean(p*p)),row,con
baseline_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
rows=[];last={};best=np.inf;derivatives={}
def probe(p):
 global best
 if last.get('key')!=tuple(p):
  obj,row,con=compute(p);row.update(center=len(rows),objective=obj,minimum_constraint=float(np.min(con)));rows.append(row);last.update(key=tuple(p),result=(obj,row,con));tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if np.min(con)>=-1e-12 and row['weighted_score']<best:
   best=row['weighted_score'];tmp=V/'best.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(V/'best-edit.wav',e,48000,subtype='FLOAT')
  print('THREE_BALANCE42_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'constraintMin',float(np.min(con)),flush=True)
 return last['result']
def derive(p):
 key=tuple(p)
 if derivatives.get('key')!=key:
  center=probe(p);points=[];steps=[]
  for j in range(42):
   step=.00025 if p[j]+.00025<=upper[j] else -.00025;pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
  values=list(pool.map(compute,points));derivatives.update(key=key,gradient=np.array([(v[0]-center[0])/s for v,s in zip(values,steps)]),jac=np.array([(v[2]-center[2])/s for v,s in zip(values,steps)]).T)
 return derivatives
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(42)
 if '--check-only' in sys.argv:
  result=compute(initial);assert np.min(result[2])>=-1e-12;assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];assert result[1]['stereo_harmonic_parameters']==cfg['stereo_harmonic_parameters'];assert result[1].get('fine_phase_harmonic_parameters')==cfg.get('fine_phase_harmonic_parameters');print('COMPLETE_MODEL_HF_CHECKED',B.name,flush=True);raise SystemExit(0)
 path=V/'best.json'
 if path.exists():
  row=json.loads(path.read_text())
  if row.get('baseline_model_SHA256')==baseline_hash:
   candidate=np.asarray(row['stereo_balance_offsets']);value=compute(candidate)
   if np.min(value[2])>=-1e-12 and value[0]<compute(initial)[0]:
    (V/'resume-origin.json').write_text(json.dumps(row,indent=2));initial=candidate.copy()
  else:
   archive=V/('previous-model-'+str(row.get('baseline_model_SHA256','unknown'))[:16]+'-best.json');archive.write_text(json.dumps(row,indent=2))
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(lambda p:probe(p)[0],initial,jac=lambda p:derive(p)['gradient'],method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:probe(p)[2],jac=lambda p:derive(p)['jac'])],options=dict(maxiter=int(os.environ.get('DIVALEAD_MAXITER','45')),ftol=1e-9,disp=False))
 repair=repair_near_feasible_rows(rows,best,initial,'stereo_balance_offsets',compute,probe)
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(near_feasible_repair=repair,status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),elapsed_seconds=time.monotonic()-start,source_base=B.name,source_hashes_checked=True,baseline_model_SHA256=baseline_hash,existing42_final_stereo_values_only=True,method='SLSQP with shared finite-difference Jacobians; tone objective and user-selected three-held guards',H24_chosen_three_cap=ANCHOR['metrics']['H24']*guards['H24'],new_source_requires_its_matching_independent_prebase=True,match_reached=False),indent=2));print('THREE_BALANCE42_DONE',fit.status,fit.message,flush=True)
