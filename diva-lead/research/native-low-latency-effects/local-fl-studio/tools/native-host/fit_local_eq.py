"""Fit real native EQ2/Stereo Shaper to original-reference analysis features.

The native WS/Chorus prefix is frozen only for training; selected states must
be validated in the complete live FL graph with fresh Chorus realizations.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,time,queue,threading,concurrent.futures,sys
import numpy as np,soundfile as sf
from scipy.optimize import least_squares
from local_native_chain import NativeChain,SESSION,ROOT
from reference_features import ReferenceFeatures
OUT=SESSION/'local-eq-search';OUT.mkdir(exist_ok=True)
start=time.monotonic();features=ReferenceFeatures();calls=0;best=float('inf');lock=threading.Lock();history=[]
source=SESSION/'renders/FL_DIVA_SOURCE_UNITY.wav'
prefix=NativeChain(source,'TRAINING_SOURCE_PREFIX');prefix.checkpoint()
for n in (4,5,6,7,8,10,11,12):prefix.bypass(n)
prefix.gain(3,1);prefix.gain(4,0)
for k in range(3):
    y,status=prefix.render();sf.write(OUT/f'prefix-{k}.wav',y,48000,subtype='FLOAT');time.sleep(.25)
prefix.close()
snapshot=json.loads((SESSION/'native-parameter-snapshot.json').read_text())
x0=np.r_[[v/100 for n in ('4','5','6','7')for v in snapshot[n][:7]],[v/65536 for n in ('4','5','6','7')for v in snapshot[n][7:14]],[v/65536 for n in ('4','5','6','7')for v in snapshot[n][14:21]],[snapshot['4'][35]/100,snapshot['6'][35]/100],[-8814/12800,9656/12800,3194/12800,3446/12800]]
lower=np.r_[np.full(28,-18),np.maximum(0,x0[28:56]-.08),np.maximum(.002,x0[56:84]-.20),[-18,-18],np.maximum(-1,x0[86:90]-.3)]
upper=np.r_[np.full(28,18),np.minimum(1,x0[28:56]+.08),np.minimum(.90,x0[56:84]+.20),[6,6],np.minimum(1,x0[86:90]+.3)]
steps=np.r_[np.full(28,.05),np.full(28,.0008),np.full(28,.0025),[.03,.03],np.full(4,.002)]
scale=np.r_[np.full(28,5),np.full(28,.04),np.full(28,.12),[3,3],np.full(4,.1)]
pool=queue.Queue();clients=[]
for k in range(4):
    c=NativeChain(OUT/'prefix-0.wav',f'EQ_SEARCH_WORKER_{k}');c.checkpoint()
    for n in (0,3,13,14):c.bypass(n)
    c.gain(0,1);c.gain(1,0);clients.append(c);pool.put(c)
def apply(c,x):
    for j,n in enumerate((4,5,6,7)):
        for band in range(7):
            k=j*7+band;c.set(n,band,round(x[k]*100));c.set(n,7+band,round(x[28+k]*65536));c.set(n,14+band,round(x[56+k]*65536))
        c.set(n,35,round(x[84+(j>=2)]*100))
    for j in range(4):c.set(8,j,round(x[86+j]*12800))
def evaluate(x,save=True):
    global best,calls
    c=pool.get()
    try:
        apply(c,x);y,status=c.render();r=features.residual(y)
        r=np.r_[r,(x[:28]-x0[:28])*.0002,(x[28:84]-x0[28:84])*.002]
        loss=float(r@r)
        with lock:
            calls+=1
            if save and loss<best:
                best=loss;row=dict(loss=loss,calls=calls,seconds=time.monotonic()-start,x=x.tolist(),native_status=status,source='FL Diva current PW+1, three held notes; native fixed WS/Chorus training prefix',original_reference_analysis=True,training_proxy_only=True,complete_graph_validation_pending=True,match_reached=False)
                history.append(row);(OUT/'best.json').write_text(json.dumps(row,indent=2));(OUT/'history.json').write_text(json.dumps(history,indent=2));sf.write(OUT/'best-training.wav',y,48000,subtype='FLOAT')
                print('BEST',json.dumps({k:row[k]for k in('loss','calls','seconds')}),flush=True)
        return r
    finally:pool.put(c)
executor=concurrent.futures.ThreadPoolExecutor(4)
def jac(x):
    center=evaluate(x,False)
    def column(i):
        d=steps[i] if x[i]+steps[i]<=upper[i] else -steps[i];v=x.copy();v[i]+=d;return(evaluate(v,False)-center)/d
    return np.column_stack(list(executor.map(column,range(len(x)))))
try:
    print('INITIAL',float(evaluate(x0)@evaluate(x0,False)),flush=True)
    fit=least_squares(evaluate,x0,jac=jac,bounds=(lower,upper),x_scale=scale,max_nfev=45,ftol=2e-5,xtol=2e-5,gtol=2e-5,tr_solver='lsmr')
    (OUT/'optimizer-result.json').write_text(json.dumps(dict(success=bool(fit.success),message=fit.message,nfev=fit.nfev,njev=fit.njev,total_calls=calls,seconds=time.monotonic()-start),indent=2))
    bestx=np.array(json.loads((OUT/'best.json').read_text())['x']);c=clients[0];apply(c,bestx)
    for node,name in[(4,'MID_EQ_A'),(5,'MID_EQ_B'),(6,'SIDE_EQ_A'),(7,'SIDE_EQ_B'),(8,'SUM_Stereo')]:c.save_state(node,OUT/(name+'.bin'))
    print('FINISHED',fit.message,calls,time.monotonic()-start,flush=True)
finally:
    executor.shutdown(wait=True)
    for c in clients:c.close()
