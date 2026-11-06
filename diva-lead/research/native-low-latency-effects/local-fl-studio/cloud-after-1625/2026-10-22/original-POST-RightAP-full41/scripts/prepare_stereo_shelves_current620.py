from pathlib import Path
J=Path(__file__).resolve().parent
s=(J/'delta29_current620_support.py').read_text().replace('/tmp/divalead-native12-delta29-current620-20261107','/tmp/divalead-native12-differential-shelves-current620-20261107').replace('ORIGINAL_NATIVE12_DELTA29_CURRENT620_STUDY.json','ORIGINAL_NATIVE12_DIFFERENTIAL_SHELVES620_STUDY.json')
(J/'stereo_shelves620_support.py').write_text(s)
s=(J/'study_delta29_current620.py').read_text().replace('import delta29_current620_support as q','import stereo_shelves620_support as q').replace('Delta29-620','DifferentialShelf-620').replace('finite_delta29_current620_complete','finite_differential_shelves620_complete')
a=s.index('def title(key):');b=s.index("assert q.prior['source_accepted_cohort']",a)
s=s[:a]+s[b:]
s=s.replace("(R/'PARAMETER_DIRECTIONS.json').write_text(json.dumps(directions,indent=2)+'\\n')",'')
a=s.index('protocol=dict(');b=s.index("(R/'PREDECLARED_PROTOCOL.json')",a)
s=s[:a]+"""protocol=dict(two_new_actual_POST_HighShelf_slots7_Left_and8_Right=True,all_existing_POST_filters_and_PRIMARY_native12_and_final_trim_fixed=True,no_added_plugin=True,frequencies=[1000,1600,2400,3600,5400],differential_gain_half=[.1,.25,.5,.75,1,1.5],common_gain_ratio=[-.5,0,.5,1],Q=.707,ordinary_actual_ZL_minphase_lookahead0_AutoGainOff=True,only_original_is_target=True,three_common_training_native_draws_plus_two_unused=True,training_gain_over0003=True,training_Air_mean_below_min_current620_full40_by0004=True,training_abs_high_LR_max159=True,training_paired_lowmid_plus0005=True,heldout_gain_over0003=True,entirely_NEW12_required=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_positive=True,Air_first10_AND_bothcold_nonincreasing_vs_current_AND_full40=True,TONE_nonincreasing=True,all12_stereo_upper148_abs16_lowmid325_paired002=True,source_native12_three_held_ARP_ADSR_unchanged=True,latest_BEST_full_supported_export_and_coldZIP_required_before_adoption=True)\n"""+s[b:]
a=s.index('def configure(model):');b=s.index('def render(',a)
s=s[:a]+"""def configure(model):
    frequency,half_difference,common_ratio=model;p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');t.load(R/'TRIM.bin')
    if not half_difference:return
    common=common_ratio*half_difference
    for slot,mode,gain in [(7,'Left',common-half_difference),(8,'Right',common+half_difference)]:
        for title,value in [('Filter Status','On'),('Filter Type','High Shelf'),('LRMode',mode),('Order','12 dB/oct'),('Freq',frequency),('Gain',gain),('Q',.707)]:z.text(ids[title+str(slot)],str(value))
"""+s[b:]
a=s.index('    for k,(alpha,beta,offset,g)');b=s.index("        for host,name in [(p,'PRIMARY')",a)
s=s[:a]+"""    models=[(2400,0,0)]+list(itertools.product([1000,1600,2400,3600,5400],[.1,.25,.5,.75,1,1.5],[-.5,0,.5,1]))
    for k,model in enumerate(models):
        folder=R/f'model-{k:03d}';folder.mkdir();configure(model)
"""+s[b:]
s=s.replace("starting_actual_current620_existing_filter_direction_screen","starting_actual_current620_differential_stereo_shelves").replace("actual_existing_filter_parameter_transplant_screen","actual_differential_stereo_shelf_screen").replace('only_existing_two_ZL_and_final_native_linear_LR_gains_changed=True','only_POST_two_static_HighShelf_filters_added=True,all_other_DSP_unchanged=True')
s=s.replace('''    for k in range(5):''','''    configure((2400,.1,0));z.save(R/'SHELF_ENUM_PROBE.bin');z.dump(R/'SHELF_ENUM_ALL610.tsv')
    probe=values(R/'SHELF_ENUM_PROBE.bin')
    assert probe['filter_status7']==probe['filter_status8']==2 and probe['filter_type7']==probe['filter_type8']==3 and probe['lr_mode7']==1 and probe['lr_mode8']==2,probe
    assert probe['total_filter_structure']==0 and probe['total_lookahead']==0 and probe['total_auto_gain']==0
    for k in range(5):''',1)
(J/'study_stereo_shelves_current620.py').write_text(s)
print('Prepared 121 actual differential LR high-shelf models; no source/native/MIDI/trim change')
