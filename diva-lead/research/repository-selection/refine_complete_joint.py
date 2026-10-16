"""Existing111 gain and phase values for a complete verified model/source manifest."""
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
W=RESEARCH;REPO=joint.REPO;SR=48000;current=W/'CURRENT_RESEARCH_MODEL.json';default_model=W/json.loads(current.read_text())['model_directory'];B=Path(os.environ.get('DIVALEAD_MODEL_BASE',str(default_model)));V=joint.analysis.WORK/('complete-joint-'+B.name);V.mkdir(exist_ok=True)
manifest=json.loads((B/'source_manifest.json').read_text())
for k in ['source_preset','source_WAV','before_spectral_WAV']:assert hashlib.sha256((REPO/manifest[k]).read_bytes()).hexdigest()==manifest[k+'_SHA256']
source_fixture=sf.read(REPO/manifest['source_WAV'])[0];before_fixture=sf.read(REPO/manifest['before_spectral_WAV'])[0];frozen_cfg=json.loads((B/'analysis/spectral_model.json').read_text());frozen_actual=sf.read(B/'REFERENCE_EDIT_WIP.wav')[0];seed=frozen_cfg
from fine_phase_model import extend_prefix,spectral_source,fine_phase_curve,carry_fine_phase
tree=ast.parse((REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets)).replace('v55','v53')
prefix=prefix.replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')')
prefix=prefix.replace("cfg=json.loads((R/'analysis/spectral_model.json').read_text())",'cfg=copy.deepcopy(frozen_cfg)').replace("actual=sf.read(R/'Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0]",'actual=frozen_actual').replace("dry=sf.read(R/'Diva_v53_VIDEO_DIVA_ONLY.wav')[0]",'dry=source_fixture').replace("before=sf.read(R/'Diva_v53_BEFORE_SPECTRAL.wav')[0]",'before=before_fixture')
prefix=extend_prefix(prefix,RESEARCH)
ns={'__name__':'complete_HF_capture','Path':Path,'copy':copy,'frozen_cfg':frozen_cfg,'frozen_actual':frozen_actual,'source_fixture':source_fixture,'before_fixture':before_fixture};exec(compile(prefix,'complete_HF_capture','exec'),ns)
cfg=ns['cfg'];c=ns['c'];Z0=ns['Z'];f=ns['f'];f0=ns['f0'];q=ns['q'];h=ns['h'];T=Z0.shape[2];kw=ns['kw'];base_gain=np.asarray(cfg['harmonic_gain_parameters']).reshape(3,31);base_phase=np.array([cfg[k] for k in ['common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic']])
_,_,pre,_,_,_,_=ns['ns']['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**dict(kw,harmonic_gain=None))
ratio=np.maximum(f[:,None]/f0,1);key=np.log2(f0/100);distance=f[:,None]-np.rint(f[:,None]/f0)*f0;gainmask=np.exp(-.5*(distance/(cfg['mask_sigma']*f0))**2)
knots=np.log(cfg['harmonic_gain_orders']);value=np.log(ratio);index=np.clip(np.searchsorted(knots,value,side='right')-1,0,len(knots)-2);u=np.clip((value-knots[index])/(knots[index+1]-knots[index]),0,1)
phase_basis=np.array([np.interp(value,np.log(cfg['common_phase_orders']),np.r_[0,row,0]) for row in np.eye(6)])
where=((q>=1)&(q<=24)).ravel();indices=(q*T+np.arange(T)[None]).ravel()[where];hm=h.ravel()[where];weights=[hm,hm**3,2*hm*hm*(1-hm),hm*(1-hm)**2]
def moments(z):
 pw=(abs(z)**2).reshape(2,-1)[:,where];a=[]
 for w in weights:a.append(np.stack([np.bincount(indices,weights=p*w,minlength=25*T).reshape(25,T)[1:25] for p in pw]))
 mom=a[0];aa,bb,cc=[v[:,1:] for v in a[1:]];unit=mom[:,0].sum(axis=0);norm=lambda a:np.divide(a.sum(axis=0),unit,out=np.zeros_like(a[0]),where=unit>0)
 return mom,aa,bb,cc,unit,norm(aa),norm(bb),norm(cc)
def changed(p):return base_gain+np.asarray(p[:93]).reshape(3,31),base_phase+np.asarray(p[93:]).reshape(3,6)
def render(p):
 delta=np.pad(np.asarray(p[:93]).reshape(3,31),((0,0),(1,1)));curve=sum(((1-u)*delta[d,index]+u*delta[d,index+1])*key**d for d in range(3));z=Z0+pre*(gainmask*curve)[None]
 phase=sum(np.einsum('i,ift->ft',np.asarray(p[93:]).reshape(3,6)[d],phase_basis)*key**d for d in range(3));z=z*np.exp(1j*phase)[None];ns['Z']=z
 for name,v in zip(['mom','aa','bb','cc','unit','an','bn','cn'],moments(z)):ns[name]=v
 return ns['render'](np.zeros(69))
_,neutral=render(np.zeros(111));actual=frozen_actual;np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7)
fullns={'__name__':'joint53_full_independent'};exec(compile(spectral_source(RESEARCH),'joint53_full_independent','exec'),fullns);errors=[]
for sign in [-1,1]:
 p=np.random.default_rng(359+sign).uniform(-.01,.01,111);gain,phase=changed(p);args=dict(kw,harmonic_gain=gain.ravel().tolist(),phase_angles=phase[0].tolist(),phase_key_slopes=phase[1].tolist(),phase_key_quadratic=phase[2].tolist(),adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);errors.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-actual))),two_nonzero_full_SciPy_errors=errors,existing111_values_only=True,selected_basis='v53-wip'),indent=2));print('V53_JOINT_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS',errors,flush=True)

