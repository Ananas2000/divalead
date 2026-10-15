"""Continue selected v53: existing93 gain +18 phase values, exact detector feedback.

No source/preset/MIDI/pre-STFT changes. Search uses fixed baseline carrier masks;
any accepted candidate must later pass fresh-carrier scoring and actual Windows.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
NUMERIC_WORKERS=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','4'))
if os.environ.get('DIVALEAD_CPU_SET'):os.sched_setaffinity(0,{int(v) for v in os.environ['DIVALEAD_CPU_SET'].split(',')})
import ast,json,time,multiprocessing as mp
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
import compare_all as analysis
from audio_match_helpers import ROOT,REPO,SR,REFERENCE,measure,harmonic_errors
HERE=Path(__file__).resolve().parent;V=analysis.WORK/('selected53-constrained-joint-fit' if '--slsqp' in __import__('sys').argv else 'selected53-joint-fit');V.mkdir(exist_ok=True)
tree=ast.parse((REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets))
prefix=prefix.replace('v55','v53').replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')')
ns={'__name__':'selected53_exact_capture','Path':Path};exec(compile(prefix,'selected53_exact_capture','exec'),ns)
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
_,neutral=render(np.zeros(111));actual=sf.read(REPO/'diva-lead/v53-wip/Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0];np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7)
fullns={'__name__':'joint53_full_independent'};exec(compile((REPO/'diva-lead/v53-wip/analysis/independent_spectral_ms.py').read_text(),'joint53_full_independent','exec'),fullns);errors=[]
for sign in [-1,1]:
 p=np.random.default_rng(359+sign).uniform(-.01,.01,111);gain,phase=changed(p);args=dict(kw,harmonic_gain=gain.ravel().tolist(),phase_angles=phase[0].tolist(),phase_key_slopes=phase[1].tolist(),phase_key_quadratic=phase[2].tolist(),adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);errors.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(zero_actual_error=float(np.max(abs(neutral-actual))),two_nonzero_full_SciPy_errors=errors,existing111_values_only=True,selected_basis='v53-wip'),indent=2));print('V53_JOINT_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS',errors,flush=True)
_,carriers,bounds=analysis.powers(neutral);assert not any(bounds)
def fixed_powers(x):
 rows=[]
 for (a,b,_),f0 in zip(analysis.WINDOWS,carriers):
  z=x[int(a*SR):int(b*SR)];w=np.hanning(len(z));ms=np.c_[z.mean(axis=1),(z[:,0]-z[:,1])/2];power=abs(np.fft.rfft(ms*w[:,None],65536,axis=0))**2;mask=abs(analysis.F-np.rint(analysis.F/f0)*f0)<.23*f0;unit=max(float(power[abs(analysis.F-f0)<.23*f0].sum()),1e-30)
  rows.append([[float(power[(analysis.F>=lo)&(analysis.F<hi)&m,ch].sum()/unit) for m in [mask,~mask] for ch in [0,1]] for lo,hi in analysis.BANDS])
 return np.asarray(rows)
ranking=json.loads((HERE/'ranking.json').read_text());scales=ranking['normalizing_errors'];wts=analysis.WEIGHTS
def metrics(x):
 errors=10*np.log10(np.maximum(fixed_powers(x),1e-15)/np.maximum(analysis.TP,1e-15));er=10*np.log10(np.maximum(analysis.erbpower(x),1e-12)/np.maximum(analysis.TE,1e-12));shape,_,_,_=analysis.wave.features(x);branches=[analysis.TS,analysis.TS*np.exp(1j*np.pi*(1-analysis.wave.ORDERS))[None]];m=measure(x);he=harmonic_errors(x)['weighted_harmonic_error_db']
 return dict(H24=he,upper_harm=float(np.sqrt(np.mean(errors[:,4:,:2]**2))),upper_off=float(np.sqrt(np.mean(errors[:,4:,2:]**2))),low_harm=float(np.sqrt(np.mean(errors[:,:4,:2]**2))),ERB=float(np.sqrt(np.sum(er**2*analysis.EW))),relative_phase=min(float(np.sqrt(np.sum(abs(shape-b)**2*analysis.TW))) for b in branches),whole=m['whole_distance'],envelope=m['envelope12_error'],body=m['body_level_error_db'],stereo_phase=m['phase_rms_degrees'],stereo_balance=m['balance_rms_db'])
base=metrics(neutral);score=lambda m:sum(wts[k]*m[k]/scales[k] for k in wts);base_score=score(base);assert abs(base_score-ranking['results'][0]['weighted_score'])<1e-8
lower=np.r_[np.full(93,-.25),np.full(18,-.25)];upper=-lower
def minimum_gain(gain):
 lo,hi=np.log2(np.array([45,220])/100);values=[]
 for a,b,q in gain.T:
  points=[lo,hi]
  if q>0 and lo<-b/(2*q)<hi:points.append(-b/(2*q))
  values.append(min(1+a+b*k+q*k*k for k in points))
 return float(min(values))
def compute(p):
 full,e=render(p);m=metrics(e);gain,phase=changed(p);peak=float(np.max(abs(full)));ming=minimum_gain(gain)
 ratios={k:m[k]/base[k] for k in m};guards={'H24':1.01,'upper_harm':1.01,'upper_off':1.02,'low_harm':1.01,'whole':1.01,'envelope':1.01,'body':1.03,'stereo_phase':1.03,'stereo_balance':1.03}
 penalty=sum(100*max(ratios[k]-limit,0)**2 for k,limit in guards.items())+100*max(peak-.99,0)**2+100*max(.02-ming,0)**2
 objective=score(m)+penalty+.0001*float(np.mean(p*p));feasible=bool(all(ratios[k]<=limit for k,limit in guards.items()) and peak<.99 and ming>.02)
 return objective,dict(metrics=m,weighted_score=score(m),penalty=penalty,peak=peak,minimum_gain_on_45_220Hz=ming,feasible_search_guards=feasible,offsets=p.tolist(),harmonic_gain_parameters=gain.ravel().tolist(),common_phase_radians=phase[0].tolist(),common_phase_key_slopes=phase[1].tolist(),common_phase_key_quadratic=phase[2].tolist(),match_reached=False)
def gain_constraints(p):
 gain,_=changed(p);lo,hi=np.log2(np.array([45,220])/100);values=[];jac=np.zeros((31,111))
 for i,(a,b,q) in enumerate(gain.T):
  points=[lo,hi]
  if q>0 and lo<-b/(2*q)<hi:points.append(-b/(2*q))
  k=min(points,key=lambda k:1+a+b*k+q*k*k);values.append(1+a+b*k+q*k*k-.020002)
  for d in range(3):jac[i,d*31+i]=k**d
 return np.array(values),jac
rows=[];last={};best=base_score;derivative_cache={}
def probe(p):
 global best
 key=tuple(p)
 if last.get('key')!=key:
  obj,row=compute(p);row.update(center=len(rows),objective=obj);rows.append(row);last.update(key=key,result=(obj,row));tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if row['feasible_search_guards'] and row['weighted_score']<best:
   best=row['weighted_score'];(V/'best.json').write_text(json.dumps(row,indent=2));full,e=render(p);sf.write(V/'best-basepdc.wav',full,SR,subtype='FLOAT');sf.write(V/'best-edit.wav',e,SR,subtype='FLOAT')
  print('V53_JOINT_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'upper',row['metrics']['upper_harm'],'ERB',row['metrics']['ERB'],'feasible',row['feasible_search_guards'],flush=True)
 return last['result'][0]
def gradient(p):
 center=probe(p);points=[];steps=[]
 for j in range(111):
  step=.00025 if j<93 else .0005
  if p[j]+step>upper[j]:step=-step
  pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
 results=list(pool.map(compute,points));return np.array([(result[0]-center)/step for result,step in zip(results,steps)])
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(111);probe(initial)
 if '--check-only' in __import__('sys').argv:
  values,jac=gain_constraints(initial);assert values.min()>0
  numerical=[]
  for j in [0,7,30,31,51,92,93,110]:
   pp=initial.copy();pp[j]+=1e-7;numerical.append(float(np.max(abs((gain_constraints(pp)[0]-values)/1e-7-jac[:,j]))))
  assert max(numerical)<1e-6
  print('SELECTED53_ANALYTIC_CONTINUOUS_KEY_GAIN_JACOBIAN_PASS',max(numerical),flush=True);raise SystemExit(0)
 if '--render-seed' in __import__('sys').argv:
  seed=json.loads((HERE/'continued53_gain_phase_seed.json').read_text());p=np.asarray(seed['offsets']);obj,row=compute(p);assert row['feasible_search_guards'];full,e=render(p);actual=sf.read(HERE/'CONTINUED53_REFERENCE_EDIT_WIP.wav')[0];np.testing.assert_allclose(e,actual,rtol=0,atol=2e-7);sf.write(V/'seed-preview.wav',e,SR,subtype='FLOAT');report=dict(actual_edit_reconstruction_max_error=float(np.max(abs(e-actual))),tolerance=2e-7,match_reached=False);(V/'seed-preview-validation.json').write_text(json.dumps(report,indent=2));print('SELECTED53_CHECKED_SEED_RECONSTRUCTED',report,flush=True);raise SystemExit(0)
 for origin in [HERE/'continued53_gain_phase_seed.json',V/'best.json']:
  if origin.exists():
   possible=np.asarray(json.loads(origin.read_text())['offsets']);obj,row=compute(possible)
   if row['feasible_search_guards'] and obj<probe(initial):initial=possible.copy()
 probe(initial)
 with ProcessPoolExecutor(max_workers=NUMERIC_WORKERS,mp_context=mp.get_context('fork')) as pool:
  if '--slsqp' in __import__('sys').argv:
   fit=minimize(probe,initial,jac=gradient,method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:gain_constraints(p)[0],jac=lambda p:gain_constraints(p)[1])],options=dict(maxiter=45,ftol=1e-9,disp=False))
  else:fit=minimize(probe,initial,jac=gradient,method='L-BFGS-B',bounds=list(zip(lower,upper)),options=dict(maxiter=45,ftol=1e-10,gtol=2e-6,maxls=12,maxcor=12))
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(status=int(fit.status),message=str(fit.message),success=bool(fit.success),nfev=int(fit.nfev),nit=int(fit.nit),elapsed_seconds=time.monotonic()-start,numeric_workers=NUMERIC_WORKERS,method='SLSQP with31explicit continuous-key positive gain constraints and analytic Jacobian' if '--slsqp' in __import__('sys').argv else 'L-BFGS-B with checkpoint guards',selected_basis='v53-wip',existing93_gain_and18_phase_only=True,fixed_baseline_carriers_search_requires_fresh_refit=True,match_reached=False),indent=2));print('V53_JOINT_DONE',fit.status,fit.message,flush=True)
