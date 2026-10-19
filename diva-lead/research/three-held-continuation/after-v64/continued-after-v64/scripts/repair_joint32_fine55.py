from pathlib import Path
import os,sys,json,subprocess
R=Path(__file__).resolve().parent;T=R/'joint32-fine55-projection';T.mkdir(exist_ok=False)
source=R/'joint-phase-continuation/round-0032-fine55/numeric/complete-fine_phase-basis/latest_center.json';assert source.with_name('optimizer.json').exists();seed=json.loads(source.read_text());(T/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'joint-phase-continuation/round-0032-fine55/basis'),DIVALEAD_SELECTION_WORK='/tmp/divalead-joint32-fine55-projection');sys.path.insert(0,str(R));import fit_three_fine55 as f
from project_three_existing_vector import project
import numpy as np
assert seed['baseline_model_SHA256']==f.baseline_hash;f.probe(np.zeros(55));point,report=project(seed['fine_phase_offsets'],f.compute,f.lower,f.upper,[list(f.guards).index('whole'),len(f.guards)+1]);(T/'projection.json').write_text(json.dumps(report,indent=2)+'\n')
if point is None:print('JOINT32_FINE55_NO_FEASIBLE_PROJECTED_POINT',report,flush=True);raise SystemExit(0)
_,row,con=f.compute(point);assert row['weighted_score']<f.rows[0]['weighted_score']-1e-6;f.probe(point);(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n');print('JOINT32_FINE55_PROJECTED_NUMERIC_PASS',row['weighted_score'],con.min(),flush=True)
with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(f.V),'verified-joint32-fine55-projection'],env=os.environ.copy(),stdout=log,stderr=log,check=True,timeout=900)
actual=json.loads((R/'verified-joint32-fine55-projection/validation.json').read_text());print('JOINT32_FINE55_PROJECTED_FULL_ACTUAL_PASS',actual['tone_score'],actual['score'],flush=True)
