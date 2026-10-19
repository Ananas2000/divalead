from pathlib import Path
import os,sys,json,subprocess
R=Path(__file__).resolve().parent;T=R/'balance42-projection-0001';T.mkdir(exist_ok=False)
seed=json.loads(Path('/tmp/divalead-balance42-numeric/complete-balance42-basis/latest_center.json').read_text());(T/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'balance42-first/basis'),DIVALEAD_SELECTION_WORK='/tmp/divalead-balance42-projection-0001')
sys.path.insert(0,str(R));import fit_three_balance42 as f
from project_three_existing_vector import project
import numpy as np
assert seed['baseline_model_SHA256']==f.baseline_hash;f.probe(np.zeros(42));point,report=project(seed['stereo_balance_offsets'],f.compute,f.lower,f.upper,[list(f.guards).index('whole'),len(f.guards)+1]);(T/'projection.json').write_text(json.dumps(report,indent=2)+'\n')
if point is None:print('BALANCE42_NO_FEASIBLE_PROJECTED_POINT',report,flush=True);raise SystemExit(0)
_,row,con=f.compute(point);assert row['weighted_score']<f.rows[0]['weighted_score']-1e-6;f.probe(point)
(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n')
print('BALANCE42_PROJECTED_NUMERIC_POINT',row['weighted_score'],con.min(),flush=True)
with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(f.V),'verified-balance42-projection-0001'],env=os.environ.copy(),stdout=log,stderr=log,check=True,timeout=900)
actual=json.loads((R/'verified-balance42-projection-0001/validation.json').read_text());print('BALANCE42_PROJECTED_FULL_ACTUAL_PASS',actual['tone_score'],actual['metrics']['stereo_balance'],flush=True)
