"""Existing42 free final balance values for a complete verified model/source manifest."""
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
W=Path(__file__).resolve().parent;REPO=joint.REPO;SR=48000;current=W/'CURRENT_RESEARCH_MODEL.json';default_model=W/json.loads(current.read_text())['model_directory'];B=Path(os.environ.get('DIVALEAD_MODEL_BASE',str(default_model)));V=joint.analysis.WORK/('complete-balance-'+B.name);V.mkdir(exist_ok=True)
manifest=json.loads((B/'source_manifest.json').read_text())
for k in ['source_preset','source_WAV','before_spectral_WAV']:assert hashlib.sha256((REPO/manifest[k]).read_bytes()).hexdigest()==manifest[k+'_SHA256']
source_fixture=sf.read(REPO/manifest['source_WAV'])[0];before_fixture=sf.read(REPO/manifest['before_spectral_WAV'])[0];frozen_cfg=json.loads((B/'analysis/spectral_model.json').read_text());frozen_actual=sf.read(B/'REFERENCE_EDIT_WIP.wav')[0];seed=frozen_cfg
from fine_phase_model import extend_prefix,spectral_source,fine_phase_curve,carry_fine_phase
tree=ast.parse((REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets)).replace('v55','v53')
prefix=prefix.replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')')
prefix=prefix.replace("cfg=json.loads((R/'analysis/spectral_model.json').read_text())",'cfg=copy.deepcopy(frozen_cfg)').replace("actual=sf.read(R/'Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0]",'actual=frozen_actual').replace("dry=sf.read(R/'Diva_v53_VIDEO_DIVA_ONLY.wav')[0]",'dry=source_fixture').replace("before=sf.read(R/'Diva_v53_BEFORE_SPECTRAL.wav')[0]",'before=before_fixture')
prefix=extend_prefix(prefix,RESEARCH)
ns={'__name__':'complete_HF_capture','Path':Path,'copy':copy,'frozen_cfg':frozen_cfg,'frozen_actual':frozen_actual,'source_fixture':source_fixture,'before_fixture':before_fixture};exec(compile(prefix,'complete_HF_capture','exec'),ns)
from scipy.signal import istft
from replay_spectral_model import kwargs
cfg=ns['cfg'];source=spectral_source(RESEARCH);cut=source.index(' if final_stereo_balance is not None:');capture=source[:cut]+' return f,t,out,f0,size,hop,fft\n';captured={'__name__':'before_final_balance'};exec(compile(capture,'before_final_balance','exec'),captured)
f,t,pre,f0,size,hop,fft=captured['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**kwargs(cfg));fullns={'__name__':'balance_full_independent'};exec(compile(source,'balance_full_independent','exec'),fullns)
fields=['log_side_scale','mid_to_side_real','mid_to_side_imag'];free=np.array([i for i in range(15) if i!=7]);assert all(cfg['final_stereo_balance'][k][7]==0 for k in fields)
def changed(p):
 settings=copy.deepcopy(cfg['final_stereo_balance']);offsets=np.asarray(p).reshape(3,14)
 for i,k in enumerate(fields):
  values=np.asarray(settings[k]).copy();values[free]+=offsets[i];settings[k]=values.tolist()
 return settings
def render(p):
 z=fullns['final_balance_gain'](pre,f,changed(p));z[:,0]=z[:,0].real;z[:,-1]=z[:,-1].real;_,ms=istft(z,fs=SR,nperseg=size,noverlap=size-hop,nfft=fft);ms=ms[:,:len(ns['before'])];full=np.stack([ms[0]+ms[1],ms[0]-ms[1]],axis=1);edit=joint.analysis.h.edit_aligned(joint.analysis.h.align_with_pdc(full,ns['c']['settings'],latency=8320));return full,edit
_,neutral=render(np.zeros(42));np.testing.assert_allclose(neutral,frozen_actual,rtol=0,atol=2e-7);checks=[]
for sign in [-1,1]:
 p=np.random.default_rng(416+sign).uniform(-.004,.004,42);kw=kwargs(cfg);kw['final_stereo_balance']=changed(p);direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**kw);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);checks.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-frozen_actual))),two_nonzero_full_SciPy_errors=checks,existing45_balance_values_42_free=True,identity1600_Hz_fixed=True,match_reached=False),indent=2));print('COMPLETE_BALANCE_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS',checks,flush=True)
