"""Repair the rejected gain point with positive margin in EVERY original guard."""
from pathlib import Path
import json, os, subprocess, sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
ROOT=Path(__file__).resolve().parent;RUN=ROOT/'pw5190-gain-interior-allguards';RUN.mkdir(exist_ok=False)
BASIS=ROOT/'pw5190-gain-research/basis';SOURCE=ROOT/'source-pw5190-basis'
SCRATCH=Path('/tmp/divalead-pw5190-gain-interior-allguards');assert not SCRATCH.exists()
os.environ.update(DIVALEAD_MODEL_BASE=str(BASIS),DIVALEAD_SELECTION_WORK=str(SCRATCH))
seed=json.loads(Path('/tmp/divalead-pw5190-gains/complete-joint-basis/best.json').read_text())
(RUN/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
(RUN/'numeric-location.json').write_text(json.dumps(dict(numeric_scratch=str(SCRATCH),temporary=True,baseline=str(BASIS),only_three_held=True),indent=2)+'\n')
sys.path.insert(0,str(ROOT));import fit_three_gains as fit
import numpy as np
from three_gain_interior_projection import project_gain
assert seed['baseline_model_SHA256']==fit.baseline_hash
fit.probe(np.zeros(93));point,projection=project_gain(seed,fit.compute,fit.lower,fit.upper,fit.guards)
(RUN/'projection.json').write_text(json.dumps(projection,indent=2)+'\n')
if point is None:
    print('PW5190_GAIN_ALL_GUARD_PROJECTION_INFEASIBLE',projection,flush=True);raise SystemExit(0)
_,row,constraints=fit.compute(point);assert constraints.min()>2e-7
assert row['weighted_score']<fit.rows[0]['weighted_score']-1e-6
fit.probe(point)
(fit.V/'history.json').write_text(json.dumps(fit.rows,indent=2)+'\n')
(fit.V/'optimizer.json').write_text(json.dumps(projection,indent=2)+'\n')
target=ROOT/'pw5190-verified-gain-interior-0001'
env=dict(os.environ,DIVALEAD_THREE_SOURCE_BASIS=str(SOURCE),DIVALEAD_THREE_SOURCE_REPORT=str(SOURCE/'preliminary-metrics.json'))
with (RUN/'validation.log').open('w') as log:
    subprocess.run([sys.executable,'-B',str(ROOT/'validate_three_source_model.py'),str(fit.V),target.name],
                   env=env,stdout=log,stderr=log,check=True,timeout=900)
actual=json.loads((target/'validation.json').read_text())
print('PW5190_GAIN_EVERY_GUARD_INTERIOR_FULL_ACTUAL_PASS',actual['tone_score'],actual['score'],flush=True)
