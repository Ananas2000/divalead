from pathlib import Path
J=Path(__file__).resolve().parent;V=Path('/workspace/divalead-work/continuation-20261104')
s=(J/'delta29_current620_support.py').read_text().replace('/tmp/divalead-native12-delta29-current620-20261107','/tmp/divalead-native12-joint109-sixdraw-current620-20261107').replace('ORIGINAL_NATIVE12_DELTA29_CURRENT620_STUDY.json','ORIGINAL_NATIVE12_JOINT109_SIXDRAW_CURRENT620_STUDY.json');(J/'joint109_sixdraw620_support.py').write_text(s)
s=(V/'study_current_native12_joint109_common.py').read_text().replace('import current_native12_joint109_support as q','import joint109_sixdraw620_support as q')
a=s.index('class JointPrimaryPostFit(');b=s.index('\nfrom native_post_trim',a)
s=s[:a]+'''class JointPrimaryPostFit(BaseJoint109):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw)
  for spec in self.post_specs:spec['step']*=.35
  for spec in self.specs[:94]:spec['step']*=.65
  (self.root/'EXACT109_PARAMETER_SPECS.json').write_text(q.json.dumps(self.specs,indent=2)+'\\n')
 def evaluate(self,case,phase=0,keep=True):
  label,x=case;p,z=self.pool.get()
  try:
   captures=[]
   for k in(range(6)if keep else[phase]):
    self.apply_to_hosts(p,z,x);mid,_=p.render(self.native_inputs[k]);pre,_=z.render(mid);out=self.trims[p.child.pid].render(pre);assert p.latency()+z.latency()==0;captures.append(self.assess(out))
   row=dict(captures[len(captures)//2]);row.update(label=label,x=list(map(float,x)),loss=float(np.mean([v['loss']for v in captures])),positive_excess_air_dB=float(np.mean([v['positive_excess_air_dB']for v in captures])),lowmid_error=float(np.mean([v['lowmid_error']for v in captures])),training_realization_assessments=captures,training_realization_losses=[v['loss']for v in captures],actual_DSP_render_count=len(captures),original_stereo_preservation_passed=all(v['original_stereo_preservation_passed']for v in captures));row['stereo_preservation_passed']=bool(row['original_stereo_preservation_passed']and(not keep or(row['positive_excess_air_dB']<=self.training_air_cap and row['lowmid_error']<=self.training_lowmid_cap)))
   if keep:
    with self.lock:self.rows.append(row)
   return row
  finally:self.pool.put((p,z))
''' +s[b:]
s=s.replace('CURRENT_NATIVE12_BOTHZL109_COMMON','JOINT109_SIXDRAW_CURRENT620').replace('Nov4Native12Joint109Common','Joint109SixDraw620').replace('/tmp/divalead-native12-bothZL109-common-new12-','/tmp/divalead-native12-joint109-sixdraw620-new12-')
s=s.replace('three_COMMON_actual_native_inputs_for_every_proposal_AND_control=True','six_COMMON_actual_native_inputs_for_every_proposal_AND_control=True')
s=s.replace('three_same_actual_native_realizations_shared_by_every_proposal_AND_control=True','six_same_actual_native_realizations_shared_by_every_proposal_AND_control=True')
s=s.replace('two_joint109_coordinate_sweeps=True,PRIMARY_step_scale1=True','one_joint109_coordinate_sweep=True,PRIMARY_step_scale065=True').replace('MINUS0003dB','MINUS0006dB').replace(')))-.003',')))-.006')
s=s.replace('range(5)','range(8)').replace('range(3)','range(6)').replace('controls[:3]','controls[:6]').replace('anchors[:3]','anchors[:6]').replace('[3,4]','[6,7]').replace('fit.fit(sweeps=2)','fit.fit(sweeps=1)').replace('actual_training_DSP_renders=3*len(fit.rows)','actual_training_DSP_renders=6*len(fit.rows)')
s=s.replace("assert q.prior['full_public_kit_directory']=='ZL-WIP40'","assert q.prior['full_public_kit_directory']=='ZL-WIP40'and q.prior['source_accepted_cohort']==620")
s=s.replace('frozen_after_two_sweeps_before_any_new_validation','frozen_after_sixdraw_one_sweep_before_any_new_validation').replace('finite_primary_mean3_common_input_complete_not_adopted','finite_joint109_sixdraw_current620_complete_not_adopted').replace('failed_preserve_current_latest_and_full39_anchor','failed_preserve_current620_and_full40_anchor')
s=s.replace('Three shared native inputs remove phase-draw confounding during PRIMARY fitting.','Six actual common native inputs per each existing109 joint proposal, original620 control; audio never averaged.')
# Six training inputs and two untouched heldout inputs; fresh12 is wholly separate.
assert "for k in(range(6)if keep else[phase]):"in s and 'fit.fit(sweeps=1)'in s and '[6,7]'in s and 'actual_training_DSP_renders=6*len(fit.rows)'in s
(J/'study_joint109_sixdraw_current620.py').write_text(s)
print('Prepared six actual shared native training draws +two untouched heldout, one485-case109 sweep; source/native/trim fixed')
