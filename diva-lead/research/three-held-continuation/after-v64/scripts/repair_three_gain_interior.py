from pathlib import Path
import os,sys,json
R=Path(__file__).resolve().parent;run=Path(sys.argv[1]);run.mkdir(exist_ok=False);seed=json.loads(Path(sys.argv[2]).read_text());(run/'seed.json').write_text(json.dumps(seed,indent=2)+'\n');basis=Path(sys.argv[3])
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(run/'numeric'))
sys.path.insert(0,str(R));import fit_three_gains as f
from three_gain_interior_projection import project_gain
import numpy as np
assert seed['baseline_model_SHA256']==f.baseline_hash
f.probe(np.zeros(93));initial=f.rows[0]['weighted_score'];point,report=project_gain(seed,f.compute,f.lower,f.upper,f.guards)
(run/'projection.json').write_text(json.dumps(report,indent=2)+'\n')
assert point is not None,report
_,row,con=f.compute(point);assert row['weighted_score']<initial-1e-6 and con.min()>=-1e-12
f.probe(point);(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n')
print('THREE_GAIN_INTERIOR_NUMERIC_PASS',str(f.V),row['weighted_score'],float(con.min()),row['minimum_gain_on_45_220Hz'],flush=True)
