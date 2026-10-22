"""Confirm small source modulation changes with repeated complete native renders."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,sys,subprocess
import numpy as np,soundfile as sf
from local_native_chain import NativeChain,SESSION,ROOT,W
OUT=SESSION/'moddepth-confirmation';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tw=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
def rel(p):return os.path.relpath(p,ROOT)
rows=[]
for tag,v in [('baseline',.16),('moddepth-63',.185),('moddepth-58',.21)]:
    raw=OUT/(tag+'-RAW.wav');preset=OUT/(tag+'.h2p');dump=OUT/(tag+'-ALL281.tsv')
    commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0',f'set 171 {v}','render '+rel(raw),'dump '+rel(dump),'save '+rel(preset),'quit']
    p=subprocess.run([str(W/'diva_source_render_host.exe'),r'C:\Program Files\VstPlugins\Diva(x64).dll',rel(SESSION/'input/Diva_NATIVE_WIP_THREE_HELD.h2p')],cwd=ROOT,input='\n'.join(commands)+'\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,timeout=60)
    (OUT/(tag+'.log')).write_text(p.stdout);assert p.returncode==0 and sum(l.startswith('NOTE ')for l in p.stdout.splitlines())==12
    c=NativeChain(raw,'CONFIRM_'+tag);c.checkpoint()
    try:
        for repeat in range(10):
            y,status=c.render();edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));path=OUT/'working.wav';sf.write(path,edit,48000,subtype='FLOAT')
            s=a.score(dict(id='working',canonical_path=str(path),aliases=[]));m=s['metrics'];score=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tw[k]*m[k]/scales[k]for k in tw)
            rows.append(dict(tag=tag,repeat=repeat,score=score,tone_score=tone,metrics=m,native_status=status));(OUT/'RESULTS.json').write_text(json.dumps(rows,indent=2))
        print(tag,json.dumps(dict(score_mean=np.mean([r['score']for r in rows if r['tag']==tag]),tone_mean=np.mean([r['tone_score']for r in rows if r['tag']==tag]))),flush=True)
    finally:c.close()
summary={t:{k:dict(mean=float(np.mean([r[k]for r in rows if r['tag']==t])),std=float(np.std([r[k]for r in rows if r['tag']==t])),min=float(min(r[k]for r in rows if r['tag']==t)),max=float(max(r[k]for r in rows if r['tag']==t)))for k in ('score','tone_score')}for t in ('baseline','moddepth-63','moddepth-58')}
(OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
