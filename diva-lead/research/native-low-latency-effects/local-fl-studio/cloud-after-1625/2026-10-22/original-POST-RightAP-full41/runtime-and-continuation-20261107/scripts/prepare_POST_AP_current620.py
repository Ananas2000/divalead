from pathlib import Path
J=Path(__file__).resolve().parent
s=(J/'stereo_shelves620_support.py').read_text().replace('/tmp/divalead-native12-differential-shelves-current620-20261107','/tmp/divalead-native12-POST-single-AP97-current620-20261107').replace('ORIGINAL_NATIVE12_DIFFERENTIAL_SHELVES620_STUDY.json','ORIGINAL_NATIVE12_POST_AP97_CURRENT620_STUDY.json');(J/'POST_AP97_620_support.py').write_text(s)
s=(J/'study_stereo_shelves_current620.py').read_text().replace('import stereo_shelves620_support as q','import POST_AP97_620_support as q').replace('DifferentialShelf-620','POSTAP97-620').replace('finite_differential_shelves620_complete','finite_POST_AP97_current620_complete')
a=s.index('"""');b=s.index('"""',a+3)+3;s='"""One ordinary Left/Right/Stereo all-pass in unused POST7; no other DSP change."""'+s[b:]
a=s.index('protocol=dict(');b=s.index("(R/'PREDECLARED_PROTOCOL.json')",a)
s=s[:a]+'''protocol=dict(one_new_actual_POST_AllPass_slot7=True,all_existing_POST_filters_PRIMARY_native12_final_trim_fixed=True,no_added_plugin=True,frequencies=[800,1600,3200,6400,10000,12800,18000,20000],Q_values=[3,6,12,25],modes=['Left','Right','Stereo'],actual_filter_type9=True,ordinary_actual_ZL_minphase_lookahead0_AutoGainOff=True,only_original_is_target=True,three_common_training_native_draws_plus_two_unused=True,training_gain_over0003=True,training_Air_mean_below_min_current620_full40_by0004=True,training_abs_high_LR_max159=True,training_paired_lowmid_plus0005=True,heldout_gain_over0003=True,entirely_NEW12_required=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_positive=True,Air_first10_AND_bothcold_nonincreasing_vs_current_AND_full40=True,TONE_nonincreasing=True,all12_stereo_upper148_abs16_lowmid325_paired002=True,source_native12_three_held_ARP_ADSR_unchanged=True,latest_BEST_full_supported_export_and_coldZIP_required_before_adoption=True)
'''+s[b:]
a=s.index('def configure(model):');b=s.index('def render(',a)
s=s[:a]+'''def configure(model):
    frequency,Q,mode=model;p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');t.load(R/'TRIM.bin')
    if not frequency:return
    z.set(ids['Filter Type7'],.9)
    for title,value in [('Filter Status','On'),('LRMode',mode),('Order','12 dB/oct'),('Freq',frequency),('Gain',0),('Q',Q)]:z.text(ids[title+'7'],str(value))
'''+s[b:]
a=s.index('    configure((2400,.1,0));');b=s.index('    for k in range(5):',a)
s=s[:a]+'''    configure((18000,12,'Left'));z.save(R/'AP_ENUM_PROBE.bin');z.dump(R/'AP_ENUM_ALL610.tsv');probe=values(R/'AP_ENUM_PROBE.bin')
    assert probe['filter_status7']==2 and probe['filter_type7']==9 and probe['lr_mode7']==1 and probe['order7']==1
    assert probe['total_filter_structure']==0 and probe['total_lookahead']==0 and probe['total_auto_gain']==0
'''+s[b:]
s=s.replace("models=[(2400,0,0)]+list(itertools.product([1000,1600,2400,3600,5400],[.1,.25,.5,.75,1,1.5],[-.5,0,.5,1]))","models=[(0,0,'Stereo')]+list(itertools.product([800,1600,3200,6400,10000,12800,18000,20000],[3,6,12,25],['Left','Right','Stereo']))")
s=s.replace('only_POST_two_static_HighShelf_filters_added=True','only_POST_one_static_AllPass_filter_added=True').replace('starting_actual_current620_differential_stereo_shelves','starting_actual_current620_POST_AllPass_screen').replace('actual_differential_stereo_shelf_screen','actual_POST_single_AllPass_screen')
assert 'two_new_actual_POST_HighShelf'not in s and 'High Shelf'not in s
(J/'study_POST_AP97_current620.py').write_text(s)
print('Prepared97 actual static Left/Right/Stereo AP models plus unchanged source/native/MIDI/trim')
