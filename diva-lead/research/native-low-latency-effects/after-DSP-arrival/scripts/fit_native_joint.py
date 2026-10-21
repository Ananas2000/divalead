"""Actual FL native DLL fit, frozen three-note Diva input, v83 migration target.

Internal gain coordinates are raw/100, NOT claimed to be UI decibels.
Native states, not Python filters, perform the audio processing.
"""
from pathlib import Path
import concurrent.futures,datetime,json,queue,struct,threading,time,sys
import numpy as np
from scipy.optimize import least_squares
import soundfile as sf
from native_chain import NativeChain,W
from native_features import Features,target

ROOT=W/'joint-stock-distinct-phase-fit';ROOT.mkdir(exist_ok=True)
base=json.loads((W/'linear-stock-fit/best.json').read_text())
old=np.asarray(base['x']);freqs=np.array([40,65,100,160,250,400,630,1000,1600,2500,4000,6300,10000,16000],float)
# EQ2 Main is dB*100. The earlier single-channel M/S calibration measured the
# combined dry Side + amplified Mid, rather than an intrinsic EQ2 gain curve.
branchraw=[(old[28]+old[k])/2 for k in [29,30]]
initial=np.r_[old[:28],branchraw,old[31:35],np.zeros(28),np.full(14,25412/65536),[0.,0.]]
if len(sys.argv)>1:initial=np.array(json.loads(Path(sys.argv[1]).read_text())['x'])
if len(initial)==78:initial=np.r_[initial,[0.,0.]]
lower=np.r_[np.full(28,-18.),np.full(2,-18.),np.full(4,-1.),np.full(28,-.48),np.full(14,.08),[-.6,-.35]]
upper=np.r_[np.full(28,18.),np.full(2,18.),np.full(4,1.),np.full(28,.48),np.full(14,.85),[.35,.5]]
steps=np.r_[np.full(30,.04),np.full(4,.002),np.full(28,.006),np.full(14,.005),[.02,.02]]
lower=np.r_[lower,[-2.,-4.]];upper=np.r_[upper,[2.,4.]];steps=np.r_[steps,[.006,.02]]
scales=np.r_[np.full(30,6.),np.full(4,.5),np.full(28,.25),np.full(14,.2),[.2,.2,.5,1.]]
assert len(initial)==len(lower)==80
template=(W/'Fruity_WaveShaper_x64-default-state.bin').read_bytes()
def curve_bytes(c3,c5):
    n=129;header=bytearray(template[:34]);struct.pack_into('<I',header,30,n)
    data=bytearray(header)
    for i,u in enumerate(np.linspace(0,1,n)):
        y=np.clip(u+c3*u**3+c5*u**5,0,1)
        data.extend(struct.pack('<ddfI',0 if i==0 else 1/128,float(y),0.,0 if i==0 else 0x02000000))
    return bytes(data)+template[82:]

features=Features(target);pool=queue.Queue();clients=[]
for i in range(4):
    c=NativeChain(W/'native-frozen-source-with-tail.wav',f'joint-stock-distinct-{i}',fl_graph=True);c.curvepath=W/f'joint-stock-distinct-{i}-curve.bin';clients.append(c)
    for n in [1,2,3,9]:c.bypass(n,True)
    for node in [4,5,6,7]:
        for band in range(7):c.set(node,21+band,6);c.set(node,28+band,0)
    for k,v in enumerate([1,0,1,1,1]):c.gain(k,v)
    pool.put(c)

def apply(c,x):
    c.curvepath.write_bytes(curve_bytes(*x[76:78]));c.load_state(0,c.curvepath)
    for node,offset in [(4,0),(5,7),(6,14),(7,21)]:
        f=freqs[offset%14:offset%14+7]*2**x[34+offset:34+offset+7]
        raw=np.rint(np.log(np.clip(f,20,20000)/20)/np.log(1000)*65536).astype(int)
        for band in range(7):
            c.set(node,band,int(round(x[offset+band]*100)))
            c.set(node,7+band,int(raw[band]));c.set(node,14+band,int(round(x[62+(offset+band)%14]*65536)))
        c.set(node,35,int(round(x[28+(offset>=14)]*100)))
    for i in range(4):c.set(8,i,int(round(x[30+i]*12800)))
    c.set(8,4,int(round(x[78]*1000)));c.set(8,5,int(round(x[79]*1000)))

best=float('inf');calls=0;mutex=threading.Lock();start=time.monotonic();history=[]
def evaluate(x,save=True):
    global best,calls
    c=pool.get()
    try:
        apply(c,x);full,status=c.render();r=features.residual(full[:len(target)])
        r=np.r_[r,x[:28]*.0005,x[28:30]*.0002,x[34:62]*.001]
        loss=float(r@r)
        with mutex:
            calls+=1
            if save and loss<best:
                best=loss;row=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),loss=loss,calls=calls,seconds=time.monotonic()-start,x=np.asarray(x).tolist(),native_status=status,peak=float(abs(full).max()),native_DLL_audio=True,declared_native_latency_frames=0,strict_waveform_match=False,original_reference_match_reached=False,internal_gain_coordinates='raw / 100; not UI dB',source='unchanged v83 Diva three-held-note source')
                history.append(row);sf.write(ROOT/'best-with-tail.wav',full,48000,subtype='FLOAT')
                (ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');(ROOT/'history.json').write_text(json.dumps(history,indent=2)+'\n')
                print('NATIVE_JOINT_BEST',json.dumps({k:row[k] for k in ['loss','calls','seconds','peak']}),flush=True)
        return r
    finally:pool.put(c)

executor=concurrent.futures.ThreadPoolExecutor(4)
def jacobian(x):
    center=evaluate(x,False)
    def column(i):
        step=steps[i] if x[i]+steps[i]<=upper[i] else -steps[i]
        changed=x.copy();changed[i]+=step
        return (evaluate(changed,False)-center)/step
    return np.column_stack(list(executor.map(column,range(len(x)))))

try:
    evaluate(initial)
    fit=least_squares(evaluate,initial,jac=jacobian,bounds=(lower,upper),max_nfev=120,x_scale=scales,ftol=1e-8,xtol=1e-8,gtol=1e-6)
    (ROOT/'optimizer-result.json').write_text(json.dumps(dict(success=bool(fit.success),message=fit.message,nfev=fit.nfev,njev=fit.njev,optimality=float(fit.optimality),total_calls=calls,elapsed_seconds=time.monotonic()-start),indent=2)+'\n')
finally:
    executor.shutdown(wait=True)
    for c in clients:c.close()
