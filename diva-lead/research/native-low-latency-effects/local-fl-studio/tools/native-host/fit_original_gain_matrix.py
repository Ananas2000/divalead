"""Fit real native gain/matrix controls using unchanged original-reference criteria."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,time,threading,queue,concurrent.futures,sys
import numpy as np,soundfile as sf
from scipy.optimize import minimize
from local_native_chain import NativeChain,SESSION,ROOT
OUT=SESSION/'original-gain-search';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tone_weights=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
snapshot=json.loads((SESSION/'native-parameter-snapshot.json').read_text())
x0=np.r_[[v/100 for n in('4','5','6','7')for v in snapshot[n][:7]],[snapshot['4'][35]/100,snapshot['6'][35]/100],[-8814/12800,9656/12800,3194/12800,3446/12800]]
lower=np.r_[np.maximum(-18,x0[:28]-5),x0[28:30]-3,np.maximum(-1,x0[30:34]-.25)]
upper=np.r_[np.minimum(18,x0[:28]+5),x0[28:30]+3,np.minimum(1,x0[30:34]+.25)]
steps=np.r_[np.full(28,.12),[.05,.05],np.full(4,.004)]
start=time.monotonic();pool=queue.Queue();clients=[];lock=threading.Lock();calls=0;best=float('inf');history=[]
for k in range(4):
    c=NativeChain(SESSION/'local-eq-search/prefix-0.wav',f'ORIGINAL_SEARCH_WORKER_{k}');c.checkpoint()
    for n in(0,3,13,14):c.bypass(n)
    c.gain(0,1);c.gain(1,0);c.label=f'worker-{k}';clients.append(c);pool.put(c)
def apply(c,x):
    for j,n in enumerate((4,5,6,7)):
        for band in range(7):c.set(n,band,round(x[j*7+band]*100))
        c.set(n,35,round(x[28+(j>=2)]*100))
    for j in range(4):c.set(8,j,round(x[30+j]*12800))
def evaluate(x):
    global best,calls
    c=pool.get()
    try:
        apply(c,x);y,status=c.render();edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));dest=OUT/(c.label+'.wav');sf.write(dest,edit,48000,subtype='FLOAT')
        score=a.score(dict(id=c.label,canonical_path=str(dest),aliases=[]));m=score['metrics'];standard=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tone_weights[k]*m[k]/scales[k]for k in tone_weights)
        gain=score['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max());value=.65*tone+.35*standard+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        with lock:
            calls+=1
            if value<best:
                best=value;row=dict(loss=value,score=standard,tone_score=tone,calls=calls,seconds=time.monotonic()-start,x=np.asarray(x).tolist(),metrics=m,peak=peak,gain_for_AB=gain,native_status=status,complete_graph_validation_pending=True,match_reached=False)
                history.append(row);(OUT/'best.json').write_text(json.dumps(row,indent=2));(OUT/'history.json').write_text(json.dumps(history,indent=2));sf.write(OUT/'best-training.wav',y,48000,subtype='FLOAT');print('ORIGINAL_BEST',json.dumps({k:row[k]for k in('loss','score','tone_score','calls','seconds')}),flush=True)
        return value
    finally:pool.put(c)
executor=concurrent.futures.ThreadPoolExecutor(4)
def jac(x):
    center=evaluate(x)
    def column(i):
        d=steps[i] if x[i]+steps[i]<=upper[i] else -steps[i];v=x.copy();v[i]+=d;return(evaluate(v)-center)/d
    return np.array(list(executor.map(column,range(len(x)))))
try:
    evaluate(x0)
    fit=minimize(evaluate,x0,method='L-BFGS-B',jac=jac,bounds=list(zip(lower,upper)),options=dict(maxiter=30,maxls=12,ftol=2e-6,gtol=.0002))
    (OUT/'optimizer-result.json').write_text(json.dumps(dict(success=bool(fit.success),message=str(fit.message),nfev=int(fit.nfev),nit=int(fit.nit),calls=calls,seconds=time.monotonic()-start),indent=2))
    x=np.array(json.loads((OUT/'best.json').read_text())['x']);c=clients[0];apply(c,x)
    for n,name in[(4,'MID_EQ_A'),(5,'MID_EQ_B'),(6,'SIDE_EQ_A'),(7,'SIDE_EQ_B'),(8,'SUM_Stereo')]:c.save_state(n,OUT/(name+'.bin'))
    print('FINISHED',fit.message,calls,time.monotonic()-start,flush=True)
finally:
    executor.shutdown(wait=True)
    for c in clients:c.close()
