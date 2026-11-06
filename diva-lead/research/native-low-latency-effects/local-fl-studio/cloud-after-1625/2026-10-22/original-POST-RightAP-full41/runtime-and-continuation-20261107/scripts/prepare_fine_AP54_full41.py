from pathlib import Path
J=Path(__file__).resolve().parent
s=(J/'POST_AP97_620_support.py').read_text().replace('/tmp/divalead-native12-POST-single-AP97-current620-20261107','/tmp/divalead-native12-fine-AP54-full41-after639-20261107').replace('ORIGINAL_NATIVE12_POST_AP97_CURRENT620_STUDY.json','ORIGINAL_NATIVE12_FINE_AP54_FULL41_AFTER639_STUDY.json');(J/'fine_AP54_full41_support.py').write_text(s)
s=(J/'study_POST_AP97_current620.py').read_text().replace('import POST_AP97_620_support as q','import fine_AP54_full41_support as q').replace('POSTAP97-620','FineAP54-Full41').replace('finite_POST_AP97_current620_complete','finite_fine_AP54_full41_complete')
s=s.replace("q.prior['source_accepted_cohort']==620","q.prior['source_accepted_cohort']==639").replace('frozen_current_cohort=620',"frozen_current_cohort=q.prior['source_accepted_cohort']")
a=s.index('protocol=dict(');b=s.index("(R/'PREDECLARED_PROTOCOL.json')",a)
s=s[:a]+'''protocol=dict(refine_existing_POST_RightAP7_and_optional_new_AP8=True,AP7_frequencies=[12000,12800,13600],AP7_Q=[20,25],AP8_frequencies=[16000,20000],AP8_Q=[12,25],AP8_modes=['Left','Right'],PRIMARY_native12_finaltrim_source_MIDI3_ARP_ADSR_fixed=True,no_added_plugin=True,original_is_only_target=True,full40_anchor_uses_BOTH_original40_components=True,three_common_training_plus_two_unused_native_inputs=True,training_gain_over0003=True,training_Air_below_min_full41_full40_by0004=True,training_abs_high_LR_max159=True,training_lowmid_each_plus0005=True,heldout_gain_over0003=True,then_entirely_NEW12=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Airfirst10_bothcold_nonincreasing_vs_current41_AND_full40=True,TONE_nonincreasing=True,all12stereo148_abs16_lowmid325_paired002=True,cold_component_latest_BEST_fullFL20_coldZIP_publication_required=True)
'''+s[b:]
a=s.index('def configure(model):');b=s.index('def render(',a)
s=s[:a]+'''def configure(model):
    frequency,Q,extra_frequency,extra_Q,extra_mode=model;p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');t.load(R/'TRIM.bin')
    for title,value in [('Freq',frequency),('Q',Q)]:z.text(ids[title+'7'],str(value))
    if extra_frequency:
        z.set(ids['Filter Type8'],.9)
        for title,value in [('Filter Status','On'),('LRMode',extra_mode),('Order','12 dB/oct'),('Freq',extra_frequency),('Gain',0),('Q',extra_Q)]:z.text(ids[title+'8'],str(value))
'''+s[b:]
s=s.replace("z.load(R/'POST.bin');t.load(R/'TRIM.bin')\n    mid,_=p.render(raw)","z.load(R/('ANCHOR40_POST.bin'if label=='anchor40'else'POST.bin'));t.load(R/'TRIM.bin')\n    mid,_=p.render(raw)")
needle="shutil.copyfile(public/'ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin',R/'ANCHOR40_PRIMARY.bin')";assert needle in s;s=s.replace(needle,needle+"\nshutil.copyfile(public/'ZL-WIP40/verification/ZL40_POST_COMPONENT.bin',R/'ANCHOR40_POST.bin')")
a=s.index("    configure((18000,12,'Left'));z.save");b=s.index('    for k in range(5):',a)
s=s[:a]+'''    configure((12800,25,0,25,'Right'));z.save(R/'BASELINE_AP7_IDENTITY.bin');assert(R/'BASELINE_AP7_IDENTITY.bin').read_bytes()==(R/'POST.bin').read_bytes()
    configure((12800,25,20000,25,'Left'));z.save(R/'AP_ENUM_PROBE.bin');probe=values(R/'AP_ENUM_PROBE.bin');assert probe['filter_status8']==2 and probe['filter_type8']==9 and probe['lr_mode8']==1 and probe['freq7']==12800 and probe['q7']==25
    assert probe['total_filter_structure']==probe['total_lookahead']==probe['total_auto_gain']==0
'''+s[b:]
a=s.index("    models=[(0,0,'Stereo')]");b=s.index('\n    for k,model in enumerate(models):',a)
s=s[:a]+'''    models=[(12800,25,0,25,'Right')]+[(f,q,0,25,'Right')for f,q in itertools.product([12000,12800,13600],[20,25])if(f,q)!=(12800,25)]+list(itertools.product([12000,12800,13600],[20,25],[16000,20000],[12,25],['Left','Right']))
'''.rstrip()+s[b:]
s=s.replace('only_POST_one_static_AllPass_filter_added=True','only_existing_AP7_frequency_Q_and_optional_new_POST_AP8_changed=True').replace('starting_actual_current620_POST_AllPass_screen','starting_actual_full41_fine_AP_screen').replace('actual_POST_single_AllPass_screen','actual_full41_fine_AP54_screen')
a=s.index('"""');b=s.index('"""',a+3)+3;s='"""Refine full41 phase correction; existing RightAP7 plus optional extra AP8."""'+s[b:]
assert "ANCHOR40_POST.bin'if label=='anchor40'"in s and "BASELINE_AP7_IDENTITY.bin"in s
(J/'study_fine_AP54_full41.py').write_text(s)
print('Prepared54 unique phase models from full41; exact baseline identity and true full40 two-component anchor checked')
