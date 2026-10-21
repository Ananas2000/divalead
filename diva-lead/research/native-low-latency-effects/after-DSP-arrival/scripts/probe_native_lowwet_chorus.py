"""Real native Chorus search, scored over several free-running LFO realizations.

The source stays the verified v83 three-held Diva performance. Off-harmonic
signed errors show missing diffuse energy, so an extra low-pass is not assumed
to be a denoising improvement. No exact FST-audio repeatability is claimed.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time
import numpy as np
from scipy.stats import qmc
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(W/'lowwet-chorus-isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target

ROOT=W/'native-lowwet-chorus-grid';ROOT.mkdir(exist_ok=False)
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];mutex=threading.Lock();rows=[];best=float('inf');start=time.monotonic()
target_rms=float(np.sqrt(np.mean(target.astype(float)**2)))
def native_settings(spec):
    return {0:int(round((spec['delay_ms']-.05)/29.95*1024)),1:int(round(spec['depth_ms']*1000)),2:int(round(spec['stereo_degrees']/180*1024)),
            3:int(round(5000*np.sqrt(spec['rate_Hz']/5))),4:int(round(5000*np.sqrt(spec['rate_Hz']/5))),5:int(round(5000*np.sqrt(spec['rate_Hz']/5))),
            6:0,7:0,8:0,9:0,10:int(round((69+12*np.log2(spec['cutoff_Hz']/440))/127*5000)),11:0}
def configure(c,x,spec):
    apply(c,x)
    if spec is None:return
    c.bypass(3,False);c.gain(0,1-spec['mix']);c.gain(1,spec['mix'])
    for p,v in native_settings(spec).items():c.set(3,p,v)
def evaluate(spec):
    global best
    c=pool.get()
    try:
        fitted=x.copy();configure(c,fitted,spec)
        if spec is not None:
            raw,_=c.render();rms=float(np.sqrt(np.mean(raw[:len(target)].astype(float)**2)))
            # Real native EQ gain adjustment, recorded in the preset vector.
            fitted[28:30]=np.clip(fitted[28:30]+10*np.log10(target_rms/rms),-18,18)
            configure(c,fitted,spec)
        captures=[]
        for rep in range(3):
            y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(fitted[:28]**2))*.00000025
            captures.append(dict(loss=loss,assessment=features.local.last,audio=y,status=status))
        values=[v['loss'] for v in captures];mean=float(np.mean(values));std=float(np.std(values));median=sorted(captures,key=lambda q:q['loss'])[1]
        row=dict(chorus=spec,chorus_raw_parameters=native_settings(spec) if spec else None,x=fitted.tolist(),selection_loss=mean,loss=mean,realization_losses=values,realization_standard_deviation=std,recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],native_status=median['status'],peak=float(abs(median['audio']).max()),native_DLL_audio=True,only_three_held_notes=True,free_running_LFO_not_sample_exact=spec is not None,strict_waveform_match=False,original_reference_match_reached=False,comparison_uses_three_actual_renders=True)
        with mutex:
            rows.append(row)
            if mean<best:
                best=mean;(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',median['audio'],48000,subtype='FLOAT')
                print('MODULATED_NATIVE_CHORUS_BEST',mean,std,spec,flush=True)
        return row
    finally:pool.put(c)

lhs=qmc.LatinHypercube(d=6,seed=830321).random(72)
specs=[]
for v in lhs:
    specs.append(dict(delay_ms=3+17*v[0],depth_ms=.4+4.6*v[1],stereo_degrees=20+150*v[2],rate_Hz=.2+4.6*v[3],cutoff_Hz=float(80*(1800/80)**v[4]),mix=float(.001*(.3/.001)**v[5])))
for mix in [.002,.005,.01,.02,.04,.08,.16,.3]:
    for rate in [1.25,3.20017741865]:specs.append(dict(delay_ms=6.969077558,depth_ms=5.,stereo_degrees=90,rate_Hz=rate,cutoff_Hz=912.332687,mix=mix))
with four_native_slots(ROOT) as parent:
    base=json.loads((Path(parent['search_root'])/'best.json').read_text());x=np.array(base['x']);assert len(x)==86
    (ROOT/'frozen-parent.json').write_text(json.dumps(base,indent=2)+'\n')
    try:
        for i in range(4):
            c=NativeChain(W/'native-frozen-source-with-tail.wav',f'lowwet-native-chorus-{i}',fl_graph=True);clients.append(c);pool.put(c)
        baseline=evaluate(None)
        with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,specs))
    finally:
        for c in clients:c.close()
rows.sort(key=lambda v:v['loss']);(ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),actual_scored_renders=3*len(rows),elapsed_seconds=time.monotonic()-start,baseline_loss=baseline['loss'],best_loss=best,match_reached=False,free_LFO_captures_not_certified_as_exactly_reproducible=True),indent=2)+'\n')
print('ACTUAL_MODULATED_NATIVE_CHORUS_COMPLETE',best,flush=True)
