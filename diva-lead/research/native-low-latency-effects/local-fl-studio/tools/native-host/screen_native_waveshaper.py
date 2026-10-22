"""Search native WaveShaper point states against unchanged reference criteria."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,time,threading,queue,concurrent.futures,sys,struct
import numpy as np,soundfile as sf
from local_native_chain import NativeChain,SESSION,ROOT
OUT=SESSION/'waveshaper-screen';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tw=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
template=(ROOT/'divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP/verification/SOURCE_WaveShaper.bin').read_bytes()
assert len(template)==3154 and struct.unpack_from('<I',template,30)[0]==129
def curve_bytes(c1,c3,c5):
    data=bytearray(template[:34])
    for i,u in enumerate(np.linspace(0,1,129)):
        y=np.float32(np.clip(c1*u+c3*u**3+c5*u**5,0,1))
        data.extend(struct.pack('<ddfI',0 if i==0 else 1/128,float(y),0.,0 if i==0 else 0x02000000))
    return bytes(data)+template[34+129*24:]
assert curve_bytes(1,.75,-.35)==template,'Baseline serialization mismatch'
start=time.monotonic();pool=queue.Queue();clients=[];lock=threading.Lock();results=[];best=1e9
for k in range(4):
    c=NativeChain(SESSION/'renders/DIVA_FRESH_DIRECT.wav',f'WAVESHAPER_{k}');c.checkpoint();c.label=f'worker-{k}';c.curvepath=OUT/(c.label+'.bin');clients.append(c);pool.put(c)
trials=[(f'baseline-{k}',(1,.75,-.35))for k in range(6)]
trials += [(f'c{j}',(c1,c3,c5))for j,(c1,c3,c5)in enumerate((a,b,c)for a in(.5,.75,1,1.3,1.7)for b in(-3,-1,0,.75,1.5,3,6)for c in(-4,-2,-.35,0,1,3))]
def evaluate(trial):
    global best
    tag,p=trial;c=pool.get()
    try:
        c.checkpoint();c.curvepath.write_bytes(curve_bytes(*p));c.load_state(0,c.curvepath)
        y,status=c.render();edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));path=OUT/(c.label+'.wav');sf.write(path,edit,48000,subtype='FLOAT')
        s=a.score(dict(id=c.label,canonical_path=str(path),aliases=[]));m=s['metrics'];standard=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tw[k]*m[k]/scales[k]for k in tw);gain=s['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max());loss=.65*tone+.35*standard+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        row=dict(tag=tag,coefficients=p,loss=loss,score=standard,tone_score=tone,peak=peak,metrics=m,gain_for_AB=gain,seconds=time.monotonic()-start,native_status=status,match_reached=False)
        (OUT/(tag+'.json')).write_text(json.dumps(row,indent=2))
        with lock:
            results.append(row);(OUT/'ranking.json').write_text(json.dumps(sorted(results,key=lambda r:r['loss']),indent=2))
            if loss<best:
                best=loss;sf.write(OUT/'BEST.wav',y,48000,subtype='FLOAT');c.save_state(0,OUT/'BEST_WAVESHAPER.bin');(OUT/'BEST.json').write_text(json.dumps(row,indent=2));print('BEST',json.dumps({k:row[k]for k in('tag','loss','score','tone_score','coefficients')}),flush=True)
            if len(results)%40==0:print('PROGRESS',len(results),time.monotonic()-start,flush=True)
        return row
    finally:pool.put(c)
try:
    with concurrent.futures.ThreadPoolExecutor(4)as e:list(e.map(evaluate,trials))
finally:
    for c in clients:c.close()
print('COMPLETE',len(results),time.monotonic()-start,flush=True)
