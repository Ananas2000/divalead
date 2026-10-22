"""Run the repository's unchanged original-reference criteria on local FL WAVs.

Only analysis and the documented fixed 819-frame/video edit; no reference-derived DSP.
"""
from pathlib import Path
import json,os,sys,hashlib
root=Path(__file__).resolve().parent.parent
session=root/'sessions/2026-10-22'
out=session/'assessment';out.mkdir(exist_ok=True);(out/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(out)
os.environ['DIVALEAD_RESEARCH_WORK']=str(out/'cache')
sys.path.insert(0,str(root/'analysis-runtime/diva-lead/research/repository-selection'))
import numpy as np,soundfile as sf
import compare_all as a
a.WORK=out
scales=json.loads((root/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text())
tone_weights=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
results=[]
for arg in sys.argv[1:]:
    path=(root/arg).resolve();x,sr=sf.read(path,dtype='float64',always_2d=True)
    assert sr==48000 and x.shape[1]==2 and np.isfinite(x).all()
    edit=a.h.edit_aligned(a.h.align_with_pdc(x,dict(alignment_frames=819),latency=0))
    dest=out/(path.stem+'_REFERENCE_EDIT.wav');sf.write(dest,edit,sr,subtype='FLOAT')
    score=a.score(dict(id=path.stem,canonical_path=str(dest),aliases=[]));m=score['metrics']
    standard=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS)
    tone=sum(tone_weights[k]*m[k]/scales[k] for k in tone_weights)
    row=dict(id=path.stem,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),samplerate=sr,frames=len(x),peak=float(abs(x).max()),rms_lr=np.sqrt(np.mean(x*x,axis=0)).tolist(),fixed_alignment_frames=819,score=standard,tone_score=tone,metrics=m,diagnostics=score['diagnostics'],match_reached=False)
    results.append(row);print(json.dumps({k:row[k] for k in ('id','score','tone_score','peak','metrics')}) ,flush=True)
    (out/(path.stem+'.json')).write_text(json.dumps(row,indent=2),encoding='utf-8')
(out/'LOCAL_COMPARISON.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
