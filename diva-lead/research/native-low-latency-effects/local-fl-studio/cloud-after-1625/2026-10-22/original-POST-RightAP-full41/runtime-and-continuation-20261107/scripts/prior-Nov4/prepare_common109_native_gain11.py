from pathlib import Path
V=Path(__file__).resolve().parent;s=(V/'common109_linked64_support.py').read_text().replace('/tmp/divalead-native12-common109-linked64-fine-20261104','/tmp/divalead-native12-common109-native-globalgain11-20261104').replace('ORIGINAL_NATIVE12_COMMON109_LINKED64_FINE_STUDY.json','ORIGINAL_NATIVE12_COMMON109_NATIVE_GLOBALGAIN11_STUDY.json');(V/'common109_native_gain11_support.py').write_text(s)
s=(V/'study_common109_linked64_fine.py').read_text().replace('import common109_linked64_support as q','import common109_native_gain11_support as q').replace('Common109Linked64','Common109NativeGain11')
a=s.index('def model(delta):');b=s.index('\ndef cascade(',a);s=s[:a]+'''def model(delta):
 p.load(R/'MODEL_PRIMARY_PARENT.bin');z.load(R/'MODEL_POST_PARENT.bin');t.configure(12764+int(delta[0]),12800+int(delta[0]))
'''+s[b:]
s=s.replace("models=[(0.,0.,0.)]+list(itertools.product([-.012,-.004,.004,.012],repeat=3))","models=[(0,)]+[(d,)for d in[-12,-8,-4,-2,-1,1,2,4,8,12]]")
s=s.replace("parent['loss']-.00001","parent['loss']-.000001")
s=s.replace("p.save(R/'CANDIDATE_PRIMARY.bin');z.save(R/'CANDIDATE_POST.bin');assert(R/'CANDIDATE_PRIMARY.bin').read_bytes()!=(R/'MODEL_PRIMARY_PARENT.bin').read_bytes()","p.save(R/'CANDIDATE_PRIMARY.bin');z.save(R/'CANDIDATE_POST.bin');t.save(R/'CANDIDATE_TRIM.bin');assert(R/'CANDIDATE_TRIM.bin').read_bytes()!=(R/'TRIM.bin').read_bytes()")
s=s.replace('new_primary_linked_gain_moves_from_prior_not_adopted_fine109_point=True','new_native_final_both_channels_common_gain_from_not_adopted_fine109_point=True')
s=s.replace('new_coupled_gain_target20_21_22_deltas=[-.012,-.004,.004,.012]','new_native_both_channels_raw_gain_deltas=[-12,-8,-4,-2,-1,0,1,2,4,8,12],native_original_left_right_raw=[12764,12800],source_and_pre_ZL_native12_unchanged=True')
s=s.replace('all65_training_models_same3_actual_native_inputs=True','all11_training_models_same3_actual_native_inputs=True').replace('new_candidate_must_improve_parent_training_loss_by000001=True','new_candidate_must_improve_parent_training_loss_by0000001=True')
s=s.replace('3*len(rows)','3*len(rows)').replace('PARTIAL_65_RESULTS','PARTIAL_11_RESULTS').replace('actual_new_linked_gain_target_grid','actual_new_native_global_gain11_grid').replace('finite_changed_linked64_complete_not_adopted','finite_native_global_gain11_complete_not_adopted').replace('common109-linked64-new12','common109-nativeGain11-new12')
s=s.replace('No source/native pipeline change','Source/native12 fixed, final native trim gain only')
s=s.replace('New coupled Gain/TargetGain moves; never rerender the unchanged near-miss as acceptance.','Calibrate finer native output gain; only actual changed presets eligible, all original gates fixed.')
(V/'study_common109_native_gain11.py').write_text(s)
print('Prepared11 actual native both-channel gain settings; unchanged point excluded from new acceptance')
