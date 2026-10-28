"""Merge a separately frozen quieter direction with372; guard cumulative drift vs37."""
from pathlib import Path
import ast,csv,datetime,gzip,hashlib,io,json,os,struct,tarfile,traceback,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
import Primary_air_direction_merge372_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;STATE=q.STATE;old=q.H/'PRIMARY_MEAN3_COMMON_INPUT_ORIGINAL37';full=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP37');assert q.prior['source_accepted_cohort']==372;assert not json.loads((old/'completion.json').read_text())['robust_improvement'];(R/'ANCHOR37_PRIMARY.bin').write_bytes((full/'verification/ZL37_PRIMARY_COMPONENT.bin').read_bytes());params={r['title']:int(r['id'])for r in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')};ns=dict(Path=Path,ET=ET,struct=struct,np=np,params=params);text=Path('/workspace/divalead-work/pc-stereo-20261024/continue_stereo_ZL_matching.py').read_text();tree=ast.parse(text)
for name in ['specs_from_component','configure']:
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);exec(compile(ast.get_source_segment(text,node),'<actual-main-'+name+'>','exec'),ns)
specs,dynamic=ns['specs_from_component'](R/'PRIMARY.bin');base_specs,_=ns['specs_from_component'](old/'PRIMARY.bin');fine_specs,_=ns['specs_from_component'](old/'CANDIDATE_PRIMARY.bin');assert [x['title']for x in specs]==[x['title']for x in base_specs]==[x['title']for x in fine_specs];ns.update(specs=specs,dynamic=dynamic);configure=ns['configure'];cache=q.threading.local();origpower=q.a.powers;p=z=trim=n=None;results=[];members=[];captures=[]
def powers(*args,**kw):
 v=origpower(*args,**kw);cache.power=v[0];return v
q.a.powers=powers
def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(e[:,4:6,2:],0).mean());v=np.array(d['LR_dB']);d['original_stereo_preservation_passed']=bool(np.sqrt(np.mean((v[1:]-q.reference_LR[1:])**2))<=1.48 and max(abs(v[1:]))<=1.6 and abs(v[0]-q.reference_LR[0])<=3.25);return d
def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),original_is_only_target=True,source_Diva281_threeheld_MIDI_ARP_ADSR_native12_POST37_nativeTrim_unchanged=True,only_PRIMARY94_changed=True,not_adopted=True,reference_match_reached=False,**kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(STATE)
def cascade(raw,component):
 p.load(component);z.load(R/'POST.bin');mid,_=p.render(raw);before,_=z.render(mid);assert p.latency()+z.latency()==0;return trim.render(before)
