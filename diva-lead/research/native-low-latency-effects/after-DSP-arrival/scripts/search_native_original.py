"""Bounded direct search through actual native DLL renders (no numerical model)."""
from pathlib import Path
import concurrent.futures,datetime,json,queue,threading,time,sys,os
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_original_objective import FeaturesOriginal as MigrationFeatures
from native_features import target
from apply_native_candidate import apply

ROOT=Path(os.environ.get('DIVALEAD_NATIVE_SEARCH_ROOT',str(W/'direct-original-stock-fit')));ROOT.mkdir(exist_ok=True)
start=time.monotonic();features=MigrationFeatures(target)
x=np.array(json.loads(Path(sys.argv[1]).read_text())['x'])
if len(x)==80:x=np.r_[x,np.zeros(6)]
assert len(x)==86
lower=np.r_[np.full(30,-18.),np.full(4,-1.),np.full(28,-.9),np.full(14,.005),[-.6,-.35,-2.,-4.],[-1.5,-4.]*3]
upper=np.r_[np.full(30,18.),np.full(4,1.),np.full(28,.9),np.full(14,.85),[.35,.5,2.,4.],[1.5,4.]*3]
steps=np.r_[np.full(28,.4),[.2,.2],np.full(4,.025),np.full(28,.007),np.full(14,.007),[.03,.03,.02,.1],[.012,.1]*3]
pool=queue.Queue();clients=[]
for i in range(4):
 c=NativeChain(W/'native-frozen-source-with-tail.wav',f'native-coordinate-{i}',fl_graph=True);clients.append(c);pool.put(c)
mutex=threading.Lock();calls=0;best=float('inf');history=[]
def evaluate(x,save=True):
 global calls,best
 c=pool.get()
 try:
  apply(c,x);y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025
  with mutex:
   calls+=1
   if save and loss<best:
    best=loss;row=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),loss=loss,calls=calls,seconds=time.monotonic()-start,x=x.tolist(),native_status=status,peak=float(abs(y).max()),native_DLL_audio=True,distinct_input_output_buffers=True,FL_stock_mixer_graph=True,declared_native_latency_frames=0,strict_waveform_match=False,original_reference_match_reached=False,original_reference_assessment=features.local.last)
    history.append(row);sf.write(ROOT/'best-with-tail.wav',y,48000,subtype='FLOAT');(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');(ROOT/'history.json').write_text(json.dumps(history,indent=2)+'\n');print('NATIVE_DIRECT_BEST',loss,calls,round(time.monotonic()-start,1),flush=True)
  return loss
 finally:pool.put(c)

executor=concurrent.futures.ThreadPoolExecutor(4)
try:
 current=evaluate(x)
 # Coarse all-pass/dephase alternatives avoid a derivative barrier at zero.
 trials=[]
 for i,vals in [(78,[-.4,-.2,-.08,-.02,0,.02,.08,.2,.4]),(79,np.linspace(-4,4,33))]+[(i,[-2.,-.5,0.,.5,2.]) for i in [81,83,85]]:
  for v in vals:
   z=x.copy();z[i]=v;trials.append(z)
 losses=list(executor.map(evaluate,trials));j=int(np.argmin(losses))
 if losses[j]<current:x=trials[j];current=losses[j]
 for sweep in range(48):
  before=current;trials=[];indices=[]
  for i in range(len(x)):
   for sign in [-1,1]:
    z=x.copy();z[i]=np.clip(z[i]+steps[i]*sign,lower[i],upper[i]);trials.append(z);indices.append(i)
  losses=list(executor.map(evaluate,trials));order=np.argsort(losses);good=[int(j) for j in order if losses[j]<current-1e-7]
  if good:
   # Compare a simultaneous proposal with the best proven single coordinate.
   z=x.copy();used=set()
   for j in good[:16]:
    i=indices[j]
    if i not in used:z[i]=trials[j][i];used.add(i)
   joint=evaluate(z);single=good[0]
   if joint<losses[single]:x=z;current=joint
   else:x=trials[single];current=losses[single]
  else:steps*=.6
  state=dict(sweep=sweep,calls=calls,loss=current,improvement=before-current,max_step=float(steps.max()),elapsed_seconds=time.monotonic()-start,match_reached=False)
  (ROOT/'search-state.json').write_text(json.dumps(state,indent=2)+'\n');print('SWEEP',state,flush=True)
  if steps.max()<.015:break
 (ROOT/'optimizer-result.json').write_text(json.dumps(dict(method='actual-DLL bounded direct coordinate and grouped proposals',calls=calls,elapsed_seconds=time.monotonic()-start,match_reached=False),indent=2)+'\n')
finally:
 executor.shutdown(wait=True)
 for c in clients:c.close()
