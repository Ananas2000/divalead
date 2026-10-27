"""New joint point: promising WS curve plus actual post-ZL channel trim."""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,json,os,struct,threading,traceback
import numpy as np,soundfile as sf
import Air22_trim_three_inputs_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;N=q.N;STATE=q.STATE;OLD=R.parent/'SIDE_AIR22_PRIMARY_COADAPT';old=json.loads((OLD/'completion.json').read_text());assert not old['robust_improvement']and old['sufficient_screen'];(R/'CONTROL_PRIMARY.bin').write_bytes((R/'PRIMARY.bin').read_bytes());(R/'PRIMARY.bin').write_bytes(Path(old['winner']['component']).read_bytes());assert(R/'PRIMARY.bin').read_bytes()!=(R/'CONTROL_PRIMARY.bin').read_bytes();(R/'CONTROL_TRIM.bin').write_bytes(Path(q.prior['post_native_trim_state']).read_bytes());rows=[];pool=q.queue.Queue();trimhosts=[];controls=[];pre_candidates=[];natives=[];vsts=[];cache=threading.local();origpowers=q.a.powers
def powers(*args,**kw):
 result=origpowers(*args,**kw);cache.power=result[0];return result
q.a.powers=powers
def assess(y):
 d=q.assessment(y);error=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(error[:,4:6,2:],0).mean());return d
