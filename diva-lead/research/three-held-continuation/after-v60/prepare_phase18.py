from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'fit_three_gains.py').read_text()
def rep(a,b):
 global s
 assert a in s,a;s=s.replace(a,b)
rep('Optimize 93 harmonic gain values of the selected three-held source; freeze phase.','Optimize18 existing common-phase values of the selected three-held source; freeze gains.')
rep("'complete-joint-'+B.name","'complete-phase-'+B.name")
rep('def changed(p):return base_gain+np.asarray(p).reshape(3,31),base_phase','def changed(p):return base_gain,base_phase+np.asarray(p).reshape(3,6)')
a=s.index(' delta=np.pad',s.index('def render'));b=s.index(" for name,v in zip",a)
s=s[:a]+''' phase=sum(np.einsum('i,ift->ft',np.asarray(p).reshape(3,6)[d],phase_basis)*key**d for d in range(3));z=Z0*np.exp(1j*phase)[None];ns['Z']=z
'''+s[b:]
s=s.replace('np.zeros(93)','np.zeros(18)').replace('uniform(-.01,.01,93)','uniform(-.01,.01,18)').replace('np.full(93,-.10)','np.full(18,-.08)').replace('range(93)','range(18)')
a=s.index('def gain_constraints(p):');b=s.index('def compute(p):',a)
s=s[:a]+'''def gain_constraints(p):
 gain,_=changed(p);lo,hi=np.log2(np.array([45,220])/100);values=[]
 for a,b,q in gain.T:
  points=[lo,hi]
  if q>0 and lo<-b/(2*q)<hi:points.append(-b/(2*q))
  values.append(min(1+a+b*k+q*k*k for k in points)-.020002)
 return np.array(values),np.zeros((31,18))
'''+s[b:]
s=s.replace('existing93_gain_values_only=True,phase_frozen=True','existing18_phase_values_only=True,gain_frozen=True').replace('only_existing93_harmonic_gain_values=True,phase_frozen=True','only_existing18_common_phase_values=True,gain_frozen=True').replace('common_phase_coefficients_frozen=True','common_phase_coefficients_frozen=False,harmonic_gain_coefficients_frozen=True').replace('existing93_harmonic_gain_values_only=True,common_phase_frozen=True','existing18_common_phase_values_only=True,gain_frozen=True').replace('COMPLETE_JOINT','THREE_PHASE18').replace('V53_JOINT_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS','THREE_PHASE18_ZERO_ACTUAL_TWO_NONZERO_FULL_SCIPY_PASS')
(R/'fit_three_phase18.py').write_text(s)
# Apply all supported model fields when validating a new checkpoint. This also
# preserves phase choices when a subsequent HF/gain fit starts from that model.
fields="['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic']"
for name in ['validate_three_model.py','validate_three_source_model.py']:
 p=R/name;old=p.read_text();s=old.replace("['hf_matrix_parameters','harmonic_gain_parameters']",fields)
 needle="setup=Path('/workspace/divalead-setup');wine="
 assert needle in s
 patch='''for field,symbol in [('common_phase_radians','SMS_PHASE_PARAMETERS'),('common_phase_key_slopes','SMS_PHASE_KEY_SLOPES'),('common_phase_key_quadratic','SMS_PHASE_KEY_QUADRATIC')]:
 values=np.asarray(cfg[field]);assert values.shape==(6,)
 array='{'+','.join(format(float(x),'.17g') for x in values)+'}'
 s,n=re.subn(symbol+r'\\[6\\]=\\{.*?\\};',symbol+'[6]='+array+';',s,flags=re.S);assert n==1;p.write_text(s)
'''
 s=s.replace(needle,patch+needle);p.write_text(s)
print('PHASE18_FITTER_AND_PHASE_PRESERVING_VALIDATORS_PREPARED')
