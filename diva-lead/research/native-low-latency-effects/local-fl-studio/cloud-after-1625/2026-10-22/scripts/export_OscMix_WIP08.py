"""Verify complete WIP08 with a real changed Diva VST chunk; no auto adoption."""
from pathlib import Path
import json,os,subprocess,zipfile
B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects');PY='/workspace/.venvs/divalead/bin/python'
candidate=B/'paired-OscMix6p3-current-FX-01/full-validated-candidate.json';choice=json.loads(candidate.read_text())
assert choice['robust_improvement'] and choice['source_manifest']['source_VST_chunk']
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
kit=B/'FL20_NATIVE_08_WIP'
steps=[(B/'export_fl20_checkpoint.py',[candidate,kit],'export'),
    (W/'verify_fst_with_pyflp.py',[kit],'parse'),
    (B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],'latency'),
    (B/'finalize_fl20_kit.py',[kit,'Diva_NATIVE_08_WIP'],'finalize')]
for script,args,name in steps:
    with(B/f'Diva_NATIVE_08_WIP-{name}.log').open('w')as log:
        subprocess.run([PY,'-B',str(script),*map(str,args)],env=env,stdout=log,stderr=log,check=True)
proof=json.loads((kit/'verification/FLP_VERIFICATION.json').read_text())
assert proof['Diva_program_from_real_effGetChunk']and not proof['Diva_state_byte_exact_against_actual_local_FL05']
assert proof['all12_native_states_exact_against_real_DLL_saved_states']and proof['MIDI224_unchanged']and proof['routes235_unchanged']
z=B/'Diva_NATIVE_08_WIP_complete_WIP.zip'
with zipfile.ZipFile(z)as archive:
    names=archive.namelist();prefix=names[0].split('/')[0]+'/'
    for name in ['verification/Diva_VST_chunk.bin','verification/all281.tsv.gz','verification/Diva.log.gz','verification/MIDI_note_events_48k.json']:
        assert prefix+name in names,name
(B/'FL20_NATIVE_08_READY.json').write_text(json.dumps(dict(kit=str(kit),candidate=str(candidate),ZIP=str(z),
    source_OscMix6p3_changed_and_audited=True,new_FLp_chunk_checked_in_actual_Diva=True,actual_FL_GUI_validation_pending=True,match_reached=False),indent=2)+'\n')
print('OSC_MIX_WIP08_FULL_KIT_VERIFIED',flush=True)
