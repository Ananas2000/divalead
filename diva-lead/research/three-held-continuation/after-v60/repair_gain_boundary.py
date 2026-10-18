from pathlib import Path
import os,sys,json,time
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
R=Path(__file__).resolve().parent
os.environ['DIVALEAD_MODEL_BASE']=str(R/'phase18-basis');os.environ['DIVALEAD_SELECTION_WORK']=str(R/'gain-boundary-repair')
sys.path.insert(0,str(R));import fit_three_gains as f
import numpy as np
from scipy.optimize import minimize
old=json.loads((R/'continuation/round-0002-gain/numeric/complete-joint-basis/latest_center.json').read_text());assert old['baseline_model_SHA256']==f.baseline_hash
f.probe(np.zeros(93));origin=np.array(old['offsets']);original=f.compute(origin)
# Repair only a few existing gain values; all other coefficients remain exact.
margin,_=f.gain_constraints(origin);eligible=np.flatnonzero(margin>.002);free=eligible[np.linspace(0,len(eligible)-1,min(12,len(eligible)),dtype=int)]
assert len(free)>=4
indexes=np.r_[np.arange(12),12+free,43,44];scale=.001
lower=np.maximum(-1.,(-.1-origin[free])/scale);upper=np.minimum(1.,(.1-origin[free])/scale)
cache={}
def evaluate(q):
 k=tuple(q)
 if k not in cache:
  p=origin.copy();p[free]+=q*scale;cache[k]=f.compute(p)
 return cache[k]
def constraints(q):return evaluate(q)[2][indexes]
start=time.monotonic();fit=minimize(lambda q:float(q@q),np.zeros(len(free)),jac=lambda q:2*q,method='SLSQP',bounds=list(zip(lower,upper)),constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=20,ftol=1e-14,disp=False))
p=origin.copy();p[free]+=fit.x*scale;_,row,con=f.compute(p)
accepted=bool(np.min(con)>=-1e-12 and row['weighted_score']<f.best-1e-6)
if accepted:f.probe(p)
(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n')
report=dict(status=int(fit.status),message=str(fit.message),elapsed_seconds=time.monotonic()-start,origin_tone=original[1]['weighted_score'],origin_minimum_constraint=float(np.min(original[2])),repaired_tone=row['weighted_score'],repaired_minimum_constraint=float(np.min(con)),accepted_numeric=accepted,free_gain_indices=free.tolist(),gain_offset_corrections=(fit.x*scale).tolist(),all_original_guards_and_feasibility_tolerance_unchanged=True,requires_fresh_actual_proof=True,match_reached=False)
(f.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n');print('GAIN_BOUNDARY_REPAIR_RESULT',json.dumps(report),flush=True)
