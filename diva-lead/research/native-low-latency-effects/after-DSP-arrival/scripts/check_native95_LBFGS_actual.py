from pathlib import Path
import json,os,subprocess
from native_chain import W
from native_cpu_slots import four_native_slots
ROOT=W/'native95-LBFGS-actual-integration-01'
with four_native_slots(ROOT) as state:
 seed=W/'native95-LBFGS-integration-seed.json';row=json.loads(Path(state['best_candidate']).read_text());assert len(row['x'])==95 and row['source_manifest'];seed.write_text(json.dumps(row,indent=2)+'\n')
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_LBFGS_MAXITER='2',DIVALEAD_LBFGS_MAXCALLS='210')
 subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'search_native_source_LBFGS.py'),str(seed),str(ROOT)],env=env,check=True)
 result=json.loads((ROOT/'full-validated-candidate.json').read_text());assert len(result['x'])==95 and result['source_manifest']==row['source_manifest'] and result['full_fresh_native_realizations']==6
 out=Path('/workspace/divalead-work/native-low-latency-effects/native95-LBFGS-actual-integration-01');out.mkdir(exist_ok=True)
 for name in ['completion.json','optimizer-result.json','full-validated-candidate.json','paired-fresh-control.json','heldout-prefix-validation.json']:(out/name).write_bytes((ROOT/name).read_bytes())
print('NATIVE95_LBFGS_ACTUAL_SOURCE_PHASE_AND_FRESH_RENDER_INTEGRATION_PASS',result['loss'])
