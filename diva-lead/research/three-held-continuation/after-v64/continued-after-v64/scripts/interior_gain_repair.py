from pathlib import Path
import os,sys,json
R=Path(__file__).resolve().parent;os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'phase18-basis'),DIVALEAD_SELECTION_WORK=str(R/'gain-interior-repair'))
sys.path.insert(0,str(R));import fit_three_gains as f
import numpy as np
seed=json.loads((R/'gain-boundary-repair/complete-joint-phase18-basis/best.json').read_text());assert seed['baseline_model_SHA256']==f.baseline_hash
p=np.array(seed['offsets']);free=np.array([0,2,4,6,9,12,14,16,19,21,23,27]);f.probe(np.zeros(93));history=[];active=np.array([list(f.guards).index('whole'),43])
for turn in range(3):
 _,row,con=f.compute(p);target=np.array([4e-7,max(4e-7,con[43])]);required=target-con[active]
 if con[active].min()>2e-7 and con.min()>=-1e-12:break
 jac=[]
 for j in free:
  step=1e-5;plus=p.copy();minus=p.copy();plus[j]+=step;minus[j]-=step
  jac.append((f.compute(plus)[2][active]-f.compute(minus)[2][active])/(2*step))
 matrix=np.array(jac).T;delta=np.linalg.lstsq(matrix,required,rcond=None)[0];assert np.max(abs(delta))<.0005
 p[free]+=delta;assert np.max(abs(p))<=.1
 _,row,con=f.compute(p);history.append(dict(turn=turn,tone=row['weighted_score'],minimum_constraint=float(con.min()),interior_whole_margin=float(con[active[0]]),interior_crest_margin=float(con[43]),gain_corrections=delta.tolist()))
 assert con.min()>=-1e-12,history[-1]
f.probe(p);_,row,con=f.compute(p);assert con[active].min()>2e-7 and row['weighted_score']<.8468365793
(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(dict(interior_steps=history,all_actual_caps_and_tolerances_unchanged=True,numeric_interor_extra_margin_only=True,requires_actual_proof=True,match_reached=False),indent=2)+'\n')
print('GAIN_STRICT_INTERIOR_REPAIR_PASS',row['weighted_score'],con.min(),con[active],flush=True)
