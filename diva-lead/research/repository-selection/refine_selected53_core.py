"""Existing147 core-matrix values from the best actual-verified power/HF model."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
if os.environ.get('DIVALEAD_CPU_SET'):os.sched_setaffinity(0,{int(v) for v in os.environ['DIVALEAD_CPU_SET'].split(',')})
import sys,ast,json,time,copy,multiprocessing as mp
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent));import refine_selected53 as joint
W=Path(__file__).resolve().parent;V=joint.analysis.WORK/'core-from-power';V.mkdir(exist_ok=True)
B=W/'after-hf-power';cfg=json.loads((B/'analysis/spectral_model.json').read_text());actual=sf.read(B/'REFERENCE_EDIT_WIP.wav')[0]
tree=ast.parse((joint.REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets)).replace('v55','v53')
prefix=prefix.replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')').replace("cfg=json.loads((R/'analysis/spectral_model.json').read_text())",'cfg=copy.deepcopy(frozen_cfg)').replace("actual=sf.read(R/'Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0]",'actual=frozen_actual')
ns={'__name__':'selected53_core_capture','Path':Path,'copy':copy,'frozen_cfg':cfg,'frozen_actual':actual};exec(compile(prefix,'selected53_core_capture','exec'),ns)
Z0=ns['Z'];f=ns['f'];f0=ns['f0'];q=ns['q'];h=ns['h'];T=Z0.shape[2];kw=ns['kw'];base_core=np.array([cfg[k] for k in ['parameters','key_slopes','key_quadratic']]).reshape(3,7,7)
source=(joint.REPO/'diva-lead/v53-wip/analysis/independent_spectral_ms.py').read_text();i=source.index(' m=Z[0];s=Z[1];out=Z.copy()');rawsource=source[:i]+' return f,t,Z,f0,size,hop,fft\n';rawns={'__name__':'raw_core53'};exec(compile(rawsource,'raw_core53','exec'),rawns)
_,_,raw,_,_,_,_=rawns['spectral_ms'](ns['before'],ns['dry'],48000,8320,cfg['parameters'],**kw)
key=np.log2(f0/100);dist=f[:,None]-np.rint(f[:,None]/f0)*f0;mask=np.exp(-.5*(dist/(cfg['mask_sigma']*f0))**2);off=1-mask;hm=np.exp(-.5*(dist/(cfg['hf_mask_sigma']*f0))**2);ho=1-hm
hc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(cfg['hf_matrix_anchors_Hz']),np.r_[0,row,0]) for row in np.asarray(cfg['hf_matrix_parameters']).reshape(10,10)])[:,:,None]
MM=1+ho*hc[0]+hm*hc[6];MS=ho*(hc[2]+1j*hc[3]);SS=1+ho*hc[1]+hm*hc[7];SM=ho*(hc[4]+1j*hc[5])+hm*(hc[8]+1j*hc[9])
ratio=np.log(np.maximum(f[:,None]/f0,1));phase=sum(np.interp(ratio,np.log(cfg['common_phase_orders']),np.r_[0,cfg[k],0])*key**d for d,k in enumerate(['common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic']))
gain=1+mask*sum(np.interp(ratio,np.log(cfg['harmonic_gain_orders']),np.r_[0,row,0])*key**d for d,row in enumerate(np.asarray(cfg['harmonic_gain_parameters']).reshape(3,31)))
lo,hi=cfg['upper_rolloff_Hz'];lp=np.ones(len(f));active=(f>lo)&(f<hi);lp[active]=(.5+.5*np.cos(np.pi*(f[active]-lo)/(hi-lo)))**2;lp[f>=hi]=0;post=np.exp(1j*phase)*gain*lp[:,None]
interpolation=np.array([np.interp(np.log(np.maximum(f,1)),np.log(cfg['anchors_Hz']),np.r_[0,row,0]) for row in np.eye(7)])
where=((q>=1)&(q<=24)).ravel();indices=(q*T+np.arange(T)[None]).ravel()[where];hh=h.ravel()[where];weights=[hh,hh**3,2*hh*hh*(1-hh),hh*(1-hh)**2]
def moments(z):
 pw=(abs(z)**2).reshape(2,-1)[:,where];a=[]
 for w in weights:a.append(np.stack([np.bincount(indices,weights=p*w,minlength=25*T).reshape(25,T)[1:25] for p in pw]))
 mom=a[0];aa,bb,cc=[v[:,1:] for v in a[1:]];unit=mom[:,0].sum(axis=0);norm=lambda a:np.divide(a.sum(axis=0),unit,out=np.zeros_like(a[0]),where=unit>0)
 return mom,aa,bb,cc,unit,norm(aa),norm(bb),norm(cc)
def render(p):
 d=np.asarray(p).reshape(3,7,7);curves=sum((d[degree]@interpolation)[:,:,None]*key**degree for degree in range(3))
 dm=(mask*curves[0]+off*curves[1])*raw[0]+off*curves[6]*raw[1]
 ds=(mask*curves[2]+off*curves[3])*raw[1]+mask*(curves[5]+1j*curves[4])*raw[0]
 z=Z0+np.stack([(MM*dm+MS*ds)*post,(SS*ds+SM*dm)*post]);ns['Z']=z
 for name,v in zip(['mom','aa','bb','cc','unit','an','bn','cn'],moments(z)):ns[name]=v
 return ns['render'](np.zeros(69))
_,neutral=render(np.zeros(147));np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7)
fullns={'__name__':'selected53_core_full_independent'};exec(compile(source,'selected53_core_full_independent','exec'),fullns);checks=[]
for sign in [-1,1]:
 p=np.random.default_rng(362+sign).uniform(-.01,.01,147);core=base_core+p.reshape(3,7,7);args=dict(kw,key_slopes=core[1].ravel().tolist(),key_quadratic=core[2].ravel().tolist(),adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],48000,8320,core[0].ravel().tolist(),**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);checks.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-actual))),two_nonzero_full_SciPy_errors=checks,baseline=str(B),only_existing147_core_values_changed=True,match_reached=False),indent=2));print('SELECTED53_CORE_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS',checks,flush=True)
base=joint.metrics(neutral);score=joint.score;lower=np.full(147,-.1);upper=-lower;original53=json.loads((W/'ranking.json').read_text())['results'][0]['metrics'];guards=dict(H24=min(original53['H24']/base['H24'],1.003),upper_harm=1.005,upper_off=1.001,low_harm=1.005,relative_phase=1.005,whole=1.005,envelope=1.005,body=1.01,stereo_phase=1.01,stereo_balance=1.01)
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));penalty=sum(100*max(m[k]/base[k]-limit,0)**2 for k,limit in guards.items())+100*max(peak-.99,0)**2;obj=score(m)+penalty+.0001*float(np.mean(p*p));feasible=bool(all(m[k]/base[k]<=limit for k,limit in guards.items()) and peak<.99);core=base_core+np.asarray(p).reshape(3,7,7)
 keys=['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','dynamic_harmonic_parameters'];row=dict(metrics=m,weighted_score=score(m),penalty=penalty,peak=peak,feasible_search_guards=feasible,core_offsets=p.tolist(),parameters=core[0].ravel().tolist(),key_slopes=core[1].ravel().tolist(),key_quadratic=core[2].ravel().tolist(),**{k:cfg[k] for k in keys},only_existing147_core_values_changed_after_actual_power_baseline=True,match_reached=False);return obj,row
rows=[];last={};best=score(base)
def probe(p):
 global best
 if last.get('key')!=tuple(p):
  obj,row=compute(p);row.update(center=len(rows),objective=obj);rows.append(row);last.update(key=tuple(p),result=obj);temp=V/'latest_center.tmp';temp.write_text(json.dumps(row,indent=2));temp.replace(V/'latest_center.json')
  if row['feasible_search_guards'] and row['weighted_score']<best:
   best=row['weighted_score'];temp=V/'best.tmp';temp.write_text(json.dumps(row,indent=2));temp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(V/'best-edit.wav',e,48000,subtype='FLOAT')
  print('SELECTED53_CORE_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'low',row['metrics']['low_harm'],'feasible',row['feasible_search_guards'],flush=True)
 return last['result']
def gradient(p):
 center=probe(p);points=[];steps=[]
 for j in range(147):
  step=.00025 if p[j]+.00025<=upper[j] else -.00025;pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
 return np.array([(r[0]-center)/step for r,step in zip(pool.map(compute,points),steps)])
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(147);probe(initial)
 if '--check-only' in sys.argv:raise SystemExit(0)
 if '--render-core-seed' in sys.argv:
  seed=json.loads((W/'after-core/choice.json').read_text());p=np.asarray(seed['core_offsets']);full,e=render(p);expected=sf.read(W/'after-core/REFERENCE_EDIT_WIP.wav')[0];np.testing.assert_allclose(e,expected,rtol=0,atol=2e-7);report=dict(actual_core_edit_reconstruction_max_error=float(np.max(abs(e-expected))),tolerance=2e-7,H24_reference_cap=original53['H24'],match_reached=False);(V/'core-seed-replay.json').write_text(json.dumps(report,indent=2));print('SELECTED53_CORE_CHECKED_SEED_RECONSTRUCTED',report,flush=True);raise SystemExit(0)
 for path in [W/'after-core/choice.json',V/'best.json']:
  if path.exists():
   row=json.loads(path.read_text());point=np.asarray(row['core_offsets'])
   if not np.all(point>=lower) or not np.all(point<=upper):continue
   wanted=np.array([row[k] for k in ['parameters','key_slopes','key_quadratic']]).reshape(3,7,7);np.testing.assert_allclose(base_core+point.reshape(3,7,7),wanted,rtol=0,atol=1e-14)
   assert all(row[k]==cfg[k] for k in ['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','dynamic_harmonic_parameters'])
   obj,result=compute(point)
   if result['feasible_search_guards'] and obj<probe(initial):initial=point.copy()
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(probe,initial,jac=gradient,method='L-BFGS-B',bounds=list(zip(lower,upper)),options=dict(maxiter=45,ftol=1e-9,gtol=2e-6,maxls=12,maxcor=12))
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),elapsed_seconds=time.monotonic()-start,baseline=str(B),existing147_core_values_only=True,full_NEW247_applicable=True,match_reached=False),indent=2));print('SELECTED53_CORE_DONE',fit.status,fit.message,flush=True)
