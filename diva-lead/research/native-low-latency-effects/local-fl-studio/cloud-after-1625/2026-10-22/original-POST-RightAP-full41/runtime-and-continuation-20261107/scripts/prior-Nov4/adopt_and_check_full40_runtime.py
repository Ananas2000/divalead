"""Adopt only after remote full-kit proof, then exercise two fresh actual cascades."""
from pathlib import Path
import hashlib,json,shutil,subprocess
import numpy as np,soundfile as sf
V=Path(__file__).resolve().parent;A=V.parent/'pc-stereo-20261024';N=V.parent/'native-low-latency-effects';P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
read=lambda p:json.loads(Path(p).read_text());receipt=read(V/'ZL40_FULL_PUBLICATION.json');commit=receipt['commit'];assert subprocess.run(['git','-C',str(P),'merge-base','--is-ancestor',commit,'origin/main']).returncode==0;assert all(c['HTTP_byte_exact']for c in receipt['HTTP_checks']);stop=N/'zl-stereo-continuation.stop';assert read(stop)['owner']=='full40-supported-export-20261104';assert not(N/'zl-stereo-numerical.pause').exists()
bestfile=A/'stereo-continuous87/BEST_CANDIDATE.json';before=bestfile.read_bytes();old=json.loads(before);assert old['source_accepted_cohort']==565;shutil.copyfile(bestfile,V/'BEST_BEFORE_FULL40.json');Q=Path('/tmp/divalead-recovered-OS17-point-new12-20261104');assert Path(old['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(old['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
kit=PUBLIC/'ZL-WIP40';layout=read(kit/'artifact_layout.json');candidate=read(kit/'verification/candidate.json');candidate.update(native_ZL_component_state=str(kit/layout['primary_component']),primary_ZL_component_state=str(kit/layout['primary_component']),post_ZL_component_state=str(kit/layout['post_component']),post_native_trim_state=str(kit/layout['post_native_trim_state']),recorded_audio=str(kit/'ZL40_STEREO_FULL_WIP.wav'),not_adopted_until_publication=False,not_automatically_adopted=False,not_automatically_adopted_into_public_FL_project=False,not_adopted_until_supported_export=False,accepted_publication_commit=commit,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
seed=candidate['native_base'];seed['native_saved_state_bundle']['directory']=str(kit);seed['waveshaper_bipolar_base_state']=str(kit/'verification/WS_BIPOLAR_GUI_CONVERTED_BASE.bin');seed['waveshaper_os_local17_parent_state']=str(kit/'verification/WS_OSSTEP1_NATIVE11_PARENT.bin')
# Install only the independently tested backwards-compatible curve helper; audio workers are stopped.
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  names=[x.replace(b'\\',b'/').rsplit(b'/',1)[-1]for x in p.read_bytes().split(b'\0')]
  assert not any(x==b'vst3_effect_host.exe' or (x.startswith(b'fl_native_')and x.endswith(b'.exe'))for x in names),'Audio host still live'
 except(FileNotFoundError,ProcessLookupError):pass
shutil.copyfile('/tmp/divalead-local-1625/fl20_curve.py',V/'PREVIOUS_RUNTIME_fl20_curve.py');shutil.copyfile(V/'fl20_curve.py','/tmp/divalead-local-1625/fl20_curve.py')
from fl20_curve import native_dsp_settings_SHA256
assert native_dsp_settings_SHA256(seed['x'],seed)==seed['native_saved_state_bundle']['settings_SHA256']
raw,sr=sf.read(kit/'verification/NATIVE12_BEFORE_ZL_WIP.wav',dtype='float32',always_2d=True);canonical,_=sf.read(kit/'verification/CANONICAL_COLD_FULL_WIP.wav',dtype='float32',always_2d=True);warm,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000
try:
 bestfile.write_text(json.dumps(candidate,indent=2)+'\n')
 from stereo_cascade_runtime import CascadedZL,POST,EXPECTED_POST,TRIM,EXPECTED_TRIM
 assert POST==kit/layout['post_component']and TRIM==kit/layout['post_native_trim_state'];assert EXPECTED_POST==hashlib.sha256((Q/'CANDIDATE_POST.bin').read_bytes()).hexdigest();assert EXPECTED_TRIM==hashlib.sha256((Q/'CANDIDATE_NATIVE_TRIM.bin').read_bytes()).hexdigest()
 scratch=Path('/tmp/divalead-full40-runtime-replay');scratch.mkdir();errors=[];warm_errors=[]
 for k in range(2):
  c=CascadedZL('WIP40-adopt-check-'+str(k))
  try:
   c.load(kit/layout['primary_component']);out,status=c.render(raw);np.testing.assert_allclose(out,canonical,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-canonical).max()));e=float(abs(out-warm).max());assert e<=2e-7;warm_errors.append(e);assert c.latency()==0;dst=scratch/('primary-'+str(k)+'.bin');c.save(dst);assert dst.read_bytes()==(kit/layout['primary_component']).read_bytes();assert(scratch/'fixed-post-component.bin').read_bytes()==POST.read_bytes();assert(scratch/'fixed-native-post-trim.bin').read_bytes()==TRIM.read_bytes()
  finally:c.close()
 result=dict(adopted_complete_public_kit='ZL-WIP40',publication_commit=commit,actual_new_runtime_two_cold_two_ZL_vs_canonical_chain_errors=errors,cold_vs_warm_validation_absolute_errors=warm_errors,unchanged_native_absolute_tolerance=2e-7,both_components_and_trim_roundtrips_exact=True,fixed_POST_SHA256=EXPECTED_POST,fixed_native_trim_SHA256=EXPECTED_TRIM,source_Diva_MIDI_ARP_ADSR_other11native_unchanged=True,first6AND10_cold2_stereo_and_nonincreasing_Air_confirmed_for_exact_point=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True);(V/'ADOPTED_FULL40_RUNTIME_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
except BaseException:bestfile.write_bytes(before);raise
