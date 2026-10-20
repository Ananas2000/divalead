"""Existing147 core-matrix values from the best actual-verified power/HF model."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
if os.environ.get('DIVALEAD_CPU_SET'):os.sched_setaffinity(0,{int(v) for v in os.environ['DIVALEAD_CPU_SET'].split(',')})
import sys,ast,json,time,copy,hashlib,multiprocessing as mp
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
RESEARCH=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(RESEARCH));import refine_selected53 as joint
W=RESEARCH;current=W/'CURRENT_RESEARCH_MODEL.json';default_model=W/(json.loads(current.read_text())['model_directory'] if current.exists() else 'after-core-source');B=Path(os.environ.get('DIVALEAD_MODEL_BASE',str(default_model)));V=joint.analysis.WORK/('complete-core-'+B.name);V.mkdir(exist_ok=True)
manifest=json.loads((B/'source_manifest.json').read_text())
for fixture_key in ['source_preset','source_WAV','before_spectral_WAV']:
 assert hashlib.sha256((joint.REPO/manifest[fixture_key]).read_bytes()).hexdigest()==manifest[fixture_key+'_SHA256']
source_fixture=sf.read(joint.REPO/manifest['source_WAV'])[0];before_fixture=sf.read(joint.REPO/manifest['before_spectral_WAV'])[0]
cfg=json.loads((B/'analysis/spectral_model.json').read_text());actual=sf.read(B/'REFERENCE_EDIT_WIP.wav')[0]
from fine_phase_model import extend_prefix,spectral_source,fine_phase_curve,carry_fine_phase
tree=ast.parse((joint.REPO/'diva-lead/research/after-v56/fit_constrained_gains.py').read_text());prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets)).replace('v55','v53')
prefix=prefix.replace("V=ROOT/'constrained-fit'",'V=Path('+repr(str(V))+')').replace("cfg=json.loads((R/'analysis/spectral_model.json').read_text())",'cfg=copy.deepcopy(frozen_cfg)').replace("actual=sf.read(R/'Diva_v53_VIDEO_REFERENCE_EDIT.wav')[0]",'actual=frozen_actual')
prefix=prefix.replace("dry=sf.read(R/'Diva_v53_VIDEO_DIVA_ONLY.wav')[0]",'dry=source_fixture').replace("before=sf.read(R/'Diva_v53_BEFORE_SPECTRAL.wav')[0]",'before=before_fixture')
prefix=extend_prefix(prefix,RESEARCH)
ns={'source_fixture':source_fixture,'before_fixture':before_fixture,'__name__':'selected53_core_capture','Path':Path,'copy':copy,'frozen_cfg':cfg,'frozen_actual':actual};exec(compile(prefix,'selected53_core_capture','exec'),ns)
Z0=ns['Z'];f=ns['f'];f0=ns['f0'];q=ns['q'];h=ns['h'];T=Z0.shape[2];kw=ns['kw'];base_core=np.array([cfg[k] for k in ['parameters','key_slopes','key_quadratic']]).reshape(3,7,7)
source=spectral_source(RESEARCH);i=source.index(' m=Z[0];s=Z[1];out=Z.copy()');rawsource=source[:i]+' return f,t,Z,f0,size,hop,fft\n';rawns={'__name__':'raw_core53'};exec(compile(rawsource,'raw_core53','exec'),rawns)
_,_,raw,_,_,_,_=rawns['spectral_ms'](ns['before'],ns['dry'],48000,8320,cfg['parameters'],**kw)
key=np.log2(f0/100);dist=f[:,None]-np.rint(f[:,None]/f0)*f0;mask=np.exp(-.5*(dist/(cfg['mask_sigma']*f0))**2);off=1-mask;hm=np.exp(-.5*(dist/(cfg['hf_mask_sigma']*f0))**2);ho=1-hm
hc=np.array([np.interp(np.log(np.maximum(f,1)),np.log(cfg['hf_matrix_anchors_Hz']),np.r_[0,row,0]) for row in np.asarray(cfg['hf_matrix_parameters']).reshape(10,10)])[:,:,None]
MM=1+ho*hc[0]+hm*hc[6];MS=ho*(hc[2]+1j*hc[3]);SS=1+ho*hc[1]+hm*hc[7];SM=ho*(hc[4]+1j*hc[5])+hm*(hc[8]+1j*hc[9])
ratio=np.log(np.maximum(f[:,None]/f0,1));phase=sum(np.interp(ratio,np.log(cfg['common_phase_orders']),np.r_[0,cfg[k],0])*key**d for d,k in enumerate(['common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic']))
if cfg.get('fine_phase_harmonic_parameters') is not None:phase+=fine_phase_curve(f,f0,cfg['fine_phase_harmonic_parameters'])
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
from compare_all import wave as crest_definition, TC as target_crest
ANCHOR=json.loads(Path('/workspace/divalead-work/three-held-continuation/baseline/validation.json').read_text())
FIXED_CREST_CAP=float(ANCHOR['crest_RMS_dB'])*1.001
NUMERICAL_CREST_CAP=FIXED_CREST_CAP-1e-5
crest_windows=[(int(a*48000),int(b*48000)) for a,b,_ in crest_definition.WINDOWS]
def crest_values(edit):
 return np.asarray([20*np.log10(np.max(abs(edit[a:b]))/np.sqrt(np.mean(edit[a:b]*edit[a:b]))) for a,b in crest_windows])
def crest_error(edit):return float(np.sqrt(np.mean((crest_values(edit)-target_crest)**2)))
for label,edit in [('zero',neutral),('nonzero',render(np.random.default_rng(1782).uniform(-.01,.01,147))[1])]:
 np.testing.assert_array_equal(crest_values(edit),crest_definition.features(edit)[2])
print('EXACT_CANONICAL_CREST_PARITY_ZERO_AND_NONZERO_PASS',crest_error(neutral),flush=True)
# Freeze carriers at this checked source/model rather than an older v53 source.
# The target powers and shared weights remain untouched. Fresh-carrier acceptance
# still follows a new actual render.
fresh_baseline_powers,joint.carriers,carrier_bounds=joint.analysis.powers(neutral)
assert not any(carrier_bounds)
np.testing.assert_array_equal(joint.fixed_powers(neutral),fresh_baseline_powers)
actual_baseline=json.loads((B/'validation.json').read_text())
current_baseline_metrics=joint.metrics(neutral)
actual_score_error=abs(joint.score(current_baseline_metrics)-actual_baseline['score'])
assert actual_score_error<1e-6,actual_score_error
(V/'current-carrier-baseline.json').write_text(json.dumps(dict(carriers_Hz=joint.carriers,carrier_at_bounds=False,fixed_power_array_exactly_matches_fresh_baseline=True,actual_baseline_score=actual_baseline['score'],numeric_baseline_score=joint.score(current_baseline_metrics),baseline_score_max_error=actual_score_error,acceptance_still_requires_new_fresh_actual_render=True,match_reached=False),indent=2))
print('CURRENT_SOURCE_MODEL_CARRIERS_BASELINE_PARITY_PASS',actual_score_error,flush=True)
base=joint.metrics(neutral)
TONE_WEIGHTS=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
score=lambda values:sum(TONE_WEIGHTS[k]*values[k]/joint.scales[k] for k in TONE_WEIGHTS)
lower=np.full(147,-.10);upper=-lower
guards=dict(H24=1.001,upper_harm=1.001,upper_off=1.001,low_harm=1.002,ERB=1.001,relative_phase=1.002,whole=1.001,envelope=1.001,body=1.002,stereo_phase=1.002,stereo_balance=1.002)
from search_global_guards import repair_near_feasible_rows
baseline_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));core=base_core+np.asarray(p).reshape(3,7,7)
 con=np.r_[[limit-m[k]/ANCHOR['metrics'][k] for k,limit in guards.items()],.99-peak,1-crest_error(e)/NUMERICAL_CREST_CAP,1.0001-joint.score(m)/ANCHOR['score']]
 row=dict(metrics=m,weighted_score=score(m),peak=peak,feasible_search_guards=bool(con.min()>=-1e-12),core_offsets=p.tolist(),parameters=core[0].ravel().tolist(),key_slopes=core[1].ravel().tolist(),key_quadratic=core[2].ravel().tolist(),**{k:cfg[k] for k in ['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','dynamic_harmonic_parameters','final_stereo_balance','stereo_harmonic_parameters']},only_existing147_core_values_changed_from_frozen_complete_model=True,crest_RMS_dB=crest_error(e),fixed_crest_cap_dB=FIXED_CREST_CAP,numerical_crest_cap_dB=NUMERICAL_CREST_CAP,fixed_crest_constraint_enforced=True,current_checked_source_model_carriers=True,baseline_model_SHA256=baseline_hash,source_manifest=manifest,guard_limits=guards,tone_focused_weights=TONE_WEIGHTS,standard_weighted_score=joint.score(m),user_selected_three_baseline=True,all_DSP_tolerances_unchanged=True,match_reached=False)
 carry_fine_phase(row,cfg)
 return score(m)+.0001*float(np.mean(p*p)),row,con
rows=[];last={};best=np.inf;derivatives={}
def probe(p):
 global best
 if last.get('key')!=tuple(p):
  obj,row,con=compute(p);row.update(center=len(rows),objective=obj,minimum_constraint=float(np.min(con)));rows.append(row);last.update(key=tuple(p),result=(obj,row,con));tmp=V/'latest_center.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'latest_center.json')
  if np.min(con)>=-1e-12 and row['weighted_score']<best:
   best=row['weighted_score'];tmp=V/'best.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(V/'best.json');full,e=render(p);sf.write(V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(V/'best-edit.wav',e,48000,subtype='FLOAT')
  print('COMPLETE_CORE_CENTER',len(rows),'score',row['weighted_score'],'H24',row['metrics']['H24'],'constraintMin',float(np.min(con)),flush=True)
 return last['result']
def derive(p):
 key=tuple(p)
 if derivatives.get('key')!=key:
  center=probe(p);points=[];steps=[]
  for j in range(147):
   step=.000025 if p[j]+.000025<=upper[j] else -.000025;pp=p.copy();pp[j]+=step;points.append(pp);steps.append(step)
  values=list(pool.map(compute,points));derivatives.update(key=key,gradient=np.array([(v[0]-center[0])/s for v,s in zip(values,steps)]),jac=np.array([(v[2]-center[2])/s for v,s in zip(values,steps)]).T)
 return derivatives
if __name__=='__main__':
 start=time.monotonic();initial=np.zeros(147)
 if '--check-only' in sys.argv:
  result=compute(initial);assert np.min(result[2])>=-1e-12;assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];assert result[1]['stereo_harmonic_parameters']==cfg['stereo_harmonic_parameters'];assert result[1].get('fine_phase_harmonic_parameters')==cfg.get('fine_phase_harmonic_parameters');print('COMPLETE_MODEL_CORE_CHECKED',B.name,flush=True);raise SystemExit(0)
 path=V/'best.json'
 if path.exists():
  row=json.loads(path.read_text())
  if row.get('baseline_model_SHA256')==baseline_hash:
   candidate=np.asarray(row['core_offsets']);value=compute(candidate)
   if np.min(value[2])>=-1e-12 and value[0]<compute(initial)[0]:
    (V/'resume-origin.json').write_text(json.dumps(row,indent=2));initial=candidate.copy()
  else:
   archive=V/('previous-model-'+str(row.get('baseline_model_SHA256','unknown'))[:16]+'-best.json');archive.write_text(json.dumps(row,indent=2))
 probe(initial)
 with ProcessPoolExecutor(max_workers=int(os.environ.get('DIVALEAD_NUMERIC_WORKERS','2')),mp_context=mp.get_context('fork')) as pool:fit=minimize(lambda p:probe(p)[0],initial,jac=lambda p:derive(p)['gradient'],method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:probe(p)[2],jac=lambda p:derive(p)['jac'])],options=dict(maxiter=int(os.environ.get('DIVALEAD_MAXITER','45')),ftol=1e-9,disp=False))
 repair=repair_near_feasible_rows(rows,best,initial,'core_offsets',compute,probe)
 from project_three_existing_vector import project
 projection=None
 eligible=[row for row in rows if row['minimum_constraint']>=-.05 and row['weighted_score']<best]
 if eligible:
  seed=min(eligible,key=lambda row:row['weighted_score'])
  point,projection=project(seed['core_offsets'],compute,lower,upper,[list(guards).index('whole'),len(guards)+2])
  if point is not None and compute(point)[1]['weighted_score']<best:probe(point)
 (V/'history.json').write_text(json.dumps(rows,indent=2));(V/'optimizer.json').write_text(json.dumps(dict(near_feasible_repair=repair,interior_projection=projection,status=int(fit.status),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev),elapsed_seconds=time.monotonic()-start,source_base=B.name,source_hashes_checked=True,baseline_model_SHA256=baseline_hash,existing147_core_values_only=True,method='SLSQP with shared finite-difference objective and constraint Jacobians',original_three_guards_unchanged=True,new_source_requires_its_matching_independent_prebase=True,match_reached=False),indent=2));print('COMPLETE_CORE_DONE',fit.status,fit.message,flush=True)
