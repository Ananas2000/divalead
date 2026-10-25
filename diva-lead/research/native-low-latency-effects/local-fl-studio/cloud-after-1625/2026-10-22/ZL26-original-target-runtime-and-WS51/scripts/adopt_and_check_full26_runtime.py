"""Adopt only the published, cold-replayed complete WIP; execute its real cascade."""
from pathlib import Path
import hashlib,json,shutil,subprocess
import numpy as np
import soundfile as sf
A=Path('/workspace/divalead-work/pc-stereo-20261024');H=Path(__file__).resolve().parent
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
receipt=json.loads((H/'ZL26_FULL_PUBLICATION.json').read_text());commit=receipt['commit']
assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',commit,'origin/main']).returncode==0
assert all(c['HTTP_byte_exact']for c in receipt['HTTP_checks'])
stop=N/'zl-stereo-continuation.stop';assert json.loads(stop.read_text())['owner']=='original-reference-tone-finite-20261025'
assert not(N/'zl-stereo-numerical.pause').exists()
bestfile=A/'stereo-continuous87/BEST_CANDIDATE.json';shutil.copyfile(bestfile,H/'BEST_BEFORE_FULL26.json')
kit=public/'ZL-WIP26';layout=json.loads((kit/'artifact_layout.json').read_text());v=kit/'verification'
candidate=json.loads((v/'candidate.json').read_text())
candidate.update(native_ZL_component_state=str(kit/layout['primary_component']),primary_ZL_component_state=str(kit/layout['primary_component']),post_ZL_component_state=str(kit/layout['post_component']),recorded_audio=str(kit/'ZL26_STEREO_FULL_WIP.wav'),full_public_kit_directory='ZL-WIP26',accepted_full_public_kit='ZL26',not_adopted_until_publication=False,not_automatically_adopted=False,not_automatically_adopted_into_public_FL_project=False,not_automatically_adopted_into_main_or_public_FL_project=False,native_parameters_changed_from_previous_public_kit=False,topology='native12/base06 -> primary accepted cohort155 -> POST Side AllPass10000Hz/Q2 +2200Hz/Q4 +895.8Hz/Q13.84 + StereoAP783.2Hz/Q19.422',accepted_publication_commit=commit,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
bestfile.write_text(json.dumps(candidate,indent=2)+'\n')
from stereo_cascade_runtime import CascadedZL,POST,EXPECTED_POST
assert POST==kit/layout['post_component']
assert EXPECTED_POST=='195e46104902cd1d5140104e8d951c859ee9ec8b1e2bb9890ce68e0597538688'
R=Path('/tmp/divalead-original-target-stereo-AllPass-20261025-01')
raw,sr=sf.read(R/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);want,sr=sf.read(R/'CANDIDATE_00.wav',dtype='float32',always_2d=True)
errors=[];roundtrips=[]
scratch=H/'actual-full26-runtime-replay';scratch.mkdir()
for k in range(2):
 c=CascadedZL('WIP26-adopt-check-'+str(k))
 try:
  c.load(kit/layout['primary_component']);out,status=c.render(raw);errors.append(float(abs(out-want).max()));np.testing.assert_allclose(out,want,rtol=8*np.finfo(np.float32).eps,atol=1e-12);assert c.latency()==0
  dst=scratch/('primary-'+str(k)+'.bin');c.save(dst);assert dst.read_bytes()==(kit/layout['primary_component']).read_bytes();assert(scratch/'fixed-post-component.bin').read_bytes()==POST.read_bytes();roundtrips.append(True)
 finally:c.close()
result=dict(adopted_complete_public_kit='ZL-WIP26',publication_commit=commit,actual_new_runtime_two_cold_two_ZL_chain_errors=errors,both_component_roundtrips_exact=all(roundtrips),fixed_POST_SHA256=EXPECTED_POST,original_objective_and_tolerances_unchanged=True,additional_lowmid_error_limit_dB=3.35,full_reference_match=False,FL_GUI_pending=True)
(H/'ADOPTED_FULL26_RUNTIME_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
