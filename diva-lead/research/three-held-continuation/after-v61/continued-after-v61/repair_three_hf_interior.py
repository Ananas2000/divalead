"""Project a near-feasible three-held HF point inside unchanged fixed guards.

The saved seed is exploratory. Only a separate fresh Diva/Windows/full-NEW proof
can accept this point. No source, note, state, guard or test tolerance changes.
"""
from pathlib import Path
import os,sys,json
R=Path(__file__).resolve().parent
run=Path(sys.argv[1]);run.mkdir(exist_ok=False)
seedpath=Path(sys.argv[2]);seed=json.loads(seedpath.read_text());(run/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
basis=Path(sys.argv[3]);os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(run/'numeric'))
sys.path.insert(0,str(R));import fit_three_hf_fixed_anchor as f
import numpy as np
from scipy.optimize import minimize
assert seed['baseline_model_SHA256']==f.baseline_hash
p=np.asarray(seed['HF_offsets'],dtype=float);free=np.r_[np.arange(10),np.arange(60,70)];initial=f.compute(np.zeros(100))[1]['weighted_score']
f.probe(np.zeros(100));steps=[];important=np.array([list(f.guards).index('whole'),len(f.guards)+1]);margin=5e-7
for turn in range(5):
 _,row,con=f.compute(p)
 if con.min()>=-1e-12 and con[important].min()>2e-7:break
 columns=[]
 for j in free:
  h=1e-5;plus=p.copy();minus=p.copy();plus[j]+=h;minus[j]-=h
  columns.append((f.compute(plus)[2]-f.compute(minus)[2])/(2*h))
 matrix=np.array(columns).T
 target=np.zeros_like(con);target[important]=margin
 required=target-con
 # Scale coordinates so tiny physical corrections have a well-conditioned cost.
 scale=.001;J=matrix*scale
 bounds=[(max(-.008,f.lower[j]-p[j])/scale,min(.008,f.upper[j]-p[j])/scale) for j in free]
 solve=minimize(lambda x:.5*float(x@x),np.zeros(len(free)),jac=lambda x:x,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=lambda x:J@x-required,jac=lambda x:J)],options=dict(ftol=1e-12,maxiter=100))
 assert np.min(J@solve.x-required)>=-1e-10,(solve.message,float(np.min(J@solve.x-required)))
 delta=solve.x*scale;p[free]+=delta
 _,newrow,newcon=f.compute(p)
 steps.append(dict(turn=turn,tone=newrow['weighted_score'],minimum_constraint=float(newcon.min()),whole_margin=float(newcon[important[0]]),crest_margin=float(newcon[important[1]]),maximum_correction=float(np.max(abs(delta))),solver_success=bool(solve.success)))
 print('THREE_HF_INTERIOR_PROJECTION',steps[-1],flush=True)
_,row,con=f.compute(p)
assert con.min()>=-1e-12 and con[important].min()>2e-7
assert row['weighted_score']<initial-1e-6
assert np.all(p>=f.lower) and np.all(p<=f.upper)
f.probe(p)
(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n')
(f.V/'optimizer.json').write_text(json.dumps(dict(method='small least-norm projection of existing HF values into unchanged fixed guards',steps=steps,all_DSP_tolerances_unchanged=True,all_quality_guards_unchanged=True,extra_numerical_interior_margin_only=True,requires_fresh_actual_proof=True,match_reached=False),indent=2)+'\n')
print('THREE_HF_INTERIOR_NUMERIC_PASS',str(f.V),row['weighted_score'],flush=True)
