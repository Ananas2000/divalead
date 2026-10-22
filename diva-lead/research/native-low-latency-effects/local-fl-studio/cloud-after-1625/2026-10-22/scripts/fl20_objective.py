"""The local handoff's full original-reference criterion, analysis only.

This intentionally omits the old cloud v83-transfer proxy. Error values from
this objective must not be compared to old NATIVE_BEST_CANDIDATE loss values.
"""
from pathlib import Path
import json,os,sys,threading
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625')
OUT=Path(os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']);OUT.mkdir(exist_ok=True,parents=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(BASE/'runtime/analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
SCALES=json.loads((BASE/'runtime/analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text())
TONE=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
class FeaturesOriginal:
    def __init__(self,ignored_target=None):self.local=threading.local();self.lock=threading.Lock();self.counter=0
    def residual(self,y):
        if not hasattr(self.local,'label'):
            with self.lock:self.local.label='fl20-worker-'+str(self.counter);self.counter+=1
        label=self.local.label;p=OUT/(label+'.wav')
        edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));sf.write(p,edit,48000,subtype='FLOAT')
        row=a.score(dict(id=label,canonical_path=str(p),aliases=[]));m=row['metrics']
        standard=sum(a.WEIGHTS[k]*m[k]/SCALES[k]for k in a.WEIGHTS);tone=sum(TONE[k]*m[k]/SCALES[k]for k in TONE)
        gain=row['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max())
        loss=.65*tone+.35*standard+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        self.local.last=dict(tone_score=tone,standard_score=standard,metrics=m,diagnostics=row['diagnostics'],peak=peak,objective_version='local_full_original_criteria_FL20_context_v1',actual_FL_validation_pending=True,reference_match_reached=False)
        return np.array([np.sqrt(max(0,float(loss)))])
