"""Held-note hard-sync timbre: source gain matched; each proposal scores3 real renders."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,traceback
import numpy as np,soundfile as sf
import Diva_sync_Tune2_mean3_support as q
from mean_three_real_primary_fit import MeanThreePrimaryFit
from native_post_trim import NativePostTrim
R=q.ROOT;STATE=q.STATE;calibration=q.H/'DIVA_LEVEL_MATCHED_SYNC_TUNE2_PROBE';cal=json.loads((calibration/'RESULTS.json').read_text());assert len(cal)==5 and all(d['level_match_within_001dB']for d in cal);baseline_RMS=float(np.sqrt(np.mean(q.baseline_raw.astype(float)**2)));cache=q.threading.local();origpower=q.a.powers;fit=None;n=None;hosts=[];trims=[];results=json.loads((R/"COMPLETED_MODEL_REFITS.json").read_text())if(R/"COMPLETED_MODEL_REFITS.json").exists()else[]
def powers(*args,**kw):
 value=origpower(*args,**kw);cache.power=value[0];return value
q.a.powers=powers
def add_actual_wave(tar,name,y,members):
 stream=q.io.BytesIO();sf.write(stream,y,48000,format='WAV',subtype='FLOAT');data=stream.getvalue();info=q.tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,q.io.BytesIO(data));members.append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
q.add=add_actual_wave
def assess(y):
 d=q.assess(y);error=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(error[:,4:6,2:],0).mean());v=np.array(d['LR_dB']);d['original_stereo_preservation_passed']=bool(np.sqrt(np.mean((v[1:]-q.reference_LR[1:])**2))<=1.48 and max(abs(v[1:]))<=1.6 and abs(v[0]-q.reference_LR[0])<=3.25);d['lowmid_error']=abs(float(v[0]-q.reference_LR[0]));return d
def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),actual_primary_POST_ZL_hosts=[c.child.pid for pair in([]if fit is None else fit.clients)for c in pair]+[c.child.pid for c in hosts],actual_native_trim_hosts=[c.chain.proc.pid for c in trims]+([]if fit is None else[c.chain.proc.pid for c in fit.trims.values()]),mean_three_original_scores_per_primary_training_proposal=True,no_audio_averaging_or_reference_samples_in_synthesis=True,source_change_only_slave_Tune2_and_MainOutput=True,masterTune_HardSync_three_incoming_held_notes_ARP_ADSR_all_other279_Diva_native12_POST_nativeTrim_unchanged=True,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);d.update(kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(STATE)
def cascade(raw,p,z,component,trim):
 p.load(component);z.load(R/'POST.bin');middle,_=p.render(raw);before,_=z.render(middle);assert p.latency()+z.latency()==0;return trim.render(before)
models=[dict(name=row['model']['name'],Tune2=row['model']['values']['Tune2'],Output=row['requested_compensated_output'])for row in cal]
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(models=models,source_only_Tune2_index87_and_MainOutput_index0=True,HardSync2_masterTune1_ARP_ADSR_MIDI3heldnotes_other279Diva_exact=True,MainOutput_level_matching_to_original_synthetic_source_RMS_within001dB=True,native12_POST_nativeTrim_fixed=True,mean_of_same_three_original_criteria_scores_for_every_primary_proposal=True,no_audio_averaging=True,two_additional_unseen_native_inputs_for_heldout=True,training_air_mean_control3_plus001=True,training_lowmid_mean_control3_plus001=True,coarse49_then_full_if_loss_within_control_mean3_plus001=True,PRIMARY_proposal_scale05=True,heldout_screen_pair_mean_gain_over0003=True,final_first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_gains_positive=True,all_stereo148_16_lowmid325_original_gates=True,perpair_lowmid_increase_max002=True,first10_and_bothcold_air_increase_max002=True,source_cold_chunk_audio_all281_MIDI_resave_byte_exact_required=True,latestcontext_full_supported_source_and_FLP_export_required=True),indent=2)+'\n')
try:
 if(R/'CONTROL_ASSESSMENTS.json').exists():
  controls=json.loads((R/'CONTROL_ASSESSMENTS.json').read_text());assert len(controls)==5;marker=json.loads((R/'RESUME_AFTER_EXPORT_WRITER_FIX.json').read_text())
  for name,digest in marker['control_and_component_SHA256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest
  record('reuse_five_original_actual_control_measurements_after_WAV_writer_fix')
 else:
  record('five_actual_native_controls_three_train_two_unseen');n=q.native(q.source['native_input'],'SyncTuneMean3-control-native');p=q.WinVST3('SyncTuneMean3-control-primary');z=q.WinVST3('SyncTuneMean3-control-post');hosts=[p,z];trim=NativePostTrim(R/'buffers','SyncTuneMean3-control-trim',cleanup_on_close=True);trim.load(q.prior['post_native_trim_state']);trims=[trim];controls=[]
  for k in range(5):
   raw,_=n.render();out=cascade(raw,p,z,R/'PRIMARY.bin',trim);controls.append(assess(out));sf.write(R/f'CONTROL_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');sf.write(R/f'CONTROL_FULL_{k}.wav',out,48000,subtype='FLOAT')
  n.close();n=None;p.close();z.close();hosts=[];trim.close();trims=[];(R/'CONTROL_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n')
 control_loss=float(np.mean([d['loss']for d in controls[:3]]));air_cap=float(np.mean([d['positive_excess_air_dB']for d in controls[:3]]))+.01;low_cap=min(3.25,float(np.mean([d['lowmid_error']for d in controls[:3]]))+.01)
 for model in models:
  if any(row['model']['name']==model['name']for row in results):continue
  folder=R/model['name'];folder.mkdir(exist_ok=True);
  if(folder/'SOURCE_PROOF.json').exists()and all((folder/f'TRAINING_NATIVE_{k}.wav').exists()for k in range(5)):
   source=json.loads((folder/'SOURCE_PROOF.json').read_text());native_inputs=[sf.read(folder/f'TRAINING_NATIVE_{k}.wav',dtype='float32',always_2d=True)[0]for k in range(5)];record('resume_interrupted_fit_with_identical_five_native_WAVs',model=model)
  else:
   h2p=folder/'Diva.h2p';h2p.write_text(q.patched({('OSC','Tune2'):model['Tune2'],('main','CcOp'):model['Output']}));source_raw,params=q.actual_Diva(h2p,folder/'actual-Diva');changed={i for i in q.original if params[i]['normalized']!=q.original[i]['normalized']};assert changed=={0,87};level_error=float(20*np.log10(np.sqrt(np.mean(source_raw.astype(float)**2))/baseline_RMS));assert abs(level_error)<=.01;inp=folder/'source-with-tail.wav';sf.write(inp,np.pad(source_raw,((0,32768),(0,0))),48000,subtype='FLOAT');source=dict(source_preset=str(h2p),source_audio=str(folder/'actual-Diva/Diva_source.wav'),source_VST_chunk=str(folder/'actual-Diva/Diva_VST_chunk.bin'),native_input=str(inp),changed_parameters={i:dict(before=q.original[i],after=params[i])for i in changed},level_error_dB=level_error,all281_and12MIDI_audited=True,only_three_held_notes=True,HardSync_masterTune_ARP_ADSR_unchanged=True);(folder/'SOURCE_PROOF.json').write_text(json.dumps(source,indent=2)+'\n');n=q.native(inp,'SyncTuneMean3-'+model['name']+'-native');native_inputs=[]
   for k in range(5):
    raw,_=n.render();native_inputs.append(raw);sf.write(folder/f'TRAINING_NATIVE_{k}.wav',raw,48000,subtype='FLOAT')
   n.close();n=None;
  fit=MeanThreePrimaryFit(folder,R/'PRIMARY.bin',R/'POST.bin',assess,lambda phase,**kw:record('actual_source_Tune2_three_input_primary94_fit',model=model,fit_phase=phase,**kw),native_inputs,q.prior['post_native_trim_state'],air_cap,low_cap)
  for parameter in fit.specs:parameter['step']*=.5
  initial,selected=fit.fit(sweeps=1,abort_after_joint=lambda row:row['loss']>control_loss+.01);held=[fit.evaluate(('unseen-heldout-'+str(k),selected['x']),k,False)for k in[3,4]];p,z=fit.clients[0];fit.configure(p,selected['x']);component=folder/'CANDIDATE_PRIMARY.bin';p.save(component);before,_=p.render(native_inputs[0]);z.load(R/'POST.bin');before,_=z.render(before);out=fit.trims[p.child.pid].render(before);sf.write(folder/'SELECTED_FULL_TRAINING_WIP.wav',out,48000,subtype='FLOAT');(folder/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(fit.rows).encode(),mtime=0));row=dict(model=model,source=source,component=str(component),training_proposals=len(fit.rows),actual_training_cascade_renders=3*len(fit.rows),initial=initial,selected=selected,heldout=held,heldout_mean_improvement=float(np.mean([controls[k]['loss']-d['loss']for k,d in zip([3,4],held)])),heldout_constraints_passed=all(d['original_stereo_preservation_passed']and d['lowmid_error']<=controls[k]['lowmid_error']+.02 and d['positive_excess_air_dB']<=controls[k]['positive_excess_air_dB']+.02 for k,d in zip([3,4],held)),not_adopted=True);results.append(row);(folder/'ASSESSMENT.json').write_text(json.dumps(row,indent=2)+'\n');fit.close();fit=None;(R/'COMPLETED_MODEL_REFITS.json').write_text(json.dumps(results,indent=2)+'\n');record('source_Tune2_mean3_model_completed',model=model,heldout_mean_improvement=row['heldout_mean_improvement'],heldout_constraints_passed=row['heldout_constraints_passed'])
 valid=[r for r in results if r['heldout_constraints_passed']];winner=max(valid,key=lambda r:r['heldout_mean_improvement'])if valid else None;ready=bool(winner and winner['heldout_mean_improvement']>.0003);summary=dict(training_proposals=sum(r['training_proposals']for r in results),actual_training_cascade_renders=sum(r['actual_training_cascade_renders']for r in results),winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False);(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  source=winner['source'];cold,params=q.actual_Diva(Path(source['source_VST_chunk']),R/'cold-source-chunk-replay');want,_=sf.read(source['source_audio'],dtype='float32',always_2d=True);np.testing.assert_array_equal(cold,want);assert params==q.parameters(Path(source['source_audio']).parent/'all281.tsv');assert(R/'cold-source-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(source['source_VST_chunk']).read_bytes();n0=q.native(q.source['native_input'],'SyncTuneMean3-validation-control');n1=q.native(source['native_input'],'SyncTuneMean3-validation-candidate');n=[n0,n1];p=q.WinVST3('SyncTuneMean3-validation-primary');z=q.WinVST3('SyncTuneMean3-validation-post');hosts=[p,z];trim=NativePostTrim(R/'buffers','SyncTuneMean3-validation-trim',cleanup_on_close=True);trim.load(q.prior['post_native_trim_state']);trims=[trim];captures=[];members=[]
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:
     n0.close();n1.close();n0=q.native(q.source['native_input'],'SyncTuneMean3-cold-control-'+str(rep));n1=q.native(source['native_input'],'SyncTuneMean3-cold-candidate-'+str(rep));n=[n0,n1]
    raw0,_=n0.render();old=cascade(raw0,p,z,R/'PRIMARY.bin',trim);d0=assess(old);raw1,_=n1.render();new=cascade(raw1,p,z,winner['component'],trim);d1=assess(new);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_dB']-d0['positive_excess_air_dB']))
    for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',new)]:q.add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('source_Tune2_mean3_first6_AND_first10_cold2',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);s6=float(delta[:6].std(ddof=1)/np.sqrt(6));s10=float(delta[:10].std(ddof=1)/np.sqrt(10));robust=bool(delta[:6].mean()>max(.0005,3*s6)and delta[:10].mean()>max(.0005,3*s10)and min(delta[10:])>0 and air[:10].mean()<=.02 and max(air[10:])<=.02 and all(r['candidate']['original_stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures));summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(delta[:6].mean()),first6_SEM=s6,first10_mean_improvement=float(delta[:10].mean()),first10_SEM=s10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(air[:10].mean()),cold2_air_increase=air[10:].tolist(),source_cold_chunk_audio_all281_MIDI_and_resave_exact=True,robust_improvement=robust)
  with q.tarfile.open(R/'TWELVE_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_source_Tune2_mean3_coadapt_complete_not_adopted',sufficient_screen=ready,robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_complete36_and_current_numeric_best',error=traceback.format_exc());raise
finally:
 if fit is not None:fit.close()
 if n is not None:
  for c in(n if isinstance(n,list)else[n]):c.close()
 for c in hosts:c.close()
 for c in trims:c.close()
