from pathlib import Path
V=Path(__file__).resolve().parent;src=V.parent/'continuation-20261031/study_WS_OS_local17_current39.py';s=src.read_text()
s=s.replace('native_dsp_settings_SHA256,HIGH_FORMAT','native_dsp_settings_SHA256,HIGH_FORMAT,os_local17_curve_bytes')
s=s.replace('/tmp/divalead-WS-OS-local17-current39-20261031','/tmp/divalead-native12-supported-local17-current576-20261104').replace('WS_OS_LOCAL17_CURRENT39','NATIVE12_SUPPORTED_LOCAL17_CURRENT576').replace('ZL-WIP39','ZL-WIP40')
s=s.replace("canonical=Path('/tmp/divalead-WS-oversampling-spinner-20261031/wheel_up/after.bin').read_bytes()","canonical=original_canonical")
s=s.replace('origin=np.zeros(17);step=np.r_[','origin=np.array(seed[\'waveshaper_os_local17_adjustment\'],float);step=.35*np.r_[')
start=s.index('def native_case(v):');end=s.index('def native(tag):',start)
s=s[:start]+'''def native_case(v):
 return dict(seed,waveshaper_os_local17_adjustment=list(map(float,v)),native_saved_state_bundle=None)
def curve(v):
 if v is None:return original_canonical
 try:return os_local17_curve_bytes(base,native_case(v))
 except AssertionError:return None
'''+s[end:]
s=s.replace("assert [i for i in range(len(canonical))if canonical[i]!=original_canonical[i]]==[18]","assert original_canonical==canonical and curve(origin)==original_canonical")
s=s.replace('seed=2026103117','seed=2026110417').replace('OSLocal17-39','SupportedLocal17-40').replace('current39-canonical-control','current576-canonical-control')
s=s.replace('not_compatible_with_standard_x95_exporter=True','not_compatible_with_standard_x95_exporter=False').replace('not_compatible_with_current_supported_curve_generator=True','not_compatible_with_current_supported_curve_generator=False')
s=s.replace('requires_explicit_supported_metadata_migration=True','requires_explicit_supported_metadata_migration=False')
s=s.replace('latest_BEST_context_and_explicit_supported_metadata_migration_required=True','latest_BEST_context_and_full_FL20_export_required=True')
s=s.replace("parent='supported39 geometry with actual GUI oversamplingstep1, unchanged source3held and all other11native'","parent='accepted native12 OSstep1 canonical local17 and current576 PRIMARY, new .35-scale local coefficient neighborhood; same supported generator and source3held'")
s=s.replace('new12_paired_native_control_vs_local17_candidate_validation','new12_supported_native12_local17_original_validation')
s=s.replace('current39-new12','current576-native12-new12').replace('current_accepted39','current_accepted40')
s=s.replace('CONTROL_NATIVE11_NO_OS.bin','CONTROL_NATIVE12_OS_LOCAL17.bin')
s=s.replace('requires_explicit_supported_metadata_migration=True','requires_explicit_supported_metadata_migration=False')
s=s.replace('Jointly refit 17 local odd/even stock WaveShaper curve controls to original.','Refine existing supported canonical native12 local17 coefficients against original.')
(V/'study_supported_native12_local17_current576.py').write_text(s)
print('Prepared actual native12 curve refinement; no quality thresholds changed')
