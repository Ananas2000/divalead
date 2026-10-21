from pathlib import Path
import hashlib,json,os,subprocess
from native_cpu_slots import four_native_slots
from native_chain import W
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=W/'native-Diva-PW-depth1-EQ-refit-01';case=W/'native-Diva-PW-keyfollow-screen-01/PW-keyfollow-depth-1';proof=json.loads((case/'verification.json').read_text());assert proof['all281_audited'] and proof['all12_MIDI_events_exact']
manifest=dict(source_preset=str(case/'Diva.h2p'),source_audio=str(case/'Diva_source.wav'),native_input=str(case/'source-with-tail.wav'),source_preset_SHA256=hashlib.sha256((case/'Diva.h2p').read_bytes()).hexdigest(),source_audio_SHA256=hashlib.sha256((case/'Diva_source.wav').read_bytes()).hexdigest(),changed_parameters=proof['changed_parameters'],all281_audited=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_and_envelopes_unchanged=True,proof=str(case/'verification.json'))
seed=W/'PW-keyfollow-depth1-native-refit-seed.json';seed.write_text(json.dumps(dict(proof,source_manifest=manifest),indent=2)+'\n')
with four_native_slots(ROOT):
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_CHORUS_SWEEPS='16')
 subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'search_native_source_chorus.py'),str(seed),str(ROOT)],env=env,check=True)
completed=N/'native-PW-keyfollow-joint-research';completed.mkdir(exist_ok=True)
for name in ['full-validated-candidate.json','completion.json','paired-fresh-control.json','heldout-prefix-validation.json']:
 (completed/name).write_bytes((ROOT/name).read_bytes())
print('ACTUAL_DIVA_PW_KEYFOLLOW_JOINT_REFIT_COMPLETE',flush=True)
