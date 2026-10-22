"""Bounded real-DLL check before scheduling 76-coordinate joint EQ work."""
from pathlib import Path
import json,os,shutil,subprocess
from native_chain import W
from native_cpu_slots import four_native_slots
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=W/'native-joint76-actual-integration-01'
seed=W/'joint76-actual-integration-seed.json'
with four_native_slots(ROOT) as state:
    prior=json.loads(Path(state['best_candidate']).read_text())
    trial=W/'native-Diva-cutoff148-profile-01/full-validated-candidate.json'
    if trial.is_file():
        candidate=json.loads(trial.read_text())
        if candidate.get('robust_improvement') and candidate['loss']<prior['loss']:prior=candidate
    seed.write_text(json.dumps(prior,indent=2)+'\n')
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_LBFGS_MAXCALLS='450',DIVALEAD_LBFGS_MAXITER='2')
    subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'search_native_joint_EQ_LBFGS.py'),str(seed),str(ROOT)],env=env,check=True)
    result=json.loads((ROOT/'full-validated-candidate.json').read_text())
    assert len(result['x'])==95 and result['full_fresh_native_realizations']==6 and result['source_manifest']
    assert not result['full_fresh_native_validation_pending'] and (ROOT/'heldout-prefix-validation.json').is_file()
    summary=json.loads((ROOT/'optimizer-result.json').read_text());assert summary['actual_native_renders']>=154
dest=N/ROOT.name;dest.mkdir(exist_ok=True)
for filename in ['seed.json','full-validated-candidate.json','completion.json','paired-fresh-control.json','heldout-prefix-validation.json','optimizer-result.json','search-state.json']:
    if (ROOT/filename).is_file():shutil.copyfile(ROOT/filename,dest/filename)
proof=dict(actual_76_coordinate_native_worker_executed=True,actual_native_DSP_renders=summary['actual_native_renders'],
    source95_and_manifest_preserved=True,six_fresh_full_graph_captures=True,two_heldout_real_Chorus_prefixes=True,
    bounded_check_only=True,robust_improvement=result['robust_improvement'],loss=result['loss'],match_reached=False)
(dest/'ACTUAL_INTEGRATION_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print('JOINT76_ACTUAL_INTEGRATION_PASS',json.dumps(proof),flush=True)
