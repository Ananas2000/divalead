"""Least-norm adjustment inside unchanged three-held guards; no new DSP values."""
def project(seed,compute,lower,upper,important,max_turns=5):
 import numpy as np
 from scipy.optimize import minimize
 p=np.asarray(seed,dtype=float).copy();steps=[];important=np.asarray(important);margin=5e-7;scale=.001
 for turn in range(max_turns):
  _,row,con=compute(p)
  if con.min()>=-1e-12 and con[important].min()>2e-7:break
  columns=[]
  for j in range(len(p)):
   h=2e-6;plus=p.copy();minus=p.copy();plus[j]+=h;minus[j]-=h
   columns.append((compute(plus)[2]-compute(minus)[2])/(2*h))
  J=np.array(columns).T*scale;target=np.full_like(con,margin);target[important]=margin;required=target-con
  bounds=[(max(-.008,lo-v)/scale,min(.008,hi-v)/scale) for lo,hi,v in zip(lower,upper,p)]
  fit=minimize(lambda x:.5*float(x@x),np.zeros(len(p)),jac=lambda x:x,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=lambda x:J@x-required,jac=lambda x:J)],options=dict(ftol=1e-12,maxiter=100))
  if np.min(J@fit.x-required)<-1e-10:return None,dict(accepted_numeric=False,reason='linear projection infeasible',solver_message=str(fit.message),steps=steps)
  delta=fit.x*scale;p+=delta;_,row,con=compute(p)
  steps.append(dict(turn=turn,tone=row['weighted_score'],minimum_constraint=float(con.min()),whole_margin=float(con[important[0]]),crest_margin=float(con[important[1]]),maximum_existing_coefficient_correction=float(np.max(abs(delta))),solver_success=bool(fit.success)))
 _,row,con=compute(p);valid=bool(con.min()>=-1e-12 and con[important].min()>2e-7 and np.all(p>=lower) and np.all(p<=upper))
 return (p if valid else None),dict(accepted_numeric=valid,steps=steps,all_original_quality_guards_unchanged=True,all_DSP_tolerances_unchanged=True,requires_full_actual_proof=True,match_reached=False)
