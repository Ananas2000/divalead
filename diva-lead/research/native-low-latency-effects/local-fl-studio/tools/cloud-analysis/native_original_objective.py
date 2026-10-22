"""Authoritative original-reference criteria; analysis only, no reference audio output."""
from pathlib import Path
import json,os,sys,threading
import numpy as np
import soundfile as sf
from native_features import Features,target
W=Path(__file__).resolve().parent;P=Path('/workspace/divalead')
ASSESSMENT=Path(os.environ.get('DIVALEAD_NATIVE_OBJECTIVE_ROOT',str(W/'direct-original-assessment')))
os.environ['DIVALEAD_SELECTION_WORK']=str(ASSESSMENT)
os.environ['DIVALEAD_RESEARCH_WORK']=str(W/'direct-original-cache')
sys.path.insert(0,str(P/'diva-lead/research/repository-selection'))
import compare_all as a
ROOT=ASSESSMENT;ROOT.mkdir(parents=True,exist_ok=True);(ROOT/'scores').mkdir(exist_ok=True);a.WORK=ROOT
SCALES=json.loads((P/'diva-lead/research/repository-selection/ranking.json').read_text())['normalizing_errors']
TONE=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
class FeaturesOriginal:
    def __init__(self,target):
        self.transfer=Features(target);self.target_rms=float(np.sqrt(np.mean(target.astype(float)**2)))
        self.local=threading.local();self.lock=threading.Lock();self.counter=0
    def residual(self,y):
        if not hasattr(self.local,'id'):
            with self.lock:self.local.id=f'native-score-worker-{self.counter}';self.counter+=1
        label=self.local.id;path=ROOT/(label+'.wav')
        edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0))
        sf.write(path,edit,48000,subtype='FLOAT')
        score=a.score(dict(id=label,canonical_path=str(path),aliases=[]));m=score['metrics']
        standard=sum(a.WEIGHTS[k]*m[k]/SCALES[k] for k in a.WEIGHTS)
        tone=sum(TONE[k]*m[k]/SCALES[k] for k in TONE)
        r=self.transfer.residual(y);transfer=float(r@r)
        rms=float(np.sqrt(np.mean(y.astype(float)**2)))
        value=.65*tone+.35*standard+.05*transfer+.2*abs(np.log((rms+1e-12)/self.target_rms))+20*max(0,float(abs(y).max())-.97)**2
        self.local.last=dict(tone_score=tone,standard_score=standard,v83_coarse_transfer_loss=transfer,metrics=m,diagnostics=score['diagnostics'])
        return np.array([np.sqrt(max(0,value))])