def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');data=b.getvalue();info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data));members.append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
def gates(d,c,a):return d['original_stereo_preservation_passed']and d['lowmid_error']<=c['lowmid_error']+.02 and d['lowmid_error']<=a['lowmid_error']+.02
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(alphas=[.5,1.,1.5,2.,3.,4.],direction_from_independent_failed_floor_mean3_point=True,baseline_actual_accepted372=True,cumulative_anchor_complete37=True,log_parameters_multiply_ratio_power_alpha_linear_parameters_add_delta_alpha=True,all94_bounds_and_saved_states_exact=True,three_train_two_unseen_common_native_inputs=True,training_mean_Air_vs_anchor37_plus0005=True,held_Air_vs_anchor37_plus002=True,held_local_loss_gain_vs372_over0003=True,newfirst6_AND_first10_local_gain_over_max0005_3SEM=True,also_anchor37_first6AND10_gain_above_same_floor=True,bothcold_local_and_anchor_gain_positive=True,all_original_stereo_lowmid_and_BOTH_local_anchor_Air_plus002_guards=True,latest_context_and_full_supported_export_before_adoption=True),indent=2)+'\n')
try:
 p=q.WinVST3('Merge372-'+str(os.getpid())+'-primary');z=q.WinVST3('Merge372-'+str(os.getpid())+'-post');trim=NativePostTrim(R/'buffers','Merge372-'+str(os.getpid())+'-trim',cleanup_on_close=True);trim.load(q.prior['post_native_trim_state']);n=q.native(q.source['native_input'],'Merge372-'+str(os.getpid())+'-native');inputs=[];controls=[];anchors=[];record('five_actual_common_inputs_anchor37_and_latest372')
 for k in range(5):
  raw,_=n.render();inputs.append(raw);c=cascade(raw,R/'PRIMARY.bin');a=cascade(raw,R/'ANCHOR37_PRIMARY.bin');controls.append(assess(c));anchors.append(assess(a));sf.write(R/f'TRAINING_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');sf.write(R/f'TRAINING_CONTROL372_{k}.wav',c,48000,subtype='FLOAT');sf.write(R/f'TRAINING_ANCHOR37_{k}.wav',a,48000,subtype='FLOAT')
 n.close();n=None;(R/'CONTROL_ANCHOR_ASSESSMENTS.json').write_text(json.dumps(dict(control372=controls,anchor37=anchors),indent=2)+'\n')
 for index,alpha in enumerate([.5,1.,1.5,2.,3.,4.]):
  x=[]
  for a,b,c in zip(specs,base_specs,fine_specs):
   value=a['value']*(c['value']/b['value'])**alpha if a['log']else a['value']+alpha*(c['value']-b['value']);x.append(float(np.clip(value,a['lo'],a['hi'])))
  configure(p,x);component=R/f'ALPHA_{index}_PRIMARY.bin';p.save(component);scores=[]
  for k,raw in enumerate(inputs):
   out=cascade(raw,component);scores.append(assess(out))
   if k==0:sf.write(R/f'ALPHA_{index}_FULL_TRAINING_WIP.wav',out,48000,subtype='FLOAT')
  gain=float(np.mean([controls[k]['loss']-scores[k]['loss']for k in[3,4]]));air3=float(np.mean([scores[k]['positive_excess_air_dB']-anchors[k]['positive_excess_air_dB']for k in range(3)]));eligible=bool(gain>.0003 and air3<=.005 and all(gates(d,c,a)and d['positive_excess_air_dB']<=a['positive_excess_air_dB']+.02 and d['positive_excess_air_dB']<=c['positive_excess_air_dB']+.02 for d,c,a in zip(scores,controls,anchors)));row=dict(alpha=alpha,component=str(component),x=x,scores=scores,heldout_mean_gain_vs372=gain,training_air_change_vs37=air3,eligible=eligible);results.append(row);record('actual_merged_PRIMARY_direction_rendered',alpha=alpha,held_gain=gain,training_air_vs37=air3,eligible=eligible)
 eligible=[x for x in results if x['eligible']];winner=max(eligible,key=lambda x:x['heldout_mean_gain_vs372'])if eligible else None;summary=dict(models=results,winner=winner,sufficient_screen=winner is not None,robust_improvement=False,not_adopted=True,reference_match_reached=False);(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if winner:
  n=q.native(q.source['native_input'],'Merge372-'+str(os.getpid())+'-validation')
  with tarfile.open(R/'TWELVE_NEW_NATIVE_ANCHOR37_CONTROL372_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'Merge372-'+str(os.getpid())+'-cold-'+str(rep))
    raw,_=n.render();a=cascade(raw,R/'ANCHOR37_PRIMARY.bin');da=assess(a);c=cascade(raw,R/'PRIMARY.bin');dc=assess(c);y=cascade(raw,winner['component']);dy=assess(y);captures.append(dict(rep=rep,anchor37=da,control372=dc,candidate=dy,local_gain=dc['loss']-dy['loss'],anchor_gain=da['loss']-dy['loss'],local_air_increase=dy['positive_excess_air_dB']-dc['positive_excess_air_dB'],anchor_air_increase=dy['positive_excess_air_dB']-da['positive_excess_air_dB']))
    for name,v in [('native',raw),('anchor37',a),('control372',c),('candidate',y)]:add(tar,f'{name}-{rep}.wav',v)
    if rep==0:
     for name,v in [('NATIVE_INPUT',raw),('ANCHOR37',a),('CONTROL372',c),('CANDIDATE',y)]:sf.write(R/(name+'_00.wav'),v,48000,subtype='FLOAT')
    record('twelve_new_local_AND_cumulative_anchor_checks',completed_pairs=rep+1,latest_local_gain=captures[-1]['local_gain'])
  checks={}
  for name,key in [('local','local_gain'),('anchor37','anchor_gain')]:
   d=np.array([x[key]for x in captures]);sem6=float(d[:6].std(ddof=1)/np.sqrt(6));sem10=float(d[:10].std(ddof=1)/np.sqrt(10));checks[name]=dict(first6_gain=float(d[:6].mean()),first6_SEM=sem6,first10_gain=float(d[:10].mean()),first10_SEM=sem10,cold2=d[10:].tolist(),passed=bool(d[:6].mean()>max(.0005,3*sem6)and d[:10].mean()>max(.0005,3*sem10)and min(d[10:])>0))
  airchecks={}
  for label,key in [('local','local_air_increase'),('anchor37','anchor_air_increase')]:
   a=np.array([x[key]for x in captures]);airchecks[label]=dict(first10_increase=float(a[:10].mean()),cold2=a[10:].tolist(),passed=bool(a[:10].mean()<=.02 and max(a[10:])<=.02))
  robust=bool(all(d['passed']for d in checks.values())and all(d['passed']for d in airchecks.values())and all(gates(x['candidate'],x['control372'],x['anchor37'])for x in captures));summary.update(captures=captures,archive_members=members,loss_checks=checks,air_checks=airchecks,robust_improvement=robust)
  with tarfile.open(R/'TWELVE_NEW_NATIVE_ANCHOR37_CONTROL372_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_merge372_complete_not_adopted',robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in ['models','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_full37_and_latest372',error=traceback.format_exc());raise
finally:
 for c in[n,p,z,trim]:
  if c is not None:c.close()
