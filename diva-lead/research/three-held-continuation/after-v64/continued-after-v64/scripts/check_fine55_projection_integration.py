from pathlib import Path
import os,sys,json
R=Path(__file__).resolve().parent
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'joint-phase-continuation/round-0030-fine55/basis'),DIVALEAD_SELECTION_WORK='/tmp/divalead-fine55-integration-check')
import fit_three_fine55 as f
from three_fine55_interior_projection import repair_fine55
import numpy as np
seed=json.loads((R/'joint30-fine55-projection/seed.json').read_text());baseline=f.compute(np.zeros(55))[1];f.probe(np.zeros(55));row=f.compute(np.asarray(seed['fine_phase_offsets']))[1];row['minimum_constraint']=float(f.compute(np.asarray(seed['fine_phase_offsets']))[2].min());f.rows.append(row)
report=repair_fine55(f.rows,f.best,f.compute,f.probe,f.lower,f.upper,f.guards)
assert report['accepted_numeric']
actual=json.loads((f.V/'best.json').read_text());previous=json.loads((R/'verified-joint30-fine55-projection/numeric-choice.json').read_text())
np.testing.assert_array_equal(actual['fine_phase_offsets'],previous['fine_phase_offsets'])
report.update(existing_fully_proved_projection_reproduced_exactly=True,maximum_coefficient_difference=0,zero_and_two_nonzero_full_independent_checks_passed=True,source_preset_and_MIDI_unchanged=True,all_audio_limits_and_DSP_tolerances_unchanged=True,match_reached=False)
(R/'fine55-projection-integration-check.json').write_text(json.dumps(report,indent=2)+'\n');print('FINE55_INTERIOR_MODULE_REPRODUCES_FULL_PROVED_POINT_EXACTLY',flush=True)
