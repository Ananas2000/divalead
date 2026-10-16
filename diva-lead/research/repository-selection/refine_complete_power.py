"""Existing69 low-degree harmonic power-target values for a complete verified model/source manifest."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
if os.environ.get('DIVALEAD_CPU_SET'):os.sched_setaffinity(0,{int(v) for v in os.environ['DIVALEAD_CPU_SET'].split(',')})
import ast,json,time,sys,copy,hashlib,multiprocessing as mp
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
RESEARCH=Path(__file__).resolve().parent;sys.path.insert(0,str(RESEARCH))
import refine_selected53 as joint
W=RESEARCH;REPO=joint.REPO;SR=48000;current=W/'CURRENT_RESEARCH_MODEL.json';default_model=W/json.loads(current.read_text())['model_directory'];B=Path(os.environ.get('DIVALEAD_MODEL_BASE',str(default_model)));V=joint.analysis.WORK/('complete-power-'+B.name);V.mkdir(exist_ok=True)
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
render=ns['render'];base_target=np.asarray(cfg['dynamic_harmonic_parameters']['target_logpower_db_polynomial']);neutral_full,neutral=render(np.zeros(69));np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7)
fullns={'__name__':'selected53_power_full_independent'};exec(compile(spectral_source(RESEARCH),'selected53_power_full_independent','exec'),fullns)
def changed(p):
 target=base_target.copy();target[:3]+=np.asarray(p).reshape(3,23);dyn=copy.deepcopy(cfg['dynamic_harmonic_parameters']);dyn['target_logpower_db_polynomial']=target.tolist();return dyn
checks=[]
for sign in [-1,1]:
 p=np.random.default_rng(361+sign).uniform(-.03,.03,69);args=dict(ns['kw'],adaptive_dynamic=changed(p),adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],48000,8320,cfg['parameters'],**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);checks.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-actual))),two_nonzero_full_SciPy_errors=checks,baseline=str(B),only_existing69_power_target_values_changed=True,match_reached=False),indent=2));print('SELECTED53_POWER_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS',checks,flush=True)
base=joint.metrics(neutral);score=joint.score;lower=np.full(69,-1.5);upper=-lower;original53=json.loads((W/'ranking.json').read_text())['results'][0]['metrics'];guards=dict(H24=min(original53['H24']/base['H24'],1.0001),upper_harm=1.005,upper_off=1.001,low_harm=1.005,relative_phase=1.005,whole=1.005,envelope=1.005,body=1.01,stereo_phase=1.01,stereo_balance=1.01)
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));penalty=sum(100*max(m[k]/base[k]-limit,0)**2 for k,limit in guards.items())+100*max(peak-.99,0)**2;obj=score(m)+penalty+.00001*float(np.mean(p*p));feasible=bool(all(m[k]/base[k]<=limit for k,limit in guards.items()) and peak<.99)
 keys=['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','parameters','key_slopes','key_quadratic'];row=dict(metrics=m,weighted_score=score(m),penalty=penalty,peak=peak,feasible_search_guards=feasible,power_offsets=p.tolist(),dynamic_harmonic_parameters=changed(p),**{k:cfg[k] for k in keys},only_existing69_power_target_values_changed_after_actual_baseline=True,match_reached=False);return obj,row
baseline_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
raw_compute=compute
def compute(p):
 _,row=raw_compute(p);row.setdefault('final_stereo_balance',cfg['final_stereo_balance']);con=np.r_[[limit-row['metrics'][k]/base[k] for k,limit in guards.items()],.99-row['peak']];objective=score(row['metrics'])+.00001*float(np.mean(p*p));row.setdefault('stereo_harmonic_parameters',cfg['stereo_harmonic_parameters']);carry_fine_phase(row,cfg);row.update(baseline_model_SHA256=baseline_hash,source_manifest=manifest,guard_limits=guards,H24_original53_cap=original53['H24'],original_common_weights_unchanged=True,all_DSP_tolerances_unchanged=True);return objective,row,con
rows=[];last={};best=np.inf;derivatives={}
def probe(p):
 global best
 if last.get('key')!=tuple(p):
  obj,row,con=compute(p);row.update(center=len(rows),objective=obj,minimum_constraint=float(np.min(con)));rows.append(row);last.update(key=tuple(p),result=(obj,row,con));tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if np.min(con)>=-1e-12 and row['weighted_score']<best:
   best=row['weighted_score'];tmp=V/'best.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(V/'best-edit.wav',e,48000,subtype='FLOAT')
  print('COMPLETE_POWER_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'constraintMin',float(np.min(con)),flush=True)
 return last['result']
def derive(p):
 key=tuple(p)
 if derivatives.get('key')!=key:
  center=probe(p);points=[];steps=[]
  for j in range(69):
   step=.001 if p[j]+.001<=upper[j] else -.001;pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
  values=list(pool.map(compute,points));derivatives.update(key=key,gradient=np.array([(v[0]-center[0])/s for v,s in zip(values,steps)]),jac=np.array([(v[2]-center[2])/s for v,s in zip(values,steps)]).T)
 return derivatives
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(69)
 if '--check-only' in sys.argv:
  result=compute(initial);assert np.min(result[2])>=-1e-12;assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];assert result[1]['stereo_harmonic_parameters']==cfg['stereo_harmonic_parameters'];assert result[1].get('fine_phase_harmonic_parameters')==cfg.get('fine_phase_harmonic_parameters');print('COMPLETE_MODEL_POWER_CHECKED',B.name,flush=True);raise SystemExit(0)
 path=V/'best.json'
 if path.exists():
  row=json.loads(path.read_text())
  if row.get('baseline_model_SHA256')==baseline_hash:
   candidate=np.asarray(row['power_offsets']);value=compute(candidate)
   if np.min(value[2])>=-1e-12 and value[0]<compute(initial)[0]:
    (V/'resume-origin.json').write_text(json.dumps(row,indent=2));initial=candidate.copy()
  else:
   archive=V/('previous-model-'+str(row.get('baseline_model_SHA256','unknown'))[:16]+'-best.json');archive.write_text(json.dumps(row,indent=2))
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(lambda p:probe(p)[0],initial,jac=lambda p:derive(p)['gradient'],method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:probe(p)[2],jac=lambda p:derive(p)['jac'])],options=dict(maxiter=int(os.environ.get('DIVALEAD_MAXITER','45')),ftol=1e-9,disp=False))
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),elapsed_seconds=time.monotonic()-start,source_base=B.name,source_hashes_checked=True,baseline_model_SHA256=baseline_hash,existing69_power_target_values_only=True,method='SLSQP with shared finite-difference objective and constraint Jacobians',H24_original53_cap=original53['H24'],new_source_requires_its_matching_independent_prebase=True,match_reached=False),indent=2));print('COMPLETE_POWER_DONE',fit.status,fit.message,flush=True)
