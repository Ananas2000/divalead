from pathlib import Path
J=Path(__file__).resolve().parent;V=Path('/workspace/divalead-work/continuation-20261104')
s=(V/'current_native12_joint109_support.py').read_text()
s=s.replace('/tmp/divalead-native12-current580-bothZL109-common-inputs-20261104','/tmp/divalead-native12-delta29-current620-20261107').replace('ORIGINAL_NATIVE12_CURRENT580_BOTHZL109_COMMON_STUDY.json','ORIGINAL_NATIVE12_DELTA29_CURRENT620_STUDY.json').replace('native10_and_both_ZL_components_unchanged=True','pre_ZL_native12_source_MIDI3_ARP_ADSR_unchanged=True')
(J/'delta29_current620_support.py').write_text(s)
print('Created isolated current-BEST helper; no source/MIDI/native change')
