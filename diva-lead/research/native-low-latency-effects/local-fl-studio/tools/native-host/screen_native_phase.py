"""Screen real native dephasing/delay and Chorus mix using original criteria."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,time,threading,queue,concurrent.futures,sys
import numpy as np,soundfile as sf
from local_native_chain import NativeChain,SESSION,ROOT
OUT=SESSION/'native-phase-screen';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tw=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
start=time.monotonic();pool=queue.Queue();clients=[];lock=threading.Lock();results=[]
for k in range(4):
    c=NativeChain(SESSION/'renders/DIVA_FRESH_DIRECT.wav',f'PHASE_SCREEN_{k}');c.checkpoint();c.label=f'worker-{k}';clients.append(c);pool.put(c)
trials=[('baseline',[],None)]
trials += [(f'common-{v}',[(13,5,v),(14,5,-v)],None)for v in range(-10000,10001,1000)]
trials += [(f'sum-phase-{v}',[(8,5,v)],None)for v in range(-4000,4001,500)]
trials += [(f'sum-delay-{v}',[(8,4,v)],None)for v in range(-2000,2001,250)]
trials += [(f'chorus-{j}',[],v)for j,v in enumerate([0,.05,.15,.25,.384609375,.5,.65,.8,1])]
def evaluate(trial):
    tag,changes,mix=trial;c=pool.get()
    try:
        c.checkpoint()
        for n,i,v in changes:c.set(n,i,v)
        if mix is not None:c.gain(0,1-mix);c.gain(1,mix)
        y,status=c.render();edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));path=OUT/(c.label+'.wav');sf.write(path,edit,48000,subtype='FLOAT')
        s=a.score(dict(id=c.label,canonical_path=str(path),aliases=[]));m=s['metrics'];standard=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tw[k]*m[k]/scales[k]for k in tw);gain=s['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max());loss=.65*tone+.35*standard+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        actual=[(n,i,c.value_hint(n,i))for n,i,v in changes]
        row=dict(tag=tag,changes=changes,actual_values=actual,chorus_mix=mix,loss=loss,score=standard,tone_score=tone,peak=peak,metrics=m,gain_for_AB=gain,seconds=time.monotonic()-start,native_status=status,match_reached=False)
        (OUT/(tag+'.json')).write_text(json.dumps(row,indent=2));sf.write(OUT/(tag+'.wav'),y,48000,subtype='FLOAT')
        with lock:
            results.append(row);(OUT/'ranking.json').write_text(json.dumps(sorted(results,key=lambda r:r['loss']),indent=2));print('PHASE',json.dumps({k:row[k]for k in('tag','loss','score','tone_score')}),flush=True)
        return row
    finally:pool.put(c)
try:
    with concurrent.futures.ThreadPoolExecutor(4)as e:list(e.map(evaluate,trials))
finally:
    for c in clients:c.close()
print('COMPLETE',len(results),time.monotonic()-start,flush=True)
