"""Deterministic native proxy derivatives propose curves; full original DSP alone accepts."""
from pathlib import Path
V=Path(__file__).resolve().parent;s=(V/'study_supported_native12_local17_current576.py').read_text();s=s.replace('/tmp/divalead-native12-supported-local17-current576-20261104','/tmp/divalead-native12-local17-zeroDepth-derivatives-fullChorus-20261104').replace('NATIVE12_SUPPORTED_LOCAL17_CURRENT576','NATIVE12_LOCAL17_PROXY_DERIVATIVES').replace('SupportedLocal17-40','Native12ProxyJ')
s=s.replace('def configure(c,v):','def configure(c,v,proxy=False):').replace('p.write_bytes(b);c.load_state(0,p)','p.write_bytes(b);c.load_state(0,p);c.set(3,1,0 if proxy else int(round(base[87]*5000)))')
s=s.replace('configure(c,v);captures=[];grouped=[]',"proxy=label.startswith('derivative-') or label=='same-canonical-parent-origin';configure(c,v,proxy=proxy);reps=1 if proxy else reps;captures=[];grouped=[]")
s=s.replace("m=modelbase['assessment']['assessment']['metrics']","m=baseline['assessment']['assessment']['metrics']")
s=s.replace("bylabel={r['label']:r for r in rows};f0=vector(modelbase);columns=[]","bylabel={r['label']:r for r in rows};f0=vector(baseline);proxy_f0=vector(modelbase);columns=[]")
s=s.replace('if lp else f0;minus=vector(bylabel[lm])if lm else f0','if lp else proxy_f0;minus=vector(bylabel[lm])if lm else proxy_f0')
a=s.index('  for k,unit in enumerate(qmc.LatinHypercube');b=s.index('  for k,row in enumerate(executor.map(evaluate,proposals)):',a);s=s[:a]+s[b:]
s=s.replace("all_proposals_actual_native_DLL=True,","all_proposals_actual_native_DLL=True,zeroDepth_only_for_local_feature_slope_not_matching_acceptance=True,full_Chorus_baseline_residual_used_for_joint_proposals=True,all_joint_models_and_finalists_and_NEW12_use_original_saved_Chorus_depth=True,no_LHS_repetition_of_previous_failed94cases=True,")
s=s.replace("actual_training_DSP_renders=sum(12 if r['label']=='current576-canonical-control'else 8 if r['label']=='same-canonical-parent-origin'else 4 for r in rows)","actual_training_DSP_renders=sum(12 if r['label']=='current580-canonical-control'else 1 if r['label']=='same-canonical-parent-origin'or r['label'].startswith('derivative-')else 4 for r in rows)")
s=s.replace("m=modelbase['assessment']['assessment']['metrics']","m=baseline['assessment']['assessment']['metrics']")
s=s.replace("eligible=sorted([r for r in rows if r['stereo_preservation_passed']","eligible=sorted([r for r in rows if r['label'].startswith('joint-')and r['stereo_preservation_passed']")
s=s.replace('current576-canonical-control','current580-canonical-control').replace('current576-native12-new12','proxyJ-native12-new12')
s=s.replace('Refine existing supported canonical native12 local17 coefficients against original.','Use actual zeroDepth native derivatives only for proposals; accept only full saved Chorus.')
s=s.replace("new .35-scale local coefficient neighborhood; same supported generator and source3held","new deterministic proxy-slope/full-Chorus-residual proposals; same supported generator and source3held")
(V/'study_proxy_derivative_local17_native12.py').write_text(s)
print('Prepared actual deterministic slope proposals; full Chorus restored for every scored candidate')
