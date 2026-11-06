from pathlib import Path
J=Path(__file__).resolve().parent;V=Path('/workspace/divalead-work/continuation-20261104')
s=(J/'delta29_current620_support.py').read_text().replace('/tmp/divalead-native12-delta29-current620-20261107','/tmp/divalead-native12-differential-shelf-joint109-current620-20261107').replace('ORIGINAL_NATIVE12_DELTA29_CURRENT620_STUDY.json','ORIGINAL_NATIVE12_SHELF_JOINT109_620_STUDY.json')
(J/'shelf_joint109_620_support.py').write_text(s)
s=(V/'study_current_native12_joint109_common.py').read_text().replace('import current_native12_joint109_support as q','import shelf_joint109_620_support as q')
s=s.replace("spec['step']*=.35","spec['step']*=.65")
s=s.replace('CURRENT_NATIVE12_BOTHZL109_COMMON','SHELF_NATIVE12_BOTHZL109_620').replace('Nov4Native12Joint109Common','ShelfJoint109620').replace('/tmp/divalead-native12-bothZL109-common-new12-','/tmp/divalead-native12-shelf-joint109-620-new12-')
s=s.replace('existing_PRIMARY94_and_POST15_jointly_changed=True','existing_PRIMARY94_and_POST15_refitted_two_new_POST_static_LR_shelves=True')
s=s.replace('POST_step_scale035=True','POST_step_scale065=True').replace('no_added_filter_or_plugin=True','two_new_POST_HighShelf_filters_no_added_plugin=True').replace('feasible_seed64_linked_gain_target_grid_before94fit=True,seed_deltas=[0.,-.02,-.04,-.08]','feasible_seed30_static_shelf_grid_before109fit=True,shelf_half_gains=[.1,.25,.5],shelf_frequencies=[1000,1600,2400,3600,5400],shelf_common_ratios=[0,.5]').replace('MINUS0003dB','MINUS0004dB').replace(')))-.003',')))-.004')
s=s.replace('existing_PRIMARY94_and_POST15_jointly_refitted=True','existing_PRIMARY94_and_POST15_jointly_refitted_static_shelves7Left8Right_fixed=True')
a=s.index(" blob=(R/'PRIMARY.bin').read_bytes()");b=s.index('\n fit=JointPrimaryPostFit',a)
s=s[:a]+''' ids={v['title']:int(v['id'])for v in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\\t')};seed_rows=[]
 def set_seed(delta):
  frequency,half,ratio=delta;p.load(R/'PRIMARY.bin');z.load(R/'POST.bin')
  for slot,mode,gain in [(7,'Left',(ratio-1)*half),(8,'Right',(ratio+1)*half)]:
   for title,value in [('Filter Status','On'),('Filter Type','High Shelf'),('LRMode',mode),('Order','12 dB/oct'),('Freq',frequency),('Gain',gain),('Q',.707)]:z.text(ids[title+str(slot)],str(value))
 for delta in itertools.product([1000,1600,2400,3600,5400],[.1,.25,.5],[0,.5]):
  ds=[]
  for k in range(3):set_seed(delta);mid,_=p.render(inputs[k]);pre,_=z.render(mid);ds.append(assess(trim.render(pre)))
  row=dict(delta=list(delta),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['positive_excess_air_dB']for d in ds])),captures=ds,feasible=all(d['original_stereo_preservation_passed']and max(abs(np.array(d['LR_dB'])[1:]))<=1.59 and d['lowmid_error']<=controls[k]['lowmid_error']+.005 for k,d in enumerate(ds))and float(np.mean([d['positive_excess_air_dB']for d in ds]))<=air_cap);seed_rows.append(row)
  if len(seed_rows)%6==0:record('actual30_static_shelf_feasible_seed_screen',completed_seed_cases=len(seed_rows),Air_cap=air_cap)
 (R/'SEED30_ACTUAL_RESULTS.json').write_text(json.dumps(seed_rows,indent=2)+'\\n');valid_seed=[d for d in seed_rows if d['feasible']];assert valid_seed,'No shelf seed reaches original constraints; preserve data, never weaken gates';seed=min(valid_seed,key=lambda d:d['loss']);set_seed(seed['delta']);p.save(R/'FIT_SEED_PRIMARY.bin');z.save(R/'FIT_SEED_POST.bin');(R/'SELECTED_FEASIBLE_SEED.json').write_text(json.dumps(seed,indent=2)+'\\n');mid,_=p.render(inputs[0]);pre,_=z.render(mid);sf.write(R/'FEASIBLE_SEED_FULL_WIP.wav',trim.render(pre),48000,subtype='FLOAT');p.close();p=None;z.close();z=None;trim.close();trim=None
''' +s[b:]
s=s.replace("fit=JointPrimaryPostFit(R,R/'FIT_SEED_PRIMARY.bin',R/'POST.bin'","fit=JointPrimaryPostFit(R,R/'FIT_SEED_PRIMARY.bin',R/'FIT_SEED_POST.bin'")
s=s.replace("assert q.prior['full_public_kit_directory']=='ZL-WIP40'","assert q.prior['full_public_kit_directory']=='ZL-WIP40' and q.prior['source_accepted_cohort']==620")
s=s.replace('finite_primary_mean3_common_input_complete_not_adopted','finite_shelf_joint109_current620_complete_not_adopted').replace('failed_preserve_current_latest_and_full39_anchor','failed_preserve_current620_and_full40_anchor')
s=s.replace('"""Three shared native inputs remove phase-draw confounding during PRIMARY fitting."""','"""Two ordinary differential LR shelves, jointly cofit existing109 controls on620."""')
assert 'MINUS0003dB' not in s and 'seed64'not in s and 'no_native_MIDI_or_trim_change=True'in s
(J/'study_shelf_joint109_current620.py').write_text(s)
print('Prepared 30 LR shelf seeds, joint109two sweeps, unchanged full NEW12 acceptance')
