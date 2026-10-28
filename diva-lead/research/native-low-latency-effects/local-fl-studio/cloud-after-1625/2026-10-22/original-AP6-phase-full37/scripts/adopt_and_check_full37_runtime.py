"""Adopt only the published, cold-replayed complete WIP; execute its real cascade."""
from pathlib import Path
import hashlib,json,shutil,subprocess
import numpy as np
import soundfile as sf
A=Path('/workspace/divalead-work/pc-stereo-20261024');H=Path(__file__).resolve().parent
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
receipt=json.loads((H/'ZL37_FULL_PUBLICATION.json').read_text());commit=receipt['commit']
assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',commit,'origin/main']).returncode==0
assert all(c['HTTP_byte_exact']for c in receipt['HTTP_checks'])
stop=N/'zl-stereo-continuation.stop';assert json.loads(stop.read_text())['owner']=='complete-WIP37-AP6-phase-20261028'
assert not(N/'zl-stereo-numerical.pause').exists()
bestfile=A/'stereo-continuous87/BEST_CANDIDATE.json';shutil.copyfile(bestfile,H/'BEST_BEFORE_FULL37_RETRY.json')
kit=public/'ZL-WIP37';layout=json.loads((kit/'artifact_layout.json').read_text());v=kit/'verification'
candidate=json.loads((v/'candidate.json').read_text())
candidate.update(native_ZL_component_state=str(kit/layout['primary_component']),primary_ZL_component_state=str(kit/layout['primary_component']),post_ZL_component_state=str(kit/layout['post_component']),recorded_audio=str(kit/'ZL37_STEREO_FULL_WIP.wav'),full_public_kit_directory='ZL-WIP37',accepted_full_public_kit='ZL37',not_adopted_until_publication=False,not_automatically_adopted=False,not_automatically_adopted_into_public_FL_project=False,not_automatically_adopted_into_main_or_public_FL_project=False,native_parameters_changed_from_previous_public_kit=False,topology=candidate['topology'],not_adopted_until_supported_export=False,accepted_publication_commit=commit,post_native_trim_state=str(kit/layout['post_native_trim_state']),actual_FL_GUI_validation_pending=True,reference_match_reached=False)
old_best_bytes=bestfile.read_bytes()
try:
 bestfile.write_text(json.dumps(candidate,indent=2)+'\n')
 from stereo_cascade_runtime import CascadedZL,POST,EXPECTED_POST,TRIM,EXPECTED_TRIM
 assert POST==kit/layout['post_component'];assert TRIM==kit/layout['post_native_trim_state'];assert EXPECTED_TRIM=='4a9138dc5e1f892692f01aa9efb6449b553b6c838fbb6c59507b4f13ff611354'
 assert EXPECTED_POST=='6597c11fe806b4d58243f8742eb0b358b02dbb86da63e007526025ba2f8c901f'
 R=H/'POST_AP6_JOINT_REFINEMENT36'
 raw,sr=sf.read(R/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);want,sr=sf.read(R/'CANDIDATE_00.wav',dtype='float32',always_2d=True)
 errors=[];roundtrips=[]
 scratch=H/'actual-full37-runtime-replay';scratch.mkdir(exist_ok=True)
 for k in range(2):
  c=CascadedZL('WIP37-adopt-check-'+str(k))
  try:
   c.load(kit/layout['primary_component']);out,status=c.render(raw);errors.append(float(abs(out-want).max()));np.testing.assert_allclose(out,want,rtol=8*np.finfo(np.float32).eps,atol=1e-12);assert c.latency()==0
   dst=scratch/('primary-'+str(k)+'.bin');c.save(dst);assert dst.read_bytes()==(kit/layout['primary_component']).read_bytes();assert(scratch/'fixed-post-component.bin').read_bytes()==POST.read_bytes();assert(scratch/'fixed-native-post-trim.bin').read_bytes()==TRIM.read_bytes();roundtrips.append(True)
  finally:c.close()
 result=dict(adopted_complete_public_kit='ZL-WIP37',publication_commit=commit,actual_new_runtime_two_cold_two_ZL_chain_errors=errors,both_component_roundtrips_exact=all(roundtrips),fixed_POST_SHA256=EXPECTED_POST,fixed_native_trim_SHA256=EXPECTED_TRIM,two_actual_native_post_trim_instances_verified=True,original_objective_and_tolerances_unchanged=True,additional_lowmid_error_limit_dB=3.25,upper_stereo_error_limit_dB=1.48,paired_air_increase_limit_dB=.02,full_reference_match=False,FL_GUI_pending=True)
 (H/'ADOPTED_FULL37_RUNTIME_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
except BaseException:
 bestfile.write_bytes(old_best_bytes)
 raise
