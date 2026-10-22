"""Transfer the four native workers only after a real joint-worker check."""
from pathlib import Path
import datetime,json,os,signal,subprocess,time,sys
from native_chain import W
from native_cpu_slots import identity,same
N=Path('/workspace/divalead-work/native-low-latency-effects')
proof=json.loads((N/'native-joint76-actual-integration-01/ACTUAL_INTEGRATION_PROOF.json').read_text())
assert proof['actual_76_coordinate_native_worker_executed'] and proof['six_fresh_full_graph_captures']
assert not (N/'NATIVE_FINITE_BRANCH.json').exists()
state=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text())
assert same(state['controller']) and same(state['child'])
current=json.loads(Path(state['best_candidate']).read_text());selected=current;selected_path=Path(state['best_candidate'])
for path in [W/'native-Diva-cutoff148-profile-01/full-validated-candidate.json',W/'native-joint76-actual-integration-01/full-validated-candidate.json',*[Path(arg) for arg in sys.argv[1:]]]:
    if not path.is_file():continue
    row=json.loads(path.read_text())
    if row.get('robust_improvement') and not row.get('full_fresh_native_validation_pending',True) and row['loss']<selected['loss']:
        selected=row;selected_path=path
assert len(selected['x'])==95 and selected['full_fresh_native_realizations']==6
fresh=json.loads(Path(selected['source_manifest']['fresh_proof']).read_text())
assert fresh['actual_fresh_Diva_plugin_render'] and fresh['same_all12_incoming_MIDI_events'] and fresh['all281_exact_against_variant']
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_state=state,
    reason='Actual bounded 76-coordinate native EQ optimizer passed; alternate joint gain/frequency/bandwidth work with existing verified searches',
    selected_path=str(selected_path),selected_loss=selected['loss'],new_worker_proof=proof,reference_match_reached=False)
os.kill(state['controller']['PID'],signal.SIGTERM)
os.kill(state['child']['PID'],signal.SIGINT)
deadline=time.monotonic()+55
while same(state['controller']) or same(state['child']):
    assert time.monotonic()<deadline,'Inspect exact old identities before any replacement launch';time.sleep(.2)
(N/'NATIVE_BEST_CANDIDATE.json').write_text(json.dumps(selected,indent=2)+'\n')
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'start_native_chorus.py')],env=env,check=True)
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'start_native_chorus.py')],env=env,check=True)
receipt['new_state']=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text())
assert same(receipt['new_state']['controller']) and receipt['new_state']['controller']['PID']!=state['controller']['PID']
(N/'NATIVE_JOINT76_HANDOFF.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('ACTUAL_JOINT76_VERIFIED_CONTROLLER_HANDOFF',selected['loss'],flush=True)
