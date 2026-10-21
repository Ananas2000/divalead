from pathlib import Path
import json,os,shutil,subprocess
import numpy as np
from native_chain import W
from native_cpu_slots import four_native_slots
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=W/'PW-keyfollow-common-phase-technical-WIP-01';physical=N/'source-bases/PW-keyfollow-depth-1'
fit=json.loads((W/'native-Diva-PW-depth1-EQ-refit-01/full-validated-candidate.json').read_text());phase=json.loads((W/'native-common-phase-pair-01/best.json').read_text());assert phase['model']=='PW-keyfollow-1'
manifest=dict(fit['source_manifest'],source_preset=str(physical/'Diva.h2p'),source_audio=str(physical/'Diva_source.wav'),fresh_proof=str(physical/'FRESH_DIVA_SOURCE_PROOF.json'),proof=str(physical/'verification.json'))
choice=dict(fit,x=[*phase['x'],phase['common_phase_raw']],source_manifest=manifest,common_phase_pair=True,previous_94_parameter_family_loss=fit['loss'],common_phase_screen_loss=phase['loss'],new_family_full_validation_pending=True)
seed=W/'PW-keyfollow-common-phase-seed-95.json';seed.write_text(json.dumps(choice,indent=2)+'\n')
e=os.environ.copy();e.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def run(name,args):subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/name),*map(str,args)],env=e,check=True)
with four_native_slots(ROOT):
 run('export_native_chorus_checkpoint.py',[seed,ROOT])
 run('verify_fst_with_pyflp.py',[ROOT]);run('complete_native_checkpoint.py',[ROOT])
 run('verify_native_latency_blocks.py',[ROOT/'verification/candidate.json',ROOT/'verification/NATIVE_LATENCY_AND_BLOCKS.json'])
 run('assess_native_reference.py',[ROOT/'verification/NATIVE_WITH_TAIL_WIP.wav'])
 shutil.copyfile(W/'reference-assessment/COMPARISON.json',ROOT/'verification/ORIGINAL_REFERENCE_COMPARISON.json')
 proof=json.loads((ROOT/'verification/NATIVE_PRESET_VERIFICATION.json').read_text());assert proof['preset_state_bytes_exact'] and proof['zero_depth_routing_audio_exact']
 control=json.loads((N/'NATIVE_RESTORED_RUNTIME_AUDIO_CHECK.json').read_text());difference=control['mean_original_objective']-proof['mean_original_objective'];uncertainty=float(np.hypot(control['std_original_objective'],proof['std_original_objective'])/np.sqrt(6));assert difference>max(.0005,3*uncertainty)
 choice=json.loads((ROOT/'verification/candidate.json').read_text());choice.update(new_family_full_validation_pending=False,robust_improvement=True,paired_frozen_v83_source_mean_loss=control['mean_original_objective'],family_mean_improvement=difference,standard_error_of_mean_difference=uncertainty)
 (ROOT/'verification/candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
 (ROOT/'verification/FAMILY_SELECTION.json').write_text(json.dumps(dict(actual_six_render_improvement_over_frozen_native=True,mean_difference=difference,standard_error=uncertainty,source_and_95_parameters_carried=True,still_worse_than_original_v83=True,reference_match_reached=False),indent=2)+'\n')
 (N/'NATIVE_PW_PHASE_BEST_CANDIDATE.json').write_text(json.dumps(choice,indent=2)+'\n')
print('FRESH_PW_SOURCE_PHASE_PAIR_KIT_VERIFIED',choice['loss'],flush=True)
