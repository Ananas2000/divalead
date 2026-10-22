"""Derivative-free bounded joint search, full native graph and original criteria.
Keep the synth, waveshaper, EQ frequencies and bandwidths fixed. Only real native
EQ gains, EQ main gains, and the real SUM StereoShaper matrix are adjustable.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,time,threading,queue,concurrent.futures,sys
import numpy as np,soundfile as sf
from scipy.optimize import differential_evolution
from local_native_chain import NativeChain,SESSION,ROOT
OUT=SESSION/'original-full-de';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tw=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
snapshot=json.loads((SESSION/'native-parameter-snapshot.json').read_text())
x0=np.r_[[v/100 for n in('4','5','6','7')for v in snapshot[n][:7]],[snapshot['4'][35]/100,snapshot['6'][35]/100],[-8814/12800,9656/12800,3194/12800,3446/12800]]
scale=np.r_[np.full(28,3.),[1.5,1.5],np.full(4,.18)]
start=time.monotonic();pool=queue.Queue();clients=[];lock=threading.Lock();calls=0;best=1e9;history=[]
for k in range(4):
    c=NativeChain(SESSION/'renders/DIVA_FRESH_DIRECT.wav',f'FULL_DE_{k}');c.checkpoint();c.label=f'worker-{k}';clients.append(c);pool.put(c)
def apply(c,x):
    for j,n in enumerate((4,5,6,7)):
        for band in range(7):c.set(n,band,round(x[j*7+band]*100))
        c.set(n,35,round(x[28+(j>=2)]*100))
    for j in range(4):c.set(8,j,round(x[30+j]*12800))
def evaluate(z):
    global best,calls
    c=pool.get()
    try:
        x=x0+np.asarray(z)*scale;apply(c,x);y,status=c.render()
        edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));path=OUT/(c.label+'.wav');sf.write(path,edit,48000,subtype='FLOAT')
        s=a.score(dict(id=c.label,canonical_path=str(path),aliases=[]));m=s['metrics'];score=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tw[k]*m[k]/scales[k]for k in tw);gain=s['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max());loss=.65*tone+.35*score+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        with lock:
            calls+=1
            if loss<best:
                best=loss;row=dict(loss=loss,score=score,tone_score=tone,x=x.tolist(),z=np.asarray(z).tolist(),metrics=m,gain_for_AB=gain,peak=peak,calls=calls,seconds=time.monotonic()-start,native_status=status,actual_FL_validation_pending=True,match_reached=False)
                history.append(row);(OUT/'best.json').write_text(json.dumps(row,indent=2));(OUT/'history.json').write_text(json.dumps(history,indent=2));sf.write(OUT/'BEST.wav',y,48000,subtype='FLOAT')
                for n,name in((4,'MID_EQ_A'),(5,'MID_EQ_B'),(6,'SIDE_EQ_A'),(7,'SIDE_EQ_B'),(8,'SUM_Stereo')):c.save_state(n,OUT/(name+'.bin'))
                print('BEST',json.dumps({k:row[k]for k in('loss','score','tone_score','calls','seconds')}),flush=True)
            if calls%100==0:print('PROGRESS',calls,time.monotonic()-start,flush=True)
        return loss
    finally:pool.put(c)
executor=concurrent.futures.ThreadPoolExecutor(4)
try:
    base=[evaluate(np.zeros(34))for _ in range(4)]
    rng=np.random.default_rng(20261022);population=np.clip(rng.normal(0,.18,size=(102,34)),-1,1);population[0]=0
    fit=differential_evolution(evaluate,[(-1,1)]*34,init=population,maxiter=14,polish=False,seed=20261022,workers=executor.map,updating='deferred',mutation=(.4,.9),recombination=.8,tol=.0001,atol=.0001)
    (OUT/'optimizer-result.json').write_text(json.dumps(dict(success=bool(fit.success),message=str(fit.message),nfev=int(fit.nfev),nit=int(fit.nit),calls=calls,seconds=time.monotonic()-start,baseline_losses=base),indent=2))
    print('COMPLETE',calls,time.monotonic()-start,flush=True)
finally:
    executor.shutdown(wait=True)
    for c in clients:c.close()
