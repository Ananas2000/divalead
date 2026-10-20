"""Recheck newest proved Finish on the separately proved physical Diva source."""
from pathlib import Path
import ctypes,datetime,json,os,subprocess,sys,time
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;S=R/'source-post74joint-basis';V=R/'source-post74-transplant';V.mkdir(exist_ok=False)
while not (R/'pw5190-live-main/round-0016-gain/decision.json').is_file():time.sleep(5)
P=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(P));import compare_all as a
a.WORK=V;(V/'scores').mkdir();anchor=json.loads((R/'baseline/validation.json').read_text());scales=json.loads((P/'ranking.json').read_text())['normalizing_errors'];weights=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
source=json.loads((S/'validation.json').read_text());sourcecfg=json.loads((S/'analysis/spectral_model.json').read_text());fields=['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters']
raw,rate=sf.read(S/'Diva_source.wav',dtype='float32');assert rate==48000
choices=sorted([(json.loads(p.read_text())['tone_score'],p) for p in R.glob('pw5190-verified-*/validation.json')])[:3];globalPWcap=choices[0][0];rows=[]
for i,(_,p) in enumerate(choices):
 proof=json.loads(p.read_text());cfg=json.loads(Path(proof['core_model']).read_text());assert all(cfg[k]==v for k,v in sourcecfg.items() if k not in fields)
 assert json.loads((p.parent/'analysis/selected_candidate.json').read_text())['effect_parameters']==json.loads((S/'analysis/selected_candidate.json').read_text())['effect_parameters']
 lib=ctypes.CDLL(str(p.parent/'native_finish.so'));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];out=np.zeros_like(raw);assert lib.native_render(raw.ctypes.data,out.ctypes.data,len(raw),rate)
 edit=a.h.edit_aligned(a.h.align_with_pdc(out.astype('float64'),dict(alignment_frames=819),latency=12416));path=V/('trial-'+str(i)+'.wav');sf.write(path,edit,rate,subtype='FLOAT');m=a.score(dict(id='transplant'+str(i),canonical_path=str(path),aliases=[]));metrics=m['metrics'];tone=sum(weights[k]*metrics[k]/scales[k] for k in weights);std=sum(a.WEIGHTS[k]*metrics[k]/scales[k] for k in a.WEIGHTS)
 feasible=all(metrics[k]<=anchor['metrics'][k]*limit for k,limit in proof['guard_limits'].items()) and m['diagnostics']['crest_RMS_db']<=proof['crest_cap_dB'] and std<=anchor['score']*1.0001 and np.max(abs(out))<.99
 row=dict(index=i,known_finish_proof=str(p),tone_score=tone,score=std,metrics=metrics,feasible=bool(feasible),guard_excesses={k:metrics[k]/anchor['metrics'][k]-limit for k,limit in proof['guard_limits'].items() if metrics[k]>anchor['metrics'][k]*limit},only_three_held=True,full_new_combination_proof_completed=False,match_reached=False);rows.append(row);print('NEW_SOURCE_EXISTING_FINISH',i,p.parent.name,tone,feasible,row['guard_excesses'],flush=True)
(V/'screens.json').write_text(json.dumps(rows,indent=2)+'\n');qualified=[row for row in rows if row['feasible'] and row['tone_score']<globalPWcap-1e-6]
decision=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),global_PW_tone_cap=globalPWcap,screened_combinations=len(rows),match_reached=False)
if qualified:
 row=min(qualified,key=lambda x:x['tone_score']);p=Path(row['known_finish_proof']);report=json.loads(p.read_text());cfg=json.loads(Path(report['core_model']).read_text());fit=V/'fit';fit.mkdir()
 choice={k:cfg[k] for k in fields};choice.update(feasible_search_guards=True,user_selected_three_baseline=True,tone_focused_weights=weights,guard_limits=report['guard_limits'],fixed_crest_cap_dB=report['crest_cap_dB'],weighted_score=row['tone_score'],existing_proved_finish_with_changed_fully_proved_Diva_source=True)
 (fit/'best.json').write_text(json.dumps(choice,indent=2)+'\n');(fit/'history.json').write_text(json.dumps([dict(weighted_score=globalPWcap)])+'\n')
 source['acceptance_tone_cap']=globalPWcap;capfile=V/'source-report-with-strict-global-cap.json';capfile.write_text(json.dumps(source,indent=2)+'\n');target=R/'post74joint-verified-transplant-0001'
 with (V/'validation.log').open('w') as log:result=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(S),DIVALEAD_THREE_SOURCE_REPORT=str(capfile)),stdout=log,stderr=log)
 if result.returncode:
  from three_candidate_decision import quality_rejection
  reject=quality_rejection(V/'validation.log',target);assert reject is not None;decision.update(reject)
 else:
  actual=json.loads((target/'validation.json').read_text());decision.update(fully_proved=True,validation=str(target/'validation.json'),tone_score=actual['tone_score'],score=actual['score'],known_finish_proof=str(p))
else:decision.update(accepted=False,reason='No measured source/Finish combination improved current global PW within original guards')
(V/'completed.json').write_text(json.dumps(decision,indent=2)+'\n');print('SOURCE_FINISH_COMBINATION_CHECK_COMPLETE',decision,flush=True)
