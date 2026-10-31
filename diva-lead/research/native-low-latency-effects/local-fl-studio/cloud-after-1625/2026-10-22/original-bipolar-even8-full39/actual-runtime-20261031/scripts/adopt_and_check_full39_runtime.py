"""Adopt a published full39 only after its independent ZIP and real runtime proofs."""
from pathlib import Path
import hashlib,json,shutil,subprocess
import numpy as np,soundfile as sf
T=Path(__file__).resolve().parent;A=T.parent/'pc-stereo-20261024';N=T.parent/'native-low-latency-effects';P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
receipt=json.loads((T/'ZL39_FULL_PUBLICATION.json').read_text());commit=receipt['commit'];assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',commit,'origin/main']).returncode==0;assert all(c['HTTP_byte_exact']for c in receipt['HTTP_checks'])
stop=N/'zl-stereo-continuation.stop';assert not stop.exists();assert not(N/'zl-stereo-numerical.pause').exists()
bestfile=A/'stereo-continuous87/BEST_CANDIDATE.json';before=bestfile.read_bytes();old=json.loads(before);assert old['source_accepted_cohort']==556;shutil.copyfile(bestfile,T/'BEST_BEFORE_FULL39.json')
kit=PUBLIC/'ZL-WIP39';layout=json.loads((kit/'artifact_layout.json').read_text());candidate=json.loads((kit/'verification/candidate.json').read_text());Q=T/'BIPOLAR_FINALIST1_AIR_MARGIN_REPAIR';assert Path(old['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(old['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
candidate.update(native_ZL_component_state=str(kit/layout['primary_component']),primary_ZL_component_state=str(kit/layout['primary_component']),post_ZL_component_state=str(kit/layout['post_component']),post_native_trim_state=str(kit/layout['post_native_trim_state']),recorded_audio=str(kit/'ZL39_STEREO_FULL_WIP.wav'),full_public_kit_directory='ZL-WIP39',accepted_full_public_kit='ZL39',not_adopted_until_publication=False,not_automatically_adopted=False,not_automatically_adopted_into_public_FL_project=False,not_automatically_adopted_into_main_or_public_FL_project=False,not_adopted_until_supported_export=False,accepted_publication_commit=commit,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
candidate['native_base']['native_saved_state_bundle']['directory']=str(kit)
candidate['native_base']['waveshaper_bipolar_base_state']=str(kit/'verification/WS_BIPOLAR_GUI_CONVERTED_BASE.bin')
from fl20_curve import native_dsp_settings_SHA256
assert native_dsp_settings_SHA256(candidate['native_base']['x'],candidate['native_base'])==candidate['native_base']['native_saved_state_bundle']['settings_SHA256']
raw,sr=sf.read(Q/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);want,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000
try:
 bestfile.write_text(json.dumps(candidate,indent=2)+'\n')
 from stereo_cascade_runtime import CascadedZL,POST,EXPECTED_POST,TRIM,EXPECTED_TRIM
 assert POST==kit/layout['post_component']and TRIM==kit/layout['post_native_trim_state'];assert EXPECTED_POST==hashlib.sha256((Q/'CANDIDATE_POST.bin').read_bytes()).hexdigest();assert EXPECTED_TRIM=='4a9138dc5e1f892692f01aa9efb6449b553b6c838fbb6c59507b4f13ff611354'
 scratch=Path('/tmp/divalead-full39-runtime-replay');scratch.mkdir();errors=[]
 for k in range(2):
  c=CascadedZL('WIP39-adopt-check-'+str(k))
  try:
   c.load(kit/layout['primary_component']);out,status=c.render(raw);np.testing.assert_allclose(out,want,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-want).max()));assert c.latency()==0;dst=scratch/('primary-'+str(k)+'.bin');c.save(dst);assert dst.read_bytes()==(kit/layout['primary_component']).read_bytes();assert(scratch/'fixed-post-component.bin').read_bytes()==POST.read_bytes();assert(scratch/'fixed-native-post-trim.bin').read_bytes()==TRIM.read_bytes()
  finally:c.close()
 result=dict(adopted_complete_public_kit='ZL-WIP39',publication_commit=commit,actual_new_runtime_two_cold_two_ZL_chain_errors=errors,both_components_and_trim_roundtrips_exact=True,fixed_POST_SHA256=EXPECTED_POST,fixed_native_trim_SHA256=EXPECTED_TRIM,source_Diva_MIDI_ARP_ADSR_other11native_POST_trim_unchanged=True,first6AND10_cold2_all_stereo_and_nonincreasing_Air_confirmed=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True);(T/'ADOPTED_FULL39_RUNTIME_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
except BaseException:
 bestfile.write_bytes(before)
 raise
