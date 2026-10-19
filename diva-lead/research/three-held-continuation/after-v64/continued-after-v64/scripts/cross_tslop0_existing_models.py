"""Measure existing proven DSPs on the newly rendered THREE-held TuneSlop0 source."""
from pathlib import Path
import os,sys,json,ctypes,subprocess,datetime,hashlib
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;B=R/'source-tslop0-basis';V=Path('/tmp/divalead-tslop0-cross-models');V.mkdir(exist_ok=False)
assert (B/'preliminary-metrics.json').exists() and not (B/'validation.json').exists()
P=Path('/workspace/divalead/diva-lead/research/repository-selection');sys.path.insert(0,str(P));import compare_all as a
a.WORK=V;(V/'scores').mkdir();anchor=json.loads((R/'baseline/validation.json').read_text());pre=json.loads((B/'preliminary-metrics.json').read_text());scales=json.loads((P/'ranking.json').read_text())['normalizing_errors'];weights=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
raw,sr=sf.read(B/'Diva_source.wav',dtype='float32');assert sr==48000 and raw.shape==(288000,2)
assert hashlib.sha256(raw.tobytes()).hexdigest()==pre['source_render_history']['source_samples_SHA256']
labels=['verified-fine55-power69-combined','verified-joint-phase-0032-fine55','verified-joint32-fine55-projection','verified-cont-0035-hf','verified-joint32-power69-combined']
history=[];best=None
for name in labels:
    model=R/name
    if not (model/'validation.json').is_file():continue
    proof=json.loads((model/'validation.json').read_text());assert proof['same_user_selected_Diva_preset_raw_and_all281']
    lib=ctypes.CDLL(str(model/'native_finish.so'));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
    full=np.zeros_like(raw);assert lib.native_render(raw.ctypes.data,full.ctypes.data,len(raw),sr)
    edit=a.h.edit_aligned(a.h.align_with_pdc(full.astype('float64'),dict(alignment_frames=819),latency=12416));path=V/(name+'.wav');sf.write(path,edit,sr,subtype='FLOAT')
    measured=a.score(dict(id=name,canonical_path=str(path),aliases=[]));m=measured['metrics'];tone=sum(weights[k]*m[k]/scales[k] for k in weights);standard=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS);crest=measured['diagnostics']['crest_RMS_db']
    failed={k:float(m[k]/anchor['metrics'][k]-limit) for k,limit in pre['guard_limits'].items() if m[k]>anchor['metrics'][k]*limit}
    if crest>pre['crest_cap_dB']:failed['crest_dB']=crest-pre['crest_cap_dB']
    if standard>anchor['score']*1.0001:failed['standard']=standard-anchor['score']*1.0001
    if np.max(np.abs(full))>=.99:failed['peak']=float(np.max(np.abs(full))-.99)
    row=dict(model=name,tone_score=tone,score=standard,metrics=m,crest_RMS_dB=crest,failed_fixed_limits=failed,feasible=not failed,only_three_held=True,source_family='TuneSlop0',match_reached=False);history.append(row)
    if name==labels[0]:
        assert abs(tone-pre['tone_score'])<1e-7
        np.testing.assert_allclose(edit,sf.read(B/'REFERENCE_EDIT_WIP.wav')[0],rtol=0,atol=2e-7)
    if not failed and tone<pre['acceptance_tone_cap']-1e-6 and (best is None or tone<best['tone_score']):best=row
    print('TSLOP0_EXISTING_MODEL_CROSS',name,tone,failed,flush=True)
    (V/'history.json').write_text(json.dumps(history,indent=2)+'\n')
decision=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),best=best,source_family='TuneSlop0',not_adopted_into_original_source=True,full_actual_proof_completed=False,match_reached=False)
if best:
    model=R/best['model'];fit=V/'selected-cross';fit.mkdir();choice=json.loads((model/'numeric-choice.json').read_text());choice.update(metrics=best['metrics'],weighted_score=best['tone_score'],standard_weighted_score=best['score'],crest_RMS_dB=best['crest_RMS_dB'],source_manifest=json.loads((B/'source_manifest.json').read_text()),feasible_search_guards=True,source_family='TuneSlop0',source_physical_change={'OPT:TSlop':0.0},selection_method='Actual native C cross-render of existing full-proved spectral coefficients, followed by mandatory fresh source-family Windows proof')
    (fit/'best.json').write_text(json.dumps(choice,indent=2)+'\n');(fit/'history.json').write_text(json.dumps([dict(weighted_score=pre['tone_score']),choice],indent=2)+'\n')
    env=dict(os.environ,DIVALEAD_THREE_SOURCE_BASIS=str(B),DIVALEAD_THREE_SOURCE_REPORT=str(B/'preliminary-metrics.json'));target=R/'tslop0-verified-cross-0001'
    try:
        with (V/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log,check=True,timeout=900)
    except subprocess.CalledProcessError:
        from three_candidate_decision import quality_rejection
        rejection=quality_rejection(V/'validation.log',target)
        if rejection is None:raise
        decision.update(rejection=rejection)
    else:
        d=json.loads((target/'validation.json').read_text());decision.update(full_actual_proof_completed=True,validation=str(target/'validation.json'),tone_score=d['tone_score'],score=d['score'])
(R/'tslop0-cross-model-decision.json').write_text(json.dumps(decision,indent=2)+'\n');(V/'decision.json').write_text(json.dumps(decision,indent=2)+'\n');print('TSLOP0_CROSS_MODEL_DECISION',decision,flush=True)
