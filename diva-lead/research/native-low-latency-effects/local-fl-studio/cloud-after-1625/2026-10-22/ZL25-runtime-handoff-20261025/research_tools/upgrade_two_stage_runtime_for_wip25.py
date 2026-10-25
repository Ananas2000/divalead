"""Keep the actually adopted three-band POST in subsequent real-plugin work."""
from pathlib import Path
import hashlib,json,shutil
A=Path('/workspace/divalead-work/pc-stereo-20261024');HERE=Path(__file__).resolve().parent
old=HERE/'runtime-before-ZL25';old.mkdir(exist_ok=True)
for name in ['stereo_cascade_runtime.py','continue_stereo_ZL_matching.py','backup_stereo_numeric_checkpoint.py']:
 shutil.copyfile(A/name,old/name)
p=A/'stereo_cascade_runtime.py';s=p.read_text();s=s.replace('import hashlib','import hashlib,json')
was="POST=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP24/verification/ZL24_POST_COMPONENT.bin')"
now="""# Freeze the currently adopted saved POST for this entire process. Never
# silently revert a new phase repair to an older hard-coded full-kit state.
BEST_PATH=Path('/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json')
ADOPTED=json.loads(BEST_PATH.read_text())
assert ADOPTED['requires_two_ZL_instances']
POST=Path(ADOPTED['post_ZL_component_state'])
assert POST.is_file()
""".rstrip()
assert was in s;s=s.replace(was,now);p.write_text(s)
p=A/'continue_stereo_ZL_matching.py';s=p.read_text()
s=s.replace('from stereo_cascade_runtime import CascadedZL as WinVST3','from stereo_cascade_runtime import CascadedZL as WinVST3, POST, EXPECTED_POST')
s=s.replace('configured_real_VST3_workers=2,','fixed_post_component=str(POST),fixed_post_SHA256=EXPECTED_POST,full_base_kit=best.get(\'full_public_kit_directory\',\'ZL-WIP24\'),additional_lowmid_300_800_error_limit_dB=3.35,configured_real_VST3_workers=2,')
s=s.replace('reference_LR=lr_bands(reference)','''reference_LR=lr_bands(reference)
lowmid_mask=(frequency>=300)&(frequency<800)
def lowmid_lr(y):
    power=abs(np.fft.rfft(y,axis=0))**2
    return float(10*np.log10(power[lowmid_mask,0].sum()/power[lowmid_mask,1].sum()))
reference_lowmid_LR=lowmid_lr(reference)''')
was="    return dict(stereo_high_band_error=error,high_LR_dB=lr.tolist(),stereo_preservation_passed=bool(error<=1.5 and np.max(np.abs(lr))<=1.6))"
now="""    low=lowmid_lr(edit);low_error=abs(low-reference_lowmid_LR)
    # Additional preservation constraint; original fit/loss/acceptance gates
    # are unchanged. Keep the independently confirmed ZL25 low-mid repair.
    return dict(stereo_high_band_error=error,high_LR_dB=lr.tolist(),lowmid_300_800_LR_dB=low,lowmid_300_800_error_dB=low_error,lowmid_preservation_passed=bool(low_error<=3.35),stereo_preservation_passed=bool(error<=1.5 and np.max(np.abs(lr))<=1.6 and low_error<=3.35))"""
