"""Adopt remotely verified full41, then exercise the actual current runtime twice."""
from pathlib import Path
import copy,hashlib,json,shutil,subprocess
import numpy as np,soundfile as sf
J=Path(__file__).resolve().parent;A=J.parent/'pc-stereo-20261024';N=J.parent/'native-low-latency-effects';P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
read=lambda p:json.loads(Path(p).read_text());receipt=read(J/'ZL41_FULL_PUBLICATION.json');assert receipt['two_cold_ZIP_full_errors']==[0.,0.]and len(receipt['HTTP_byte_exact_paths'])==4
assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',receipt['commit'],'origin/main']).returncode==0
stop=N/'zl-stereo-continuation.stop';assert read(stop)['owner']=='full41-POST-RightAP-supported-export-20261107'and not(N/'zl-stereo-numerical.pause').exists()
bestfile=A/'stereo-continuous87/BEST_CANDIDATE.json';before=bestfile.read_bytes();old=json.loads(before);assert old['source_accepted_cohort']==620;shutil.copyfile(bestfile,J/'BEST_BEFORE_FULL41.json')
kit=PUBLIC/'ZL-WIP41';layout=read(kit/'artifact_layout.json');candidate=read(kit/'verification/candidate.json');assert Path(old['native_ZL_component_state']).read_bytes()==(kit/layout['primary_component']).read_bytes()
candidate.update(native_ZL_component_state=str(kit/layout['primary_component']),primary_ZL_component_state=str(kit/layout['primary_component']),post_ZL_component_state=str(kit/layout['post_component']),post_native_trim_state=str(kit/layout['post_native_trim_state']),recorded_audio=str(kit/'ZL41_STEREO_FULL_WIP.wav'),not_adopted_until_publication=False,not_automatically_adopted=False,not_automatically_adopted_into_public_FL_project=False,not_adopted_until_supported_export=False,accepted_publication_commit=receipt['commit'],reference_match_reached=False)
seed=candidate['native_base'];seed['native_saved_state_bundle']['directory']=str(kit)
for key in ['waveshaper_bipolar_base_state','waveshaper_os_local17_parent_state']:seed[key]=str(kit/'verification'/Path(seed[key]).name)
from fl20_curve import native_dsp_settings_SHA256
assert native_dsp_settings_SHA256(seed['x'],seed)==seed['native_saved_state_bundle']['settings_SHA256']
raw,rate=sf.read(kit/'verification/ACTUAL_NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);want,sr=sf.read(kit/'ZL41_STEREO_FULL_WIP.wav',dtype='float32',always_2d=True);assert rate==sr==48000
try:
    bestfile.write_text(json.dumps(candidate,indent=2)+'\n')
    from stereo_cascade_runtime import CascadedZL,POST,EXPECTED_POST,TRIM,EXPECTED_TRIM
    assert POST==kit/layout['post_component']and TRIM==kit/layout['post_native_trim_state'];scratch=Path('/tmp/divalead-full41-runtime-replay');scratch.mkdir();errors=[]
    for k in range(2):
        host=CascadedZL('WIP41-adopt-check-'+str(k))
        try:
            host.load(kit/layout['primary_component']);out,status=host.render(raw);np.testing.assert_array_equal(out,want);assert host.latency()==0;errors.append(float(abs(out-want).max()));dst=scratch/f'primary-{k}.bin';host.save(dst);assert dst.read_bytes()==(kit/layout['primary_component']).read_bytes();assert(scratch/'fixed-post-component.bin').read_bytes()==POST.read_bytes();assert(scratch/'fixed-native-post-trim.bin').read_bytes()==TRIM.read_bytes()
        finally:host.close()
    proof=dict(adopted_complete_public_kit='ZL-WIP41',publication_commit=receipt['commit'],actual_runtime_two_cold_cascade_vs_published_working_WAV_errors=errors,components_and_trim_roundtrips_exact=True,fixed_POST_SHA256=EXPECTED_POST,fixed_native_trim_SHA256=EXPECTED_TRIM,source_Diva_MIDI3_ARP_ADSR_all13_native_PRIMARY_unchanged=True,exact_full41_NEW12_and_coldZIP_passed=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False);(J/'ADOPTED_FULL41_RUNTIME_CHECK.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
except BaseException:bestfile.write_bytes(before);raise
