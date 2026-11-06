from pathlib import Path
J=Path(__file__).resolve().parent
s=(J/'joint109_sixdraw620_support.py').read_text().replace('/tmp/divalead-native12-joint109-sixdraw-current620-20261107','/tmp/divalead-native12-joint109-sixdraw-full41-20261107').replace('ORIGINAL_NATIVE12_JOINT109_SIXDRAW_CURRENT620_STUDY.json','ORIGINAL_NATIVE12_JOINT109_SIXDRAW_FULL41_STUDY.json');(J/'joint109_sixdraw41_support.py').write_text(s)
s=(J/'study_joint109_sixdraw_current620.py').read_text().replace('import joint109_sixdraw620_support as q','import joint109_sixdraw41_support as q').replace('JOINT109_SIXDRAW_CURRENT620','JOINT109_SIXDRAW_FULL41').replace('Joint109SixDraw620','Joint109SixDrawFull41').replace('joint109-sixdraw620-new12','joint109-sixdrawFull41-new12')
s=s.replace("q.prior['full_public_kit_directory']=='ZL-WIP40'and q.prior['source_accepted_cohort']==620", "q.prior['full_public_kit_directory']=='ZL-WIP41'and q.prior['source_accepted_cohort']=='full41-RightAP12800-Q25-after620'")
s=s.replace("assert (PUBLIC/'ZL-WIP40/verification/ZL40_POST_COMPONENT.bin').read_bytes()==(R/'POST.bin').read_bytes()", "(R/'ANCHOR40_POST.bin').write_bytes((PUBLIC/'ZL-WIP40/verification/ZL40_POST_COMPONENT.bin').read_bytes());assert (R/'POST.bin').read_bytes()!=(R/'ANCHOR40_POST.bin').read_bytes()")
s=s.replace("z.load(post_component or R/'POST.bin')", "z.load(post_component or(R/'ANCHOR40_POST.bin'if Path(component).name=='ANCHOR40_PRIMARY.bin'else R/'POST.bin'))")
s=s.replace('existing_PRIMARY94_and_POST15_jointly_refitted=True','existing_PRIMARY94_and_POST15_jointly_refitted=True,existing_RightAP7_12800_Q25_from_full41_fixed=True,anchor40_uses_BOTH_original_PRIMARY_and_POST40=True')
s=s.replace('finite_joint109_sixdraw_current620_complete_not_adopted','finite_joint109_sixdraw_full41_complete_not_adopted').replace('failed_preserve_current620_and_full40_anchor','failed_preserve_full41_and_full40_anchor')
s=s.replace('original620 control','full41 control').replace('Eight_actual','Eight_actual')
assert "R/'ANCHOR40_POST.bin'"in s and "source_accepted_cohort']=='full41-RightAP12800-Q25-after620'"in s
(J/'study_joint109_sixdraw_full41.py').write_text(s)
print('Prepared six-draw joint109 from adopted41; new RightAP7 fixed; full40 anchor loads BOTH actual40 components')
