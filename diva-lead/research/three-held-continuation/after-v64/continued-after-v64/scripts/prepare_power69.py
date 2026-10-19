from pathlib import Path
R=Path(__file__).resolve().parent;s=(R/'fit_three_fine55.py').read_text();a=s.index('power_render=');b=s.index('neutral_full,neutral=',a)
s=s[:a]+'''power_render=ns['render'];base_dynamic=copy.deepcopy(cfg['dynamic_harmonic_parameters']);base_target=np.asarray(base_dynamic['target_logpower_db_polynomial']);assert base_target.shape==(5,23)
def changed(p):
 dyn=copy.deepcopy(base_dynamic);target=base_target.copy();target[:3]+=np.asarray(p).reshape(3,23);dyn['target_logpower_db_polynomial']=target.tolist();return dyn
def render(p):return power_render(p)
'''+s[b:]
s=s.replace('np.zeros(55)','np.zeros(69)').replace('uniform(-.01,.01,55)','uniform(-.03,.03,69)').replace("adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],fine_phase=changed(p)","adaptive_dynamic=changed(p),adaptive_stereo=cfg['stereo_harmonic_parameters'],fine_phase=cfg['fine_phase_harmonic_parameters']")
s=s.replace('np.full(55,-.08)','np.full(69,-1.0)').replace('range(55)','range(69)').replace('fine_phase_offsets','power_offsets')
s=s.replace("'key_slopes','key_quadratic','dynamic_harmonic_parameters','stereo_harmonic_parameters'","'key_slopes','key_quadratic','stereo_harmonic_parameters'")
s=s.replace('fine_phase_harmonic_parameters=changed(p),',"fine_phase_harmonic_parameters=cfg['fine_phase_harmonic_parameters'],dynamic_harmonic_parameters=changed(p),")
s=s.replace("'complete-fine_phase-'+B.name","'complete-power69-'+B.name").replace('THREE_FINE55','THREE_POWER69').replace('only_existing55_fine_phase_values=True','only_existing69_dynamic_target_values=True').replace('existing55_fine_phase_values_only=True','existing69_dynamic_target_values_only=True').replace('SELECTED53_FINE_PHASE_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS','THREE_POWER69_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS').replace('only_additional55_fine_phase_values_changed=True','only_existing69_dynamic_power_values_changed=True')
compile(s,str(R/'fit_three_power69.py'),'exec');(R/'fit_three_power69.py').write_text(s)
print('THREE_POWER69_REUSES_EXISTING_ADAPTIVE_STAGE_WITH_UNCHANGED_ORIGINAL_GUARDS')
