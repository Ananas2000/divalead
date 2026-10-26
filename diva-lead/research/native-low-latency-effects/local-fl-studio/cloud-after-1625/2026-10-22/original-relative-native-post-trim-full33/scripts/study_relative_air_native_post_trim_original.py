"""Actual post-ZL native channel trim preserves frequency settings and adds no delay."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,traceback
import numpy as np,soundfile as sf
import relative_air_native_trim_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;H=Path(__file__).resolve().parent;STATE=q.STATE;WinVST3=q.WinVST3;failed=H/'RELATIVE_AIR_PRIMARY_JOINT_RETRY2';assert not json.loads((failed/'completion.json').read_text())['robust_improvement'];assert json.loads((H/'ACTUAL_NATIVE_POST_TRIM_PROBE_VERIFIED/RESULTS.json').read_text())['impulse_added_delay_samples']==0
(R/'CONTROL_PRIMARY.bin').write_bytes((R/'PRIMARY.bin').read_bytes());(R/'PRIMARY.bin').write_bytes((failed/'CANDIDATE_PRIMARY.bin').read_bytes());controls=[];before_trim=[];clients=[];pool=q.queue.Queue();mutex=q.threading.Lock();rows=[];cache=q.threading.local();original_power=q.a.powers
def capture(*args,**kw):
 result=original_power(*args,**kw);cache.power=result[0];return result
q.a.powers=capture
def assess(y):
 d=q.assessment(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_3500_6500_dB']=float(np.maximum(e[:,4:6,2:],0).mean());return d
def record(phase,**extra):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_native_trim_hosts=[c.chain.proc.pid for c in clients],actual_Fruity_Stereo_Shaper_after_two_actual_ZL=True,only_channel_gain_trim_varied=True,relative_primary_fixed_POST32_unchanged=True,source_native10_WS52_Diva281_MIDI3heldnotes_ARP_ADSR_unchanged=True,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);d.update(extra);p=STATE.with_suffix('.partial');p.write_text(json.dumps(d,indent=2)+'\n');p.replace(STATE)
def cascade(raw,p,z,component):
 p.load(component);z.load(R/'CONTROL_POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return out
def eligible(r,k=0,margin=1.46):return r['upper_error']<=margin and max(abs(np.array(r['LR_dB'])[3:]))<=1.6 and r['lowmid_error']<=min(3.25,controls[k]['lowmid_error']+.02)and r['positive_excess_air_3500_6500_dB']<=controls[k]['positive_excess_air_3500_6500_dB']+.02
def evaluate(case,phase=0,keep=True):
 label,v=case;c=pool.get()
 try:
  c.configure(v['left_raw'],v['right_raw']);out=c.render(before_trim[phase]);row=dict(label=label,settings=v,**assess(out))
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put(c)
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(one_ordinary_actual_Fruity_Stereo_Shaper_added_after_ZLs=True,diagonal_channel_gains_only_no_delay_or_crossfeed=True,all_two_ZL_components_fixed=True,original_source_native12_WS52_MIDI3heldnotes_ARP_ADSR_fixed=True,training_upper_LR_RMS_error_margin_dB=1.46,heldout_and_validation_upper_LR_RMS_limit_dB=1.48,original_upper_abs_LR_max_dB=1.6,lowmid_error_max_dB=3.25,paired_lowmid_and_air_increase_max_dB=.02,original_full_score_weights_alignment_unchanged=True,three_new_training_inputs_with_two_heldout=True,first6_AND_first10_gain_over_max_0005_and_3SEM=True,warm10_cold2=True,both_cold_gains_positive=True,same_native_input_per_validation_pair=True,actual_native_trim_identity_and_gain_calibration_and_cold_impulse_proved=True,strict_native_FST_absolute_tolerance=2e-7),indent=2)+'\n')
n=None;working=[];validation_trim=None
try:
 record('three_new_actual_native_and_two_ZL_inputs');n=q.native('RelativeNativeTrim-training-source');p=WinVST3('RelativeNativeTrim-training-primary');z=WinVST3('RelativeNativeTrim-training-post');working=[p,z]
 for k in range(3):
  raw,_=n.render();sf.write(R/f'TRAINING_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');old=cascade(raw,p,z,R/'CONTROL_PRIMARY.bin');controls.append(assess(old));sf.write(R/f'TRAINING_CONTROL_{k}.wav',old,48000,subtype='FLOAT');out=cascade(raw,p,z,R/'PRIMARY.bin');before_trim.append(out);sf.write(R/f'TRAINING_BEFORE_TRIM_{k}.wav',out,48000,subtype='FLOAT')
 n.close();n=None;p.close();z.close();working=[];(R/'CONTROL_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n')
 for k in range(2):c=NativePostTrim(R/'isolated-host-inputs','RelativeNativeTrim-worker-'+str(k));clients.append(c);pool.put(c)
 cases=[]
 for db in[.02,.035,.05,.075,.1,.15,.2,.35,.5]:
  for mode,left,right in[('LeftCut',-db,0.),('RightBoost',0.,db),('Symmetric',-db/2,db/2)]:cases.append((mode+'-'+str(db),dict(mode=mode,requested_left_dB=left,requested_right_dB=right,left_raw=NativePostTrim.raw_from_dB(left),right_raw=NativePostTrim.raw_from_dB(right))))
 with q.concurrent.futures.ThreadPoolExecutor(2)as executor:checked=list(executor.map(evaluate,cases))
 valid=[r for r in checked if eligible(r)];winner=min(valid,key=lambda r:r['loss'])if valid else None;held=[]
 if winner:
  held=[evaluate(('new-heldout-'+str(k),winner['settings']),k,False)for k in[1,2]];clients[0].configure(winner['settings']['left_raw'],winner['settings']['right_raw']);clients[0].save(R/'CANDIDATE_TRIM.bin')
 (R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(R/'HELDOUT.json').write_text(json.dumps(held,indent=2)+'\n');ready=bool(winner and controls[0]['loss']-winner['loss']>.0003 and all(eligible(r,k,1.48)and r['loss']<controls[k]['loss']-.0001 for k,r in zip([1,2],held)));summary=dict(training_cases=len(rows),winner=winner,heldout=held,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  record('twelve_new_native_paired_validation');n=q.native('RelativeNativeTrim-validation-source');p=WinVST3('RelativeNativeTrim-validation-primary');z=WinVST3('RelativeNativeTrim-validation-post');working=[p,z];validation_trim=NativePostTrim(R/'isolated-host-inputs','RelativeNativeTrim-validation-trim');validation_trim.load(R/'CANDIDATE_TRIM.bin');captures=[];members=[]
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_CONTROL_BEFORE_TRIM_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native('RelativeNativeTrim-cold-source-'+str(rep));validation_trim.close();validation_trim=NativePostTrim(R/'isolated-host-inputs','RelativeNativeTrim-cold-trim-'+str(rep));validation_trim.load(R/'CANDIDATE_TRIM.bin')
    raw,_=n.render();old=cascade(raw,p,z,R/'CONTROL_PRIMARY.bin');d0=assess(old);pre=cascade(raw,p,z,R/'PRIMARY.bin');out=validation_trim.render(pre);d1=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_3500_6500_dB']-d0['positive_excess_air_3500_6500_dB']))
    for name,y in[('native',raw),('control',old),('before-trim',pre),('candidate',out)]:q.add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in[('NATIVE_INPUT',raw),('CONTROL',old),('BEFORE_TRIM',pre),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('fresh6_AND_first10_cold2_with_native_trim',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  n.close();n=None;p.close();z.close();working=[];validation_trim.close();validation_trim=None;delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);s6=float(np.std(delta[:6],ddof=1)/np.sqrt(6));s10=float(np.std(delta[:10],ddof=1)/np.sqrt(10));robust=bool(np.mean(delta[:6])>max(.0005,3*s6)and np.mean(delta[:10])>max(.0005,3*s10)and min(delta[10:])>0 and np.mean(air[:10])<=.02 and max(air[10:])<=.02 and all(r['candidate']['upper_error']<=1.48 and max(abs(np.array(r['candidate']['LR_dB'])[3:]))<=1.6 and r['candidate']['lowmid_error']<=min(3.25,r['control']['lowmid_error']+.02)for r in captures));summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=s6,first10_mean_improvement=float(np.mean(delta[:10])),first10_SEM=s10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(np.mean(air[:10])),cold2_air_increase=air[10:].tolist(),robust_improvement=robust)
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_CONTROL_BEFORE_TRIM_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_relative_air_actual_native_trim_complete_not_adopted',sufficient_screen=ready,robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in['winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_full32_and_BEST',error=traceback.format_exc());raise
finally:
 if n is not None:n.close()
 if validation_trim is not None:validation_trim.close()
 for c in working:c.close()
 for c in clients:c.close()
