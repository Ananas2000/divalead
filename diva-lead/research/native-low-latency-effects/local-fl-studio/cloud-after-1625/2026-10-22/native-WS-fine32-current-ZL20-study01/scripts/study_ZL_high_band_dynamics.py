"""Real additional high-band dynamics: quiet-band attenuation and compression.
Isolated study; never modifies the running matcher's accepted component.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,itertools,json,math,os,queue,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from win_vst3 import D,WinVST3
from native_chain import NativeChain
from fl20_curve import apply_candidate
ROOT=D/'ZL-high-band-dynamics-after-rebase-01';ROOT.mkdir(exist_ok=False);N=Path('/workspace/divalead-work/native-low-latency-effects');STATE=N/'ZL_HIGH_BAND_DYNAMIC_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
f=FeaturesOriginal();prior=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];component=ROOT/'INITIAL_COMPONENT.bin';component.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')};clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_VST3_hosts=[c.child.pid for c in clients],only_three_held_notes=True,source_and_native_base_unchanged=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(o,indent=2)+'\n');p.replace(STATE)
def score(y):
 a=f.residual(y[:288000]);return float(a@a)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025

def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
 for k,v in seed['chorus_overrides'].items():c.set(3,int(k),int(v))
 return c
def configure(c,bands):
 for k in [20,21]:
  b=bands[k-20]if k-20<len(bands)else None;c.set(params['Filter Status'+str(k)],1 if b else 0)
  if not b:continue
  c.set(params['Filter Type'+str(k)],0);c.set(params['Order'+str(k)],1/6);c.set(params['LRMode'+str(k)],b['mode']/4);c.set(params['Dynamic ON'+str(k)],1);c.set(params['Dynamic Learn'+str(k)],0);c.set(params['Dynamic Relative'+str(k)],0)
  for title,value in [('Gain',b['gain']),('Target Gain',b['target']),('Freq',b['frequency']),('Q',b['Q']),('Side Freq',b['frequency']),('Side Q',b['Q']),('Threshold (dB)',b['threshold']),('Attack',b['attack']),('Release',b['release'])]:c.text(params[title+str(k)],str(value))
def evaluate(case,phase=0,save=True):
 label,bands=case;c=pool.get()
 try:
  configure(c,bands);y,status=c.render(input_file=ROOT/f'frozen-{phase}.f32');loss=score(y);assert c.latency()==0;row=dict(label=label,bands=bands,loss=loss,assessment=f.local.last)
  if save:
   with mutex:rows.append(row)
  return row
 finally:pool.put(c)
try:
 record('generating_three_actual_native_realizations')
 c=native('ZL-high-band-dynamics-frozen-native')
 try:
  for k in range(3):y,_=c.render();y.astype('<f4').tofile(ROOT/f'frozen-{k}.f32')
 finally:c.close()
 blob=component.read_bytes();xml=ET.fromstring(blob[8:8+struct.unpack_from('<I',blob,4)[0]]);v={p.attrib['id']:float(p.attrib['value'])for p in xml.find('Para')};assert all(v['filter_status'+str(k)]!=2 for k in [20,21])
 for k in range(2):c=WinVST3(f'ZL-high-band-dynamics-worker-{k}');c.load(component);clients.append(c);pool.put(c)
 baseline=evaluate(('unchanged-control',[]));cases=[]
 for frequency,mode,threshold,Q,magnitude,direction in itertools.product([4500,7500,11500,15500],[0,3,4],[-50,-35,-20],[.4,.8],[3,6],['quiet-cut','loud-cut']):
  b=dict(frequency=frequency,mode=mode,threshold=threshold,Q=Q,gain=-magnitude if direction=='quiet-cut'else 0,target=0 if direction=='quiet-cut'else-magnitude,attack=3,release=80);cases.append((f'grid-{frequency}-{mode}-{threshold}-{Q}-{magnitude}-{direction}',[b]))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if k%16==0:record('actual_single_high_band_dynamic_grid',best_training=min(r['loss']for r in rows))
  current=min(rows,key=lambda r:r['loss']);rng=np.random.default_rng(2026102387);cases=[]
  for k in range(128):
   b=dict(frequency=float(2**rng.uniform(math.log2(2500),math.log2(17500))),mode=int(rng.choice([0,3,4])),threshold=float(rng.uniform(-60,-12)),Q=float(2**rng.uniform(-1.7,1)),gain=float(rng.uniform(-9,1)),target=float(rng.uniform(-6,4)),attack=float(2**rng.uniform(-2,5)),release=float(2**rng.uniform(3,8)));cases.append((f'two-band-{k}',current['bands'][:1]+[b]))
  for k,row in enumerate(executor.map(evaluate,cases)):
   if k%16==0:record('actual_two_high_band_dynamic_candidates',best_training=min(r['loss']for r in rows))
  current=min(rows,key=lambda r:r['loss'])
  for sweep in range(2):
   for index in range(len(current['bands'])):
    for key,step,lo,hi,log in [('frequency',.12,1500,19000,True),('Q',.15,.2,5,True),('gain',.5,-15,10,False),('target',.5,-15,12,False),('threshold',2,-65,-5,False),('attack',.4,.1,500,True),('release',.4,5,2000,True)]:
     cases=[]
     for factor in [-2,-1,1,2]:
      bands=[dict(b)for b in current['bands']];old=bands[index][key];bands[index][key]=float(np.clip(old*2**(factor*step/(sweep+1))if log else old+factor*step/(sweep+1),lo,hi));cases.append((f'fine-{sweep}-{index}-{key}-{factor}',bands))
     winner=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
     if winner['loss']<current['loss']:current=winner
     record('actual_high_band_dynamic_coordinate_fit',best_training=current['loss'])
 held=[]
 for row in [baseline,*sorted(rows,key=lambda r:r['loss'])[:4]]:
  checks=[evaluate(('heldout-'+row['label'],row['bands']),phase,False)for phase in [1,2]];held.append(dict(candidate=row,heldout=checks,mean=float(np.mean([row['loss'],*[r['loss']for r in checks]]))))
 selected=min(held,key=lambda r:r['mean'])['candidate'];(ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'heldout.json').write_text(json.dumps(held,indent=2)+'\n')
 latest=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());latest_state=ROOT/'LATEST_CONTROL_COMPONENT.bin';latest_state.write_bytes(Path(latest['native_ZL_component_state']).read_bytes());control,candidate=clients
 for c in clients:c.load(latest_state)
 configure(control,[]);configure(candidate,selected['bands']);candidate.save(ROOT/'CANDIDATE_COMPONENT.bin');candidate.dump(ROOT/'ACTUAL_610_PARAMETERS.tsv')
 a=native('ZL-high-band-dynamics-independent6');captures=[];audio=[];record('actual_independent6_against_latest_accepted_component')
 try:
  for k in range(6):
   raw,_=a.render();old,_=control.render(raw);old_loss=score(old);out,_=candidate.render(raw);loss=score(out);captures.append(dict(rep=k,base_loss=old_loss,loss=loss,assessment=f.local.last));audio.append((old,out))
 finally:a.close()
 delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(6));robust=bool(np.mean(delta)>max(.0005,3*sem));impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];response,_=candidate.render(impulse);first=int(np.flatnonzero(np.max(abs(response),axis=1)>1e-9)[0])-4096;assert first==0 and candidate.latency()==0
 cold1=WinVST3('ZL-high-band-dynamics-cold1');cold2=WinVST3('ZL-high-band-dynamics-cold2')
 try:
  for c in[cold1,cold2]:c.load(ROOT/'CANDIDATE_COMPONENT.bin')
  y1,_=cold1.render(input_file=ROOT/'frozen-0.f32');y2,_=cold2.render(input_file=ROOT/'frozen-0.f32');error=float(abs(y1-y2).max());np.testing.assert_allclose(y1,y2,rtol=8*np.finfo(np.float32).eps,atol=1e-12);cold1.save(ROOT/'COMPONENT_RESAVED.bin');assert(ROOT/'CANDIDATE_COMPONENT.bin').read_bytes()==(ROOT/'COMPONENT_RESAVED.bin').read_bytes()
 finally:cold1.close();cold2.close()
 archive=ROOT/'SIX_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';members=[]
 with tarfile.open(archive,'w:gz',compresslevel=3)as z:
  for k,pair in enumerate(audio):
   for label,y in zip(['control','candidate'],pair):
    buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');b=buf.getvalue();name=f'{label}-{k}.wav';info=tarfile.TarInfo(name);info.size=len(b);z.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
 with tarfile.open(archive)as z:
  for m in members:assert hashlib.sha256(z.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 median=sorted(range(6),key=lambda k:captures[k]['loss'])[3];sf.write(ROOT/'SELECTED_COMBINED_WIP.wav',audio[median][1],48000,subtype='FLOAT')
 summary=dict(robust_improvement=robust,current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,selected_extra_dynamic_bands=selected['bands'],cold_instance_replay_max_abs_error=error,cold_instance_replay_bit_exact=bool(error==0),component_state_roundtrip_exact=True,declared_PDC_frames=0,impulse_first_response_frames=first,captures=captures,archive_members=members,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,not_adopted=True)
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_high_band_dynamics_study_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print('REAL_HIGH_BAND_DYNAMICS_STUDY_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 record('failed_preserve_all_confirmed_kits',error=traceback.format_exc());raise
finally:
 for c in clients:c.close()
