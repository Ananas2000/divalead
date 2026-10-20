"""Interpolate existing proved Finish coefficients on the matching physical source."""
from pathlib import Path
import copy,json,os,subprocess,sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;S=R/'source-post74joint-basis';V=R/'source-post74-blend';V.mkdir(exist_ok=False);P=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(P));import compare_all as a
a.WORK=V;(V/'scores').mkdir();sys.path.insert(0,str(S/'analysis'));from independent_spectral_ms import spectral_ms
anchor=json.loads((R/'baseline/validation.json').read_text());scales=json.loads((P/'ranking.json').read_text())['normalizing_errors'];weights=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
A=R/'post74joint-verified-transplant-0001';F=R/'pw5190-verified-live-phase-0043-fine55';seed=json.loads((A/'analysis/spectral_model.json').read_text());target=json.loads((F/'analysis/spectral_model.json').read_text());proof=json.loads((F/'validation.json').read_text());source=json.loads((S/'validation.json').read_text());fields=['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters'];assert all(seed[k]==v for k,v in target.items() if k not in fields)
raw=sf.read(S/'Diva_source.wav')[0];before=sf.read(S/'NEW-independent-base-pdc.wav')[0];rows=[];configs={}
def blend(x,y,t):
 if x==y:return copy.deepcopy(x)
 if isinstance(x,dict):assert x.keys()==y.keys();return {k:blend(x[k],y[k],t) for k in x}
 if isinstance(x,list):assert len(x)==len(y);return [blend(a,b,t) for a,b in zip(x,y)]
 assert type(x) in (int,float) and type(y) in (int,float)
 return (1-t)*x+t*y
for i,alpha in enumerate([0.,.75,.85,.90,.95,1.]):
 c=copy.deepcopy(seed)
 for k in fields:c[k]=blend(seed[k],target[k],alpha)
 kw=dict(sigma=c['mask_sigma'],key_quadratic=c['key_quadratic'],key_slopes=c['key_slopes'],phase_angles=c['common_phase_radians'],hf_parameters=c['hf_matrix_parameters'],hf_anchors=c['hf_matrix_anchors_Hz'],upper_rolloff=c['upper_rolloff_Hz'],harmonic_gain=c['harmonic_gain_parameters'],gain_orders=c['harmonic_gain_orders'],hf_sigma=c['hf_mask_sigma'],phase_key_slopes=c['common_phase_key_slopes'],phase_key_quadratic=c['common_phase_key_quadratic'],core_anchors=c['anchors_Hz'],adaptive_dynamic=c['dynamic_harmonic_parameters'],adaptive_stereo=c['stereo_harmonic_parameters'],final_stereo_balance=c['final_stereo_balance'],fine_phase=c['fine_phase_harmonic_parameters'])
 y,extra=spectral_ms(before,raw,48000,8320,c['parameters'],**kw);out=np.zeros_like(y);out[extra:]=y[:-extra]
 if alpha==0:np.testing.assert_allclose(out,sf.read(A/'actual-Windows.wav')[0],rtol=0,atol=3e-7)
 edit=a.h.edit_aligned(a.h.align_with_pdc(out,dict(alignment_frames=819),latency=12416));path=V/('trial-'+str(i)+'.wav');sf.write(path,edit,48000,subtype='FLOAT');m=a.score(dict(id='blend'+str(i),canonical_path=str(path),aliases=[]));metrics=m['metrics'];tone=sum(weights[k]*metrics[k]/scales[k] for k in weights);std=sum(a.WEIGHTS[k]*metrics[k]/scales[k] for k in a.WEIGHTS)
 feasible=all(metrics[k]<=anchor['metrics'][k]*limit for k,limit in proof['guard_limits'].items()) and m['diagnostics']['crest_RMS_db']<=proof['crest_cap_dB'] and std<=anchor['score']*1.0001 and np.max(abs(out))<.99
 row=dict(index=i,alpha=alpha,tone_score=tone,score=std,feasible=bool(feasible),metrics=metrics,crest_RMS_dB=m['diagnostics']['crest_RMS_db'],independent_matching_source_render=True,not_yet_Windows_full_proof=True,match_reached=False);rows.append(row);configs[i]=c;print('PHYSICAL_SOURCE_COEFFICIENT_BLEND',alpha,tone,feasible,flush=True)
(V/'screens.json').write_text(json.dumps(rows,indent=2)+'\n');globalcap=min(json.loads(p.read_text())['tone_score'] for p in list(R.glob('pw5190-verified-*/validation.json'))+list(R.glob('post74joint-verified-*/validation.json')));qualified=[x for x in rows if x['feasible'] and x['tone_score']<globalcap-1e-6];decision=dict(global_tone_cap=globalcap,match_reached=False)
if qualified:
 row=min(qualified,key=lambda x:x['tone_score']);c=configs[row['index']];fit=V/'fit';fit.mkdir();choice={k:c[k] for k in fields};choice.update(feasible_search_guards=True,user_selected_three_baseline=True,tone_focused_weights=weights,guard_limits=proof['guard_limits'],fixed_crest_cap_dB=proof['crest_cap_dB'],weighted_score=row['tone_score'],existing_coefficients_interpolation_alpha=row['alpha']);(fit/'best.json').write_text(json.dumps(choice,indent=2)+'\n');(fit/'history.json').write_text(json.dumps([dict(weighted_score=globalcap)])+'\n');source['acceptance_tone_cap']=globalcap;cap=V/'strict-global-cap-source-report.json';cap.write_text(json.dumps(source,indent=2)+'\n');dest=R/'post74joint-verified-blend-0001'
 with (V/'validation.log').open('w') as log:result=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),dest.name],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(S),DIVALEAD_THREE_SOURCE_REPORT=str(cap)),stdout=log,stderr=log)
 if result.returncode:
  from three_candidate_decision import quality_rejection
  reject=quality_rejection(V/'validation.log',dest);assert reject is not None;decision.update(reject)
 else:
  d=json.loads((dest/'validation.json').read_text());decision.update(fully_proved=True,validation=str(dest/'validation.json'),tone_score=d['tone_score'],score=d['score'],alpha=row['alpha'])
else:decision.update(accepted=False,reason='No feasible interpolation improves current global tone')
(V/'completed.json').write_text(json.dumps(decision,indent=2)+'\n');out=Path('/tmp/divalead-source-post74blend');out.mkdir(exist_ok=False);(out/'completed.json').write_text(json.dumps(dict(trials=6,best=decision),indent=2)+'\n');print('EXISTING_FINISH_BLEND_CHECK_COMPLETE',decision,flush=True)
