"""Unmodified repository criteria and fixed 819-frame alignment for Oct 24 WAVs."""
from pathlib import Path
import os,sys,json,hashlib
ROOT=Path(__file__).resolve().parent.parent
SESSION=ROOT/'sessions/2026-10-24'
OUT=SESSION/'assessment';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT)
os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import numpy as np,soundfile as sf
import compare_all as a
a.WORK=OUT
SCALES=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text())
TONE=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
def assess(path):
    path=Path(path);x,sr=sf.read(path,dtype='float64',always_2d=True)
    assert sr==48000 and x.shape[1]==2 and np.isfinite(x).all()
    # Exported GUI tail may be shorter than the cloud 6-second carrier.
    # All scored samples fall inside the same original fixed video edit.
    edit=a.h.edit_aligned(a.h.align_with_pdc(x,dict(alignment_frames=819),latency=0))
    dest=OUT/(path.stem+'_REFERENCE_EDIT.wav');sf.write(dest,edit,sr,subtype='FLOAT')
    score=a.score(dict(id=path.stem,canonical_path=str(dest),aliases=[]));m=score['metrics']
    standard=sum(a.WEIGHTS[k]*m[k]/SCALES[k] for k in a.WEIGHTS)
    tone=sum(TONE[k]*m[k]/SCALES[k] for k in TONE)
    row=dict(id=path.stem,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),samplerate=sr,frames=len(x),peak=float(abs(x).max()),rms_lr=np.sqrt(np.mean(x*x,axis=0)).tolist(),fixed_alignment_frames=819,standard_score=standard,tone_score=tone,metrics=m,diagnostics=score['diagnostics'],match_reached=False)
    (OUT/(path.stem+'.json')).write_text(json.dumps(row,indent=2),encoding='utf-8')
    return row
if __name__=='__main__':
    for arg in sys.argv[1:]:
        row=assess(ROOT/arg);print(json.dumps({k:row[k]for k in('id','standard_score','tone_score','peak','diagnostics')}),flush=True)