base=joint.metrics(neutral);score=joint.score;lower=np.r_[np.full(93,-.1),np.full(18,-.08)];upper=-lower;original53=json.loads((W/'ranking.json').read_text())['results'][0]['metrics'];guards=dict(H24=min(original53['H24']/base['H24'],1.003),upper_harm=1.005,upper_off=1.001,low_harm=1.005,relative_phase=1.005,whole=1.005,envelope=1.01,body=1.02,stereo_phase=1.01,stereo_balance=1.01)
def minimum_gain(gain):
 lo,hi=np.log2(np.array([45,220])/100);values=[]
 for a,b,q in gain.T:
  points=[lo,hi]
  if q>0 and lo<-b/(2*q)<hi:points.append(-b/(2*q))
  values.append(min(1+a+b*k+q*k*k for k in points))
 return float(min(values))
def gain_constraints(p):
 gain,_=changed(p);lo,hi=np.log2(np.array([45,220])/100);values=[];jac=np.zeros((31,111))
 for i,(a,b,q) in enumerate(gain.T):
  points=[lo,hi]
  if q>0 and lo<-b/(2*q)<hi:points.append(-b/(2*q))
  k=min(points,key=lambda k:1+a+b*k+q*k*k);values.append(1+a+b*k+q*k*k-.020002)
  for d in range(3):jac[i,d*31+i]=k**d
 return np.array(values),jac
def compute(p):
 full,e=render(p);m=joint.metrics(e);gain,phase=changed(p);peak=float(np.max(abs(full)));con=np.r_[[limit-m[k]/base[k] for k,limit in guards.items()],.99-peak,gain_constraints(p)[0]]
 row=dict(metrics=m,weighted_score=score(m),penalty=0.,peak=peak,minimum_gain_on_45_220Hz=minimum_gain(gain),feasible_search_guards=bool(np.min(con)>=-1e-12),offsets=p.tolist(),final_stereo_balance=cfg['final_stereo_balance'],stereo_harmonic_parameters=cfg['stereo_harmonic_parameters'],harmonic_gain_parameters=gain.ravel().tolist(),common_phase_radians=phase[0].tolist(),common_phase_key_slopes=phase[1].tolist(),common_phase_key_quadratic=phase[2].tolist(),**{k:seed[k] for k in ['hf_matrix_parameters','parameters','key_slopes','key_quadratic','dynamic_harmonic_parameters']},baseline_model_SHA256=baseline_hash,source_manifest=manifest,guard_limits=guards,H24_original53_cap=original53['H24'],only_existing111_gain_phase_values=True,original_common_weights_unchanged=True,all_DSP_tolerances_unchanged=True,match_reached=False)
 carry_fine_phase(row,cfg)
 return score(m)+.0001*float(np.mean(p*p)),row,con
