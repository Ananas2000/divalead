"""Jointly fit93 existing gains+42 existing stereo values; preserve every guard."""
from pathlib import Path
import copy, datetime, json, os, shutil, subprocess, sys, time
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
ROOT=Path(__file__).resolve().parent
RUN=ROOT/'post77-coupled135-research'
RUN.mkdir(exist_ok=False)
SOURCE=ROOT/'source-post74joint-basis'
PREVIOUS=min([p.parent for p in ROOT.glob('post74joint-verified-*/validation.json')],key=lambda p:json.loads((p/'validation.json').read_text())['tone_score'])
BASIS=RUN/'basis';(BASIS/'analysis').mkdir(parents=True)
for source,target in [(PREVIOUS/'analysis/spectral_model.json',BASIS/'analysis/spectral_model.json'),
                      (PREVIOUS/'validation.json',BASIS/'validation.json'),
                      (PREVIOUS/'REFERENCE_EDIT_WIP.wav',BASIS/'REFERENCE_EDIT_WIP.wav'),
                      (SOURCE/'source_manifest.json',BASIS/'source_manifest.json')]:
    shutil.copyfile(source,target)
SCRATCH=Path('/tmp/divalead-post77-coupled135');assert not SCRATCH.exists()
(RUN/'numeric-location.json').write_text(json.dumps(dict(numeric_scratch=str(SCRATCH),temporary=True,
    baseline=str(BASIS),only_three_held=True),indent=2)+'\n')
os.environ.update(DIVALEAD_MODEL_BASE=str(BASIS),DIVALEAD_SELECTION_WORK=str(SCRATCH))
sys.path.insert(0,str(ROOT))
import fit_three_gains as gain
import numpy as np
import soundfile as sf
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor
from project_three_existing_vector import project
import multiprocessing as mp

fields=['log_side_scale','mid_to_side_real','mid_to_side_imag']
balance0=copy.deepcopy(gain.cfg['final_stereo_balance'])
coeff0=np.array([balance0[k] for k in fields]);active=np.delete(np.arange(15),7)
assert coeff0.shape==(3,15) and np.all(coeff0[:,7]==0)
lower=np.r_[gain.lower,np.full(42,-.03)];upper=-lower
def balance_values(p):
    result=copy.deepcopy(balance0);coeff=coeff0.copy();coeff[:,active]+=np.asarray(p).reshape(3,14)
    for name,values in zip(fields,coeff):result[name]=values.tolist()
    return result
def select_balance(balance):
    curves=[np.interp(np.log(np.maximum(gain.f,1)),np.log(balance['anchors_Hz']),np.r_[0,balance[k],0])[:,None] for k in fields]
    gain.ns['scale']=np.exp(curves[0]);gain.ns['mix']=curves[1]+1j*curves[2]
def render(p):
    select_balance(balance_values(p[93:]));return gain.render(p[:93])
def compute(p):
    balance=balance_values(p[93:]);select_balance(balance)
    objective,row,constraints=gain.compute(p[:93])
    row.update(final_stereo_balance=balance,coupled135_offsets=p.tolist(),
               only_existing93_harmonic_gain_values=False,only_existing135_gain_and_final_balance_values=True)
    return objective+.0001*float(np.mean(np.asarray(p[93:])**2)),row,constraints

checks=[]
for sign in [-1,0,1]:
    point=np.zeros(135) if sign==0 else np.random.default_rng(65135+sign).uniform(-.004,.004,135)
    full,_=render(point);gains,phase=gain.changed(point[:93])
    args=dict(gain.kw,harmonic_gain=gains.ravel().tolist(),phase_angles=phase[0].tolist(),
              phase_key_slopes=phase[1].tolist(),phase_key_quadratic=phase[2].tolist(),
              adaptive_dynamic=gain.cfg['dynamic_harmonic_parameters'],
              adaptive_stereo=gain.cfg['stereo_harmonic_parameters'],final_stereo_balance=balance_values(point[93:]))
    independent,_=gain.fullns['spectral_ms'](gain.ns['before'],gain.ns['dry'],48000,8320,gain.cfg['parameters'],**args)
    error=float(np.max(abs(full-independent)));assert error<2e-10
    checks.append(dict(sign=sign,full_independent_max_error=error))
