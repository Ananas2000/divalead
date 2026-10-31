"""Three shared native inputs remove phase-draw confounding during PRIMARY fitting."""
from pathlib import Path
import itertools,csv,struct,time,xml.etree.ElementTree as ET
import datetime,gzip,hashlib,io,json,os,tarfile,traceback
import numpy as np,soundfile as sf
import Joint109_current556_anchor38_support as q
from joint_primary_post_fit import JointPrimaryPostFit
from native_post_trim import NativePostTrim
R=q.ROOT;STATE=q.STATE;fit=n=p=z=trim=None;cache=q.threading.local();origpower=q.a.powers;rows=[];captures=[];members=[];last_progress=0.
def powers(*args,**kw):
 v=origpower(*args,**kw);cache.power=v[0];return v
q.a.powers=powers
def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(e[:,4:6,2:],0).mean());v=np.array(d['LR_dB']);d['original_stereo_preservation_passed']=bool(np.sqrt(np.mean((v[1:]-q.reference_LR[1:])**2))<=1.48 and max(abs(v[1:]))<=1.6 and abs(v[0]-q.reference_LR[0])<=3.25);return d
def record(phase,**kw):
 global last_progress
 if fit is not None and not phase.startswith('failed')and time.monotonic()-last_progress>60:
  with fit.lock:partial=list(fit.rows)
  if partial:
   target=R/'PARTIAL_TRAINING_RESULTS.json.gz';tmp=target.with_suffix('.partial');tmp.write_bytes(gzip.compress(json.dumps(partial).encode(),mtime=0));tmp.replace(target);eligible=[row for row in partial if row['stereo_preservation_passed']]
   if eligible:
    selected_progress=min(eligible,key=lambda row:row['loss']);host,post=fit.pool.get()
    try:fit.apply_to_hosts(host,post,selected_progress['x']);host.save(R/'PROGRESS_PRIMARY.bin');post.save(R/'PROGRESS_POST.bin')
    finally:fit.pool.put((host,post))
    (R/'PROGRESS_NOT_ADOPTED.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),training_cases=len(partial),selected=selected_progress,not_adopted=True,independent_final12_not_yet_confirmed=True),indent=2)+'\n')
  last_progress=time.monotonic()
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),actual_fit_ZL_hosts=[]if fit is None else[c.child.pid for pair in fit.clients for c in pair],actual_fit_trim_hosts=[]if fit is None else[c.chain.proc.pid for c in fit.trims.values()],three_COMMON_native_inputs_for_current556_anchor38_and_every_training_proposal=True,no_audio_averaging=True,source_Diva281_MIDI3held_ARP_ADSR_native12_nativeTrim_unchanged=True,PRIMARY94_plus_existing_POST15_changed=True,original_is_only_target=True,not_adopted=True,reference_match_reached=False,**kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(STATE)
def cascade(raw,component,post_component=None):
 p.load(component);z.load(post_component or R/'POST.bin');mid,_=p.render(raw);before,_=z.render(mid);assert p.latency()+z.latency()==0;return trim.render(before)
