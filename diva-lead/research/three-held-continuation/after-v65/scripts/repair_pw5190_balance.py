"""Repair the screened physical PW source within the original unchanged guards."""
from pathlib import Path
import os, sys, json, subprocess
ROOT = Path(__file__).resolve().parent
BASIS = ROOT / 'source-pw5190-basis'
WORK = ROOT / 'pw5190-research'
WORK.mkdir(exist_ok=False)
SCRATCH = Path('/tmp/divalead-pw5190-balance-projection')
assert not SCRATCH.exists()
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  DIVALEAD_MODEL_BASE=str(BASIS), DIVALEAD_SELECTION_WORK=str(SCRATCH),
                  DIVALEAD_BASELINE_REPORT=str(BASIS / 'preliminary-metrics.json'))
sys.path.insert(0, str(ROOT))
import fit_three_balance42 as fit
import numpy as np
from project_three_existing_vector import project

fit.probe(np.zeros(42))
point, projection = project(np.zeros(42), fit.compute, fit.lower, fit.upper,
                            [list(fit.guards).index('whole'), len(fit.guards)+1])
(WORK / 'projection.json').write_text(json.dumps(projection, indent=2) + '\n')
if point is None:
    print('PW5190_NO_FEASIBLE_PROJECTED_POINT', projection, flush=True)
    raise SystemExit(0)
_, row, constraints = fit.compute(point)
assert constraints.min() > 2e-7
fit.probe(point)
(fit.V / 'history.json').write_text(json.dumps(fit.rows, indent=2) + '\n')
(fit.V / 'optimizer.json').write_text(json.dumps(projection, indent=2) + '\n')
cap = json.loads((BASIS / 'preliminary-metrics.json').read_text())['acceptance_tone_cap']
if row['weighted_score'] >= cap - 1e-6:
    print('PW5190_PROJECTED_POINT_HAS_NO_PROVED_BASE_TONE_IMPROVEMENT', row['weighted_score'], cap, flush=True)
    raise SystemExit(0)
env = dict(os.environ, DIVALEAD_THREE_SOURCE_BASIS=str(BASIS),
           DIVALEAD_THREE_SOURCE_REPORT=str(BASIS / 'preliminary-metrics.json'))
with (WORK / 'validation.log').open('w') as log:
    subprocess.run([sys.executable, '-B', str(ROOT / 'validate_three_source_model.py'),
                    str(fit.V), 'pw5190-verified-balance-0001'],
                   env=env, stdout=log, stderr=log, check=True, timeout=900)
report = json.loads((ROOT / 'pw5190-verified-balance-0001/validation.json').read_text())
print('PW5190_BALANCE_REPAIR_FULL_ACTUAL_PASS', report['tone_score'], report['score'], flush=True)
