"""Actual joint Mid/Side/Stereo all-pass fit, same original criterion and native input."""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,json,os,queue,threading,traceback
import numpy as np,soundfile as sf
import Mid_Side_phase_joint35_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;STATE=q.STATE;slots=[0,1,2,3,5];specs=[]
for k in slots:
 assert q.original['filter_type'+str(k)]==9 and q.original['filter_status'+str(k)]==2
 specs.extend([dict(title='Freq'+str(k),key='freq'+str(k),step=.055,lo=30.,hi=18000.),dict(title='Q'+str(k),key='q'+str(k),step=.1,lo=.15,hi=25.)])
cache=threading.local();origpower=q.a.powers;controls=[];clients=[];pool=queue.Queue();rows=[];results=[];mutex=threading.Lock();active_component=None;n=None;primary=None
def powers(*args,**kw):
 result=origpower(*args,**kw);cache.power=result[0];return result
q.a.powers=powers
def assess(y):
 d=q.assessment(y);error=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(error[:,4:6,2:],0).mean());d['original_stereo_preservation_passed']=bool(d['upper_error']<=1.48 and max(abs(np.array(d['LR_dB'])[3:]))<=1.6 and d['lowmid_error']<=3.25);return d
def training_ok(d):return d['original_stereo_preservation_passed']and d['upper_error']<=controls[0]['upper_error']-.025 and d['lowmid_error']<=controls[0]['lowmid_error']-.25 and d['bass_error']<=controls[0]['bass_error']+.1 and d['positive_excess_air_dB']<=controls[0]['positive_excess_air_dB']+.005
def held_ok(d,c):return d['original_stereo_preservation_passed']and d['upper_error']<=c['upper_error']-.02 and d['lowmid_error']<=c['lowmid_error']-.2 and d['bass_error']<=c['bass_error']+.15 and d['positive_excess_air_dB']<=c['positive_excess_air_dB']+.02
def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_POST_ZL_hosts=[z.child.pid for z,c in clients],actual_native_trim_hosts=[c.chain.proc.pid for z,c in clients],only_existing_POST_AP_frequency_Q_in_slots=slots,source_Diva281_MIDI3held_ARP_ADSR_native12_CURRENT_PRIMARY_and_nativeTrim_unchanged=True,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);d.update(kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(STATE)
def configure(z,x):
 z.load(active_component)
 for p,v in zip(specs,x):z.text(q.params[p['title']],format(v,'.12g'))
def evaluate(case,k=0,keep=True):
 label,x=case;z,c=pool.get()
 try:
  configure(z,x);before,_=z.render(input_file=R/f'primary-{k}.f32');out=c.render(before);assert z.latency()==0;row=dict(label=label,x=list(map(float,x)),**assess(out));row['training_constraints_passed']=training_ok(row)
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put((z,c))
def choose(candidates,current):
 candidates=[current,*candidates];valid=[r for r in candidates if r['training_constraints_passed']]
 if valid:return min(valid,key=lambda r:r['loss'])
 def violation(r):return max(0,r['upper_error']-controls[0]['upper_error']+.025)/.05+max(0,r['lowmid_error']-controls[0]['lowmid_error']+.25)/.1+max(0,r['bass_error']-controls[0]['bass_error']-.1)/.1+max(0,r['positive_excess_air_dB']-controls[0]['positive_excess_air_dB']-.005)/.02
 return min(candidates,key=lambda r:(violation(r),r['loss']))
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(starting_models=[dict(MidFrequency=650.,Q=6.),dict(MidFrequency=650.,Q=8.),dict(MidFrequency=660.,Q=9.6)],only_existing_AP_freq_Q_slots=slots,LeftEQ4_and_all_modes_types_statuses_fixed=True,new_point_requires_changes_to_other_AP_besides_Mid5=True,original_fullscore_weights_alignment_unchanged=True,training_upper_error_reduction_min_dB=.025,training_lowmid_error_reduction_min_dB=.25,validation_each_upper_error_reduction_min_dB=.02,validation_each_lowmid_error_reduction_min_dB=.2,bass_error_increase_max_dB=.15,first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_gains_positive=True,first10_and_bothcold_air_increase_max_dB=.02,strict_native_ZL_cold_and_fullkit_latestcontext_required=True),indent=2)+'\n')
try:
 for k in range(2):z=q.WinVST3('MidSideJoint35-post-'+str(k));c=NativePostTrim(R/'buffers','MidSideJoint35-trim-'+str(k),cleanup_on_close=True);c.load(q.prior['post_native_trim_state']);clients.append((z,c));pool.put((z,c))
 n=q.native('MidSideJoint35-training-native');primary=q.WinVST3('MidSideJoint35-fixed-primary');record('three_new_actual_native_PRIMARY_inputs')
 for k in range(3):
  raw,_=n.render();primary.load(R/'PRIMARY.bin');p,_=primary.render(raw);assert primary.latency()==0;p.astype('<f4').tofile(R/f'primary-{k}.f32');z,c=clients[0];z.load(R/'CONTROL_POST.bin');before,_=z.render(p);out=c.render(before);controls.append(assess(out));sf.write(R/f'TRAINING_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');sf.write(R/f'TRAINING_PRIMARY_{k}.wav',p,48000,subtype='FLOAT');sf.write(R/f'TRAINING_CONTROL_{k}.wav',out,48000,subtype='FLOAT')
 n.close();n=None;primary.close();primary=None;(R/'CONTROL_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n');rng=np.random.default_rng(2026102708)
 with concurrent.futures.ThreadPoolExecutor(2)as ex:
  for k,(frequency,Q)in enumerate([(650.,6.),(650.,8.),(660.,9.6)]):
   folder=R/f'model-{k}';folder.mkdir();z,c=clients[0];z.load(R/'CONTROL_POST.bin');z.text(q.params['Freq5'],str(frequency));z.text(q.params['Q5'],str(Q));active_component=folder/'INITIAL_POST.bin';z.save(active_component);values=q.values(active_component);initial=[values[p['key']]for p in specs];rows=[];current=evaluate(('initial-joint-phase-model',initial));initial_row=current;cases=[]
   for rep in range(48):
    x=list(current['x']);groups=rng.choice(5,size=1+rep%3,replace=False)
    for group in groups:
     for j in[2*int(group),2*int(group)+1]:p=specs[j];x[j]=float(np.clip(x[j]*2**(rng.normal()*p['step']*float(rng.choice([.5,1.,2.]))),p['lo'],p['hi']))
    cases.append((f'coupled-{rep}',x))
   current=choose(list(ex.map(evaluate,cases)),current)
   for sweep in range(2):
    for j in rng.permutation(len(specs)):
     p=specs[j];cases=[]
     for factor in[-2,-1,1,2]:x=list(current['x']);x[j]=float(np.clip(x[j]*2**(factor*p['step']*(.65**sweep)),p['lo'],p['hi']));cases.append((f'coordinate-{sweep}-{j}-{factor}',x))
     current=choose(list(ex.map(evaluate,cases)),current);record('actual_joint_Mid_Side_phase_coordinate_fit',model=k,sweep=sweep,coordinate=int(j),selected_loss=current['loss'],feasible=current['training_constraints_passed'])
   held=[evaluate(('heldout-'+str(k),current['x']),k,False)for k in[1,2]];z,c=clients[0];configure(z,current['x']);component=folder/'CANDIDATE_POST.bin';z.save(component);now=q.values(component);changed={key:[old,now[key]]for key,old in q.original.items()if old!=now[key]};assert all(key in[p['key']for p in specs]for key in changed);new_joint=any(key not in['freq5','q5']for key in changed);before,_=z.render(input_file=R/'primary-0.f32');out=c.render(before);sf.write(folder/'FULL_TRAINING_WIP.wav',out,48000,subtype='FLOAT');(folder/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));row=dict(model=k,component=str(component),training_cases=len(rows),initial=initial_row,selected=current,heldout=held,changed_XML_fields=changed,new_joint_point=new_joint,heldout_mean_gain=float(np.mean([controls[k]['loss']-d['loss']for k,d in zip([1,2],held)])),heldout_passed=bool(new_joint and all(held_ok(d,controls[k])for k,d in zip([1,2],held))),not_adopted=True);results.append(row);(folder/'ASSESSMENT.json').write_text(json.dumps(row,indent=2)+'\n');(R/'COMPLETED_MODEL_REFITS.json').write_text(json.dumps(results,indent=2)+'\n')
 valid=[r for r in results if r['heldout_passed']];winner=max(valid,key=lambda r:r['heldout_mean_gain'])if valid else None;ready=bool(winner and winner['heldout_mean_gain']>.0003);summary=dict(training_cases=sum(r['training_cases']for r in results),winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  n=q.native('MidSideJoint35-validation-native');primary=q.WinVST3('MidSideJoint35-validation-primary');captures=[];members=[]
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_PRIMARY_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native('MidSideJoint35-cold-native-'+str(rep))
    raw,_=n.render();primary.load(R/'PRIMARY.bin');p,_=primary.render(raw);z0,c0=clients[0];z1,c1=clients[1];z0.load(R/'CONTROL_POST.bin');before,_=z0.render(p);old=c0.render(before);d0=assess(old);z1.load(winner['component']);before,_=z1.render(p);new=c1.render(before);d1=assess(new);assert primary.latency()+z0.latency()+z1.latency()==0;captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_dB']-d0['positive_excess_air_dB']))
    for name,y in [('native',raw),('primary',p),('control',old),('candidate',new)]:q.add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_INPUT',raw),('CONTROL',old),('BEFORE_TRIM',before),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('joint_phase_first6_AND_first10_cold2',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);s6=float(delta[:6].std(ddof=1)/np.sqrt(6));s10=float(delta[:10].std(ddof=1)/np.sqrt(10));robust=bool(delta[:6].mean()>max(.0005,3*s6)and delta[:10].mean()>max(.0005,3*s10)and min(delta[10:])>0 and air[:10].mean()<=.02 and max(air[10:])<=.02 and all(held_ok(r['candidate'],r['control'])for r in captures));summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(delta[:6].mean()),first6_SEM=s6,first10_mean_improvement=float(delta[:10].mean()),first10_SEM=s10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(air[:10].mean()),cold2_air_increase=air[10:].tolist(),robust_improvement=robust)
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_PRIMARY_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_Mid_Side_phase_joint35_complete_not_adopted',sufficient_screen=ready,robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_complete35_and_current_numeric_best',error=traceback.format_exc());raise
finally:
 if n is not None:n.close()
 if primary is not None:primary.close()
 for z,c in clients:z.close();c.close()
