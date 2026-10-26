"""New hypothesis: common stereo phase correction scored ONLY against original.
Actual native training inputs and actual official ZL DSP; unchanged objective.
No new Diva instances/GUI exports, reference samples never enter synthesis.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,struct,tarfile,threading,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3,D
A=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');OLD=Path('/workspace/divalead-work/pc-stereo-20261024')
ROOT=Path('/tmp/divalead-post-joint11-20261026-01');ROOT.mkdir(exist_ok=False)
STATE=N/'ORIGINAL_POST_JOINT11_STUDY.json';OWNER='post-joint11-finite-parallel-20261026';STOP=N/'zl-stereo-continuation.stop'
prior=json.loads((OLD/'stereo-continuous87/BEST_CANDIDATE.json').read_text())
seed=prior['native_base'];BASE=Path(prior['native_base_export_directory']);manifest=json.loads((BASE/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest']
for name,source in [('PRIMARY.bin',prior['native_ZL_component_state']),('CONTROL_POST.bin',prior['post_ZL_component_state'])]:(ROOT/name).write_bytes(Path(source).read_bytes())
(ROOT/'PRIOR_CONFIRMED.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal();reg=float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def values(path):
 b=Path(path).read_bytes();x=ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]])
 return {p.attrib['id']:float(p.attrib['value'])for p in x.find('Para')}
original=values(ROOT/'CONTROL_POST.bin');assert all(original['filter_status'+str(k)]==2 for k in range(5))
specs=[]
for k in range(4):
 specs += [dict(title='Freq'+str(k),key='freq'+str(k),step=.12,lo=30.,hi=18000.,log=True),dict(title='Q'+str(k),key='q'+str(k),step=.18,lo=.15,hi=25.,log=True)]
specs += [dict(title='Gain4',key='gain4',step=.5,lo=-6.,hi=6.,log=False),dict(title='Freq4',key='freq4',step=.12,lo=300.,hi=2500.,log=True),dict(title='Q4',key='q4',step=.18,lo=.15,hi=25.,log=True)]
origin={p['key']:original[p['key']]for p in specs}
ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);freqs=np.fft.rfftfreq(len(ref),1/48000)
bands=[(40,300),(300,800),(800,2000),(2000,5000),(5000,10000),(10000,14000)];masks=[(freqs>=lo)&(freqs<hi)for lo,hi in bands]
def lr(edit):
 p=abs(np.fft.rfft(edit,axis=0))**2
 return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref)
def assessment(y):
 residual=features.residual(y);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));balance=lr(edit);high=float(np.sqrt(np.mean((balance[3:]-target[3:])**2)))
 return dict(loss=float(residual@residual)+reg,assessment=features.local.last,LR_dB=balance.tolist(),lowmid_error=abs(float(balance[1]-target[1])),bass_error=abs(float(balance[0]-target[0])),upper_error=high,upper_stereo_guard=bool(high<=1.5 and np.max(np.abs(balance[3:]))<=1.6))
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def state(phase,**extra):
 p=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,root=str(ROOT),cases=len(rows),real_VST3_hosts=[c.child.pid for c in clients],only_three_held_notes=True,source_native_primary_unchanged=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(STATE)
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
 for row in manifest:
  p=BASE/row['state'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['state_SHA256'];c.load_state(row['node'],p)
 return c
def configure(c,settings):
 c.load(ROOT/'CONTROL_POST.bin')
 if settings is not None:
  for p in specs:c.text(params[p['title']],format(settings[p['key']],'.12g'))
def evaluate(case,phase=0,keep=True):
 label,settings=case;c=pool.get()
 try:
  configure(c,settings);out,status=c.render(input_file=ROOT/f'primary-{phase}.f32');row=dict(label=label,settings=settings,**assessment(out),VST3_status=status);assert c.latency()==0
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put(c)
def wave(y):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');return f.getvalue()
def add(tar,name,y,members):
 b=wave(y);info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()))
assert prior['native_base_export_directory'].endswith('_10')
(ROOT/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(existing_POST_four_AllPass_freqQ_and_LeftPeak_freqQgain_only=True,all_filter_modes_types_statuses_unchanged=True,extra_per_pair_lowmid_error_not_worse_over_dB=.02,actual_primary_and_native10_frozen=True,BOTH_first6_and_first10=True,warm10_cold2=True,floor=.0005,SEM_multiplier=3,latest_context_match_required_before_adoption=True),indent=2)+'\n')
try:
 state('capture_three_NEW_actual_native_and_primary_inputs')
 n=native('PostJoint11-stereo-training-native');p=WinVST3('PostJoint11-stereo-training-primary');members=[]
 try:
  with tarfile.open(ROOT/'TRAINING_NATIVE_AND_PRIMARY_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for k in range(3):
    raw,status=n.render();p.load(ROOT/'PRIMARY.bin');out,_=p.render(raw);raw.astype('<f4').tofile(ROOT/f'native-{k}.f32');out.astype('<f4').tofile(ROOT/f'primary-{k}.f32');add(tar,f'native-{k}.wav',raw,members);add(tar,f'primary-{k}.wav',out,members)
 finally:n.close();p.close()
 (ROOT/'TRAINING_AUDIO_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n')
 for k in range(2):c=WinVST3('PostJoint11-stereo-worker-'+str(k));clients.append(c);pool.put(c)
 baseline=evaluate(('current-confirmed-control',None));current=baseline;maximum_lowmid=min(3.35,baseline['lowmid_error']+.02);rng=np.random.default_rng(2026102614);cases=[]
 def eligible(row):return row['upper_stereo_guard']and row['lowmid_error']<=maximum_lowmid
 for k in range(96):
  v=dict(origin);strength=[.4,.8,1.6,3.2][k%4]
  for p in specs:
   d=float(rng.uniform(-1,1))*p['step']*strength;v[p['key']]=float(np.clip(v[p['key']]*2**d if p['log']else v[p['key']]+d,p['lo'],p['hi']))
  cases.append((f'joint11-{k}',v))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for k,row in enumerate(executor.map(evaluate,cases)):
   if eligible(row)and row['loss']<current['loss']:current=row
   if k%8==0:state('actual_POST11_joint_proposals',control_loss=baseline['loss'],best_loss=current['loss'])
  for sweep in range(3):
   for index in rng.permutation(len(specs)):
    p=specs[int(index)];cases=[]
    for factor in [-2,-1,1,2]:
     v=dict(current['settings']or origin);d=factor*p['step']*(.55**sweep);v[p['key']]=float(np.clip(v[p['key']]*2**d if p['log']else v[p['key']]+d,p['lo'],p['hi']));cases.append((f'fine11-{sweep}-{index}-{factor}',v))
    checked=list(executor.map(evaluate,cases));valid=[r for r in checked if eligible(r)]
    if valid and min(valid,key=lambda r:r['loss'])['loss']<current['loss']:current=min(valid,key=lambda r:r['loss'])
    state('actual_POST11_coordinate_refit',control_loss=baseline['loss'],best_loss=current['loss'],sweep=sweep,coordinate=int(index))
 held=[]
 for k in [1,2]:held.append(dict(control=evaluate(('heldout-control',None),k,False),candidate=evaluate(('heldout-frozen-candidate',current['settings']),k,False)))
 c=clients[0];configure(c,current['settings']);c.save(ROOT/'CANDIDATE_POST.bin');c.dump(ROOT/'ACTUAL_POST_610_PARAMETERS.tsv');now=values(ROOT/'CANDIDATE_POST.bin');changed={k:[old,now[k]]for k,old in original.items()if now[k]!=old};assert set(changed).issubset({p['key']for p in specs}),changed
 frozen=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),primary_SHA256=hashlib.sha256((ROOT/'PRIMARY.bin').read_bytes()).hexdigest(),post_SHA256=hashlib.sha256((ROOT/'CANDIDATE_POST.bin').read_bytes()).hexdigest(),selected_settings=current['settings'],changed_XML_fields=changed,not_adopted=True);(ROOT/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(frozen,indent=2)+'\n')
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'HELDOUT.json').write_text(json.dumps(held,indent=2)+'\n')
 ready=bool(current['settings']is not None and baseline['loss']-current['loss']>.0003 and all(r['control']['loss']>r['candidate']['loss']+.0001 and r['candidate']['upper_stereo_guard']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in held))
 summary=dict(training_cases=len(rows),training_control=baseline,training_candidate=current,heldout_positive=all(r['control']['loss']>r['candidate']['loss']for r in held),sufficient_training_and_heldout_improvement=ready,robust_improvement=False,source_native_primary_unchanged=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,not_adopted=True,requires_latest_context_match_before_adoption=True)
 if ready:
  state('NEW_native6_plus_two_cold_paired_validation')
  primary=WinVST3('PostJoint11-stereo-validation-primary');control=WinVST3('PostJoint11-stereo-validation-control');candidate=WinVST3('PostJoint11-stereo-validation-candidate');n=native('PostJoint11-stereo-independent-native');captures=[];members=[]
  try:
   with tarfile.open(ROOT/'NEW_NATIVE12_INPUT_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
    for k in range(12):
     if k in [10,11]:n.close();n=native('PostJoint11-stereo-cold-native-'+str(k))
     raw,status=n.render();primary.load(ROOT/'PRIMARY.bin');middle,_=primary.render(raw);control.load(ROOT/'CONTROL_POST.bin');candidate.load(ROOT/'CANDIDATE_POST.bin');old,_=control.render(middle);out,_=candidate.render(middle);a0=assessment(old);a1=assessment(out);captures.append(dict(rep=k,control=a0,candidate=a1,improvement=a0['loss']-a1['loss'],mono_error=float(abs(out.sum(axis=1)-middle.sum(axis=1)).max())))
     for label,y in [('native-input',raw),('control',old),('candidate',out)]:add(tar,f'{label}-{k}.wav',y,members)
     if k==0:
      for label,y in [('NATIVE_INPUT',raw),('CONTROL',old),('CANDIDATE',out)]:sf.write(ROOT/(label+'_00.wav'),y,48000,subtype='FLOAT')
    candidate.save(ROOT/'POST_RESAVED.bin');assert (ROOT/'POST_RESAVED.bin').read_bytes()==(ROOT/'CANDIDATE_POST.bin').read_bytes()
  finally:primary.close();control.close();candidate.close();n.close()
  delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));sem10=float(np.std(delta[:10],ddof=1)/np.sqrt(10));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and np.mean(delta[:10])>max(.0005,3*sem10)and min(delta[10:])>0 and all(r['candidate']['upper_stereo_guard']and r['candidate']['lowmid_error']<=3.35 and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures))
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),first10_mean_improvement=float(np.mean(delta[:10])),first10_SEM=sem10,required_first10=max(.0005,3*sem10),cold2_improvements=delta[10:].tolist(),robust_improvement=robust)
 for archive in ROOT.glob('*WAVs.tar.gz'):
  with tarfile.open(archive)as tar:
   expected=members if archive.name.startswith('NEW_NATIVE12')else json.loads((ROOT/'TRAINING_AUDIO_MEMBERS.json').read_text())
   for row in expected:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');state('finite_original_target_stereo_phase_hypothesis_complete_not_adopted',training_gain=baseline['loss']-current['loss'],robust_improvement=summary['robust_improvement'],sufficient_training=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members','training_control','training_candidate']}),flush=True)
except BaseException:
 import traceback
 state('failed_preserve_prior_and_all_evidence',error=traceback.format_exc());raise
finally:
 for c in clients:c.close()
