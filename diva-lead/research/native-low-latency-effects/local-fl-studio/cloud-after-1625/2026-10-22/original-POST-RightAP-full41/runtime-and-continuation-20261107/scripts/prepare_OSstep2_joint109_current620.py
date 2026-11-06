from pathlib import Path
J=Path(__file__).resolve().parent;V=Path('/workspace/divalead-work/continuation-20261104')
s=(J/'delta29_current620_support.py').read_text().replace('/tmp/divalead-native12-delta29-current620-20261107','/tmp/divalead-OSstep2-native12-joint109-current620-20261107').replace('ORIGINAL_NATIVE12_DELTA29_CURRENT620_STUDY.json','ORIGINAL_OSSTEP2_NATIVE12_JOINT109_CURRENT620_STUDY.json')
(J/'OSstep2_joint109_620_support.py').write_text(s)
s=(V/'study_current_native12_joint109_common.py').read_text().replace('import current_native12_joint109_support as q','import OSstep2_joint109_620_support as q')
s=s.replace("spec['step']*=.35","spec['step']*=.65").replace('CURRENT_NATIVE12_BOTHZL109_COMMON','OSSTEP2_NATIVE12_JOINT109_CURRENT620').replace('Nov4Native12Joint109Common','OSstep2Joint109620')
s=s.replace('/tmp/divalead-native12-bothZL109-common-new12-','/tmp/divalead-OSstep2-native12-joint109-620-new12-')
s=s.replace('Diva_all281_MIDI3held_ARP_ADSR_native12_nativeTrim_unchanged=True','Diva_all281_MIDI3held_ARP_ADSR_other_native11_nativeTrim_unchanged=True,native_WaveShaper_actual_GUI_OSstep2_changed=True')
s=s.replace('three_COMMON_actual_native_inputs_for_every_proposal_AND_control=True','three_actual_OS2_candidate_inputs_shared_by_proposals_control_OS1_independent_Chorus_draws=True')
s=s.replace('source_Diva_MIDI_ARP_ADSR_all_native12_and_trim_unchanged=True','source_Diva_MIDI_ARP_ADSR_other_native11_and_trim_unchanged=True,native_WaveShaper_GUI_OSstep2_changed=True').replace('POST_step_scale035=True','POST_step_scale065=True')
s=s.replace('no_native_MIDI_or_trim_change=True','only_native_WaveShaper_OS_step_changed_no_MIDI_or_trim_change=True')
s=s.replace('three_same_actual_native_realizations_shared_by_every_proposal_AND_control=True','three_same_actual_OS2_native_realizations_shared_by_every_proposal_control_native_OS1_draws_independent=True')
s=s.replace('MINUS0003dB','MINUS0006dB').replace(')))-.003',')))-.006')
s=s.replace("assert q.prior['full_public_kit_directory']=='ZL-WIP40'","assert q.prior['full_public_kit_directory']=='ZL-WIP40'and q.prior['source_accepted_cohort']==620")
a=s.index("(R/'PREDECLARED_PROTOCOL.json')")
s=s[:a]+'''gui=Path('/tmp/divalead-WS-native12-OSstep2-GUI-20261104/after.bin');blob=gui.read_bytes();old=(Path(q.seed['native_saved_state_bundle']['directory'])/'verification/SOURCE_WaveShaper.bin').read_bytes();assert len(blob)==len(old)and[i for i in range(len(blob))if blob[i]!=old[i]]==[18]and struct.unpack_from('<I',blob,16)[0]==131073
(R/'GUI_OSSTEP2_NATIVE_STATE.bin').write_bytes(blob)
def os_native(tag):
 c=q.native(q.source['native_input'],tag);c.load_state(0,R/'GUI_OSSTEP2_NATIVE_STATE.bin');dst=R/(tag+'-actual-WS-resaved.bin');c.save_state(0,dst);assert dst.read_bytes()==blob;return c
''' +s[a:]
s=s.replace(";nc=None;p=q.WinVST3", ";nc=os_native('OS2Candidate-'+str(os.getpid()));p=q.WinVST3")
s=s.replace('candidate_raw=raw.copy();','candidate_raw,_=nc.render();')
s=s.replace('n.close();n=None;(R/','n.close();n=None;nc.close();nc=None;(R/')
s=s.replace("if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'OSstep2Joint109620-'+str(os.getpid())+'-cold-native-'+str(rep));nc=None;","if rep in[10,11]:n.close();nc.close();n=q.native(q.source['native_input'],'OSstep2Joint109620-'+str(os.getpid())+'-cold-native-'+str(rep));nc=os_native('OS2ColdNative-'+str(rep)+'-'+str(os.getpid()));")
s=s.replace("native_base=q.seed,native_ZL_component_state", "native_base=q.seed,native_WaveShaper_override_state=str(R/'GUI_OSSTEP2_NATIVE_STATE.bin'),not_compatible_with_standard_x95_exporter=True,requires_supported_OSstep2_generator_and_fingerprint_migration=True,native_ZL_component_state")
s=s.replace('finite_primary_mean3_common_input_complete_not_adopted','finite_OSstep2_joint109_current620_complete_not_adopted').replace('failed_preserve_current_latest_and_full39_anchor','failed_preserve_current620_and_full40_anchor')
s=s.replace('Three shared native inputs remove phase-draw confounding during PRIMARY fitting.','Actual native GUI OSstep2 plus existing109 cofit. OS1 control draws remain independent.')
s=s.replace('requires_latest_BEST_revalidation=True','requires_latest_BEST_revalidation=True,source_MIDI_ARP_ADSR_other_native11_trim_unchanged=True')
assert s.count("nc=os_native(")==3 and s.count('candidate_raw,_=nc.render();')==2
assert 'native12_nativeTrim_unchanged=True'not in s
(J/'study_OSstep2_joint109_current620.py').write_text(s)
print('Prepared actual GUI-native OSstep2 plus both ZL109 cofit; unsupported research state never directly adopted')
