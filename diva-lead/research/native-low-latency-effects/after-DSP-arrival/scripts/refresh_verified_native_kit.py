"""Publish the latest accepted native95 WIP with actual preset/audio checks."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,sys
from native_chain import W
from native_cpu_slots import four_native_slots
N=Path('/workspace/divalead-work/native-low-latency-effects')
tag='native-verified-progress-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
kit=W/(tag+'-checkpoint-WIP');seed=W/(tag+'-seed.json')
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def run(script,args,label):
    with (W/(tag+'-'+label+'.log')).open('w') as f:
        subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/script),*map(str,args)],env=env,stdout=f,stderr=f,check=True)
with four_native_slots(kit) as state:
    choice=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else state['best_candidate']).read_text());assert len(choice['x'])==95 and choice['robust_improvement']
    seed.write_text(json.dumps(choice,indent=2)+'\n')
    run('export_native_chorus_checkpoint.py',[seed,kit],'export')
    run('verify_fst_with_pyflp.py',[kit],'parse')
    run('complete_native_checkpoint.py',[kit],'guide')
    run('verify_native_latency_blocks.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],'latency')
    run('assess_native_reference.py',[kit/'verification/NATIVE_WITH_TAIL_WIP.wav'],'original-reference')
    shutil.copyfile(W/'reference-assessment/COMPARISON.json',kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json')
    proof=json.loads((kit/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())
    actual=json.loads((kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json').read_text())[-1]
    expected=json.loads((kit/'verification/candidate.json').read_text())['original_reference_assessment']
    assert proof['preset_state_bytes_exact'] and proof['zero_depth_routing_audio_exact']
    assert abs(actual['tone_score']-expected['tone_score'])<2e-5
    (N/'LATEST_VERIFIED_NATIVE_KIT_PATH.json').write_text(json.dumps(dict(kit=str(kit),seed=str(seed),original_reference_match_reached=False),indent=2)+'\n')
run('publish_native_progress.py',[kit],'Git')
print('VERIFIED_NATIVE_WIP_PUBLISHED',kit,flush=True)
