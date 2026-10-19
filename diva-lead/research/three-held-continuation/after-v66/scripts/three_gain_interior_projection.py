"""Project existing three-held harmonic gains inside the same original guards."""
def project_gain(seed,compute,lower,upper,guards,max_turns=5):
 import numpy as np
 from scipy.optimize import minimize
 p=np.asarray(seed['offsets'],dtype=float).copy();free=np.arange(31)
 important=np.array([list(guards).index('whole'),len(guards)+1+31]);margin=5e-7;steps=[]
 for turn in range(max_turns):
  _,row,con=compute(p)
  if con.min()>2e-7:break
  columns=[]
  for j in free:
   h=1e-5;plus=p.copy();minus=p.copy();plus[j]+=h;minus[j]-=h
   columns.append((compute(plus)[2]-compute(minus)[2])/(2*h))
  matrix=np.array(columns).T;target=np.full_like(con,margin);required=target-con;scale=.001;J=matrix*scale
  bounds=[(max(-.008,lower[j]-p[j])/scale,min(.008,upper[j]-p[j])/scale) for j in free]
  fit=minimize(lambda x:.5*float(x@x),np.zeros(len(free)),jac=lambda x:x,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=lambda x:J@x-required,jac=lambda x:J)],options=dict(ftol=1e-12,maxiter=100))
  if np.min(J@fit.x-required)<-1e-10:return None,dict(accepted_numeric=False,reason='linear projection infeasible',solver_message=str(fit.message),steps=steps)
  delta=fit.x*scale;p[free]+=delta;_,row,con=compute(p)
  steps.append(dict(turn=turn,tone=row['weighted_score'],minimum_constraint=float(con.min()),whole_margin=float(con[important[0]]),crest_margin=float(con[important[1]]),maximum_correction=float(np.max(abs(delta))),continuous_minimum_gain=row['minimum_gain_on_45_220Hz'],solver_success=bool(fit.success)))
 _,row,con=compute(p);valid=bool(con.min()>2e-7 and np.all(p>=lower) and np.all(p<=upper))
 return (p if valid else None),dict(accepted_numeric=valid,steps=steps,all_quality_guards_unchanged=True,continuous_gain_constraints_kept=True,all_DSP_tolerances_unchanged=True,extra_numerical_margin_only=True,requires_fresh_actual_proof=True,match_reached=False)

def repair_gain_rows(rows,best_score,compute,probe,lower,upper,guards):
 eligible=[row for row in rows if row['weighted_score']<best_score-1e-6 and -1e-4<=row['minimum_constraint']<0]
 if not eligible:return dict(attempted=False,requires_fresh_actual_proof=True)
 seed=min(eligible,key=lambda row:row['weighted_score']);point,report=project_gain(seed,compute,lower,upper,guards);report.update(attempted=True,seed_score=seed['weighted_score'])
 if point is not None:
  _,row,_=compute(point);report['projected_score']=row['weighted_score']
  if row['weighted_score']<best_score-1e-6:probe(point);report['best_model_updated']=True
  else:report['best_model_updated']=False
 return report