baseline_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
rows=[];last={};best=np.inf;derivatives={}
def probe(p):
 global best
 if last.get('key')!=tuple(p):
  obj,row,con=compute(p);row.update(center=len(rows),objective=obj,minimum_constraint=float(np.min(con)));rows.append(row);last.update(key=tuple(p),result=(obj,row,con));tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if np.min(con)>=-1e-12 and row['weighted_score']<best:
   best=row['weighted_score'];tmp=V/'best.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(V/'best-edit.wav',e,48000,subtype='FLOAT')
  print('COMPLETE_JOINT_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'constraintMin',float(np.min(con)),flush=True)
 return last['result']
def derive(p):
 key=tuple(p)
 if derivatives.get('key')!=key:
  center=probe(p);points=[];steps=[]
  for j in range(111):
   step=.00025 if p[j]+.00025<=upper[j] else -.00025;pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
  values=list(pool.map(compute,points));derivatives.update(key=key,gradient=np.array([(v[0]-center[0])/s for v,s in zip(values,steps)]),jac=np.array([(v[2]-center[2])/s for v,s in zip(values,steps)]).T)
 derivatives['jac'][-31:]=gain_constraints(p)[1]
 return derivatives
def repair_near_feasible(initial):
 # Keep the same guards: interpolate a nearly admissible point toward the checked
 # initial point, then save only points satisfying the original constraints.
 eligible=[row for row in rows if row['weighted_score']<best and -1e-4<=row['minimum_constraint']<0];trials=[]
 if eligible:
  candidate=min(eligible,key=lambda row:row['weighted_score'])
  offsets=np.asarray(candidate['offsets']);origin=np.asarray(initial)
  for fraction in [.999,.995,.99,.98,.95,.9,.8,.5]:
   point=origin+fraction*(offsets-origin);_,row,con=compute(point);feasible=bool(np.min(con)>=-1e-12)
   trials.append(dict(fraction=fraction,score=row['weighted_score'],minimum_constraint=float(np.min(con)),feasible=feasible))
   if feasible and row['weighted_score']<best:probe(point)
 return dict(probes=trials,guard_limits_unchanged=True,feasibility_tolerance_unchanged=True,selected_best_score=best,requires_fresh_actual_validation=True)
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(111)
 if '--check-only' in sys.argv:
  result=compute(initial);assert np.min(result[2])>=-1e-12;assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];assert result[1]['stereo_harmonic_parameters']==cfg['stereo_harmonic_parameters'];assert result[1].get('fine_phase_harmonic_parameters')==cfg.get('fine_phase_harmonic_parameters');print('COMPLETE_MODEL_JOINT_CHECKED',B.name,flush=True);raise SystemExit(0)
 path=V/'best.json'
 if path.exists():
  row=json.loads(path.read_text())
  if row.get('baseline_model_SHA256')==baseline_hash:
   candidate=np.asarray(row['offsets']);value=compute(candidate)
   if np.min(value[2])>=-1e-12 and value[0]<compute(initial)[0]:
    (V/'resume-origin.json').write_text(json.dumps(row,indent=2));initial=candidate.copy()
  else:
   archive=V/('previous-model-'+str(row.get('baseline_model_SHA256','unknown'))[:16]+'-best.json');archive.write_text(json.dumps(row,indent=2))
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(lambda p:probe(p)[0],initial,jac=lambda p:derive(p)['gradient'],method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:probe(p)[2],jac=lambda p:derive(p)['jac'])],options=dict(maxiter=int(os.environ.get('DIVALEAD_MAXITER','45')),ftol=1e-9,disp=False))
 repair=repair_near_feasible(initial)
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),elapsed_seconds=time.monotonic()-start,source_base=B.name,source_hashes_checked=True,baseline_model_SHA256=baseline_hash,existing111_gain_phase_values_only=True,method='SLSQP with shared finite-difference objective/metric Jacobians and analytic continuous-gain Jacobian',near_feasible_repair=repair,H24_original53_cap=original53['H24'],new_source_requires_its_matching_independent_prebase=True,match_reached=False),indent=2));print('COMPLETE_JOINT_DONE',fit.status,fit.message,flush=True)
