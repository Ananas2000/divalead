"""New native SUM matrix hypothesis in the fixed full25 two-ZL context.

Only four native Stereo Shaper coefficients vary. Actual DLL/VST3 DSP,
three independently captured training prefixes; cold full-chain/state proof
and the existing original criterion remain mandatory. Research only.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,os,queue,tarfile,threading,traceback
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=Path('/tmp/divalead-native-SUM-matrix-after25-20261025-01');ROOT.mkdir(exist_ok=False)
STATE=N/'NATIVE_SUM_MATRIX_AFTER25_FINITE_STUDY.json'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];origin=np.array(seed['x']);assert prior['full_public_kit_directory']=='ZL-WIP25'
manifest=seed['native_saved_state_bundle'];BASE=Path(manifest['directory']);nodes=[r['node']for r in manifest['manifest']]
for name,key in [('PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(ROOT/name).write_bytes(Path(prior[key]).read_bytes())
(ROOT/'PRIOR_SNAPSHOT_RESEARCH_ONLY.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
f=FeaturesOriginal();reg=float(np.sum(origin[:28]**2))*.00000025
reference,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);freq=np.fft.rfftfreq(len(reference),1/48000)
masks=[(freq>=lo)&(freq<hi)for lo,hi in [(40,300),(300,800),(800,2000),(2000,5000),(5000,10000),(10000,14000)]]
def lr(y):
 power=abs(np.fft.rfft(y,axis=0))**2
 return np.array([10*np.log10(power[m,0].sum()/power[m,1].sum())for m in masks])
target=lr(reference)
def assess(y):
 residual=f.residual(y[:288000]);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));balance=lr(edit);err=float(np.sqrt(np.mean((balance[3:]-target[3:])**2)));low=abs(float(balance[1]-target[1]))
 return dict(loss=float(residual@residual)+reg,assessment=f.local.last,LR_dB=balance.tolist(),upper_error=err,lowmid_error=low,stereo_preservation_passed=bool(err<=1.5 and np.max(abs(balance[3:]))<=1.6 and low<=3.35))
def full(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,origin,seed)
 for row in manifest['manifest']:
  p=BASE/row['state'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['state_SHA256'];c.load_state(row['node'],p)
 return c
def matrix(c,x):
 for j,value in enumerate(x):c.set(8,j,int(round(float(value)*12800)))
def quant(v):return np.round(np.clip(np.asarray(v,dtype=float),-1,1)*12800)/12800
def blob(y):
 stream=io.BytesIO();sf.write(stream,y,48000,format='WAV',subtype='FLOAT');return stream.getvalue()
def add(tar,name,y,items):
 b=blob(y);info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));items.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
clients=[];others=[];rows=[];pool=queue.Queue();mutex=threading.Lock()
def record(phase,**kw):
 state=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(ROOT),cases=len(rows),four_native_matrix_coefficients_only=True,real_native_hosts=[c.proc.pid for c,p,z in clients],real_ZL_hosts=[z.child.pid for c,p,z in clients]+[p.child.pid for c,p,z in clients],does_not_stop_or_adopt_main_matcher=True,full_reference_match=False,actual_FL_GUI_validation_pending=True,**kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(STATE)
def evaluate(case,phase=0,keep=True):
 label,x=case;x=quant(x);c,p,z=pool.get()
 try:
  c.load_input(ROOT/f'prefix-{phase}.wav');matrix(c,x);raw,status=c.render();p.load(ROOT/'PRIMARY.bin');z.load(ROOT/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);row=dict(label=label,matrix=x.tolist(),**assess(out));assert p.latency()+z.latency()==0
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put((c,p,z))
try:
 record('actual_native_prefix_generation_and_canonical_routing_check')
 prefix=full('ST25-SUM-training-prefix');control=full('ST25-SUM-zero-depth-control');others.extend([prefix,control]);prefix.bypass(8,True);train_items=[]
 with tarfile.open(ROOT/'THREE_TRAINING_PREFIX_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
  for k in range(3):
   y,_=prefix.render();sf.write(ROOT/f'prefix-{k}.wav',y,48000,subtype='FLOAT');add(tar,f'prefix-{k}.wav',y,train_items)
 prefix.set(3,1,0);zero_prefix,_=prefix.render();sf.write(ROOT/'prefix-3.wav',zero_prefix,48000,subtype='FLOAT');control.set(3,1,0);zero_control,_=control.render()
 prefix.close();control.close();others.clear()
 for k in range(2):
  c=NativeChain(ROOT/'prefix-0.wav','ST25-SUM-matrix-worker-'+str(k),fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
  for node in range(15):c.bypass(node,node!=8)
  for j,value in enumerate([1,0,1,1,0]):c.gain(j,value)
  # Preserve all native SUM parameters beyond the four measured controls.
  saved=next(row for row in manifest['manifest']if row['node']==8);c.load_state(8,BASE/saved['state'])
  p=WinVST3('ST25-SUM-matrix-primary-'+str(k));z=WinVST3('ST25-SUM-matrix-post-'+str(k));clients.append((c,p,z));pool.put((c,p,z))
 c,p,z=clients[0];c.load_input(ROOT/'prefix-3.wav');matrix(c,origin[30:34]);zero_again,_=c.render();routing_error=float(abs(zero_again-zero_control).max());assert routing_error<=2e-7,('canonical routing failed',routing_error)
 (ROOT/'ACTUAL_PREFIX_ROUTING_PROOF.json').write_text(json.dumps(dict(zero_depth_prefix_replay_vs_actual_complete_native_max_abs_error=routing_error,unchanged_absolute_tolerance=2e-7,no_Python_simulated_DSP=True,real_native_SUM_matrix_only=True,training_audio_members=train_items),indent=2)+'\n')
 baseline=evaluate(('current-confirmed-matrix',origin[30:34]));current=baseline;rng=np.random.default_rng(2026102502)
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for sweep in range(4):
   cases=[];step=.018*(.65**sweep)
   for j in range(24):cases.append((f'coupled-{sweep}-{j}',np.array(current['matrix'])+rng.normal(size=4)*step*float(rng.choice([.5,1,2]))))
   checked=list(executor.map(evaluate,cases));allowed=[r for r in checked if r['stereo_preservation_passed']]
   if allowed and min(allowed,key=lambda r:r['loss'])['loss']<current['loss']:current=min(allowed,key=lambda r:r['loss'])
   for j in rng.permutation(4):
    cases=[]
    for factor in [-2,-1,1,2]:v=np.array(current['matrix']);v[j]+=factor*step;cases.append((f'axis-{sweep}-{j}-{factor}',v))
    checked=list(executor.map(evaluate,cases));allowed=[r for r in checked if r['stereo_preservation_passed']]
    if allowed and min(allowed,key=lambda r:r['loss'])['loss']<current['loss']:current=min(allowed,key=lambda r:r['loss'])
   record('actual_native_SUM_matrix_fit',sweep=sweep,control_loss=baseline['loss'],best_loss=current['loss'],matrix=current['matrix'])
 held=[]
 for k in [1,2]:held.append(dict(control=evaluate(('heldout-control',origin[30:34]),k,False),candidate=evaluate(('heldout-candidate',current['matrix']),k,False)))
 chosen=quant(current['matrix']);(ROOT/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),matrix=chosen.tolist(),primary_SHA256=hashlib.sha256((ROOT/'PRIMARY.bin').read_bytes()).hexdigest(),post_SHA256=hashlib.sha256((ROOT/'POST.bin').read_bytes()).hexdigest(),not_adopted=True),indent=2)+'\n')
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'HELDOUT.json').write_text(json.dumps(held,indent=2)+'\n')
 ready=bool(baseline['loss']-current['loss']>.0003 and all(r['control']['loss']-r['candidate']['loss']>.0001 and r['candidate']['stereo_preservation_passed']for r in held))
 summary=dict(training_cases=len(rows),training_control=baseline,training_candidate=current,heldout_positive=all(r['control']['loss']>r['candidate']['loss']for r in held),sufficient_training=ready,robust_improvement=False,only_four_native_SUM_coefficients_varied=True,source_native_other11_and_both_ZL_components_unchanged=True,actual_FL_GUI_validation_pending=True,not_adopted=True,full_reference_match=False,requires_latest_main_context_revalidation_before_adoption=True)
 if ready:
  record('eight_NEW_prefix_paired_full_chain_realizations_six_plus_two_cold')
  prefix=full('ST25-SUM-independent-prefix');prefix.bypass(8,True);others.append(prefix);c0,p0,z0=clients[0];c1,p1,z1=clients[1];captures=[];items=[]
  with tarfile.open(ROOT/'NEW_EIGHT_PREFIX_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(8):
    if rep in [6,7]:prefix.close();others.remove(prefix);prefix=full('ST25-SUM-cold-prefix-'+str(rep));prefix.bypass(8,True);others.append(prefix)
    shared,status=prefix.render();sf.write(ROOT/'fresh-shared-prefix.wav',shared,48000,subtype='FLOAT');pair=[]
    for c,p,z,x in [(c0,p0,z0,origin[30:34]),(c1,p1,z1,chosen)]:
     c.load_input(ROOT/'fresh-shared-prefix.wav');matrix(c,x);raw,_=c.render();p.load(ROOT/'PRIMARY.bin');z.load(ROOT/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);pair.append((raw,out,assess(out)))
    captures.append(dict(rep=rep,control=pair[0][2],candidate=pair[1][2],improvement=pair[0][2]['loss']-pair[1][2]['loss']))
    for label,y in [('shared-prefix',shared),('native-control',pair[0][0]),('native-candidate',pair[1][0]),('control',pair[0][1]),('candidate',pair[1][1])]:add(tar,f'{label}-{rep}.wav',y,items)
    if rep==0:
     for label,y in [('SHARED_PREFIX',shared),('NATIVE_CONTROL',pair[0][0]),('NATIVE_CANDIDATE',pair[1][0]),('CONTROL',pair[0][1]),('CANDIDATE',pair[1][1])]:sf.write(ROOT/(label+'_00.wav'),y,48000,subtype='FLOAT')
  c1.save_state(8,ROOT/'CANDIDATE_SUM_STATE.bin');c1.save_state(8,ROOT/'CANDIDATE_SUM_RESAVED.bin');assert(ROOT/'CANDIDATE_SUM_STATE.bin').read_bytes()==(ROOT/'CANDIDATE_SUM_RESAVED.bin').read_bytes()
  delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  # Independent complete native chain proves that training-prefix routing and
  # the actual single saved SUM state transfer to the real canonical graph.
  canonical=full('ST25-SUM-independent-canonical-state');others.append(canonical);canonical.load_state(8,ROOT/'CANDIDATE_SUM_STATE.bin');canonical.save_state(8,ROOT/'CANDIDATE_SUM_CANONICAL_RESAVED.bin');assert(ROOT/'CANDIDATE_SUM_STATE.bin').read_bytes()==(ROOT/'CANDIDATE_SUM_CANONICAL_RESAVED.bin').read_bytes();canonical.set(3,1,0);expected,_=canonical.render()
  zero_prefix=full('ST25-SUM-independent-zero-prefix');others.append(zero_prefix);zero_prefix.bypass(8,True);zero_prefix.set(3,1,0);raw,_=zero_prefix.render();sf.write(ROOT/'fresh-shared-prefix.wav',raw,48000,subtype='FLOAT');c1.load_input(ROOT/'fresh-shared-prefix.wav');matrix(c1,chosen);again,_=c1.render();canonical_error=float(abs(again-expected).max());assert canonical_error<=2e-7,canonical_error
  x=origin.copy();x[30:34]=chosen;new_seed=dict(seed,x=x.tolist(),native_saved_state_bundle=None);assert np.array_equal(x[:30],origin[:30])and np.array_equal(x[34:],origin[34:])
  (ROOT/'NATIVE_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(new_seed,indent=2)+'\n')
  summary.update(captures=captures,archive_members=items,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,actual_saved_SUM_state_roundtrip_exact=True,independent_complete_native_zero_depth_state_replay_max_abs_error=canonical_error)
  with tarfile.open(ROOT/'NEW_EIGHT_PREFIX_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in items:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
 with tarfile.open(ROOT/'THREE_TRAINING_PREFIX_WAVs.tar.gz')as tar:
  for item in train_items:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_SUM_matrix_study_complete_research_only',robust_improvement=summary['robust_improvement'],training_gain=baseline['loss']-current['loss'],sufficient_training=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['training_control','training_candidate','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_main_and_all_previous_full_kits',error=traceback.format_exc());raise
finally:
 for c in others:c.close()
 for c,p,z in clients:c.close();p.close();z.close()
