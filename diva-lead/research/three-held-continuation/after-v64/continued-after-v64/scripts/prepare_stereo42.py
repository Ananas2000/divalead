from pathlib import Path
R=Path(__file__).resolve().parent;s=(R/'fit_three_fine55.py').read_text()
a=s.index('power_render=');b=s.index('neutral_full,neutral=',a)
s=s[:a]+'''power_render=ns['render'];base_balance=copy.deepcopy(cfg['final_stereo_balance']);fields=['log_side_scale','mid_to_side_real','mid_to_side_imag'];base_coeff=np.array([base_balance[k] for k in fields]);active_indices=np.delete(np.arange(15),7);assert base_coeff.shape==(3,15) and np.all(base_coeff[:,7]==0)
def changed(p):
 balance=copy.deepcopy(base_balance);values=base_coeff.copy();values[:,active_indices]+=np.asarray(p).reshape(3,14)
 for k,row in zip(fields,values):balance[k]=row.tolist()
 return balance
def render(p):
 balance=changed(p);curves=[np.interp(np.log(np.maximum(ns['f'],1)),np.log(balance['anchors_Hz']),np.r_[0,balance[k],0])[:,None] for k in fields];ns['scale']=np.exp(curves[0]);ns['mix']=curves[1]+1j*curves[2]
 return power_render(np.zeros(69))
'''+s[b:]
s=s.replace('np.zeros(55)','np.zeros(42)').replace('uniform(-.01,.01,55)','uniform(-.005,.005,42)').replace('fine_phase=changed(p),final_stereo_balance=cfg[\'final_stereo_balance\']','fine_phase=cfg[\'fine_phase_harmonic_parameters\'],final_stereo_balance=changed(p)')
s=s.replace('only_additional55_fine_phase_values_changed=True','only_existing42_final_balance_values_changed=True').replace('np.full(55,-.08)','np.full(42,-.03)').replace('fine_phase_offsets','stereo_balance_offsets').replace('range(55)','range(42)')
s=s.replace("'dynamic_harmonic_parameters','stereo_harmonic_parameters','final_stereo_balance']","'dynamic_harmonic_parameters','stereo_harmonic_parameters']")
s=s.replace('fine_phase_harmonic_parameters=changed(p),','fine_phase_harmonic_parameters=cfg[\'fine_phase_harmonic_parameters\'],final_stereo_balance=changed(p),')
s=s.replace('only_existing55_fine_phase_values=True','only_existing42_final_stereo_values=True').replace("'complete-fine_phase-'+B.name","'complete-balance42-'+B.name").replace('THREE_FINE55','THREE_BALANCE42').replace('existing55_fine_phase_values_only=True','existing42_final_stereo_values_only=True').replace('SELECTED53_FINE_PHASE_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS','THREE_BALANCE42_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS')
s=s.replace("assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];", "assert result[1]['final_stereo_balance']==cfg['final_stereo_balance'];")
compile(s,str(R/'fit_three_balance42.py'),'exec');(R/'fit_three_balance42.py').write_text(s)
print('THREE_BALANCE42_PREPARED_WITH_FIXED_ZERO_COEFFICIENTS_AND_SAME_ORIGINAL_GUARDS')
