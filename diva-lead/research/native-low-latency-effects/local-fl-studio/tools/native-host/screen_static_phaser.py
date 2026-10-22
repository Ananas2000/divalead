"""Screen a real Fruity Phaser after SUM, with constant depth and zero feedback.
No reference-derived filter is applied. Only installed native DLLs process audio.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,time,threading,queue,concurrent.futures,sys
import numpy as np,soundfile as sf
from local_native_chain import NativeChain,SESSION,ROOT
OUT=SESSION/'static-phaser-screen';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tw=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
start=time.monotonic();pool=queue.Queue();clients=[];lock=threading.Lock();results=[];best=1e9
for k in range(4):
    c=NativeChain(SESSION/'renders/DIVA_FRESH_DIRECT.wav',f'STATIC_PHASER_{k}',extra_phaser=True);c.checkpoint();c.label=f'worker-{k}';clients.append(c);pool.put(c)
trials=[(f'baseline-{k}',None)for k in range(6)]
trials += [(f'd{d}-s{s}-w{w}',dict(depth=d,stages=s,wet=w))for d in (0,50,100,200,350,500,650,800,950,1000)for s in (0,1,3,7,11,15,20)for w in (256,512,768,1000)]
def evaluate(trial):
    global best
    tag,p=trial;c=pool.get()
    try:
        c.checkpoint();c.bypass(15,p is None);c.bypass(16,True)
        if p:
            c.load_state(15,SESSION/'PHASER_DEFAULT.bin')
            for i,v in enumerate((0,p['depth'],p['depth'],0,0,p['stages'],0,p['wet'],2500)):c.set(15,i,v)
        y,status=c.render();edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));path=OUT/(c.label+'.wav');sf.write(path,edit,48000,subtype='FLOAT')
        s=a.score(dict(id=c.label,canonical_path=str(path),aliases=[]));m=s['metrics'];standard=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tw[k]*m[k]/scales[k]for k in tw);gain=s['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max());loss=.65*tone+.35*standard+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        row=dict(tag=tag,parameters=p,loss=loss,score=standard,tone_score=tone,peak=peak,metrics=m,gain_for_AB=gain,seconds=time.monotonic()-start,native_status=status,match_reached=False)
        (OUT/(tag+'.json')).write_text(json.dumps(row,indent=2))
        with lock:
            results.append(row);(OUT/'ranking.json').write_text(json.dumps(sorted(results,key=lambda r:r['loss']),indent=2))
            if loss<best:
                best=loss;sf.write(OUT/'BEST.wav',y,48000,subtype='FLOAT');c.save_state(15,OUT/'BEST_PHASER.bin');(OUT/'BEST.json').write_text(json.dumps(row,indent=2));print('BEST',json.dumps({k:row[k]for k in('tag','loss','score','tone_score','parameters')}),flush=True)
            if len(results)%40==0:print('PROGRESS',len(results),time.monotonic()-start,flush=True)
        return row
    finally:pool.put(c)
try:
    with concurrent.futures.ThreadPoolExecutor(4)as e:list(e.map(evaluate,trials))
finally:
    for c in clients:c.close()
print('COMPLETE',len(results),time.monotonic()-start,flush=True)
