"""Calibrate finer native output gain; only actual changed presets eligible, all original gates fixed."""
from pathlib import Path
import csv,datetime,hashlib,io,itertools,json,os,shutil,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
import common109_native_gain11_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;V=Path(__file__).resolve().parent;PARENT=Path('/tmp/divalead-native12-common109-fine-margin-20261104');n=p=z=t=None;cache=threading.local();power=q.a.powers;inputs=[];controls=[];anchors=[];rows=[];captures=[];members=[]
for name,target in [('CANDIDATE_PRIMARY.bin','MODEL_PRIMARY_PARENT.bin'),('CANDIDATE_POST.bin','MODEL_POST_PARENT.bin')]:(R/target).write_bytes((PARENT/name).read_bytes())
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');shutil.copyfile(public/'ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin',R/'ANCHOR40_PRIMARY.bin');shutil.copyfile(q.prior['post_native_trim_state'],R/'TRIM.bin')
b=(R/'MODEL_PRIMARY_PARENT.bin').read_bytes();origin={e.attrib['id']:float(e.attrib['value'])for e in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')};ids={r['title']:int(r['id'])for r in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')}

def powers(*args,**kw):v=power(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);err=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(err[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),frozen_comparator=q.prior['source_accepted_cohort'],source_MIDI3_ARP_ADSR_native12_trim_unchanged=True,new_native_final_both_channels_common_gain_from_not_adopted_fine109_point=True,all_control_candidate_same_actual_native_draw=True,original_is_only_target=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def model(delta):
 p.load(R/'MODEL_PRIMARY_PARENT.bin');z.load(R/'MODEL_POST_PARENT.bin');t.configure(12764+int(delta[0]),12800+int(delta[0]))

def cascade(raw,label,delta=None):
 if label=='candidate':model(delta)
 else:p.load(R/('ANCHOR40_PRIMARY.bin'if label=='anchor40'else'PRIMARY.bin'));z.load(R/'POST.bin');t.load(R/'TRIM.bin')
 mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(parent_fine109_not_adopted=True,new_native_both_channels_raw_gain_deltas=[-12,-8,-4,-2,-1,0,1,2,4,8,12],native_original_left_right_raw=[12764,12800],source_and_pre_ZL_native12_unchanged=True,all11_training_models_same3_actual_native_inputs=True,parent_zero_move_only_training_control_not_eligible_as_new_candidate=True,new_candidate_must_improve_parent_training_loss_by0000001=True,training_Air_min_current_and_full40_MINUS0006=True,training_each_lowmid_control_plus0005=True,heldout2_mean_gain_over0003=True,then_entirely_NEW12_same_native_draw_all3_cascades=True,unchanged_first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Air_first10_and_bothcold_nonincreasing_vs_current_AND_full40=True,TONE_nonincreasing=True,all_stereo148_abs16_lowmid325_paired002=True,no_pooling_or_repeating_unchanged_nearmiss_for_acceptance=True,latest_BEST_and_complete_FL20_export_before_adoption=True),indent=2)+'\n')
try:
 n=q.native(q.source['native_input'],'Common109NativeGain11-N-'+str(os.getpid()));p=q.WinVST3('Common109NativeGain11-P-'+str(os.getpid()));z=q.WinVST3('Common109NativeGain11-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Common109NativeGain11-T-'+str(os.getpid()),cleanup_on_close=True)
 for k in range(5):
  raw,_=n.render();inputs.append(raw);out=cascade(raw,'control');controls.append(assess(out));anchor=cascade(raw,'anchor40');anchors.append(assess(anchor));sf.write(R/f'TRAIN_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');sf.write(R/f'TRAIN_CONTROL_{k}.wav',out,48000,subtype='FLOAT');sf.write(R/f'TRAIN_ANCHOR40_{k}.wav',anchor,48000,subtype='FLOAT')
 aircap=min(np.mean([d['Air']for d in controls[:3]]),np.mean([d['Air']for d in anchors[:3]]))-.006
 models=[(0,)]+[(d,)for d in[-12,-8,-4,-2,-1,1,2,4,8,12]]
 for k,delta in enumerate(models):
  ds=[]
  for raw in inputs[:3]:ds.append(assess(cascade(raw,'candidate',delta)))
  feasible=bool(np.mean([d['Air']for d in ds])<=aircap and all(d['stereo_preservation_passed']and d['lowmid_error']<=controls[j]['lowmid_error']+.005 for j,d in enumerate(ds)));row=dict(delta=list(delta),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),feasible=feasible,captures=ds);rows.append(row);(R/'PARTIAL_11_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n')
  if k%8==0:record('actual_new_native_global_gain11_grid',completed_models=k+1)
 parent=rows[0];eligible=[d for d in rows[1:]if d['feasible']and d['loss']<parent['loss']-.000001];winner=min(eligible,key=lambda d:d['loss'])if eligible else None;held=[];ready=False
 if winner:
  for k in[3,4]:out=cascade(inputs[k],'candidate',winner['delta']);d=assess(out);held.append(dict(input=k,control=controls[k],candidate=d,gain=controls[k]['loss']-d['loss']))
  ready=bool(np.mean([d['gain']for d in held])>.0003 and all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 and d['candidate']['Air']<=min(d['control']['Air'],anchors[d['input']]['Air'])+.02 for d in held))
 result=dict(training_cases=len(rows),actual_training_cascade_renders=3*len(rows),parent=parent,winner=winner,heldout=held,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_comparator=q.prior['source_accepted_cohort']);(R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(result,indent=2)+'\n')
 if ready:
  model(winner['delta']);p.save(R/'CANDIDATE_PRIMARY.bin');z.save(R/'CANDIDATE_POST.bin');t.save(R/'CANDIDATE_TRIM.bin');assert(R/'CANDIDATE_TRIM.bin').read_bytes()!=(R/'TRIM.bin').read_bytes();sf.write(R/'SELECTED_TRAIN_WIP.wav',cascade(inputs[0],'candidate',winner['delta']),48000,subtype='FLOAT');n.close();n=q.native(q.source['native_input'],'Common109NativeGain11-New12-'+str(os.getpid()));arc=Path('/tmp/divalead-common109-nativeGain11-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_COMMON_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(arc)
  with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'Common109NativeGain11-Cold-'+str(rep)+'-'+str(os.getpid()))
    raw,_=n.render();old=cascade(raw,'control');d0=assess(old);anchor=cascade(raw,'anchor40');da=assess(anchor);out=cascade(raw,'candidate',winner['delta']);d1=assess(out);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
    for name,y in [('native',raw),('control',old),('anchor40',anchor),('candidate',out)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in [('NATIVE',raw),('CONTROL',old),('ANCHOR40',anchor),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(captures,indent=2)+'\n');record('actual_NEW12_changed_point_common_input',completed_pairs=rep+1)
  gain=np.array([d['gain']for d in captures]);air=np.array([d['Air_delta']for d in captures]);aa=np.array([d['Air_delta_vs40']for d in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([d['candidate']['assessment']['tone_score']-d['control']['assessment']['tone_score']for d in captures[:10]]));guard=all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 for d in captures);passed=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guard)
  with tarfile.open(arc)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
  result.update(captures=captures,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guard,robust_improvement=passed)
 (R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('finite_native_global_gain11_complete_not_adopted',robust_improvement=result['robust_improvement']);print(json.dumps({k:v for k,v in result.items()if k not in['parent','winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_BEST_and_parent_fine_point',error=traceback.format_exc());raise
finally:
 for host in[n,p,z,t]:
  if host is not None:host.close()
