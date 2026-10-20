"""Recheck the last completed old-source Finish on the independently proved Plate68 source."""
from pathlib import Path
import ctypes,datetime,json,os,subprocess,sys
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;B=R/'source-post80plate68-basis'
OUT=R/'post80-source-transplant';OUT.mkdir(exist_ok=False)
script=R/'auto_backup_three.py';ns={'__file__':str(script),'__name__':'post80_transplant_global_check'}
exec(compile(script.read_text().split("\nif '--check-only' in sys.argv:",1)[0],str(script),'exec'),ns)
rows=ns['choices']();previous=min([x for x in rows if x[2]=='Post74 joint oscillator-filter'],key=lambda x:x[1]['tone_score'])
current=min(rows,key=lambda x:x[1]['tone_score']);F=previous[0].parent;cfg=json.loads(Path(previous[1]['core_model']).read_text())
P=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(P));import compare_all as a
raw,sr=sf.read(B/'Diva_source.wav',dtype='float32');assert sr==48000
lib=ctypes.CDLL(str(F/'native_finish.so'));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
actual=np.zeros_like(raw);assert lib.native_render(raw.ctypes.data,actual.ctypes.data,len(raw),sr)
edit=a.h.edit_aligned(a.h.align_with_pdc(actual.astype('float64'),dict(alignment_frames=819),latency=12416))
sf.write(OUT/'native-WITH_PDC.wav',actual,sr,subtype='FLOAT');sf.write(OUT/'REFERENCE_EDIT_SCREEN_ONLY.wav',edit,sr,subtype='FLOAT')
a.WORK=OUT;(OUT/'scores').mkdir();measured=a.score(dict(id='post80_transplant',canonical_path=str(OUT/'REFERENCE_EDIT_SCREEN_ONLY.wav'),aliases=[]))
scales=json.loads((P/'ranking.json').read_text())['normalizing_errors'];tone=sum(ns['TONE'][k]*measured['metrics'][k]/scales[k] for k in ns['TONE'])
score=sum(a.WEIGHTS[k]*measured['metrics'][k]/scales[k] for k in a.WEIGHTS);crest=measured['diagnostics']['crest_RMS_db']
feasible=bool(all(measured['metrics'][k]<=ns['ANCHOR']['metrics'][k]*limit for k,limit in ns['LIMITS'].items()) and crest<=ns['ANCHOR']['crest_RMS_dB']*1.001 and score<=ns['ANCHOR']['score']*1.0001 and np.max(abs(actual))<.99)
decision=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozen_old_source_validation=str(previous[0]),new_matching_source_basis=str(B),native_source_screen_tone=tone,previous_global_tone=current[1]['tone_score'],native_screen_all_original_guards=feasible,full_proof_completed=False,match_reached=False)
if feasible and tone<current[1]['tone_score']-1e-6:
    fit=OUT/'frozen-existing-model';fit.mkdir()
    choice=json.loads((F/'numeric-choice.json').read_text())
    for field in ['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters']:choice[field]=cfg[field]
    choice.update(feasible_search_guards=True,user_selected_three_baseline=True,guard_limits=ns['LIMITS'],tone_focused_weights=ns['TONE'],fixed_crest_cap_dB=ns['ANCHOR']['crest_RMS_dB']*1.001,source_screen_only_until_fresh_proof=True)
    (fit/'best.json').write_text(json.dumps(choice,indent=2)+'\n');(fit/'history.json').write_text(json.dumps([dict(weighted_score=current[1]['tone_score'])],indent=2)+'\n')
    env=dict(os.environ,DIVALEAD_THREE_SOURCE_BASIS=str(B),DIVALEAD_THREE_SOURCE_REPORT=str(B/'validation.json'))
    target=R/'post80plate68-verified-transplant-0001'
    with (OUT/'validation.log').open('w') as log:
        result=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log,timeout=900)
    if result.returncode:
        from three_candidate_decision import quality_rejection
        rejection=quality_rejection(OUT/'validation.log',target);assert rejection is not None,'Infrastructure failure in transplant validation'
        decision.update(rejection)
    else:
        report=ns['checked'](target/'validation.json')[0]
        decision.update(full_proof_completed=True,validation=str(target/'validation.json'),tone_score=report['tone_score'],score=report['score'])
else:decision.update(accepted=False,reason='No better feasible native screen; preserve completed old-source and Plate68 proofs')
(OUT/'decision.json').write_text(json.dumps(decision,indent=2)+'\n');print(json.dumps(decision),flush=True)