def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_native_hosts=[c.proc.pid for c in natives],actual_ZL_hosts=[c.child.pid for c in vsts],actual_native_trim_hosts=[c.chain.proc.pid for c in trimhosts],new_joint_air22_primary_and_post_trim_point=True,three_input_feasible_selection=True,original_is_the_only_target=True,Diva281_three_held_notes_ARP_ADSR_native12_and_POST_unchanged=True,not_adopted=True,reference_match_reached=False);d.update(kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(STATE)
def native(tag,candidate=False):
 c=q.native(tag)
 assert not candidate
 return c
def prefix(raw,p,z,component):
 p.load(component);z.load(R/'CONTROL_POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return out
def wave(name,y):sf.write(R/(name+'.wav'),y,48000,subtype='FLOAT')
def allowed(row,k=0,margin=1.47):return row['upper_error']<=margin and max(abs(np.array(row['LR_dB'])[3:]))<=1.6 and row['lowmid_error']<=min(3.25,controls[k]['lowmid_error']+.02)and row['positive_excess_air_dB']<=controls[k]['positive_excess_air_dB']-.02
def evaluate(case,k=0,keep=True):
 label,settings=case;c=pool.get()
 try:
  c.configure(settings['left_raw'],settings['right_raw']);row=dict(label=label,settings=settings,**assess(c.render(pre_candidates[k])))
  if keep:rows.append(row)
  return row
 finally:pool.put(c)
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(new_candidate_is_air22primary_AND_changed_native_trim_not_retesting_rejected_primary_alone=True,old_negative_first10_floor_study_preserved=True,old_rejected_first10_floor_point=old['winner'],three_existing_byte_verified_training_inputs_same_input_control_and_candidate=True,not_repeating_failed_trim_until_random_pass=True,source_Diva281_ARP_ADSR_three_heldnotes_native12_and_POST_fixed_newPRIMARY94_and_nativeTrim_only=True,actual_original_Fruity_Stereo_Shaper_after_ZLs=True,post_trim_no_crossfeed_no_delay=True,training_phase0_upper_margin_dB=1.465,training_phase1_2_upper_margin_dB=1.475,all_27_models_assessed_on_all_three_preexisting_inputs=True,selected_point_must_differ_from_previously_failed_trim=True,all_validation_upper_RMS_max_dB=1.48,abs_upper_LR_max_dB=1.6,lowmid_error_max_dB=3.25,each_pair_lowmid_increase_limit_dB=.02,training_and_first10_air_reduction_min_dB=.02,both_cold_air_increase_max_dB=0,first6_AND_first10_gain_over_max_0005_3SEM=True,both_cold_gains_positive=True,original_fullscore_weights_alignment_unchanged=True,supported_metadata_latest_context_fullkit_cold_replay_required=True),indent=2)+'\n')
try:
 prior_trim=R.parent/'AIR22_WITH_NATIVE_TRIM';assert not json.loads((prior_trim/'completion.json').read_text())['robust_improvement'];assert(R/'CONTROL_PRIMARY.bin').read_bytes()==(prior_trim/'CONTROL_PRIMARY.bin').read_bytes();assert(R/'PRIMARY.bin').read_bytes()==(prior_trim/'PRIMARY.bin').read_bytes();controls.extend(json.loads((prior_trim/'CONTROL_ASSESSMENTS.json').read_text()));record('reuse_three_actual_training_pairs_different_trim_point_no_retry_of_failed_point')
 for k in range(3):
  y,sr=sf.read(prior_trim/f'TRAINING_CANDIDATE_PRETRIM_{k}.wav',dtype='float32',always_2d=True);assert sr==48000;pre_candidates.append(y)
  for name in ['TRAINING_CONTROL_NATIVE','TRAINING_CONTROL','TRAINING_CANDIDATE_NATIVE','TRAINING_CANDIDATE_PRETRIM']:os.link(prior_trim/(name+'_'+str(k)+'.wav'),R/(name+'_'+str(k)+'.wav'))
 (R/'CONTROL_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n')
 for k in range(2):c=NativePostTrim(R/'buffers','Air22Trim3-fit-'+str(k),cleanup_on_close=True);trimhosts.append(c);pool.put(c)
 settings=q.prior['post_native_trim'];baseL=settings['requested_left_dB'];baseR=settings['requested_right_dB'];cases=[]
 for dl in[-.025,-.015,-.005,.005,.01,.015,.02,.025,.035]:
  for dr in[-.015,0.,.015]:
   l=baseL+dl;r=baseR+dr;cases.append((f'dL{dl}_dR{dr}',dict(requested_left_dB=l,requested_right_dB=r,left_raw=NativePostTrim.raw_from_dB(l),right_raw=NativePostTrim.raw_from_dB(r))))
 with concurrent.futures.ThreadPoolExecutor(2)as ex:checked=list(ex.map(evaluate,cases))
 all_models=[]
 for row in checked:
  held_rows=[evaluate(('heldout-'+str(k)+'-'+row['label'],row['settings']),k,False)for k in[1,2]];assessments=[row,*held_rows];gains=[controls[k]['loss']-r['loss']for k,r in enumerate(assessments)];good=all(allowed(r,k,1.465 if k==0 else 1.475)and gains[k]>.0001 for k,r in enumerate(assessments));all_models.append(dict(training=row,heldout=held_rows,mean_gain=float(np.mean(gains)),all_three_inputs_feasible=good))
 (R/'ALL_THREE_INPUT_MODEL_ASSESSMENTS.json').write_text(json.dumps(all_models,indent=2)+'\n');valid=[r for r in all_models if r['all_three_inputs_feasible']];selected=max(valid,key=lambda r:r['mean_gain'])if valid else None;winner=None if selected is None else selected['training'];held=[]if selected is None else selected['heldout']
 if winner:
  trimhosts[0].configure(winner['settings']['left_raw'],winner['settings']['right_raw']);trimhosts[0].save(R/'CANDIDATE_TRIM.bin')
 ready=bool(selected and selected['mean_gain']>.0003 and(R/'CANDIDATE_TRIM.bin').read_bytes()!=(R/'CONTROL_TRIM.bin').read_bytes()and(R/'CANDIDATE_TRIM.bin').read_bytes()!=(prior_trim/'CANDIDATE_TRIM.bin').read_bytes());summary=dict(training_cases=len(rows),actual_training_DSP_assessments=3*len(rows),winner=winner,heldout=held,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);(R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  record('twelve_new_WS_and_trim_full_chain_validation');n0=native('Air22Trim3-validation-control');natives=[n0];p=q.WinVST3('Air22Trim3-validation-primary');z=q.WinVST3('Air22Trim3-validation-post');vsts=[p,z];oldtrim=NativePostTrim(R/'buffers','Air22Trim3-validation-old',cleanup_on_close=True);oldtrim.load(R/'CONTROL_TRIM.bin');newtrim=NativePostTrim(R/'buffers','Air22Trim3-validation-new',cleanup_on_close=True);newtrim.load(R/'CANDIDATE_TRIM.bin');trimhosts.extend([oldtrim,newtrim]);captures=[];members=[]
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:
     n0.close();n0=native('Air22Trim3-cold-control-'+str(rep));natives=[n0];newtrim.close();newtrim=NativePostTrim(R/'buffers','Air22Trim3-cold-trim-'+str(rep),cleanup_on_close=True);newtrim.load(R/'CANDIDATE_TRIM.bin');trimhosts.append(newtrim)
    raw0,_=n0.render();out0=oldtrim.render(prefix(raw0,p,z,R/'CONTROL_PRIMARY.bin'));d0=assess(out0);raw1=raw0;pre1=prefix(raw1,p,z,R/'PRIMARY.bin');out1=newtrim.render(pre1);d1=assess(out1);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_dB']-d0['positive_excess_air_dB']))
    for name,y in [('native-control',raw0),('native-candidate',raw1),('control',out0),('candidate',out1)]:q.add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',out0),('BEFORE_TRIM',pre1),('CANDIDATE',out1)]:wave(name+'_00',y)
    record('Air22_trim_first6_AND_first10_cold2',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);s6=float(np.std(delta[:6],ddof=1)/np.sqrt(6));s10=float(np.std(delta[:10],ddof=1)/np.sqrt(10));robust=bool(np.mean(delta[:6])>max(.0005,3*s6)and np.mean(delta[:10])>max(.0005,3*s10)and min(delta[10:])>0 and np.mean(air[:10])<=-.02 and max(air[10:])<=0 and all(r['candidate']['upper_error']<=1.48 and max(abs(np.array(r['candidate']['LR_dB'])[3:]))<=1.6 and r['candidate']['lowmid_error']<=min(3.25,r['control']['lowmid_error']+.02)for r in captures));summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=s6,first10_mean_improvement=float(np.mean(delta[:10])),first10_SEM=s10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(np.mean(air[:10])),cold2_air_increase=air[10:].tolist(),robust_improvement=robust)
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
  replay_errors=[]
  expected,_=sf.read(R/'CANDIDATE_00.wav',dtype='float32',always_2d=True);raw,_=sf.read(R/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True)if(R/'NATIVE_INPUT_00.wav').exists()else sf.read(R/'NATIVE_CONTROL_00.wav',dtype='float32',always_2d=True)
  for repeat in range(2):
   freshp=q.WinVST3('Air22Trim3-cold-component-P-'+str(repeat));freshz=q.WinVST3('Air22Trim3-cold-component-Z-'+str(repeat));freshtrim=NativePostTrim(R/'buffers','Air22Trim3-cold-component-native-'+str(repeat),cleanup_on_close=True);freshtrim.load(R/'CANDIDATE_TRIM.bin')
   try:
    again=freshtrim.render(prefix(raw,freshp,freshz,R/'PRIMARY.bin'));np.testing.assert_allclose(again,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);replay_errors.append(float(abs(again-expected).max()));freshp.save(R/('COLD_PRIMARY_'+str(repeat)+'.bin'));freshz.save(R/('COLD_POST_'+str(repeat)+'.bin'));freshtrim.save(R/('COLD_NATIVE_TRIM_'+str(repeat)+'.bin'));assert(R/('COLD_PRIMARY_'+str(repeat)+'.bin')).read_bytes()==(R/'PRIMARY.bin').read_bytes();assert(R/('COLD_POST_'+str(repeat)+'.bin')).read_bytes()==(R/'CONTROL_POST.bin').read_bytes();assert(R/('COLD_NATIVE_TRIM_'+str(repeat)+'.bin')).read_bytes()==(R/'CANDIDATE_TRIM.bin').read_bytes()
   finally:freshp.close();freshz.close();freshtrim.close()
  summary.update(two_independent_actual_ZL_ZL_nativeTrim_cold_replay_errors=replay_errors,cold_component_and_native_trim_state_resaves_byte_exact=True,ZL_added_PDC_frames=0,native_trim_parameters_no_crossfeed_no_delay=True)
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_new_Air22_plus_native_trim_complete_not_adopted',sufficient_screen=ready,robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_confirmed_native10_full33_and_main',error=traceback.format_exc());raise
finally:
 for c in natives:c.close()
 for c in vsts:c.close()
 for c in trimhosts:c.close()
