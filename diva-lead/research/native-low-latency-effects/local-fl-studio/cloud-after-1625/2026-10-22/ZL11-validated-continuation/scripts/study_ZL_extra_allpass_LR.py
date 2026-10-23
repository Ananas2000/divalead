"""Genuine causal phase-filter study after the existing native + ZL chain.
Separate research branch: never races the running matcher's BEST file.
"""
from pathlib import Path
import concurrent.futures,csv,gzip,hashlib,io,itertools,json,math,os,queue,struct,tarfile,threading,time,traceback
import numpy as np
import soundfile as sf
from win_vst3 import D,WinVST3
from native_chain import NativeChain
from fl20_curve import apply_candidate
ROOT=D/'ZL-extra-allpass-LR-after-ZL06-01';ROOT.mkdir(exist_ok=False)
N=Path('/workspace/divalead-work/native-low-latency-effects');STATE=N/'ZL_EXTRA_ALLPASS_LR_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
best=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=best['native_base'];base=ROOT/'BASE_ACCEPTED_COMPONENT.bin';base.write_bytes(Path(best['native_ZL_component_state']).read_bytes())
(ROOT/'BASE_ACCEPTED_CANDIDATE.json').write_text(json.dumps(best,indent=2)+'\n')
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def record(phase,**kw):
 p=STATE.with_suffix('.partial');p.write_text(json.dumps(dict(PID=os.getpid(),phase=phase,UTC=time.time(),root=str(ROOT),cases=len(rows),only_three_held_notes=True,original_reference_criterion_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw),indent=2)+'\n');p.replace(STATE)
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
 for k,v in seed['chorus_overrides'].items():c.set(3,int(k),int(v))
 return c
def score(y):
 a=features.residual(y[:288000]);return float(a@a)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025

def configure(c,bands):
 for k in [19,20]:
  b=bands[k-19]if k-19<len(bands)else None
  c.set(params['Filter Status'+str(k)],1 if b else 0)
  if b:
   c.set(params['Filter Type'+str(k)],.9);c.set(params['Order'+str(k)],1/6);c.set(params['LRMode'+str(k)],b['mode']/4);c.set(params['Dynamic ON'+str(k)],0)
   c.text(params['Freq'+str(k)],str(b['frequency']));c.text(params['Q'+str(k)],str(b['Q']))

def evaluate(case,phase=0,save=True):
 label,bands=case;c=pool.get()
 try:
  configure(c,bands);y,_=c.render(input_file=ROOT/f'frozen-{phase}.f32');assert c.latency()==0
  row=dict(label=label,bands=bands,loss=score(y),assessment=features.local.last)
  if save:
   with mutex:rows.append(row)
  return row
 finally:pool.put(c)
