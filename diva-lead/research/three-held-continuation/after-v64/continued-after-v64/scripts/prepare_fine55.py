from pathlib import Path
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead/diva-lead/research/repository-selection')
s=(P/'refine_guarded_fine_phase.py').read_text();s=s[:s.index('base=joint.metrics(neutral);score=joint.score;')]
s=s.replace('RESEARCH=Path(__file__).resolve().parent','RESEARCH=Path('+repr(str(P))+')')
s=s.replace('FIXED_CREST_CAP=.5555931508910259',"ANCHOR=json.loads(Path('/workspace/divalead-work/three-held-continuation/baseline/validation.json').read_text())\nFIXED_CREST_CAP=ANCHOR['crest_RMS_dB']*1.001")
s+='''fresh_powers,joint.carriers,boundaries=joint.analysis.powers(neutral)
assert not any(boundaries)
np.testing.assert_array_equal(joint.fixed_powers(neutral),fresh_powers)
actual_baseline=json.loads((B/'validation.json').read_text())
assert abs(joint.score(joint.metrics(neutral))-actual_baseline['score'])<1e-6
TONE_WEIGHTS=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
base=joint.metrics(neutral);score=lambda m:sum(TONE_WEIGHTS[k]*m[k]/joint.scales[k] for k in TONE_WEIGHTS)
lower=np.full(55,-.08);upper=-lower
guards=dict(H24=1.001,upper_harm=1.001,upper_off=1.001,low_harm=1.002,ERB=1.001,relative_phase=1.002,whole=1.001,envelope=1.001,body=1.002,stereo_phase=1.002,stereo_balance=1.002)
from search_global_guards import repair_near_feasible_rows
def compute(p):
 full,e=render(p);m=joint.metrics(e);peak=float(np.max(abs(full)));con=np.r_[[limit-m[k]/ANCHOR['metrics'][k] for k,limit in guards.items()],.99-peak,1-crest_error(e)/NUMERICAL_CREST_CAP,1.0001-joint.score(m)/ANCHOR['score']]
 keys=['harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','hf_matrix_parameters','parameters','key_slopes','key_quadratic','dynamic_harmonic_parameters','stereo_harmonic_parameters','final_stereo_balance']
 row=dict(metrics=m,weighted_score=score(m),peak=peak,feasible_search_guards=bool(np.min(con)>=-1e-12),fine_phase_offsets=p.tolist(),fine_phase_harmonic_parameters=changed(p),**{k:cfg[k] for k in keys},baseline_model_SHA256=baseline_hash,source_manifest=manifest,guard_limits=guards,only_existing55_fine_phase_values=True,original_common_weights_unchanged=False,tone_focused_weights=TONE_WEIGHTS,standard_weighted_score=joint.score(m),user_selected_three_baseline=True,crest_RMS_dB=crest_error(e),fixed_crest_cap_dB=FIXED_CREST_CAP,all_DSP_tolerances_unchanged=True,match_reached=False)
 return score(m)+.0001*float(np.mean(p*p)),row,con
baseline_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
'''
# Reuse the proved checkpoint/finite-difference runner with55 coordinates.
t=(R/'fit_three_hf_fixed_anchor.py').read_text();tail=t[t.index('rows=[];last={};best=np.inf;derivatives={}'):]
tail=tail.replace('HF_offsets','fine_phase_offsets').replace('np.zeros(100)','np.zeros(55)').replace('range(100)','range(55)').replace('COMPLETE_HF','THREE_FINE55').replace('existing100_HF_values_only=True','existing55_fine_phase_values_only=True').replace("H24_chosen_three_cap=ANCHOR['metrics']['H24']*guards['H24']","H24_chosen_three_cap=ANCHOR['metrics']['H24']*guards['H24']")
tail=tail.replace(' from three_hf_interior_projection import repair_hf_rows\n interior_repair=repair_hf_rows(rows,best,compute,probe,lower,upper,guards)\n','').replace('interior_projection=interior_repair,','')
s+=tail
compile(s,str(R/'fit_three_fine55.py'),'exec');(R/'fit_three_fine55.py').write_text(s)
print('PREPARED_THREE_FINE55_WITH_ORIGINAL_THREE_GUARDS')