base=joint.metrics(neutral);score=joint.score;lower=np.r_[np.full(14,-.12),np.full(28,-.06)];upper=-lower;original53=json.loads((W/'ranking.json').read_text())['results'][0]['metrics'];guards=dict(H24=min(original53['H24']/base['H24'],1.003),upper_harm=1.005,upper_off=1.001,low_harm=1.005,relative_phase=1.005,whole=1.005,envelope=1.01,body=1.02,stereo_phase=1.001,stereo_balance=1.001)
from search_global_guards import cap_with_original53,repair_near_feasible_rows
guards=cap_with_original53(guards,original53,base)
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));row=dict(metrics=m,weighted_score=score(m),penalty=0.,peak=peak,feasible_search_guards=bool(all(m[k]/base[k]<=v for k,v in guards.items()) and peak<.99),balance_offsets=p.tolist(),final_stereo_balance=changed(p),**{k:seed[k] for k in ['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','parameters','key_slopes','key_quadratic','dynamic_harmonic_parameters']},existing45_balance_values_42_free=True,identity1600_Hz_fixed=True,match_reached=False);return score(m),row
baseline_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
raw_compute=compute
def compute(p):
 _,row=raw_compute(p);con=np.r_[[limit-row['metrics'][k]/base[k] for k,limit in guards.items()],.99-row['peak']];objective=score(row['metrics'])+.0001*float(np.mean(p*p));row.setdefault('stereo_harmonic_parameters',cfg['stereo_harmonic_parameters']);carry_fine_phase(row,cfg);row.update(baseline_model_SHA256=baseline_hash,source_manifest=manifest,guard_limits=guards,H24_original53_cap=original53['H24'],original_common_weights_unchanged=True,all_DSP_tolerances_unchanged=True);return objective,row,con
rows=[];last={};best=np.inf;derivatives={}
def probe(p):
 global best
 if last.get('key')!=tuple(p):
  obj,row,con=compute(p);row.update(center=len(rows),objective=obj,minimum_constraint=float(np.min(con)));rows.append(row);last.update(key=tuple(p),result=(obj,row,con));tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if np.min(con)>=-1e-12 and row['weighted_score']<best:
   best=row['weighted_score'];tmp=V/'best.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(V/'best-edit.wav',e,48000,subtype='FLOAT')
  print('COMPLETE_BALANCE_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'constraintMin',float(np.min(con)),flush=True)
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
  result=compute(initial);assert np.min(result[2])>=-1e-12;assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];assert result[1]['stereo_harmonic_parameters']==cfg['stereo_harmonic_parameters'];assert result[1].get('fine_phase_harmonic_parameters')==cfg.get('fine_phase_harmonic_parameters');print('COMPLETE_MODEL_BALANCE_CHECKED',B.name,flush=True);raise SystemExit(0)
 path=V/'best.json'
 if path.exists():
  row=json.loads(path.read_text())
  if row.get('baseline_model_SHA256')==baseline_hash:
   candidate=np.asarray(row['balance_offsets']);value=compute(candidate)
   if np.min(value[2])>=-1e-12 and value[0]<compute(initial)[0]:
    (V/'resume-origin.json').write_text(json.dumps(row,indent=2));initial=candidate.copy()
  else:
   archive=V/('previous-model-'+str(row.get('baseline_model_SHA256','unknown'))[:16]+'-best.json');archive.write_text(json.dumps(row,indent=2))
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(lambda p:probe(p)[0],initial,jac=lambda p:derive(p)['gradient'],method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:probe(p)[2],jac=lambda p:derive(p)['jac'])],options=dict(maxiter=int(os.environ.get('DIVALEAD_MAXITER','45')),ftol=1e-9,disp=False))
 repair=repair_near_feasible_rows(rows,best,initial,'balance_offsets',compute,probe)
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(near_feasible_repair=repair,status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),elapsed_seconds=time.monotonic()-start,source_base=B.name,source_hashes_checked=True,baseline_model_SHA256=baseline_hash,existing42_free_final_balance_values_only=True,method='SLSQP with shared finite-difference objective and constraint Jacobians',H24_original53_cap=original53['H24'],new_source_requires_its_matching_independent_prebase=True,match_reached=False),indent=2));print('COMPLETE_BALANCE_DONE',fit.status,fit.message,flush=True)
