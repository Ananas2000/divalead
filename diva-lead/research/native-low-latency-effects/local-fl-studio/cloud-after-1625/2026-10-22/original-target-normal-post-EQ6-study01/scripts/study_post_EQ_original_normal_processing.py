"""Six ordinary zero-lookahead Stereo EQ bands AFTER current nonlinear chain.

Frozen actual primary outputs, two withheld native realizations; original-only
objective. Screen only: adoption requires latest-primary fresh6/cold2/fullZIP.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,json,os,queue,threading,traceback
import numpy as np,soundfile as sf
from win_vst3 import WinVST3,D
from native_chain import NativeChain
from fl20_curve import apply_candidate
A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=Path('/tmp/divalead-original-target-post-EQ6-20261025-01');ROOT.mkdir(exist_ok=False);STATE=N/'ORIGINAL_TARGET_NORMAL_POST_EQ6_SCREEN.json'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];assert prior['accepted_full_public_kit']=='ZL26'
for name,key in [('PRIMARY_FROZEN_FOR_TRAINING.bin','native_ZL_component_state'),('CONTROL_POST.bin','post_ZL_component_state')]:(ROOT/name).write_bytes(Path(prior[key]).read_bytes())
(ROOT/'PRIOR_FOR_TRAINING.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
f=FeaturesOriginal();reg=float(np.sum(np.array(seed['x'])[:28]**2))*.00000025;ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);np.testing.assert_array_equal(ref,a.REF);frequency=np.fft.rfftfreq(len(ref),1/48000);masks=[(frequency>=lo)&(frequency<hi)for lo,hi in [(300,800),(2000,5000),(5000,10000),(10000,14000)]]
def lr(y):
 p=abs(np.fft.rfft(y,axis=0))**2;return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref)
def assess(y):
 r=f.residual(y);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));v=lr(edit);return dict(loss=float(r@r)+reg,assessment=f.local.last,LR_dB=v.tolist(),stereo_preservation_passed=bool(np.sqrt(np.mean((v[1:]-target[1:])**2))<=1.5 and max(abs(v[1:]))<=1.6 and abs(v[0]-target[0])<=3.35))
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def configure(c,x):
 c.load(ROOT/'CONTROL_POST.bin')
 if x is None:return
 for j in range(6):
  k=j+4;c.set(params['Filter Status'+str(k)],1);c.set(params['Filter Type'+str(k)],0);c.set(params['LRMode'+str(k)],0);c.set(params['Dynamic ON'+str(k)],0)
  for label,value in [('Gain',x[j]),('Freq',x[6+j]),('Q',x[12+j])]:c.text(params[label+str(k)],str(value))
clients=[];pool=queue.Queue();mutex=threading.Lock();rows=[]
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(ROOT),cases=len(rows),actual_post_ZL_hosts=[c.child.pid for c in clients],six_normal_static_EQ_bands_only=True,original_is_the_only_target=True,v83_Finish_not_used=True,only_three_held_notes=True,main_matcher_not_stopped=True,not_adopted=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def evaluate(case,phase=0,keep=True):
 label,x=case;c=pool.get()
 try:
  configure(c,x);y,_=c.render(input_file=ROOT/f'primary-{phase}.f32');r=dict(label=label,x=x,**assess(y));assert c.latency()==0
  if keep:
   with mutex:rows.append(r)
  return r
 finally:pool.put(c)
try:
 record('capture_three_new_native_and_frozen_primary_inputs')
 c=NativeChain(seed['source_manifest']['native_input'],'OriginalPostEQ-training-native',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 p=WinVST3('OriginalPostEQ-training-primary')
 try:
  for k in range(3):
   raw,_=c.render();p.load(ROOT/'PRIMARY_FROZEN_FOR_TRAINING.bin');y,_=p.render(raw);y.astype('<f4').tofile(ROOT/f'primary-{k}.f32');sf.write(ROOT/f'TRAINING_PRIMARY_{k}.wav',y,48000,subtype='FLOAT')
 finally:c.close();p.close()
 for k in range(2):c=WinVST3('OriginalPostEQ-worker-'+str(k));clients.append(c);pool.put(c)
 baseline=evaluate(('unchanged-full26-control',None));x=[0.]*6+[110.,220.,440.,880.,1760.,3520.]+[.7]*6;current=evaluate(('active-zero-gain-control',x));assert abs(current['loss']-baseline['loss'])<1e-6,(current['loss'],baseline['loss'])
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for sweep in range(2):
   for j in range(6):
    cases=[]
    for delta in [-.8,-.4,.4,.8]:v=list(current['x']);v[j]=float(np.clip(v[j]+delta/(sweep+1),-4,4));cases.append((f'gain-{sweep}-{j}-{delta}',v))
    checked=list(executor.map(evaluate,cases));valid=[r for r in checked if r['stereo_preservation_passed']]
    if valid and min(valid,key=lambda r:r['loss'])['loss']<current['loss']:current=min(valid,key=lambda r:r['loss'])
    record('actual_normal_post_EQ_gain_fit',control_loss=baseline['loss'],best_loss=current['loss'],best_gains=current['x'][:6])
  for j in range(6):
   for offset,step,lo,hi in [(6,.22,35,12000),(12,.4,.2,6)]:
    cases=[]
    for factor in [-1,1]:v=list(current['x']);v[offset+j]=float(np.clip(v[offset+j]*2**(factor*step),lo,hi));cases.append((f'shape-{offset}-{j}-{factor}',v))
    checked=list(executor.map(evaluate,cases));valid=[r for r in checked if r['stereo_preservation_passed']]
    if valid and min(valid,key=lambda r:r['loss'])['loss']<current['loss']:current=min(valid,key=lambda r:r['loss'])
   record('actual_normal_post_EQ_frequency_Q_fit',control_loss=baseline['loss'],best_loss=current['loss'])
 held=[]
 for k in [1,2]:held.append(dict(control=evaluate(('heldout-control',None),k,False),candidate=evaluate(('heldout-candidate',current['x']),k,False)))
 configure(clients[0],current['x']);clients[0].save(ROOT/'CANDIDATE_POST_RESEARCH_ONLY.bin');clients[0].dump(ROOT/'ACTUAL_POST_PARAMETERS.tsv');out,_=clients[0].render(input_file=ROOT/'primary-0.f32');sf.write(ROOT/'SELECTED_TRAINING_WIP.wav',out,48000,subtype='FLOAT')
 s=dict(training_cases=len(rows),training_control=baseline,training_candidate=current,heldout=held,sufficient_screen=bool(baseline['loss']-current['loss']>.0003 and all(r['control']['loss']-r['candidate']['loss']>.0001 and r['candidate']['stereo_preservation_passed']for r in held)),not_adopted=True,requires_latest_main_context_fresh6_cold2_full_ZIP=True,original_is_the_only_target=True,v83_Finish_not_used=True,reference_match_reached=False)
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'completion.json').write_text(json.dumps(s,indent=2)+'\n');record('finite_normal_post_EQ_screen_complete',sufficient_screen=s['sufficient_screen'],training_gain=baseline['loss']-current['loss']);print(json.dumps(dict(sufficient_screen=s['sufficient_screen'],training_control=baseline['loss'],training_candidate=current['loss'],heldout_gains=[r['control']['loss']-r['candidate']['loss']for r in held])),flush=True)
except BaseException:record('failed_preserve_full26_and_live_main',error=traceback.format_exc());raise
finally:
 for c in clients:c.close()
