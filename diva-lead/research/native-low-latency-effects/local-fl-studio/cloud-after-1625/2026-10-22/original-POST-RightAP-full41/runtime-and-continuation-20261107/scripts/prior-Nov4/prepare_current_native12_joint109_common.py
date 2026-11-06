from pathlib import Path
import re
V=Path(__file__).resolve().parent;s=(V/'source_cutoff_primary94_support.py').read_text().replace('/tmp/divalead-native12-Diva-cutoff144p04-primary94-20261104','/tmp/divalead-native12-current580-bothZL109-common-inputs-20261104').replace('ORIGINAL_NATIVE12_DIVA_CUTOFF_PRIMARY94_STUDY.json','ORIGINAL_NATIVE12_CURRENT580_BOTHZL109_COMMON_STUDY.json');(V/'current_native12_joint109_support.py').write_text(s)
s=(V/'study_source_cutoff_primary94_native12.py').read_text().replace('import source_cutoff_primary94_support as q','import current_native12_joint109_support as q')
a=s.index('from checked_mean_three_real_primary_fit import');b=s.index('\nfrom native_post_trim',a)
s=s[:a]+'''from joint_primary_post_fit import JointPrimaryPostFit as BaseJoint109
class JointPrimaryPostFit(BaseJoint109):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw)
  for spec in self.post_specs:spec['step']*=.35
  (self.root/'EXACT109_PARAMETER_SPECS.json').write_text(q.json.dumps(self.specs,indent=2)+'\\n')
'''+s[b:]
s=s.replace('DIVA_CUTOFF_PRIMARY94_NATIVE12','CURRENT_NATIVE12_BOTHZL109_COMMON')
s=s.replace("q.patched({('VCF1','Freq'):144.04})","q.patched({})").replace('assert changed=={148};assert not np.array_equal(source_now,q.baseline_raw)','assert changed==set();np.testing.assert_array_equal(source_now,q.baseline_raw)')
s=re.sub(r"nc=q\.native\([^;\r\n]+\);?","nc=None;",s);s=s.replace('candidate_raw,_=nc.render();','candidate_raw=raw.copy();').replace('n.close();n=None;nc.close();nc=None;','n.close();n=None;').replace('n.close();nc.close();','n.close();')
s=s.replace('source_only_VCF1Freq144p04_changed_from144p16=True','source_Diva_MIDI_ARP_ADSR_all_native12_and_trim_unchanged=True,POST_step_scale035=True')
s=s.replace('Diva_all281_audited_only_VCF1Freq_changed_MIDI3held_ARP_ADSR_native12_nativeTrim_unchanged=True','Diva_all281_MIDI3held_ARP_ADSR_native12_nativeTrim_unchanged=True')
s=s.replace('Diva_VCF1Freq_and_PRIMARY94_changed_POST_unchanged=True','existing_PRIMARY94_and_POST15_jointly_changed=True')
s=s.replace('three_COMMON_candidate_native_inputs_for_every_primary_proposal_control_uses_old_source=True','three_COMMON_actual_native_inputs_for_every_proposal_AND_control=True')
s=s.replace('existing_PRIMARY94_refitted_POST_unchanged=True','existing_PRIMARY94_and_POST15_jointly_refitted=True')
s=s.replace('three_candidate_native_realizations_shared_by_every_primary_proposal_control_old_Diva_source_unchanged=True','three_same_actual_native_realizations_shared_by_every_proposal_AND_control=True')
s=s.replace('native_base=dict(q.seed,source_manifest=source_manifest)','native_base=q.seed')
s=s.replace('Nov4CutoffJoint94','Nov4Native12Joint109Common').replace('/tmp/divalead-native12-sourceCutoff-primary94-new12-','/tmp/divalead-native12-bothZL109-common-new12-')
s=s.replace("assert q.prior['full_public_kit_directory']=='ZL-WIP40'","assert q.prior['full_public_kit_directory']=='ZL-WIP40'")
s=s.replace('actual_Diva_changed_source_before_joint_primary_fit','actual_Diva_unchanged_source_recheck_before_bothZL_fit')
s=s.replace('no_native_MIDI_or_trim_change=True','no_native_MIDI_or_trim_change=True,no_Diva_parameter_change=True')
s=s.replace('two_primary_coordinate_sweeps=True','two_joint109_coordinate_sweeps=True')
s=s.replace('original_target_loss_and_latest559_positive_gates_not_replaced_by_anchor40_comparison','original_target_loss_and_current_positive_gates_not_replaced_by_anchor40_comparison')
s=s.replace('candidate_native_DSP_renders','common_native_DSP_renders')
(V/'study_current_native12_joint109_common.py').write_text(s)
print('Prepared PRIMARY94+POST15 common-input fit, POST step .35, all source/native/notes fixed')
