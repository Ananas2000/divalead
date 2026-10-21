"""Two genuine Stereo Shapers rotate both channels identically; real DLL only."""
from pathlib import Path
import concurrent.futures,json,os,queue,threading,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-common-phase-pair-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
features=FeaturesOriginal(target);pool=queue.Queue();clients=[];rows=[];mutex=threading.Lock();start=time.monotonic()
base=json.loads(Path('/workspace/divalead-work/native-low-latency-effects/NATIVE_RESTORED_ACCEPTED_SEED.json').read_text());models={'v83-frozen':base}
pw=W/'native-Diva-PW-depth1-EQ-refit-01/full-validated-candidate.json'
if pw.is_file():models['PW-keyfollow-1']=json.loads(pw.read_text())
def configure(c,x,raw):
 apply(c,x)
 for node,value in [(13,raw),(14,-raw)]:
  for i,v in enumerate([0,12800,12800,0,0,int(value)]):c.set(node,i,v)
def evaluate(case):
 model,raw=case;choice=models[model];x=np.array(choice['x']);c=pool.get()
 try:
  source=Path(choice.get('source_manifest',{}).get('native_input',str(W/'native-frozen-source-with-tail.wav')));c.load_input(source);configure(c,x,raw);captures=[]
  for rep in range(3):
   y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025;captures.append(dict(loss=loss,audio=y,status=status,assessment=features.local.last))
  captures.sort(key=lambda v:v['loss']);chosen=captures[1];mean=float(np.mean([r['loss'] for r in captures]));std=float(np.std([r['loss'] for r in captures]))
  row=dict(model=model,x=x.tolist(),common_phase_raw=raw,loss=mean,realization_standard_deviation=std,realization_losses=[r['loss'] for r in captures],recorded_render_loss=chosen['loss'],original_reference_assessment=chosen['assessment'],native_status=chosen['status'],only_three_held_notes=True,actual_native_common_allpass_DLLs=True,reference_match_reached=False,source_manifest=choice.get('source_manifest'))
  with mutex:
   rows.append(row);prior=min((r['loss'] for r in rows[:-1]),default=float('inf'))
   if mean<prior:
    (ROOT/'best.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',chosen['audio'],48000,subtype='FLOAT');print('NATIVE_COMMON_PHASE_BEST',model,raw,mean,chosen['assessment']['metrics']['relative_phase'],flush=True)
  return row
 finally:pool.put(c)
with four_native_slots(ROOT):
 # A non-modulated identity-pair control proves the extra mixer routing.
 x=np.array(base['x']);a=NativeChain(W/'native-frozen-source-with-tail.wav','common-phase-control-existing',fl_graph=True,engine_override='fl_native_chorus_verified_host.exe');b=NativeChain(W/'native-frozen-source-with-tail.wav','common-phase-control-new',fl_graph=True,phase_pair=True,engine_override='fl_native_common_phase_host.exe')
 try:
  apply(a,x);configure(b,x,0);a.set(3,1,0);b.set(3,1,0);y,_=a.render();z,_=b.render();err=float(abs(y-z).max());assert err<=2e-7,err
 finally:a.close();b.close()
 try:
  for i in range(4):
   c=NativeChain(W/'native-frozen-source-with-tail.wav',f'native-common-phase-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_common_phase_host.exe');clients.append(c);pool.put(c)
  cases=[(model,raw) for model in models for raw in [0,1,2,3,5,8,12,20,32,50,80,128,200,320,512,800,1200,1800,2600,3400,4000]]
  with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,cases))
 finally:
  for c in clients:c.close()
rows.sort(key=lambda v:v['loss']);(ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n');(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),actual_scored_renders=3*len(rows),seconds=time.monotonic()-start,identity_pair_zero_depth_max_abs=err,best_model=rows[0]['model'],best_common_phase_raw=rows[0]['common_phase_raw'],best_loss=rows[0]['loss'],match_reached=False),indent=2)+'\n');print('COMMON_PHASE_PAIR_SCREEN_COMPLETE',rows[0]['loss'],flush=True)
