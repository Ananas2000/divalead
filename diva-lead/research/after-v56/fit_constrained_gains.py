"""Standalone93-gain continuation with explicit nonlinear timbre constraints.
Requires only committed55 assets; output is an unvalidated research candidate.
"""
import ast,json,multiprocessing as mp,os,time
from concurrent.futures import ProcessPoolExecutor
import numpy as np,soundfile as sf
from scipy.optimize import least_squares
from scipy.signal import butter,sosfilt
from audio_match_helpers import HERE,ROOT,REPO,SR,REFERENCE,HT,measure,harmonic_errors
M=REPO/'diva-lead/v55-wip';V=ROOT/'constrained-fit';V.mkdir(exist_ok=True)
os.sched_setaffinity(0,set(sorted(os.sched_getaffinity(0))[:2]))
assert json.loads((M/'analysis/spectral_independent_checks.json').read_text())['full_independent_pipeline_max_error']<3e-7
prefix='"""Optimize existing power-target coefficients against the rendered reference.\n\nExact cached pre-feedback frames and moments, verified against actual50.\nFour numeric workers; no additional runtime feature, states or reference lookup.\n"""\nimport json,multiprocessing as mp,time\nfrom concurrent.futures import ProcessPoolExecutor\nimport numpy as np,soundfile as sf\nfrom scipy.signal import istft,lfilter\nfrom scipy.optimize import least_squares,minimize_scalar\nfrom audio_match_helpers import HERE,ROOT,REPO,SR,REFERENCE,HT,measure,harmonic_errors,align_with_pdc,edit_aligned\nR=REPO/\'diva-lead/v55-wip\';V=ROOT/\'constrained-fit\';V.mkdir(exist_ok=True)\ncfg=json.loads((R/\'analysis/spectral_model.json\').read_text());c=json.loads((R/\'analysis/selected_candidate.json\').read_text());dry=sf.read(R/\'Diva_v55_VIDEO_DIVA_ONLY.wav\')[0];before=sf.read(R/\'Diva_v55_BEFORE_SPECTRAL.wav\')[0]\nsource=(R/\'analysis/independent_spectral_ms.py\').read_text();i=source.index(\' if adaptive_dynamic is not None:out=\');source=source[:i]+\' return f,t,out,f0,size,hop,fft\\n\';ns={\'__name__\':\'capture218\'};exec(compile(source,\'capture218\',\'exec\'),ns)\nkw=dict(sigma=cfg[\'mask_sigma\'],key_quadratic=cfg[\'key_quadratic\'],key_slopes=cfg[\'key_slopes\'],phase_angles=cfg[\'common_phase_radians\'],hf_parameters=cfg[\'hf_matrix_parameters\'],hf_anchors=cfg[\'hf_matrix_anchors_Hz\'],upper_rolloff=cfg[\'upper_rolloff_Hz\'],harmonic_gain=cfg[\'harmonic_gain_parameters\'],gain_orders=cfg[\'harmonic_gain_orders\'],hf_sigma=cfg[\'hf_mask_sigma\'],phase_key_slopes=cfg[\'common_phase_key_slopes\'],phase_key_quadratic=cfg[\'common_phase_key_quadratic\'],core_anchors=cfg[\'anchors_Hz\'])\nf,t,Z,f0,size,hop,fft=ns[\'spectral_ms\'](before,dry,SR,8320,cfg[\'parameters\'],**kw);key=np.log2(f0/100);q=np.floor(f[:,None]/f0+.5).astype(int);h=np.exp(-.5*((f[:,None]-q*f0)/(.23*f0))**2);power=abs(Z)**2\nmom=np.array([np.sum(power*(h*(q==o))[None],axis=1) for o in range(1,25)]).transpose(1,0,2)\naa=np.array([np.sum(power*(h**3*(q==o))[None],axis=1) for o in range(2,25)]).transpose(1,0,2)\nbb=np.array([2*np.sum(power*(h*h*(1-h)*(q==o))[None],axis=1) for o in range(2,25)]).transpose(1,0,2)\ncc=np.array([np.sum(power*(h*(1-h)**2*(q==o))[None],axis=1) for o in range(2,25)]).transpose(1,0,2)\nunit=mom[:,0].sum(axis=0);norm=lambda a:np.divide(a.sum(axis=0),unit,out=np.zeros_like(a[0]),where=unit>0)\nan,bn,cn=norm(aa),norm(bb),norm(cc);dyn=cfg[\'dynamic_harmonic_parameters\'];st=cfg[\'stereo_harmonic_parameters\'];base_target=np.asarray(dyn[\'target_logpower_db_polynomial\']);target_st=np.clip(sum(np.asarray(st[\'target_stereo_logodds_db_polynomial\'])[d,:,None]*key**d for d in range(5)),-60,20)\nstrength=np.asarray(dyn[\'group_strengths\'])[:,None];alpha=np.exp(-(hop/SR)/dyn[\'tau_seconds\']);alpha_st=np.exp(-(hop/SR)/st[\'tau_seconds\']);limit=dyn[\'limit_db\']*np.log(10)/20;limit_st=st[\'limit_db\']*np.log(10)/20\ngather=np.clip(q-2,0,22);active=(q>=2)&(q<=24);gather_st=np.clip(q-1,0,23);active_st=(q>=1)&(q<=24)\nbalance=cfg[\'final_stereo_balance\'];curves=[np.interp(np.log(np.maximum(f,1)),np.log(balance[\'anchors_Hz\']),np.r_[0,balance[k],0])[:,None] for k in [\'log_side_scale\',\'mid_to_side_real\',\'mid_to_side_imag\']];scale=np.exp(curves[0]);mix=curves[1]+1j*curves[2]\ndef render(p):\n target=base_target.copy();target[:3]+=np.asarray(p).reshape(3,23);td=np.clip(sum(target[d,:,None]*key**d for d in range(5)),-120,20);goal=10**(td/10);delta=goal-cn\n desired=np.maximum(np.where(delta>0,2*delta/np.maximum(bn+np.sqrt(np.maximum(bn*bn+4*an*delta,0)),1e-30),1e-6),1e-6);lg=np.log(desired);lg[:,unit<=0]=0\n gain=np.exp(lfilter([1-alpha],[1,-alpha],strength*np.clip(lg,-limit,limit),axis=1));curve=1+h*(np.take_along_axis(gain,gather,axis=0)-1)*active;out=Z*curve[None]\n moments=mom.copy();moments[:,1:]=aa*gain[None]**2+bb*gain[None]+cc;total=moments.sum(axis=0);fraction=np.clip(np.divide(moments[1],total,out=np.full_like(total,.5),where=total>0),1e-9,1-1e-9)\n wanted=.25*(target_st*np.log(10)/10-np.log(fraction/(1-fraction)));wanted[total<=0]=0;ls=lfilter([1-alpha_st],[1,-alpha_st],st[\'strength\']*np.clip(wanted,-limit_st,limit_st),axis=1)\n gm=1+h*(np.take_along_axis(np.exp(-ls),gather_st,axis=0)-1)*active_st;gs=1+h*(np.take_along_axis(np.exp(ls),gather_st,axis=0)-1)*active_st\n oldpower=np.sum(abs(out)**2,axis=0);changed=out*np.stack([gm,gs]);newpower=np.sum(abs(changed)**2,axis=0);out=changed*np.sqrt(np.divide(oldpower,newpower,out=np.ones_like(oldpower),where=newpower>0))[None]\n changed=np.stack([out[0],scale*out[1]+mix*out[0]]);newpower=np.sum(abs(changed)**2,axis=0);out=changed*np.sqrt(np.divide(oldpower,newpower,out=np.ones_like(oldpower),where=newpower>0))[None];out[:,0]=out[:,0].real;out[:,-1]=out[:,-1].real\n _,y=istft(out,fs=SR,nperseg=size,noverlap=size-hop,nfft=fft);y=y[:,:len(before)];full=np.c_[y[0]+y[1],y[0]-y[1]];return full,edit_aligned(align_with_pdc(full,c[\'settings\']))\nneutral_full,neutral=render(np.zeros(69));actual=sf.read(R/\'Diva_v55_VIDEO_REFERENCE_EDIT.wav\')[0];np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7);print(\'TARGET218_CLOSED_MOMENT_NEUTRAL_ACTUAL50_PASS\',np.max(abs(neutral-actual)),flush=True)\n'
ns={'__name__':'erb330_exact_capture'};exec(compile(prefix,'erb330_exact_capture','exec'),ns)
cfg=ns['cfg'];Z0=ns['Z'];f=ns['f'];f0=ns['f0'];q=ns['q'];h=ns['h'];T=Z0.shape[2];kw=ns['kw'];base_gain=np.asarray(cfg['harmonic_gain_parameters']).reshape(3,31)
args=dict(kw,harmonic_gain=None);_,_,pre,_,_,_,_=ns['ns']['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**args)
ratio=np.maximum(f[:,None]/f0,1);key=np.log2(f0/100);distance=f[:,None]-np.rint(f[:,None]/f0)*f0;gainmask=np.exp(-.5*(distance/(cfg['mask_sigma']*f0))**2)
knots=np.log(cfg['harmonic_gain_orders']);value=np.log(ratio);index=np.clip(np.searchsorted(knots,value,side='right')-1,0,len(knots)-2);u=np.clip((value-knots[index])/(knots[index+1]-knots[index]),0,1)
selected=(q>=1)&(q<=24);where=selected.ravel();indices=(q*T+np.arange(T)[None]).ravel()[where];hm=h.ravel()[where];weights=[hm,hm**3,2*hm*hm*(1-hm),hm*(1-hm)**2]
def moments(z):
 pw=(abs(z)**2).reshape(2,-1)[:,where];a=[]
 for weight in weights:a.append(np.stack([np.bincount(indices,weights=p*weight,minlength=25*T).reshape(25,T)[1:25] for p in pw]))
 mom=a[0];aa,bb,cc=[v[:,1:] for v in a[1:]];unit=mom[:,0].sum(axis=0);norm=lambda a:np.divide(a.sum(axis=0),unit,out=np.zeros_like(a[0]),where=unit>0)
 return mom,aa,bb,cc,unit,norm(aa),norm(bb),norm(cc)
def changed_gain(p):return base_gain+np.asarray(p).reshape(3,31)
def render(p):
 delta=np.pad(np.asarray(p).reshape(3,31),((0,0),(1,1)));curve=sum(((1-u)*delta[d,index]+u*delta[d,index+1])*key**d for d in range(3));z=Z0+pre*(gainmask*curve)[None];ns['Z']=z
 for name,v in zip(['mom','aa','bb','cc','unit','an','bn','cn'],moments(z)):ns[name]=v
 return ns['render'](np.zeros(69))
_,neutral=render(np.zeros(93));actual=sf.read(M/'Diva_v55_VIDEO_REFERENCE_EDIT.wav')[0];np.testing.assert_allclose(neutral,actual,rtol=0,atol=2e-7)
fullns={'__name__':'erb330_full_independent'};exec(compile((M/'analysis/independent_spectral_ms.py').read_text(),'erb330_full_independent','exec'),fullns);errors=[]
for sign in [-1,1]:
 p=np.random.default_rng(330+sign).uniform(-.015,.015,93);args=dict(kw,harmonic_gain=changed_gain(p).ravel().tolist(),adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);direct,_=fullns['spectral_ms'](ns['before'],ns['dry'],SR,8320,cfg['parameters'],**args);cached,_=render(p);np.testing.assert_allclose(cached,direct,rtol=0,atol=2e-10);errors.append(float(np.max(abs(cached-direct))))
(V/'cache_checks.json').write_text(json.dumps(dict(neutral_actual_error=float(np.max(abs(neutral-actual))),two_nonzero_full_SciPy_errors=errors,existing93_controls_only=True),indent=2));print('CONSTRAINED_GAIN_RESEARCH_ACTUAL_ZERO_TWO_NONZERO_FULL_INDEPENDENT_PASS',errors,flush=True)
windows=[]
for r in range(2):
 for i in range(8):
  a=r*7/3+i/6+.045;windows.append((int(a*SR),int((a+.085)*SR)))
F=np.fft.rfftfreq(16384,1/SR);erb=lambda f:21.4*np.log10(1+.00437*np.asarray(f));centers=np.linspace(erb(40),erb(16000),40);bank=np.exp(-.5*((erb(F)[None]-centers[:,None])/.5)**2);band=(F>=40)&(F<=16000);bank[:,~band]=0
def erb_power(x):
 result=[]
 for lo,hi in windows:
  y=x[lo:hi];pw=np.sum(abs(np.fft.rfft(y*np.hanning(len(y))[:,None],16384,axis=0))**2,axis=1);result.append(bank@pw/max(float(pw[band].sum()),1e-30))
 return np.asarray(result)
target=erb_power(REFERENCE);auditory_weight=np.maximum(target,1e-6)**.2;auditory_weight/=auditory_weight.sum();sw_erb=np.sqrt(auditory_weight);baseline_erb=10*np.log10(np.maximum(erb_power(neutral),1e-12)/np.maximum(target,1e-12));base_erb_error=float(np.sqrt(np.sum(baseline_erb**2*auditory_weight)))
(V/'erb_analysis.json').write_text(json.dumps(dict(centers_Hz=((10**(centers/21.4)-1)/.00437).tolist(),ERB_width=.5,FFT_size=16384,windows_frames=windows,reference_relative_power=target.tolist(),baseline_db_error=baseline_erb.tolist(),baseline_weighted_RMS_db=base_erb_error,analysis_only_not_runtime_or_perceptual_percentage=True),indent=2))
bm=measure(neutral);bh=harmonic_errors(neutral)['weighted_harmonic_error_db'];hw=np.maximum(HT,1e-5)**.5;hw[:,0]=0;hw/=hw.sum();sw=np.sqrt(hw)
filters=[butter(3,b,fs=SR,btype='bandpass',output='sos') for b in [(40,300),(300,800),(800,1600),(1600,2500),(2500,4000),(4000,6500),(6500,10000),(10000,14000),(14000,16000)]]
def lr(x):
 out=[]
 for sos in filters:
  y=sosfilt(sos,x,axis=0);p=np.mean(y*y,axis=0);out.append(10*np.log10(p[1]/p[0]))
 return np.asarray(out)
target_lr=lr(REFERENCE);upper=np.full(93,.25);lower=-upper;gain_keys=np.linspace(*np.log2([45/100,220/100]),101)
def compute(p):
 full,e=render(p);m=measure(e);h=harmonic_errors(e);he=h['weighted_harmonic_error_db'];er=10*np.log10(np.maximum(erb_power(e),1e-12)/np.maximum(target,1e-12));error=float(np.sqrt(np.sum(er*er*auditory_weight)));balance=lr(e)-target_lr;lr_error=float(np.sqrt(np.mean(balance**2)));peak=float(np.max(abs(full)));gain=changed_gain(p);minimum=1+sum(gain[d,:,None]*gain_keys**d for d in range(3))
 res=np.r_[4*(er*sw_erb).ravel()/base_erb_error,np.sqrt(2)*(np.asarray(h['harmonic_errors_db'])*sw).ravel()/bh,m['weighted_db_error']/bm['weighted_db_error'],m['whole_distance']/bm['whole_distance'],np.sqrt(.5)*m['envelope12_error']/bm['envelope12_error'],np.sqrt(.5)*m['body_level_error_db']/bm['body_level_error_db'],100*max(he/bh-1.001,0),100*max(m['weighted_db_error']/bm['weighted_db_error']-1.005,0),100*max(m['envelope12_error']/bm['envelope12_error']-1.01,0),100*max(m['body_level_error_db']/bm['body_level_error_db']-1.02,0),80*max(lr_error/.5-1,0),80*max(peak-.99,0),150*np.maximum(.08-minimum,0).ravel(),.025*p,.02*np.diff(p.reshape(3,31),axis=1).ravel()]
 return res,dict(metrics=m,harmonics=h,weighted_ERB_RMS_error_db=error,band_LR_RMS_error_db=lr_error,cost=float(np.linalg.norm(res)),peak=peak,min_gain_on101_keys=float(minimum.min()))
# Analysis only: fixed, separately fitted carriers from the actual55 diagnostic.
PUBLIC=REPO/'diva-lead/v55-wip'
upper_diagnostic=json.loads((PUBLIC/'analysis/stationary_upper_power_measurements.json').read_text())
upper_bands=upper_diagnostic['bands_Hz'];upper_f=np.fft.rfftfreq(65536,1/SR)
upper_windows=[(int(a*SR),int(b*SR)) for a,b,_ in upper_diagnostic['windows']]
def upper_power(x,carriers):
 result=[]
 for (lo,hi),carrier in zip(upper_windows,carriers):
  y=x[lo:hi];ms=np.c_[y.mean(axis=1),.5*(y[:,0]-y[:,1])];pw=abs(np.fft.rfft(ms*np.hanning(len(y))[:,None],65536,axis=0))**2
  harmonic=abs(upper_f-np.rint(upper_f/carrier)*carrier)<.23*carrier;unit=pw[abs(upper_f-carrier)<.23*carrier].sum()
  result.append([[float(pw[(upper_f>=low)&(upper_f<high)&mask,ch].sum()/unit) for mask in [harmonic,~harmonic] for ch in [0,1]] for low,high in upper_bands])
 return np.asarray(result)
reference_carriers=upper_diagnostic['fitted_carriers_Hz']['reference'];current_carriers=upper_diagnostic['fitted_carriers_Hz']['v55']
upper_target=upper_power(REFERENCE,reference_carriers)
def upper_errors(x):return 10*np.log10(np.maximum(upper_power(x,current_carriers),1e-15)/np.maximum(upper_target,1e-15))
actual55=sf.read(PUBLIC/'Diva_v55_VIDEO_REFERENCE_EDIT.wav')[0]
np.testing.assert_allclose(upper_errors(actual55),upper_diagnostic['results']['v55']['window_errors_db'],rtol=0,atol=1e-10)
upper_baseline=upper_errors(neutral);upper_rms=np.sqrt(np.mean(upper_baseline**2,axis=0));upper_scale=np.maximum(upper_rms,.5)
original_compute=compute;original_render=render;last_edit=[None]
def render(p):
 result=original_render(p);last_edit[0]=result[1];return result
def compute(p):
 res,row=original_compute(p);ue=upper_errors(last_edit[0]);rms=np.sqrt(np.mean(ue*ue,axis=0))
 # Shape across all fitted notes, with Mid/Side and harmonic/off components retained.
 res=np.r_[res,np.sqrt(8)*(ue/upper_scale[None]).ravel()/np.sqrt(ue.size),200*np.maximum(rms[:,:2]/upper_rms[:,:2]-1.01,0).ravel()]
 row.update(cost=float(np.linalg.norm(res)),upper_fixed_carrier_RMS_db=rms.tolist(),upper_harmonic_max_ratio55=float(np.max(rms[:,:2]/upper_rms[:,:2])),upper_fixed_carrier_analysis_only=True)
 return res,row
(V/'upper_analysis_definition.json').write_text(json.dumps(dict(bands_Hz=upper_bands,component_order=upper_diagnostic['component_order'],FFT_size=65536,window_frames=upper_windows,carriers_for_reference=reference_carriers,carriers_for_current=current_carriers,baseline_upper_RMS_db=upper_rms.tolist(),fixed_carriers_for_smooth_search=True,requires_fresh_carrier_refit_after_actual_selection=True,not_isolated_hiss_or_listening_score=True),indent=2))

from scipy.optimize import minimize
rows=[];best=np.inf;last={};derivatives={}
def exact_gain_minimum(p):
 gain=changed_gain(p);lo,hi=np.log2(np.asarray([45,220])/100);out=[]
 for a,b,q in gain.T:
  points=[lo,hi]
  if q>0 and lo<-b/(2*q)<hi:points.append(-b/(2*q))
  out.append(min(1+a+b*k+q*k*k for k in points))
 return np.asarray(out)
def constraints_for(p,row):
 m=row['metrics'];up=np.asarray(row['upper_fixed_carrier_RMS_db'])
 return np.r_[1.00005-row['harmonics']['weighted_harmonic_error_db']/bh,(1.009-up[:,:2]/upper_rms[:,:2]).ravel(),(1.02-up[:,2:]/upper_rms[:,2:]).ravel(),1.005-m['weighted_db_error']/bm['weighted_db_error'],1.005-m['whole_distance']/bm['whole_distance'],1.01-m['envelope12_error']/bm['envelope12_error'],1.02-m['body_level_error_db']/bm['body_level_error_db'],(.5-row['band_LR_RMS_error_db'])/.5,.99-row['peak'],exact_gain_minimum(p)-.02]
def compute_constrained(p):
 res,row=compute(p);con=constraints_for(p,row);return res,row,con
def record(p,result,center):
 global best
 res,row,con=result;row=dict(row,trial=len(rows),offsets=p.tolist(),accepted_center=center,minimum_constraint=float(np.min(con)),constraint_values=con.tolist(),explicit_non_linear_constraints=True,existing93_coefficients_only=True,match_reached=False);rows.append(row)
 if center and row['cost']<best and np.min(con)>=0 and np.all(p>=lower) and np.all(p<=upper):
  best=row['cost'];row['harmonic_gain_parameters']=changed_gain(p).ravel().tolist();(V/'best.json').write_text(json.dumps(row,indent=2));full,e=render(p);sf.write(V/'best-basepdc.wav',full,SR,subtype='FLOAT');sf.write(V/'best-edit.wav',e,SR,subtype='FLOAT')
 if center:
  checkpoint=V/'latest_center.json';temporary=checkpoint.with_suffix('.tmp');temporary.write_text(json.dumps(row,indent=2));temporary.replace(checkpoint)
 if center:print('CONSTRAINED_GAIN_RESEARCH_CENTER',len(rows),'cost',row['cost'],'ERBdb',row['weighted_ERB_RMS_error_db'],'H24',row['harmonics']['weighted_harmonic_error_db'],'constraintMin',row['minimum_constraint'],flush=True)
 return res,row,con
def probe(p):
 key=tuple(p)
 if last.get('key')!=key:
  result=record(p,compute_constrained(p),True);last.update(key=key,result=result)
 return last['result']
def objective(p):
 res,_,_=probe(p);return float(res@res)
def constraint_values(p):return probe(p)[2]
def derive(p):
 key=tuple(p)
 if derivatives.get('key')==key:return derivatives['objective'],derivatives['constraints']
 res,_,con=probe(p);points=[];steps=[]
 for j in range(93):
  step=.00025 if p[j]+.00025<=upper[j] else -.00025;point=p.copy();point[j]+=step;points.append(point);steps.append(step)
 J=[];C=[]
 for point,step,result in zip(points,steps,pool.map(compute_constrained,points)):
  value,_,cv=record(point,result,False);J.append((value-res)/step);C.append((cv-con)/step)
 grad=2*np.asarray(J)@res;cjac=np.asarray(C).T;derivatives.update(key=key,objective=grad,constraints=cjac);return grad,cjac
def objective_gradient(p):return derive(p)[0]
def constraint_gradient(p):return derive(p)[1]
if __name__=='__main__':
 import sys
 if '--check-only' in sys.argv:
  res,row,con=compute_constrained(np.zeros(93));assert np.isfinite(res).all() and np.min(con)>=0
  print('PORTABLE_AFTER56_CACHE_TWO_NONZERO_METRICS_CONSTRAINTS_PASS',float(np.min(con)),flush=True);raise SystemExit(0)
 if '--render-seed' in sys.argv:
  seed=json.loads((HERE/'feasible_gain_seed.json').read_text());point=np.asarray(seed['offsets']);res,row,con=compute_constrained(point);assert np.min(con)>=0
  full,edit=render(point);actual=sf.read(HERE/'GUARDED_GAIN_RESEARCH_EDIT.wav')[0];np.testing.assert_allclose(edit,actual,rtol=0,atol=2e-7)
  sf.write(V/'seed-preview.wav',edit,48000,subtype='FLOAT');report=dict(max_error_against_actual_Windows_edit=float(np.max(abs(edit-actual))),minimum_constraint=float(np.min(con)),match_reached=False);(V/'seed-preview-validation.json').write_text(json.dumps(report,indent=2));print('PORTABLE_CHECKED_SEED_RECONSTRUCTION_PASS',report,flush=True);raise SystemExit(0)
 start=time.monotonic();initial=np.zeros(93)
 choices=[]
 for warm in [ROOT/'resume_offsets.json',V/'best.json',HERE/'feasible_gain_seed.json']:
  if warm.exists():
   possible=np.asarray(json.loads(warm.read_text())['offsets']);result=compute_constrained(possible)
   if np.min(result[2])>=0:choices.append((result[1]['cost'],possible,str(warm)))
 if choices:
  _,initial,origin=min(choices,key=lambda item:item[0]);(V/'resume_origin.json').write_text(json.dumps(dict(path=origin,offsets=initial.tolist(),same_objective_bounds_regularization=True,optimizer_Hessian_not_restored=True),indent=2))
 with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('fork')) as pool:
  fit=minimize(objective,initial,jac=objective_gradient,method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=constraint_values,jac=constraint_gradient)],options=dict(maxiter=60,ftol=1e-9,disp=False))
 probe(fit.x)
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(status=int(fit.status),message=str(fit.message),success=bool(fit.success),nfev=int(fit.nfev),nit=int(fit.nit),observed_evaluations=len(rows),elapsed_seconds=time.monotonic()-start,numeric_workers=2,method='SLSQP with finite-difference objective and explicit constraint Jacobians',existing93_gain_values_only=True,no_new_DSP_or_source=True,match_reached=False),indent=2));print('CONSTRAINED_GAIN_RESEARCH_DONE',fit.status,fit.message,flush=True)