(RUN/'coupled-cache-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('COUPLED135_ZERO_TWO_NONZERO_FULL_INDEPENDENT_PASS',checks,flush=True)

rows=[];cache={};derivatives={};best=float('inf')
def probe(p):
    global best
    key=tuple(p)
    if cache.get('key')!=key:
        result=compute(p);obj,row,con=result;row.update(center=len(rows),objective=obj,minimum_constraint=float(con.min()))
        rows.append(row);cache.update(key=key,result=result)
        temp=gain.V/'latest_center.tmp';temp.write_text(json.dumps(row,indent=2)+'\n');temp.replace(gain.V/'latest_center.json')
        if con.min()>=-1e-12 and row['weighted_score']<best:
            best=row['weighted_score'];temp=gain.V/'best.tmp';temp.write_text(json.dumps(row,indent=2)+'\n');temp.replace(gain.V/'best.json')
            full,edit=render(p);sf.write(gain.V/'best-basepdc.wav',full,48000,subtype='FLOAT');sf.write(gain.V/'best-edit.wav',edit,48000,subtype='FLOAT')
        print('POST77_COUPLED135_CENTER',len(rows),row['weighted_score'],float(con.min()),flush=True)
    return cache['result']
def derive(p):
    if derivatives.get('key')!=tuple(p):
        center=probe(p);points=[];steps=[]
        for j in range(135):
            step=.00025 if p[j]+.00025<=upper[j] else -.00025
            point=p.copy();point[j]+=step;points.append(point);steps.append(step)
        values=list(pool.map(compute,points))
        jac=np.array([(v[2]-center[2])/h for v,h in zip(values,steps)]).T
        jac[-33:-2,:93]=gain.gain_constraints(p[:93])[1];jac[-33:-2,93:]=0
        derivatives.update(key=tuple(p),gradient=np.array([(v[0]-center[0])/h for v,h in zip(values,steps)]),jac=jac)
    return derivatives

if __name__=='__main__':
    start=time.monotonic();initial=np.zeros(135);probe(initial)
    with ProcessPoolExecutor(max_workers=1,mp_context=mp.get_context('fork')) as pool:
        fitted=minimize(lambda p:probe(p)[0],initial,jac=lambda p:derive(p)['gradient'],method='SLSQP',
                        bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=lambda p:probe(p)[2],jac=lambda p:derive(p)['jac'])],
                        options=dict(maxiter=24,ftol=1e-9,disp=False))
    eligible=[r for r in rows if r['weighted_score']<best and r['minimum_constraint']>=-1e-4]
    projection=None
    if eligible:
        seed=min(eligible,key=lambda r:r['weighted_score'])
        point,projection=project(seed['coupled135_offsets'],compute,lower,upper,[list(gain.guards).index('whole'),len(gain.guards)+1+31])
        if point is not None and compute(point)[1]['weighted_score']<best:probe(point)
    (gain.V/'history.json').write_text(json.dumps(rows,indent=2)+'\n')
    (gain.V/'optimizer.json').write_text(json.dumps(dict(status=int(fitted.status),message=str(fitted.message),
        nit=int(fitted.nit),nfev=int(fitted.nfev),elapsed_seconds=time.monotonic()-start,projection=projection,
        existing135_coefficients_only=True,source_base=str(PREVIOUS),all_original_guards_unchanged=True,match_reached=False),indent=2)+'\n')
    old=json.loads((PREVIOUS/'validation.json').read_text())
    if best>=old['tone_score']-1e-6:
        (RUN/'decision.json').write_text(json.dumps(dict(accepted=False,reason='No new feasible improvement from frozen fully proved basis',best_numeric_tone=best,frozen_basis=str(PREVIOUS),full_proof_completed=False,match_reached=False),indent=2)+'\n');print('COUPLED135_NO_NEW_FEASIBLE_TONE_IMPROVEMENT',best,flush=True);raise SystemExit(0)
    target=ROOT/'post74joint-verified-post77-coupled135-0001'
    env=dict(os.environ,DIVALEAD_THREE_SOURCE_BASIS=str(SOURCE),DIVALEAD_THREE_SOURCE_REPORT=str(PREVIOUS/'validation.json'))
    try:
        with (RUN/'validation.log').open('w') as log:
            subprocess.run([sys.executable,'-B',str(ROOT/'validate_three_source_model.py'),str(gain.V),target.name],
                           env=env,stdout=log,stderr=log,check=True,timeout=900)
    except subprocess.CalledProcessError:
        from three_candidate_decision import quality_rejection
        rejected=quality_rejection(RUN/'validation.log',target)
        if rejected is None:raise
        (RUN/'decision.json').write_text(json.dumps(rejected,indent=2)+'\n')
        print('COUPLED135_FRESH_QUALITY_REJECTED',rejected,flush=True)
    else:
        actual=json.loads((target/'validation.json').read_text())
        (RUN/'decision.json').write_text(json.dumps(dict(accepted=True,validation=str(target/'validation.json'),
            tone_score=actual['tone_score'],score=actual['score'],full_proof_completed=True,match_reached=False),indent=2)+'\n')
        print('COUPLED135_FULL_ACTUAL_PASS',actual['tone_score'],flush=True)