assert was in s;s=s.replace(was,now);p.write_text(s)
p=A/'backup_stereo_numeric_checkpoint.py';s=p.read_text()
was="full=PUBLIC/'ZL-WIP24';old=(full/'verification/ZL24_PRIMARY_COMPONENT.bin').read_bytes();primary=(work/'candidate-component.bin').read_bytes();post=(work/'fixed-post-component.bin').read_bytes();assert post==(full/'verification/ZL24_POST_COMPONENT.bin').read_bytes()"
now="""best=read(A/'stereo-continuous87/BEST_CANDIDATE.json');full=PUBLIC/best.get('full_public_kit_directory','ZL-WIP24');layout=read(full/'artifact_layout.json')if(full/'artifact_layout.json').exists()else dict(project='Diva_ZL24_STEREO_WIP.flp',primary_component='verification/ZL24_PRIMARY_COMPONENT.bin',post_component='verification/ZL24_POST_COMPONENT.bin',primary_preset='presets/SUM_ZL24_PRIMARY.fst',post_preset='presets/SUM_ZL24_STEREO_FIX.fst',sum_insert='presets/04_SUM.fst',primary_vstpreset='presets/ZL24_PRIMARY.vstpreset');old=(full/layout['primary_component']).read_bytes();primary=(work/'candidate-component.bin').read_bytes();post=(work/'fixed-post-component.bin').read_bytes();assert post==(full/layout['post_component']).read_bytes();post_description='+'.join(str(p['frequency'])+'Hz/Q'+str(p['Q'])for p in best.get('post_Side_AllPasses',[dict(frequency=10000,Q=2),dict(frequency=2200,Q=4)]));primary_name=Path(layout['primary_preset']).name;post_name=Path(layout['post_preset']).name"""
assert was in s;s=s.replace(was,now)
was="  (playable/'Diva_STEREO_CONTINUED_WIP.flp').write_bytes(replace_primary((full/'Diva_ZL24_STEREO_WIP.flp').read_bytes(),old,primary))\n  for name in ['SUM_ZL24_PRIMARY.fst','04_SUM.fst']:(presets/name).write_bytes(replace_primary((full/'presets'/name).read_bytes(),old,primary))\n  (presets/'ZL24_PRIMARY.vstpreset').write_bytes(vstpreset(primary))"
now="""  (playable/'Diva_STEREO_CONTINUED_WIP.flp').write_bytes(replace_primary((full/layout['project']).read_bytes(),old,primary))
  for name in [layout['primary_preset'],layout['sum_insert']]:(playable/name).write_bytes(replace_primary((full/name).read_bytes(),old,primary))
  (playable/layout['primary_vstpreset']).write_bytes(vstpreset(primary))
  assert post in (playable/'Diva_STEREO_CONTINUED_WIP.flp').read_bytes() or post_description
  # Byte replacement touches the primary only. Full saved native/MIDI/POST
  # structure retains the already serialized and cold-replayed complete base.
""".rstrip()
assert was in s;s=s.replace(was,now)
# Component wrappers can be encoded/compressed inside the project; do not
# claim a raw byte-substring check validates them. replace_primary proves
# unchanged XML and untouched serialized wrapper nodes in its own parser.
s=s.replace("  assert post in (playable/'Diva_STEREO_CONTINUED_WIP.flp').read_bytes() or post_description\n",'')
s=s.replace('# Продолжение ZL24 на трёх нотах:',"# Продолжение {full.name} на трёх нотах:")
s=s.replace('10000Гц/Q2+2200Гц/Q4 неизменен.','{post_description} неизменен.')
s=s.replace('presets/SUM_ZL24_PRIMARY.fst','presets/{primary_name}').replace('presets/SUM_ZL24_STEREO_FIX.fst','presets/{post_name}')
# Above text replacements must not corrupt the non-f-string fallback layout.
s=s.replace("primary_preset='presets/{primary_name}'","primary_preset='presets/SUM_ZL24_PRIMARY.fst'").replace("post_preset='presets/{post_name}'","post_preset='presets/SUM_ZL24_STEREO_FIX.fst'")
s=s.replace('и |LR|<=1.6dB по2–5/5–10/10–14кГц.','и |LR|<=1.6dB по2–5/5–10/10–14кГц; дополнительный предел ошибки300–800Гц3.35dB.')
s=s.replace('../ZL24_CONTINUATION_RU.md.',"../{full.name.replace('ZL-WIP','ZL')}_CONTINUATION_RU.md.")
s=s.replace('Latest complete base remains ZL24','Latest complete base {full.name}')
s=s.replace('postSide10000Q2+2200Q4 unchanged','postSide{post_description} unchanged; additional lowmid300-800 errorlimit3.35dB')
p.write_text(s)
for name in ['stereo_cascade_runtime.py','continue_stereo_ZL_matching.py','backup_stereo_numeric_checkpoint.py']:
 p=A/name;compile(p.read_text(),p.name,'exec')
(HERE/'RUNTIME_UPGRADE_SYNTAX_PROOF.json').write_text(json.dumps(dict(files={name:hashlib.sha256((A/name).read_bytes()).hexdigest()for name in ['stereo_cascade_runtime.py','continue_stereo_ZL_matching.py','backup_stereo_numeric_checkpoint.py']},post_follows_adopted_best=True,original_objective_and_numerical_tolerances_unchanged=True,additional_lowmid_preservation_error_limit_dB=3.35),indent=2)+'\n')
print('Actual two-stage runtime and auto-backup upgraded; syntax verified. Not yet adopted or started.')
