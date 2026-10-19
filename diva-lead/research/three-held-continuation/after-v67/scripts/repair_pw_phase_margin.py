"""Recover a rejected thin-margin fine55 point without changing any audio limit."""
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parent;RUN=ROOT/'pw5190-phase-interior-0030';RUN.mkdir(exist_ok=False)
BASIS=ROOT/'pw5190-live-phase/round-0030-fine55/basis';SOURCE=ROOT/'source-pw5190-basis'
SCRATCH=Path('/tmp/divalead-pw5190-phase-interior-0030');assert not SCRATCH.exists()
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(BASIS),DIVALEAD_SELECTION_WORK=str(SCRATCH))
seed=json.loads(Path('/tmp/divalead-pw5190-live-phase/round-0030-fine55/complete-fine_phase-basis/best.json').read_text())
(RUN/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
(RUN/'numeric-location.json').write_text(json.dumps(dict(numeric_scratch=str(SCRATCH),temporary=True,baseline=str(BASIS),only_three_held=True),indent=2)+'\n')
sys.path.insert(0,str(ROOT));import fit_three_fine55 as fit
from project_three_existing_vector import project
import numpy as np
assert seed['baseline_model_SHA256']==fit.baseline_hash
fit.probe(np.zeros(55));point,report=project(seed['fine_phase_offsets'],fit.compute,fit.lower,fit.upper,[list(fit.guards).index('whole'),len(fit.guards)+1])
(RUN/'projection.json').write_text(json.dumps(report,indent=2)+'\n')
if point is None:
    print('PW_FINE55_ALL_GUARD_PROJECTION_INFEASIBLE',report,flush=True);raise SystemExit(0)
_,row,con=fit.compute(point);assert con.min()>2e-7 and row['weighted_score']<fit.rows[0]['weighted_score']-1e-6
fit.probe(point);(fit.V/'history.json').write_text(json.dumps(fit.rows,indent=2)+'\n');(fit.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n')
env=dict(os.environ,DIVALEAD_THREE_SOURCE_BASIS=str(SOURCE),DIVALEAD_THREE_SOURCE_REPORT=str(BASIS/'validation.json'))
target=ROOT/'pw5190-verified-fine55-interior-0030'
with (RUN/'validation.log').open('w') as log:
    subprocess.run([sys.executable,'-B',str(ROOT/'validate_three_source_model.py'),str(fit.V),target.name],env=env,stdout=log,stderr=log,check=True,timeout=900)
actual=json.loads((target/'validation.json').read_text())
print('PW_FINE55_INTERIOR_FRESH_FULL_PROOF_PASS',actual['tone_score'],actual['score'],flush=True)
