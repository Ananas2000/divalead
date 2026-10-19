"""Fully recompute and actually validate a feasible checkpoint of a live fine55 fit."""
from pathlib import Path
import os,sys,json,subprocess
R=Path(__file__).resolve().parent;T=R/'fine55-preview-0001';T.mkdir(exist_ok=False)
seed=json.loads((R/'fine55-first/numeric/complete-fine_phase-basis/best.json').read_text());(T/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'fine55-first/basis'),DIVALEAD_SELECTION_WORK=str(T/'numeric'))
sys.path.insert(0,str(R));import fit_three_fine55 as f
import numpy as np
assert seed['baseline_model_SHA256']==f.baseline_hash and seed['feasible_search_guards']
f.probe(np.zeros(55));point=np.asarray(seed['fine_phase_offsets']);_,row,con=f.compute(point);assert con.min()>=-1e-12 and row['weighted_score']<f.rows[0]['weighted_score']-1e-6
f.probe(point);(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(dict(method='recomputed live feasible55 checkpoint; source search continues',same_zero_and_nonzero_full_independent_checks=True,all_quality_guards_unchanged=True,all_DSP_tolerances_unchanged=True,requires_fresh_actual_proof=True,match_reached=False),indent=2)+'\n')
print('FINE55_LIVE_POINT_RECOMPUTED_AND_FEASIBLE',row['weighted_score'],flush=True)
with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(f.V),'verified-fine55-preview-0001'],stdout=log,stderr=log,env=os.environ.copy(),check=True,timeout=900)
report=json.loads((R/'verified-fine55-preview-0001/validation.json').read_text());print('FINE55_NONZERO_ACTUAL_FULL_PROOF_PASS',report['tone_score'],report['score'],flush=True)
