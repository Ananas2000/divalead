"""Tune the two existing stock Stereo Shapers independently, with real repeats."""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-independent-phase-screen-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
features=FeaturesOriginal(target);clients=[];pool=queue.Queue();mutex=threading.Lock();rows=[];best=float('inf');start=time.monotonic()
def evaluate(pair,reps=3,save=True):
 global best
 right,left=pair;c=pool.get()
 try:
  apply(c,x);c.set(13,5,right);c.set(14,5,-left);captures=[]
  for i in range(reps):
   y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025;captures.append(dict(loss=loss,audio=y,status=status,assessment=features.local.last))
  captures.sort(key=lambda v:v['loss']);chosen=captures[len(captures)//2];mean=float(np.mean([v['loss'] for v in captures]));std=float(np.std([v['loss'] for v in captures]));row=dict(x=[*x[:94],right,left],right_phase_raw=right,left_phase_raw=left,loss=mean,realization_standard_deviation=std,realization_losses=[v['loss'] for v in captures],recorded_render_loss=chosen['loss'],original_reference_assessment=chosen['assessment'],native_status=chosen['status'],source_manifest=seed['source_manifest'],only_three_held_notes=True,actual_native_DLL_audio=True,not_yet_supported_as_public_96_parameter_kit=True,reference_match_reached=False)
  with mutex:
   rows.append(row)
   if save and mean<best:
    best=mean;(ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',chosen['audio'],48000,subtype='FLOAT');print('NATIVE_INDEPENDENT_PHASE_BEST',right,left,mean,chosen['assessment']['metrics']['stereo_phase'],flush=True)
  return row,chosen['audio']
 finally:pool.put(c)
with four_native_slots(ROOT) as state:
 seed=json.loads(Path(state['best_candidate']).read_text());x=np.array(seed['x']);assert len(x)==95 and seed['source_manifest'];source=Path(seed['source_manifest']['native_input']);(ROOT/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
 try:
  for i in range(4):
   c=NativeChain(source,f'independent-phase-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_common_phase_host.exe');clients.append(c);pool.put(c)
  center=int(round(x[94]));control,control_audio=evaluate((center,center),6)
  values=sorted(set(int(np.clip(center+step,0,4096)) for step in [-400,-200,-100,-50,0,50,100,200,400]));trials=[(a,b) for a in values for b in values]
  for raw in [0,400,800,1200,1800,2400,3200,4000]:trials.extend([(raw,center),(center,raw)])
  with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,trials))
  candidate=json.loads((ROOT/'best.json').read_text());result,audio=evaluate((candidate['right_phase_raw'],candidate['left_phase_raw']),6,False)
  uncertainty=float(np.hypot(control['realization_standard_deviation'],result['realization_standard_deviation'])/np.sqrt(6));robust=control['loss']-result['loss']>max(.0005,3*uncertainty)
  result.update(robust_improvement=robust,seed_fresh_mean_loss=control['loss'],standard_error_of_mean_difference=uncertainty,full_fresh_native_realizations=6)
  (ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n');sf.write(ROOT/'best-validated-with-tail.wav',audio,48000,subtype='FLOAT');(ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n');(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),seconds=time.monotonic()-start,control_loss=control['loss'],candidate_loss=result['loss'],robust_improvement=robust,reference_match_reached=False),indent=2)+'\n');print('INDEPENDENT_PHASE_FRESH_VALIDATION_COMPLETE',result['loss'],robust,flush=True)
 finally:
  for c in clients:c.close()
