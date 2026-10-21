"""Compare actual native output to the ORIGINAL with the unchanged video edit."""
from pathlib import Path
import os,sys,json
import numpy as np
import soundfile as sf
W=Path(__file__).resolve().parent;P=Path('/workspace/divalead')
os.environ['DIVALEAD_SELECTION_WORK']=str(W/'reference-assessment')
os.environ['DIVALEAD_RESEARCH_WORK']=str(W/'reference-analysis-cache')
sys.path.insert(0,str(P/'diva-lead/research/repository-selection'))
import compare_all as a
out=W/'reference-assessment';out.mkdir(exist_ok=True);(out/'scores').mkdir(exist_ok=True)
scale=json.loads((P/'diva-lead/research/repository-selection/ranking.json').read_text())['normalizing_errors']
tone_weights=dict(H24=.30,upper_harm=.25,ERB=.20,low_harm=.10,upper_off=.10,relative_phase=.05)
result=[]
paths=[('v83-complete',P/'diva-lead/v83-wip/Diva_Lead_v83_FULL_180BPM.wav')]
paths += [(Path(s).parent.name,Path(s)) for s in sys.argv[1:]]
for name,path in paths:
    y,sr=sf.read(path,dtype='float64',always_2d=True);assert sr==48000
    edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0))
    dest=out/(name+'-REFERENCE_EDIT.wav');sf.write(dest,edit,48000,subtype='FLOAT')
    a.WORK=out;score=a.score(dict(id=name,canonical_path=str(dest),aliases=[]))
    m=score['metrics'];standard=sum(a.WEIGHTS[k]*m[k]/scale[k] for k in a.WEIGHTS)
    tone=sum(tone_weights[k]*m[k]/scale[k] for k in tone_weights)
    row=dict(id=name,actual_audio=str(path),score=standard,tone_score=tone,tone_weights=tone_weights,metrics=m,diagnostics=score['diagnostics'],declared_latency_frames=0,alignment_frames=819,unchanged_video_reference_edit=True,match_reached=False)
    result.append(row);print(name,standard,tone,m,flush=True)
(out/'COMPARISON.json').write_text(json.dumps(result,indent=2)+'\n')
