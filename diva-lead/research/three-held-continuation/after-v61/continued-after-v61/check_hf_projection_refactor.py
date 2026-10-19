from pathlib import Path
import os,sys,json
R=Path(__file__).resolve().parent
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'continuation/round-0011-hf/basis'),DIVALEAD_SELECTION_WORK=str(R/'hf-projection-module-check'))
sys.path.insert(0,str(R));import fit_three_hf_fixed_anchor as f
from three_hf_interior_projection import project_hf,repair_hf_rows
import numpy as np
seed=json.loads((R/'hf-interior-repair-0001/seed.json').read_text());expected=json.loads((R/'hf-interior-repair-0001/numeric/complete-hf-basis/best.json').read_text())
point,report=project_hf(seed,f.compute,f.lower,f.upper,f.guards)
assert point is not None
np.testing.assert_allclose(point,expected['HF_offsets'],rtol=0,atol=1e-13)
_,row,con=f.compute(point);assert abs(row['weighted_score']-expected['weighted_score'])<1e-12
_,origin,_=f.compute(np.zeros(100));accepted=[]
result=repair_hf_rows([seed],origin['weighted_score'],f.compute,lambda p:accepted.append(p),f.lower,f.upper,f.guards)
assert result['best_model_updated'] and len(accepted)==1
np.testing.assert_allclose(accepted[0],point,rtol=0,atol=1e-13)
assert (R/'verified-hf-interior-0001/validation.json').exists()
result=dict(refactored_projection_matches_previously_full_proved_point=True,maximum_offset_difference=float(np.max(abs(point-np.asarray(expected['HF_offsets'])))),tone=row['weighted_score'],minimum_constraint=float(con.min()),integrated_selection_calls_only_original_guard_feasible_improvement=True,all_quality_guards_and_DSP_tolerances_unchanged=True,fresh_actual_proof_reference='verified-hf-interior-0001/validation.json',report=report,match_reached=False)
(R/'hf-projection-module-check.json').write_text(json.dumps(result,indent=2)+'\n')
print('THREE_HF_PROJECTION_MODULE_AND_INTEGRATED_SELECTION_REAL_MODEL_PASS',flush=True)
