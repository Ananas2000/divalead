"""Small HF corrections inside unchanged fixed three-held quality limits.

A successful numeric projection still requires the existing fresh actual proof.
"""
def project_hf(seed,compute,lower,upper,guards,max_turns=5):
 import numpy as np
 from scipy.optimize import minimize
 p=np.asarray(seed['HF_offsets'],dtype=float).copy()
 free=np.r_[np.arange(10),np.arange(60,70)]
 important=np.array([list(guards).index('whole'),len(guards)+1])
 steps=[];margin=5e-7
 for turn in range(max_turns):
  _,row,con=compute(p)
  if con.min()>=-1e-12 and con[important].min()>2e-7:break
  columns=[]
  for j in free:
   h=1e-5;plus=p.copy();minus=p.copy();plus[j]+=h;minus[j]-=h
   columns.append((compute(plus)[2]-compute(minus)[2])/(2*h))
  matrix=np.array(columns).T;target=np.zeros_like(con);target[important]=margin;required=target-con
  scale=.001;J=matrix*scale
  bounds=[(max(-.008,lower[j]-p[j])/scale,min(.008,upper[j]-p[j])/scale) for j in free]
  fit=minimize(lambda x:.5*float(x@x),np.zeros(len(free)),jac=lambda x:x,method='SLSQP',bounds=bounds,constraints=[dict(type='ineq',fun=lambda x:J@x-required,jac=lambda x:J)],options=dict(ftol=1e-12,maxiter=100))
  if np.min(J@fit.x-required)<-1e-10:
   return None,dict(accepted_numeric=False,reason='linear projection infeasible',solver_message=str(fit.message),steps=steps)
  delta=fit.x*scale;p[free]+=delta;_,row,con=compute(p)
  steps.append(dict(turn=turn,tone=row['weighted_score'],minimum_constraint=float(con.min()),whole_margin=float(con[important[0]]),crest_margin=float(con[important[1]]),maximum_correction=float(np.max(abs(delta))),solver_success=bool(fit.success)))
 _,row,con=compute(p)
 valid=bool(con.min()>=-1e-12 and con[important].min()>2e-7 and np.all(p>=lower) and np.all(p<=upper))
 return (p if valid else None),dict(accepted_numeric=valid,steps=steps,all_quality_guards_unchanged=True,all_DSP_tolerances_unchanged=True,extra_numerical_margin_only=True,requires_fresh_actual_proof=True,match_reached=False)

def _repair_hf_rows(rows,best_score,compute,probe,lower,upper,guards):
 eligible=[row for row in rows if row['weighted_score']<best_score-1e-6 and -1e-4<=row['minimum_constraint']<0]
 if not eligible:return dict(attempted=False,requires_fresh_actual_proof=True)
 seed=min(eligible,key=lambda row:row['weighted_score'])
 point,report=project_hf(seed,compute,lower,upper,guards)
 report.update(attempted=True,seed_score=seed['weighted_score'])
 if point is not None:
  _,row,_=compute(point);report['projected_score']=row['weighted_score']
  if row['weighted_score']<best_score-1e-6:probe(point);report['best_model_updated']=True
  else:report['best_model_updated']=False
 return report

def repair_hf_rows(rows,best_score,compute,probe,lower,upper,guards):
 report=_repair_hf_rows(rows,best_score,compute,probe,lower,upper,guards)
 # A quieter tradeoff is kept separately; it never replaces the tone-selected
 # best and is never a full proof or a claimed improvement by itself.
 if not rows or not rows[0].get('cleaner_HF100_research'):return report
 from pathlib import Path
 import json
 baseline=rows[0];eligible=[r for r in rows if r['metrics']['upper_off']<baseline['metrics']['upper_off']-1e-3 and r['weighted_score']<=baseline['weighted_score']+2e-4 and r['minimum_constraint']>=-1e-4]
 if not eligible:return report
 seed=min(eligible,key=lambda r:r['metrics']['upper_off'])
 point,projection=project_hf(seed,compute,lower,upper,guards)
 report['separate_quieter_alternative_projection']=projection
 if point is not None:
  _,row,con=compute(point)
  if con.min()>=-1e-12 and row['metrics']['upper_off']<baseline['metrics']['upper_off']-1e-3 and row['weighted_score']<=baseline['weighted_score']+2e-4:
   row.update(quieter_alternative_NOT_tone_selected_best=True,original_tone_score_not_claimed_improved=True,alternative_baseline_tone_score=baseline['weighted_score'],alternative_tone_cap=baseline['weighted_score']+2e-4,requires_full_actual_proof=True)
   directory=Path(probe.__globals__['V']);(directory/'quieter-alternative.json').write_text(json.dumps(row,indent=2)+'\n')
   report['quieter_alternative_saved_separately']=True
 return report
