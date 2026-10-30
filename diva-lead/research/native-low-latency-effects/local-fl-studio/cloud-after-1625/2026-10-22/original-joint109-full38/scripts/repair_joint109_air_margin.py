"""Keep the stronger joint tone fit; measure a small real-DSP detector-band trim.

The failed non-increasing-Air gate is retained, not relaxed. No new effect,
source change, MIDI change or reference audio in synthesis.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,hashlib,io,itertools,json,os,queue,shutil,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
import Joint109_air_margin_support as q
from native_post_trim import NativePostTrim

R=q.ROOT;T=Path(__file__).resolve().parent;old=T/'JOINT_PRIMARY_POST_109_CURRENT413';STATE=q.STATE
for source,target in [('CANDIDATE_PRIMARY.bin','JOINT109_PRIMARY.bin'),('CANDIDATE_POST.bin','JOINT109_POST.bin')]:shutil.copyfile(old/source,R/target)
inputs=[]
for k in range(5):
 src=old/f'TRAINING_NATIVE_{k}.wav';os.link(src,R/src.name);audio,sr=sf.read(src,dtype='float32',always_2d=True);assert sr==48000;inputs.append(audio)
ids={r['title']:int(r['id'])for r in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def values(path):
 b=Path(path).read_bytes();return{r.attrib['id']:float(r.attrib['value'])for r in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')}
origin=values(R/'JOINT109_PRIMARY.bin');bands=[20,21,22];clients=[];pool=queue.Queue();cache=threading.local();oldpowers=q.a.powers;rows=[];controls=[];captures=[];members=[];n=None;lock=threading.Lock()
for band in bands:assert origin['filter_status'+str(band)]==2 and origin['dynamic_on'+str(band)]==1
def powers(*args,**kw):
 v=oldpowers(*args,**kw);cache.power=v[0];return v
q.a.powers=powers
def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(e[:,4:6,2:],0).mean());v=np.array(d['LR_dB']);d['original_stereo_preservation_passed']=bool(np.sqrt(np.mean((v[1:]-q.reference_LR[1:])**2))<=1.48 and max(abs(v[1:]))<=1.6 and abs(v[0]-q.reference_LR[0])<=3.25);return d
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),actual_ZL_hosts=[c.child.pid for p,z,t in clients for c in[p,z]],actual_trim_hosts=[t.chain.proc.pid for p,z,t in clients],source_native_MIDI3held_ARP_ADSR_and_joint109_POST_unchanged=True,only_linked_Gain_and_TargetGain20_21_22_shifted=True,not_adopted=True,reference_match_reached=False,**kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(s,indent=2)+'\n');tmp.replace(STATE)
def configure(p,delta):
 p.load(R/'JOINT109_PRIMARY.bin')
 for band,shift in zip(bands,delta):
  if shift:
   for title,key in [('Gain','gain'),('Target Gain','target_gain')]:p.text(ids[title+str(band)],format(origin[key+str(band)]+shift,'.12g'))
def cascade(raw,primary,post,p,z,t):
 p.load(primary);z.load(post);mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)
def evaluate(case,indices=(0,1,2),keep=True):
 label,delta=case;p,z,t=pool.get()
 try:
  ds=[]
  for k in indices:
   configure(p,delta);z.load(R/'JOINT109_POST.bin');mid,_=p.render(inputs[k]);pre,_=z.render(mid);ds.append(assess(t.render(pre)));assert p.latency()+z.latency()==0
  gain=float(np.mean([controls[k]['loss']-d['loss']for k,d in zip(indices,ds)]));air=float(np.mean([d['positive_excess_air_dB']-controls[k]['positive_excess_air_dB']for k,d in zip(indices,ds)]));guard=all(d['original_stereo_preservation_passed']and d['lowmid_error']<=controls[k]['lowmid_error']+.02 for k,d in zip(indices,ds));row=dict(label=label,delta=list(delta),loss=float(np.mean([d['loss']for d in ds])),mean_gain_vs413=gain,mean_Air_delta_vs413=air,captures=ds,stereo_guards=guard,training_feasible=bool(guard and air<=-.005))
  if keep:
   with lock:rows.append(row)
  return row
 finally:pool.put((p,z,t))
def add(tar,name,audio):
 f=io.BytesIO();sf.write(f,audio,48000,format='WAV',subtype='FLOAT');data=f.getvalue();i=tarfile.TarInfo(name);i.size=len(data);tar.addfile(i,io.BytesIO(data));members.append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(parent109_tone_gain_confirmed_but_extra_Air_gate_failed=True,parent109_all_previous_gates_passed_not_adopted=True,linked_band_gain_target_shifts_grid=[0.,-.01,-.02,-.04],grid_bands=bands,training_same3_native_inputs_and_freshly_measured413_controls=True,training_Air_margin_minus0005dB=True,two_unseen_then12new_native_pairs=True,final_first6ANDfirst10_gain_over_max0005_3SEM_bothcold_positive=True,all_absolute_and_paired_stereo_gates_unchanged=True,final_Air_first10_and_bothcold_at_most0_unchanged=True,latest_context_full_export_and_coldZIP_replay_required=True),indent=2)+'\n')
try:
 for k in range(2):
  tag='AirMargin109-'+str(os.getpid())+'-'+str(k);p=q.WinVST3(tag+'-primary');z=q.WinVST3(tag+'-post');t=NativePostTrim(R/'buffers',tag+'-trim',cleanup_on_close=True);t.load(q.prior['post_native_trim_state']);clients.append((p,z,t));pool.put((p,z,t))
 p,z,t=clients[0];record('five_actual_control413_assessments')
 for raw in inputs:controls.append(assess(cascade(raw,R/'PRIMARY.bin',R/'POST.bin',p,z,t)))
 (R/'CONTROL413_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n');neutral=[]
 for k,(p,z,t)in enumerate(clients):
  direct=cascade(inputs[0],R/'JOINT109_PRIMARY.bin',R/'JOINT109_POST.bin',p,z,t);configure(p,[0.,0.,0.]);z.load(R/'JOINT109_POST.bin');mid,_=p.render(inputs[0]);pre,_=z.render(mid);actual=t.render(pre);np.testing.assert_array_equal(actual,direct);neutral.append(dict(worker=k,neutral_shift_vs_direct_load_max_error=0.))
 (R/'BOTH_WORKERS_NEUTRAL_IDENTITY.json').write_text(json.dumps(neutral,indent=2)+'\n');cases=[('grid-'+str(k),d)for k,d in enumerate(itertools.product([0.,-.01,-.02,-.04],repeat=3))]
 with concurrent.futures.ThreadPoolExecutor(2)as ex:
  for row in ex.map(evaluate,cases):record('actual_three_common_input_Air_margin_grid',cases=len(rows),latest_gain=row['mean_gain_vs413'],latest_Air_delta=row['mean_Air_delta_vs413'])
 valid=[d for d in rows if d['training_feasible']];winner=min(valid,key=lambda d:d['loss'])if valid else None;held=[];ready=False
 if winner:
  held=[evaluate(('unseen-'+str(k),winner['delta']),(k,),False)for k in[3,4]];ready=bool(np.mean([d['mean_gain_vs413']for d in held])>.0003 and all(d['stereo_guards']and d['mean_Air_delta_vs413']<=0 for d in held));p,z,t=clients[0];configure(p,winner['delta']);component=R/'CANDIDATE_PRIMARY.bin';p.save(component);shutil.copyfile(R/'JOINT109_POST.bin',R/'CANDIDATE_POST.bin');post_component=R/'CANDIDATE_POST.bin';now=values(component);changed={k:[v,now[k]]for k,v in origin.items()if v!=now[k]};assert set(changed)<={key+str(band)for band in bands for key in['gain','target_gain']};out=cascade(inputs[0],component,post_component,p,z,t);sf.write(R/'SELECTED_TRAINING_WIP.wav',out,48000,subtype='FLOAT')
 summary=dict(training_cases=len(rows),actual_training_DSP_renders=3*len(rows),winner=winner,heldout=held,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,component=None if not winner else str(component),post_component=None if not winner else str(post_component));(R/'TRAINING_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');(R/'FROZEN_BEFORE_NEW_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  assert shutil.disk_usage('/workspace').free>120*2**20,'Promising frozen point preserved; restore space before full12 capture'
  n=q.native(q.source['native_input'],'AirMargin109-'+str(os.getpid())+'-validation-native');p,z,t=clients[0]
  with tarfile.open(R/'ALL12_NATIVE_CONTROL413_AIR_REPAIRED_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'AirMargin109-'+str(os.getpid())+'-cold-'+str(rep))
    raw,_=n.render();a=cascade(raw,R/'PRIMARY.bin',R/'POST.bin',p,z,t);da=assess(a);b=cascade(raw,component,post_component,p,z,t);db=assess(b);captures.append(dict(rep=rep,control=da,candidate=db,improvement=da['loss']-db['loss'],air_increase=db['positive_excess_air_dB']-da['positive_excess_air_dB']))
    for name,y in [('native',raw),('control413',a),('candidate',b)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in [('NATIVE_INPUT',raw),('CONTROL413',a),('CANDIDATE',b)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('new_first6AND10_cold2_nonincreasing_Air_validation',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([d['improvement']for d in captures]);air=np.array([d['air_increase']for d in captures]);s6=float(delta[:6].std(ddof=1)/np.sqrt(6));s10=float(delta[:10].std(ddof=1)/np.sqrt(10));guard=all(d['candidate']['original_stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 for d in captures);robust=bool(delta[:6].mean()>max(.0005,3*s6)and delta[:10].mean()>max(.0005,3*s10)and min(delta[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and guard);summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(delta[:6].mean()),first6_SEM=s6,first10_mean_improvement=float(delta[:10].mean()),first10_SEM=s10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(air[:10].mean()),cold2_air_increase=air[10:].tolist(),all12_original_stereo_lowmid_guards=guard,robust_improvement=robust)
  with tarfile.open(R/'ALL12_NATIVE_CONTROL413_AIR_REPAIRED_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_Air_margin_repair_complete_not_adopted',robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in['winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_413_and_frozen_joint109',error=traceback.format_exc());raise
finally:
 if n is not None:n.close()
 for p,z,t in clients:p.close();z.close();t.close()
