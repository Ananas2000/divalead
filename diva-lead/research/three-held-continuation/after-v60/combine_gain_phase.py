from pathlib import Path
import os,sys,json,copy
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;G=R/'verified-gain-interior-0001';P=R/'verified-phase18-0001';V=R/'gain-phase-coupled-preview';V.mkdir(exist_ok=False);(V/'scores').mkdir();REPO=Path('/workspace/divalead')
sys.path.insert(0,str(REPO/'diva-lead/research/repository-selection'));import compare_all as a
a.WORK=V;sys.path.insert(0,str(G/'analysis'));from independent_spectral_ms import spectral_ms
cfg=json.loads((G/'analysis/spectral_model.json').read_text());phase=json.loads((P/'analysis/spectral_model.json').read_text());old=json.loads((R/'phase18-basis/analysis/spectral_model.json').read_text());anchor=json.loads((R/'baseline/validation.json').read_text());control=json.loads((G/'validation.json').read_text());choice=json.loads((G/'numeric-choice.json').read_text());scales=json.loads((REPO/'diva-lead/research/repository-selection/ranking.json').read_text())['normalizing_errors']
fields=['common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic'];dry=sf.read(R/'baseline/Diva_source.wav')[0];before=sf.read(R/'baseline/Diva_before_spectral.wav')[0]
kwargs=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])
rows=[];best=None
for fraction in [0.,1.,.75,.5,.25,.1]:
 changed=copy.deepcopy(cfg)
 for k in fields:changed[k]=(np.array(old[k])+fraction*(np.array(phase[k])-np.array(old[k]))).tolist()
 ind,extra=spectral_ms(before,dry,48000,8320,cfg['parameters'],**kwargs,phase_angles=changed[fields[0]],phase_key_slopes=changed[fields[1]],phase_key_quadratic=changed[fields[2]])
 full=np.pad(ind,((extra,0),(0,0)))[:len(dry)]
 if fraction==0:np.testing.assert_allclose(full[extra:],sf.read(G/'actual-Windows.wav')[0][extra:],rtol=0,atol=2e-7)
 edit=a.h.edit_aligned(a.h.align_with_pdc(full,dict(alignment_frames=819),latency=12416));path=V/('preview-'+str(fraction)+'.wav');sf.write(path,edit,48000,subtype='DOUBLE');measured=a.score(dict(id='fraction'+str(fraction),canonical_path=str(path),aliases=[]));m=measured['metrics'];tone=sum(choice['tone_focused_weights'][k]*m[k]/scales[k] for k in choice['tone_focused_weights']);standard=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS)
 feasible=bool(all(m[k]<=anchor['metrics'][k]*limit for k,limit in choice['guard_limits'].items()) and measured['diagnostics']['crest_RMS_db']<=choice['fixed_crest_cap_dB'] and np.max(abs(full))<.99 and standard<=anchor['score']*1.0001)
 row=copy.deepcopy(choice);row.update(fraction=fraction,weighted_score=tone,standard_weighted_score=standard,metrics=m,feasible_search_guards=feasible,crest_RMS_dB=measured['diagnostics']['crest_RMS_db'],common_phase_coefficients_frozen=False,phase_frozen=(fraction==0.),coupled_existing_gain_and_phase=True,only_existing93_harmonic_gain_values=False)
 for k in fields:row[k]=changed[k]
 rows.append(row)
 if feasible and tone<control['tone_score']-1e-6 and (best is None or tone<best['weighted_score']):best=row
 print('COUPLED_GAIN_PHASE',fraction,tone,standard,feasible,flush=True)
(V/'history.json').write_text(json.dumps(rows,indent=2)+'\n');(V/'decision.json').write_text(json.dumps(dict(numeric_improvement=best is not None,requires_full_actual_proof=True,not_a_new_accepted_release=True,match_reached=False),indent=2)+'\n')
if best is not None:(V/'best.json').write_text(json.dumps(best,indent=2)+'\n')