def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');data=b.getvalue();info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data));members.append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
assert q.prior['source_accepted_cohort']==556
PUBLIC=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');(R/'ANCHOR38_PRIMARY.bin').write_bytes((PUBLIC/'ZL-WIP38/verification/ZL38_PRIMARY_COMPONENT.bin').read_bytes());assert (PUBLIC/'ZL-WIP38/verification/ZL38_POST_COMPONENT.bin').read_bytes()==(R/'POST.bin').read_bytes()
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(no_source_native_MIDI_or_trim_change=True,existing_PRIMARY94_and_POST15_jointly_fitted=True,no_added_filter_or_plugin=True,three_exact_same_native_realizations_shared_by_control_and_every_primary_proposal=True,no_averaged_audio=True,two_additional_unseen_native_inputs=True,three_primary_coordinate_sweeps=True,PRIMARY_step_scale1=True,training_Air_mean_min_current556_anchor38_MINUS0003dB=True,feasible_seed64_linked_gain_target_grid_before109fit=True,seed_deltas=[0.,-.02,-.04,-.08],both_hosts_neutral_identity_required=True,training_lowmid_mean_control_plus0005dB=True,heldout_pair_mean_gain_over0003=True,newfirst6_AND_first10_gain_over_max0005_3SEM=True,bothcold_gains_positive=True,all12_upper148_abs16_lowmid325_eachpaired_lowmid_plus002=True,first10_and_bothcold_air_nonpositive_vs_BOTH_current556_and_anchor38_required=True,EXTRA_first10_TONE_score_nonincreasing_vs556=True,original_target_loss_and_latest556_positive_gates_not_replaced_by_anchor38_comparison=True,latest_context_revalidation_and_full_supported_export_before_adoption=True),indent=2)+'\n')
try:
 record('actual_Diva_current_source_replay_before_fit');source_now,parameters_now=q.actual_Diva(Path(q.source['source_preset']),R/'CURRENT_DIVA_REAL_RUN');np.testing.assert_array_equal(source_now,q.baseline_raw);assert parameters_now==q.original;(R/'CURRENT_DIVA_EXACT_SOURCE_PROOF.json').write_text(json.dumps(dict(actual_Diva_executed=True,all281_parameters_and12MIDI_events_unchanged=True,source_audio_array_exact=True,source_preset_SHA256=q.source['source_preset_SHA256'],only_three_held_notes=True),indent=2)+'\n');record('five_actual_native_common_inputs_control_and_primary');n=q.native(q.source['native_input'],'Oct31Joint109-556-'+str(os.getpid())+'-native');p=q.WinVST3('Oct31Joint109-556-'+str(os.getpid())+'-primary');z=q.WinVST3('Oct31Joint109-556-'+str(os.getpid())+'-post');trim=NativePostTrim(R/'buffers','Oct31Joint109-556-'+str(os.getpid())+'-trim',cleanup_on_close=True);trim.load(q.prior['post_native_trim_state']);inputs=[];controls=[];anchors=[]
 for k in range(5):
  raw,_=n.render();inputs.append(raw);out=cascade(raw,R/'PRIMARY.bin');controls.append(assess(out));anchor=cascade(raw,R/'ANCHOR38_PRIMARY.bin');anchors.append(assess(anchor));sf.write(R/f'TRAINING_ANCHOR38_{k}.wav',anchor,48000,subtype='FLOAT');sf.write(R/f'TRAINING_NATIVE_{k}.wav',raw,48000,subtype='FLOAT');sf.write(R/f'TRAINING_CONTROL556_{k}.wav',out,48000,subtype='FLOAT')
 n.close();n=None;(R/'CONTROL556_ASSESSMENTS.json').write_text(json.dumps(controls,indent=2)+'\n');(R/'ANCHOR38_ASSESSMENTS.json').write_text(json.dumps(anchors,indent=2)+'\n');air_cap=min(float(np.mean([d['positive_excess_air_dB']for d in controls[:3]])),float(np.mean([d['positive_excess_air_dB']for d in anchors[:3]])))-.003;low_cap=min(3.25,float(np.mean([d['lowmid_error']for d in controls[:3]]))+.005)
 blob=(R/'PRIMARY.bin').read_bytes();xml=ET.fromstring(blob[8:8+struct.unpack_from('<I',blob,4)[0]]);origin={v.attrib['id']:float(v.attrib['value'])for v in xml.find('Para')};ids={v['title']:int(v['id'])for v in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')};seed_rows=[]
 def set_seed(delta):
  p.load(R/'PRIMARY.bin');z.load(R/'POST.bin')
  for band,shift in zip([20,21,22],delta):
   if shift:
    for title,key in [('Gain','gain'),('Target Gain','target_gain')]:p.text(ids[title+str(band)],format(origin[key+str(band)]+shift,'.12g'))
 for delta in itertools.product([0.,-.02,-.04,-.08],repeat=3):
  ds=[]
  for k in range(3):set_seed(delta);mid,_=p.render(inputs[k]);pre,_=z.render(mid);ds.append(assess(trim.render(pre)))
  row=dict(delta=list(delta),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['positive_excess_air_dB']for d in ds])),captures=ds,feasible=all(d['original_stereo_preservation_passed']and d['lowmid_error']<=controls[k]['lowmid_error']+.005 for k,d in enumerate(ds))and float(np.mean([d['positive_excess_air_dB']for d in ds]))<=air_cap);seed_rows.append(row)
  if len(seed_rows)%8==0:record('actual64_feasible_seed_grid_vs_current556_and_anchor38',completed_seed_cases=len(seed_rows),Air_cap=air_cap)
 (R/'SEED64_ACTUAL_RESULTS.json').write_text(json.dumps(seed_rows,indent=2)+'\n');valid_seed=[d for d in seed_rows if d['feasible']];assert valid_seed,'No seed reaches declared Air/stereo constraints; preserve data, do not weaken gates';seed=min(valid_seed,key=lambda d:d['loss']);set_seed(seed['delta']);p.save(R/'FIT_SEED_PRIMARY.bin');(R/'SELECTED_FEASIBLE_SEED.json').write_text(json.dumps(seed,indent=2)+'\n');mid,_=p.render(inputs[0]);pre,_=z.render(mid);sf.write(R/'FEASIBLE_SEED_FULL_WIP.wav',trim.render(pre),48000,subtype='FLOAT');p.close();p=None;z.close();z=None;trim.close();trim=None

 fit=JointPrimaryPostFit(R,R/'FIT_SEED_PRIMARY.bin',R/'POST.bin',assess,record,inputs,q.prior['post_native_trim_state'],air_cap,low_cap)
 fit.check_neutral_identity()
 initial,selected=fit.fit(sweeps=3);held=[fit.evaluate(('unseen-heldout-'+str(k),selected['x']),k,False)for k in[3,4]];p0,z0=fit.clients[0];fit.apply_to_hosts(p0,z0,selected['x']);component=R/'CANDIDATE_PRIMARY.bin';post_component=R/'CANDIDATE_POST.bin';p0.save(component);z0.save(post_component);p0.load(component);z0.load(post_component);p0.save(R/'PRIMARY_RESAVED.bin');z0.save(R/'POST_RESAVED.bin');assert component.read_bytes()==(R/'PRIMARY_RESAVED.bin').read_bytes();assert post_component.read_bytes()==(R/'POST_RESAVED.bin').read_bytes();mid,_=p0.render(inputs[0]);before,_=z0.render(mid);out=fit.trims[p0.child.pid].render(before);sf.write(R/'SELECTED_FULL_TRAINING_WIP.wav',out,48000,subtype='FLOAT');(R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(fit.rows).encode(),mtime=0));gain=float(np.mean([controls[k]['loss']-d['loss']for k,d in zip([3,4],held)]));held_ok=all(d['original_stereo_preservation_passed']and d['lowmid_error']<=controls[k]['lowmid_error']+.02 and d['positive_excess_air_dB']<=min(controls[k]['positive_excess_air_dB'],anchors[k]['positive_excess_air_dB'])+.02 for k,d in zip([3,4],held));summary=dict(training_cases=len(fit.rows),actual_training_DSP_renders=3*len(fit.rows),initial=initial,selected=selected,heldout=held,heldout_mean_gain=gain,heldout_constraints_passed=held_ok,component=str(component),post_component=str(post_component),sufficient_screen=bool(gain>.0003 and held_ok),robust_improvement=False,not_adopted=True,reference_match_reached=False);fit.close();fit=None;(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n');record('frozen_after_three_sweeps_before_any_new_validation',heldout_mean_gain=gain,sufficient_screen=summary['sufficient_screen'])
 if summary['sufficient_screen']:
  assert q.shutil.disk_usage('/workspace').free>192*2**20 and q.shutil.disk_usage('/tmp').free>64*2**20,'Frozen promising point retained; storage reserve required before twelve-pair capture'
  n=q.native(q.source['native_input'],'Oct31Joint109-556-'+str(os.getpid())+'-validation-native');p=q.WinVST3('Oct31Joint109-556-'+str(os.getpid())+'-validation-primary');z=q.WinVST3('Oct31Joint109-556-'+str(os.getpid())+'-validation-post');trim=NativePostTrim(R/'buffers','Oct31Joint109-556-'+str(os.getpid())+'-validation-trim',cleanup_on_close=True);trim.load(q.prior['post_native_trim_state'])
  archive=Path('/tmp/divalead-joint109-current556-anchor38-'+str(os.getpid())+'.tar.gz');(R/'TWELVE_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(archive)
  with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'Oct31Joint109-556-'+str(os.getpid())+'-cold-native-'+str(rep))
    raw,_=n.render();old=cascade(raw,R/'PRIMARY.bin');d0=assess(old);anchor=cascade(raw,R/'ANCHOR38_PRIMARY.bin');da=assess(anchor);new=cascade(raw,component,post_component);d1=assess(new);captures.append(dict(rep=rep,control=d0,anchor38=da,candidate=d1,improvement=d0['loss']-d1['loss'],air_increase=d1['positive_excess_air_dB']-d0['positive_excess_air_dB'],Air_delta_vs_anchor38=d1['positive_excess_air_dB']-da['positive_excess_air_dB']))
    for name,y in [('native',raw),('control556',old),('anchor38',anchor),('candidate',new)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in [('NATIVE_INPUT',raw),('CONTROL556',old),('ANCHOR38',anchor),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('actual_first6_AND_first10_two_cold_common_input_validation',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([r['improvement']for r in captures]);air=np.array([r['air_increase']for r in captures]);air_anchor=np.array([r['Air_delta_vs_anchor38']for r in captures]);tone_delta=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));sem6=float(delta[:6].std(ddof=1)/np.sqrt(6));sem10=float(delta[:10].std(ddof=1)/np.sqrt(10));guard=all(r['candidate']['original_stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(delta[:6].mean()>max(.0005,3*sem6)and delta[:10].mean()>max(.0005,3*sem10)and min(delta[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and air_anchor[:10].mean()<=0 and max(air_anchor[10:])<=0 and tone_delta<=0 and guard);summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(delta[:6].mean()),first6_SEM=sem6,first10_mean_improvement=float(delta[:10].mean()),first10_SEM=sem10,cold2_improvements=delta[10:].tolist(),first10_air_increase=float(air[:10].mean()),cold2_air_increase=air[10:].tolist(),first10_Air_delta_vs_anchor38=float(air_anchor[:10].mean()),cold2_Air_delta_vs_anchor38=air_anchor[10:].tolist(),first10_TONE_delta_vs556=tone_delta,all12_original_stereo_lowmid_guards=guard,robust_improvement=robust)
  with tarfile.open(archive)as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'COMBINED_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(dict(q.prior,native_ZL_component_state=str(component),post_ZL_component_state=str(post_component),not_adopted_until_supported_full_export=True,requires_latest_BEST_revalidation=True),indent=2)+'\n');(R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_primary_mean3_common_input_complete_not_adopted',robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in ['initial','selected','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current556_and_full38_anchor',error=traceback.format_exc());raise
finally:
 if fit is not None:fit.close()
 for c in[n,p,z,trim]:
  if c is not None:c.close()