try:
 record('generating_three_actual_native_training_and_heldout_inputs')
 a=native('ZL-extra-allpass-LR-frozen-native')
 try:
  for phase in range(3):raw,_=a.render();raw.astype('<f4').tofile(ROOT/f'frozen-{phase}.f32')
 finally:a.close()
 for k in range(2):
  c=WinVST3('ZL-extra-allpass-LR-worker-'+str(k));clients.append(c);c.load(base);pool.put(c)
 baseline=evaluate(('unchanged-control',[]));grid=[]
 for f,q,m in itertools.product([150,300,600,1000,1600,2500,4000,6500,10500,15500],[.35,.7,1.4,2.8],[0,1,2,3,4]):grid.append((f'one-{f}-{q}-{m}',[dict(frequency=f,Q=q,mode=m)]))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for k,r in enumerate(executor.map(evaluate,grid)):
   if k%12==0:record('actual_one_extra_allpass_grid',best_training=min(t['loss']for t in rows))
  current=min(rows,key=lambda r:r['loss']);rng=np.random.default_rng(2026102327)
  cases=[]
  for k in range(128):
   b=dict(frequency=float(2**rng.uniform(math.log2(120),math.log2(16000))),Q=float(2**rng.uniform(-1.8,1.8)),mode=int(rng.choice([0,1,2,3,4])))
   cases.append((f'two-extra-{k}',current['bands'][:1]+[b]))
  for k,r in enumerate(executor.map(evaluate,cases)):
   if k%12==0:record('actual_two_extra_allpass_grid',best_training=min(t['loss']for t in rows))
  current=min(rows,key=lambda r:r['loss'])
  for sweep in range(3):
   for index in range(len(current['bands'])):
    for key,step,lo,hi in [('frequency',.18,100,18000),('Q',.22,.15,8)]:
     cases=[]
     for factor in [-2,-1,1,2]:
      bands=[dict(b)for b in current['bands']];bands[index][key]=float(np.clip(bands[index][key]*2**(factor*step/(sweep+1)),lo,hi));cases.append((f'fine-{sweep}-{index}-{key}-{factor}',bands))
     selected=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
     if selected['loss']<current['loss']:current=selected
     record('actual_extra_allpass_fine_fit',best_training=current['loss'])
 held=[]
 for row in [baseline,*sorted(rows,key=lambda r:r['loss'])[:4]]:
  checks=[evaluate(('heldout-'+row['label'],row['bands']),phase,False)for phase in [1,2]];held.append(dict(candidate=row,heldout=checks,mean=float(np.mean([row['loss'],*[x['loss']for x in checks]]))))
 selected=min(held,key=lambda r:r['mean'])['candidate'];(ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'heldout.json').write_text(json.dumps(held,indent=2)+'\n')
 # Validate against the latest accepted main-branch component, not the older
 # frozen training control. This remains a separate, non-adopted branch.
 latest=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());latest_state=ROOT/'LATEST_CONTROL_COMPONENT.bin';latest_state.write_bytes(Path(latest['native_ZL_component_state']).read_bytes())
 for c in clients:c.load(latest_state)
 control=clients[0];candidate=clients[1];configure(control,[]);configure(candidate,selected['bands']);component=ROOT/'CANDIDATE_COMPONENT.bin';candidate.save(component)
 # Check two genuinely new instances; hot-host history is not preset state.
 cold1=WinVST3('ZL-extra-allpass-LR-cold1');cold2=WinVST3('ZL-extra-allpass-LR-cold2')
 try:
  cold1.load(component);cold2.load(component);y1,_=cold1.render(input_file=ROOT/'frozen-0.f32');y2,_=cold2.render(input_file=ROOT/'frozen-0.f32');replay=float(abs(y1-y2).max());np.testing.assert_allclose(y1,y2,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
  cold1.save(ROOT/'COMPONENT_RESAVED.bin');assert component.read_bytes()==(ROOT/'COMPONENT_RESAVED.bin').read_bytes()
 finally:cold1.close();cold2.close()
 a=native('ZL-extra-allpass-LR-independent6-native');captures=[];audio=[];record('actual_paired_independent6_against_latest_accepted_control')
 try:
  for k in range(6):
   raw,_=a.render();old,_=control.render(raw);old_loss=score(old);out,_=candidate.render(raw);loss=score(out);captures.append(dict(rep=k,control=old_loss,loss=loss,assessment=features.local.last));audio.append((old,out))
 finally:a.close()
 delta=np.array([r['control']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(6));robust=bool(np.mean(delta)>max(.0005,3*sem))
 impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];response,_=candidate.render(impulse);first=int(np.flatnonzero(np.max(abs(response),axis=1)>1e-9)[0])-4096;assert first==0 and candidate.latency()==0
 members=[]
 if robust:
  archive=ROOT/'PAIRED6_CONTROL_CANDIDATE_WAVs.tar.gz'
  with tarfile.open(archive,'w:gz',compresslevel=3)as z:
   for k,pair in enumerate(audio):
    for label,y in zip(['control','candidate'],pair):
     buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');b=buf.getvalue();name=f'{label}-{k}.wav';info=tarfile.TarInfo(name);info.size=len(b);z.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
  with tarfile.open(archive)as z:
   for m in members:assert hashlib.sha256(z.extractfile(m['name']).read()).hexdigest()==m['SHA256']
  median=sorted(range(6),key=lambda k:captures[k]['loss'])[3];sf.write(ROOT/'SELECTED_CANDIDATE_WIP.wav',audio[median][1],48000,subtype='FLOAT')
 summary=dict(robust_improvement=robust,current_control_mean=float(np.mean([r['control']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,selected_extra_allpass_bands=selected['bands'],captures=captures,cold_instance_max_abs_error=replay,cold_instance_audio_bit_exact=bool(replay==0),component_bytes_roundtrip_exact=True,declared_PDC_frames=0,impulse_first_response_frames=first,archive_members=members,reference_match_reached=False,not_adopted_into_main_or_FL_project=True)
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('completed_separate_research_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print(json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 record('failed_preserve_all_confirmed_candidates',error=traceback.format_exc());raise
finally:
 for c in clients:c.close()
