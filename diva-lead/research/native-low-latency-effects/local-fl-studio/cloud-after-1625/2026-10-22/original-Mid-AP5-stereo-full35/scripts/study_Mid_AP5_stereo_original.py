"""Actual extra zero-PDC Side dynamic band: reduce quiet HF without changing MIDI."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,threading,traceback
import numpy as np,soundfile as sf
import Mid_AP5_stereo_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;STATE=q.STATE;original_post=q.values(R/'CONTROL_POST.bin');assert original_post['filter_status5']==0;cache=threading.local();origpower=q.a.powers;rows=[];n=None;p=z=trim=None
def powers(*args,**kw):
 result=origpower(*args,**kw);cache.power=result[0];return result
q.a.powers=powers
def assess(y):
 d=q.assessment(y);error=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(error[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_error']<=1.48 and max(abs(np.array(d['LR_dB'])[3:]))<=1.6 and d['lowmid_error']<=3.25);return d
def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_native_prefix_host=None if n is None else n.proc.pid,actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],actual_native_post_trim_host=None if trim is None else trim.chain.proc.pid,new_POST_Mid_AllPass5_only=True,original_is_the_only_target=True,source_Diva281_three_held_notes_ARP_ADSR_native12_PRIMARY_existing_POST_bands_native_post_trim_unchanged=True,not_adopted=True,reference_match_reached=False);d.update(kw);temp=STATE.with_suffix('.partial');temp.write_text(json.dumps(d,indent=2)+'\n');temp.replace(STATE)
def cascade(raw,component):
 p.load(R/'PRIMARY.bin');z.load(component);mid,_=p.render(raw);before,_=z.render(mid);assert p.latency()+z.latency()==0;return trim.render(before)
def allowed(d,c):return d['stereo_preservation_passed']and d['lowmid_error']<=c['lowmid_error']-.25
models=[{'frequency': 200.0, 'Q': 0.3}, {'frequency': 200.0, 'Q': 0.6}, {'frequency': 200.0, 'Q': 1.2}, {'frequency': 200.0, 'Q': 2.4}, {'frequency': 200.0, 'Q': 4.8}, {'frequency': 200.0, 'Q': 9.6}, {'frequency': 350.0, 'Q': 0.3}, {'frequency': 350.0, 'Q': 0.6}, {'frequency': 350.0, 'Q': 1.2}, {'frequency': 350.0, 'Q': 2.4}, {'frequency': 350.0, 'Q': 4.8}, {'frequency': 350.0, 'Q': 9.6}, {'frequency': 500.0, 'Q': 0.3}, {'frequency': 500.0, 'Q': 0.6}, {'frequency': 500.0, 'Q': 1.2}, {'frequency': 500.0, 'Q': 2.4}, {'frequency': 500.0, 'Q': 4.8}, {'frequency': 500.0, 'Q': 9.6}, {'frequency': 650.0, 'Q': 0.3}, {'frequency': 650.0, 'Q': 0.6}, {'frequency': 650.0, 'Q': 1.2}, {'frequency': 650.0, 'Q': 2.4}, {'frequency': 650.0, 'Q': 4.8}, {'frequency': 650.0, 'Q': 9.6}, {'frequency': 1000.0, 'Q': 0.3}, {'frequency': 1000.0, 'Q': 0.6}, {'frequency': 1000.0, 'Q': 1.2}, {'frequency': 1000.0, 'Q': 2.4}, {'frequency': 1000.0, 'Q': 4.8}, {'frequency': 1000.0, 'Q': 9.6}, {'frequency': 1800.0, 'Q': 0.3}, {'frequency': 1800.0, 'Q': 0.6}, {'frequency': 1800.0, 'Q': 1.2}, {'frequency': 1800.0, 'Q': 2.4}, {'frequency': 1800.0, 'Q': 4.8}, {'frequency': 1800.0, 'Q': 9.6}, {'frequency': 3000.0, 'Q': 0.3}, {'frequency': 3000.0, 'Q': 0.6}, {'frequency': 3000.0, 'Q': 1.2}, {'frequency': 3000.0, 'Q': 2.4}, {'frequency': 3000.0, 'Q': 4.8}, {'frequency': 3000.0, 'Q': 9.6}, {'frequency': 6000.0, 'Q': 0.3}, {'frequency': 6000.0, 'Q': 0.6}, {'frequency': 6000.0, 'Q': 1.2}, {'frequency': 6000.0, 'Q': 2.4}, {'frequency': 6000.0, 'Q': 4.8}, {'frequency': 6000.0, 'Q': 9.6}]
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(models=models,only_enable_unused_POST_MidAllPass_slot5=True,source_PRIMARY_native12_MIDI_three_held_notes_ARP_ADSR_and_post_nativeTrim_unchanged=True,same_three_new_native_inputs_for_all_models=True,extra_each_pair_lowmid_balance_error_reduction_dB=.25,original_fullscore_weights_alignment_unchanged=True,upperRMS148_abs16_lowmid325=True,first6_AND_first10_gain_over_max0005_3SEM=True,both_cold_gains_positive=True,first10_AND_bothcold_air_increase_limit_dB=.02,fullkit_latestcontext_and_coldreplay_required=True),indent=2)+'\n')
try:
 n=q.native('MidAP5-training-native');p=q.WinVST3('MidAP5-primary');z=q.WinVST3('MidAP5-post');trim=NativePostTrim(R/'buffers','MidAP5-native-posttrim',cleanup_on_close=True);trim.load(q.prior['post_native_trim_state']);native_inputs=[];controls=[];record('three_new_native_controls_for_side_air_band22')
 for k in range(3):
  raw,_=n.render();native_inputs.append(raw);out=cascade(raw,R/'CONTROL_POST.bin');controls.append(assess(out));sf.write(R/f'TRAINING_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');sf.write(R/f'TRAINING_CONTROL_{k}.wav',out,48000,subtype='FLOAT')
 n.close();n=None;(R/'CONTROL_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n')
 for k,model in enumerate(models):
  folder=R/f'model-{k:02}';folder.mkdir();z.load(R/'CONTROL_POST.bin')
  for title,value in [('Filter Status',1),('Filter Type',.9),('LRMode',.75),('Order',1/6),('Dynamic ON',0)]:z.set(q.params[title+'5'],value)
  for title,value in [('Freq',model['frequency']),('Q',model['Q']),('Gain',0.)]:z.text(q.params[title+'5'],str(value))
  component=folder/'POST_MODEL.bin';z.save(component);now=q.values(component);changed={key:[old,now[key]]for key,old in original_post.items()if now[key]!=old};assert all(key.endswith('5')for key in changed);assert now['filter_status5']==2 and now['filter_type5']==9 and now['dynamic_on5']==0 and now['lr_mode5']==3;captures=[]
  for phase,raw in enumerate(native_inputs):
   out=cascade(raw,component);d=assess(out);captures.append(d)
   if phase==0:sf.write(folder/'FULL_TRAINING_WIP.wav',out,48000,subtype='FLOAT')
  delta=np.array([c['loss']-d['loss']for c,d in zip(controls,captures)]);air=np.array([d['positive_excess_air_dB']-c['positive_excess_air_dB']for c,d in zip(controls,captures)]);row=dict(model=model,component=str(component),changed_XML_fields=changed,captures=captures,mean_improvement=float(delta.mean()),mean_air_increase=float(air.mean()),eligible=bool(delta.mean()>.0003 and min(delta[1:])>0 and air.mean()<=.02 and all(allowed(d,c)for c,d in zip(controls,captures))),not_adopted=True);rows.append(row);(folder/'ASSESSMENT.json').write_text(json.dumps(row,indent=2)+'\n');record('actual_Mid_AP5_model_rendered',model=model,mean_gain=row['mean_improvement'],air_increase=row['mean_air_increase'],eligible=row['eligible'])
 eligible=[r for r in rows if r['eligible']];winner=max(eligible,key=lambda r:r['mean_improvement'])if eligible else None;ready=winner is not None;summary=dict(training_cases=len(rows),winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);(R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  n=q.native('MidAP5-validation-native');captures=[];members=[]
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native('MidAP5-cold-native-'+str(rep))
    raw,_=n.render();old=cascade(raw,R/'CONTROL_POST.bin');d0=assess(old);new=cascade(raw,winner['component']);d1=assess(new);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_dB']-d0['positive_excess_air_dB']))
    for name,y in [('native',raw),('control',old),('candidate',new)]:q.add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_INPUT',raw),('CONTROL',old),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('Mid_AP5_first6_AND_first10_cold2',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);s6=float(delta[:6].std(ddof=1)/np.sqrt(6));s10=float(delta[:10].std(ddof=1)/np.sqrt(10));robust=bool(delta[:6].mean()>max(.0005,3*s6)and delta[:10].mean()>max(.0005,3*s10)and min(delta[10:])>0 and air[:10].mean()<=.02 and max(air[10:])<=.02 and all(allowed(r['candidate'],r['control'])for r in captures));summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(delta[:6].mean()),first6_SEM=s6,first10_mean_improvement=float(delta[:10].mean()),first10_SEM=s10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(air[:10].mean()),cold2_air_increase=air[10:].tolist(),robust_improvement=robust)
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_new_Mid_AP5_original_stereo_complete_not_adopted',sufficient_screen=ready,robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_full33_current_best',error=traceback.format_exc());raise
finally:
 if n is not None:n.close()
 if p is not None:p.close()
 if z is not None:z.close()
 if trim is not None:trim.close()
