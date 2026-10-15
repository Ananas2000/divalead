"""Existing100 upper-matrix values after actual-validated v53 joint continuation."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
if os.environ.get('DIVALEAD_CPU_SET'):os.sched_setaffinity(0,{int(v) for v in os.environ['DIVALEAD_CPU_SET'].split(',')})
import ast,json,time,sys,multiprocessing as mp
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
RESEARCH=Path(__file__).resolve().parent;sys.path.insert(0,str(RESEARCH))
import refine_selected53 as joint
W=Path(__file__).resolve().parent;V=joint.analysis.WORK/'HF-refit';V.mkdir(parents=True,exist_ok=True)
REPO=joint.REPO;SR=48000;seed=json.loads((W/'continued53_gain_phase_seed.json').read_text());frozen_actual=sf.read(W/'CONTINUED53_REFERENCE_EDIT_WIP.wav')[0]
tree=ast.parse((REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets)).replace('v55','v53')
prefix=prefix.replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')')
needle="cfg=json.loads((R/'analysis/spectral_model.json').read_text());"
prefix=prefix.replace(needle,needle+"cfg.update({k:seed[k] for k in ['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic']});")
prefix=prefix.replace("actual=sf.read(R/'Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0]",'actual=frozen_actual')
ns={'__name__':'selected53_HF_capture','Path':Path,'seed':seed,'frozen_actual':frozen_actual};exec(compile(prefix,'selected53_HF_capture','exec'),ns)
cfg=ns['cfg'];Z0=ns['Z'];f=ns['f'];f0=ns['f0'];q=ns['q'];h=ns['h'];T=Z0.shape[2];kw=ns['kw'];base_hf=np.asarray(cfg['hf_matrix_parameters']).reshape(10,10)
source=(REPO/'diva-lead/v53-wip/analysis/independent_spectral_ms.py').read_text();i=source.index(' if hf_parameters is not None:');pre_source=source[:i]+' return f,t,out,f0,size,hop,fft\n';pre_ns={'__name__':'preHF53'};exec(compile(pre_source,'preHF53','exec'),pre_ns)
_,_,pre,_,_,_,_=pre_ns['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**kw)
distance=f[:,None]-np.rint(f[:,None]/f0)*f0;hmatrix=np.exp(-.5*(distance/(cfg['hf_mask_sigma']*f0))**2);off=1-hmatrix;gainmask=np.exp(-.5*(distance/(cfg['mask_sigma']*f0))**2);key=np.log2(f0/100)
ratio=np.log(np.maximum(f[:,None]/f0,1));gain=1+gainmask*sum(np.interp(ratio,np.log(cfg['harmonic_gain_orders']),np.r_[0,row,0])*key**d for d,row in enumerate(np.asarray(cfg['harmonic_gain_parameters']).reshape(3,31)))
lo,hi=cfg['upper_rolloff_Hz'];lp=np.ones(len(f));active=(f>lo)&(f<hi);lp[active]=(.5+.5*np.cos(np.pi*(f[active]-lo)/(hi-lo)))**2;lp[f>=hi]=0;post=gain*lp[:,None]
interpolation=np.array([np.interp(np.log(np.maximum(f,1)),np.log(cfg['hf_matrix_anchors_Hz']),np.r_[0,row,0]) for row in np.eye(10)])
where=((q>=1)&(q<=24)).ravel();indices=(q*T+np.arange(T)[None]).ravel()[where];hm=h.ravel()[where];weights=[hm,hm**3,2*hm*hm*(1-hm),hm*(1-hm)**2]
def moments(z):
 pw=(abs(z)**2).reshape(2,-1)[:,where];a=[]
 for w in weights:a.append(np.stack([np.bincount(indices,weights=p*w,minlength=25*T).reshape(25,T)[1:25] for p in pw]))
 mom=a[0];aa,bb,cc=[v[:,1:] for v in a[1:]];unit=mom[:,0].sum(axis=0);norm=lambda a:np.divide(a.sum(axis=0),unit,out=np.zeros_like(a[0]),where=unit>0)
 return mom,aa,bb,cc,unit,norm(aa),norm(bb),norm(cc)
def render(p):
 dc=(np.asarray(p).reshape(10,10)@interpolation)[:,:,None]
 dm=(off*dc[0]+hmatrix*dc[6])*pre[0]+off*(dc[2]+1j*dc[3])*pre[1]
 ds=(off*dc[1]+hmatrix*dc[7])*pre[1]+(off*(dc[4]+1j*dc[5])+hmatrix*(dc[8]+1j*dc[9]))*pre[0]
 z=Z0+np.stack([dm,ds])*post[None];ns['Z']=z
 for name,v in zip(['mom','aa','bb','cc','unit','an','bn','cn'],moments(z)):ns[name]=v
 return ns['render'](np.zeros(69))
_,neutral=render(np.zeros(100));np.testing.assert_allclose(neutral,frozen_actual,rtol=0,atol=2e-7)
full_ns={'__name__':'HF53_full_independent'};exec(compile(source,'HF53_full_independent','exec'),full_ns);checks=[]
for sign in [-1,1]:
 p=np.random.default_rng(360+sign).uniform(-.01,.01,100);args=dict(kw,hf_parameters=(base_hf+p.reshape(10,10)).ravel().tolist(),adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);direct,_=full_ns['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);checks.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-frozen_actual))),two_nonzero_full_independent_errors=checks,baseline_actual='explicit-gain-constraints',only_existing100_HF_values=True,match_reached=False),indent=2));print('SELECTED53_HF_ZERO_ACTUAL_TWO_NONZERO_FULL_SCI_PY_PASS',checks,flush=True)
base=joint.metrics(neutral);score=joint.score;lower=np.full(100,-.10);upper=-lower;guards=dict(H24=1.001,upper_harm=1.005,upper_off=1.001,low_harm=1.005,relative_phase=1.005,whole=1.005,envelope=1.01,body=1.02,stereo_phase=1.01,stereo_balance=1.01)
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));penalty=sum(100*max(m[k]/base[k]-limit,0)**2 for k,limit in guards.items())+100*max(peak-.99,0)**2;value=score(m);obj=value+penalty+.0001*float(np.mean(p*p));feasible=bool(all(m[k]/base[k]<=limit for k,limit in guards.items()) and peak<.99)
 row=dict(metrics=m,weighted_score=value,penalty=penalty,peak=peak,feasible_search_guards=feasible,HF_offsets=p.tolist(),hf_matrix_parameters=(base_hf+p.reshape(10,10)).ravel().tolist(),**{k:seed[k] for k in ['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic']},baseline='selected53 actual explicit111',only_existing100_HF_values_changed_after_frozen111=True,match_reached=False)
 return obj,row
rows=[];last={};best=score(base)
def probe(p):
 global best
 key=tuple(p)
 if last.get('key')!=key:
  obj,row=compute(p);row.update(center=len(rows),objective=obj);rows.append(row);last.update(key=key,result=obj);tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if row['feasible_search_guards'] and row['weighted_score']<best:
   best=row['weighted_score'];tmp=V/'best.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,SR,subtype='FLOAT');sf.write(V/'best-edit.wav',e,SR,subtype='FLOAT')
  print('SELECTED53_HF_CENTER',len(rows),'score',row['weighted_score'],'upperoff',row['metrics']['upper_off'],'H24',row['metrics']['H24'],'feasible',row['feasible_search_guards'],flush=True)
 return last['result']
def gradient(p):
 center=probe(p);points=[];steps=[]
 for j in range(100):
  step=.00025 if p[j]+.00025<=upper[j] else -.00025;pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
 return np.array([(r[0]-center)/step for r,step in zip(pool.map(compute,points),steps)])
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(100);probe(initial)
 if '--check-only' in sys.argv:raise SystemExit(0)
 if '--render-hf-seed' in sys.argv:
  warmseed=json.loads((W/'continued53_HF_seed.json').read_text());point=np.asarray(warmseed['HF_offsets']);full,e=render(point);expected=sf.read(W/'CONTINUED53_HF_REFERENCE_EDIT_WIP.wav')[0];np.testing.assert_allclose(e,expected,rtol=0,atol=2e-7);report=dict(actual_HF_edit_reconstruction_max_error=float(np.max(abs(e-expected))),tolerance=2e-7,match_reached=False);(V/'HF-seed-replay.json').write_text(json.dumps(report,indent=2));print('SELECTED53_HF_CHECKED_SEED_RECONSTRUCTED',report,flush=True);raise SystemExit(0)
 for warm in [W/'continued53_HF_seed.json',V/'best.json']:
  if warm.exists():
   point=np.asarray(json.loads(warm.read_text())['HF_offsets']);obj,row=compute(point)
   if row['feasible_search_guards'] and obj<probe(initial):initial=point.copy()
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(probe,initial,jac=gradient,method='L-BFGS-B',bounds=list(zip(lower,upper)),options=dict(maxiter=45,ftol=1e-9,gtol=2e-6,maxls=12,maxcor=12))
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(status=int(fit.status),message=str(fit.message),nfev=int(fit.nfev),nit=int(fit.nit),elapsed_seconds=time.monotonic()-start,numeric_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),existing100_HF_values_only=True,source53_full_NEW247_applicable=True,match_reached=False),indent=2));print('SELECTED53_HF_DONE',fit.status,fit.message,flush=True)
