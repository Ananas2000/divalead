"""Validate a saved progress preset from an interrupted fit; no search rerun or pooling."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import recovered_OS17_support as q
from native_post_trim import NativePostTrim
V=Path(__file__).resolve().parent;R=q.ROOT;OLD=Path('/tmp/divalead-OS-local17-joint109-left004-current39-20261031');progress=json.loads((OLD/'PROGRESS_NOT_ADOPTED.json').read_text());assert progress['training_cases']==897;assert progress['selected']['stereo_preservation_passed'];assert q.prior['native_base']['native_saved_state_bundle']['settings_SHA256']==json.loads((OLD/'PRIOR_COMBINED_CANDIDATE.json').read_text())['native_base']['native_saved_state_bundle']['settings_SHA256'];cache=threading.local();power=q.a.powers;c0=c1=p=z=t=None;captures=[];members=[]
for source,target in [('PROGRESS_PRIMARY.bin','CANDIDATE_PRIMARY.bin'),('PROGRESS_POST.bin','CANDIDATE_POST.bin'),('CANONICAL_OS_LOCAL17_WS.bin','CANDIDATE_WS.bin'),('CANDIDATE_NATIVE_POST_TRIM_LEFT004.bin','CANDIDATE_NATIVE_TRIM.bin'),('GUI_OS_PARENT_NATIVE11.bin','GUI_OS_PARENT_NATIVE11.bin'),('CANONICAL_POINT_AND_FLOAT32_RECIPE.json','CANONICAL_POINT_AND_FLOAT32_RECIPE.json')]:shutil.copyfile(OLD/source,R/target)
(R/'ANCHOR39_PRIMARY.bin').write_bytes((OLD/'ANCHOR39_PRIMARY.bin').read_bytes());assert (OLD/'POST.bin').read_bytes()==(R/'POST.bin').read_bytes()

def powers(*args,**kw):v=power(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(e[:,4:6,2:],0).mean());d['original_stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),frozen_current_cohort=q.prior['source_accepted_cohort'],recovered_training_records=897,original_fit_interrupted_not_complete=True,actual_native_hosts=[c.proc.pid for c in[c0,c1]if c],actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],only_three_held_notes=True,original_WAV_is_only_target=True,source_Diva_ARP_ADSR_MIDI_other11_native_unchanged=True,not_adopted=True,reference_match_reached=False,**kw);temp=q.STATE.with_suffix('.partial');temp.write_text(json.dumps(d,indent=2)+'\n');temp.replace(q.STATE)

def cascade(raw,candidate=False,anchor=False):
 primary=R/'CANDIDATE_PRIMARY.bin'if candidate else R/'ANCHOR39_PRIMARY.bin'if anchor else R/'PRIMARY.bin';post=R/'CANDIDATE_POST.bin'if candidate else R/'POST.bin';trim=R/'CANDIDATE_NATIVE_TRIM.bin'if candidate else Path(q.prior['post_native_trim_state']);p.load(primary);z.load(post);t.load(trim);mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def native(tag,candidate):
 c=q.native(q.source['native_input'],tag)
 if candidate:c.load_state(0,R/'CANDIDATE_WS.bin')
 return c

def add(tar,name,y):
 stream=io.BytesIO();sf.write(stream,y,48000,format='WAV',subtype='FLOAT');b=stream.getvalue();entry=tarfile.TarInfo(name);entry.size=len(b);tar.addfile(entry,io.BytesIO(b));members.append(dict(name=name,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(recovered_point_fixed_before_testing_unused_inputs=True,original_897_recorded_search_not_claimed_completed=True,no_search_rerun=True,stored_inputs3_and4_unused_by_training=True,heldout_mean_gain_over0003_and_original_constraints=True,then_entirely_new12_pairs=True,final_first6AND10_mean_gain_over_max0005_3SEM=True,bothcold_positive=True,strictAir_first10_and_bothcold_nonincreasing_vs_current_and_full39=True,TONEfirst10_nonincreasing=True,all_stereo148_abs16_lowmid325_and_eachpaired_lowmid002=True,all_presets_roundtrip_exact_and_native_two_zeroDepth_cold_replay=True,no_pooling_with_any_Oct31_validation=True,latest_context_supported_metadata_full_FL20_export_coldZIP_and_publication_before_adoption=True),indent=2)+'\n')
try:
 record('cold_actual_saved_state_and_training_point_replay');p=q.WinVST3('Nov4Recovered-P-'+str(os.getpid()));z=q.WinVST3('Nov4Recovered-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Nov4Recovered-Trim-'+str(os.getpid()),cleanup_on_close=True)
 for host,path,name in[(p,R/'CANDIDATE_PRIMARY.bin','PRIMARY'),(z,R/'CANDIDATE_POST.bin','POST'),(t,R/'CANDIDATE_NATIVE_TRIM.bin','TRIM')]:host.load(path);dst=R/(name+'_RESAVED.bin');host.save(dst);assert dst.read_bytes()==path.read_bytes()
 training=[]
 for k in range(3):
  raw,sr=sf.read(OLD/f'TRAINING_OS_NATIVE_{k}.wav',dtype='float32',always_2d=True);assert sr==48000;out=cascade(raw,candidate=True);training.append(assess(out));
  if k==0:sf.write(R/'RECOVERED_SAVED_PRESET_TRAINING_WIP.wav',out,48000,subtype='FLOAT')
 oldloss=progress['selected']['loss'];newloss=float(np.mean([d['loss']for d in training]));(R/'RECOVERED_TRAINING_POINT_REPLAY.json').write_text(json.dumps(dict(original_recorded_mean=oldloss,current_cold_saved_preset_mean=newloss,absolute_difference=abs(newloss-oldloss),same_exact_recorded_native_inputs=True,original_states_resaved_byte_exact=True),indent=2)+'\n')
 record('two_previously_unused_recorded_inputs');held=[]
 for k in[3,4]:
  raw0,sr=sf.read(OLD/f'TRAINING_NATIVE_{k}.wav',dtype='float32',always_2d=True);raw1,_=sf.read(OLD/f'TRAINING_OS_NATIVE_{k}.wav',dtype='float32',always_2d=True);old=cascade(raw0);d0=assess(old);anc=cascade(raw0,anchor=True);da=assess(anc);new=cascade(raw1,candidate=True);d1=assess(new);held.append(dict(input=k,control=d0,anchor39=da,candidate=d1,gain=d0['loss']-d1['loss']));sf.write(R/f'UNSEEN_CANDIDATE_{k}.wav',new,48000,subtype='FLOAT')
 gain=float(np.mean([d['gain']for d in held]));held_ok=all(r['candidate']['original_stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 and r['candidate']['positive_excess_air_dB']<=min(r['control']['positive_excess_air_dB'],r['anchor39']['positive_excess_air_dB'])+.02 for r in held);ready=bool(gain>.0003 and held_ok);summary=dict(recovered_original_training_records=897,original_search_interrupted=True,recorded_point_replay_loss_difference=abs(newloss-oldloss),heldout=held,heldout_mean_gain=gain,heldout_constraints_passed=held_ok,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_comparator=q.prior['source_accepted_cohort']);(R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  record('two_fresh_actual_native_zeroDepth_preset_replays');expected=None;errors=[];manifest=[];bundle=q.seed['native_saved_state_bundle']
  for k in range(2):
   c=native('Nov4Recovered-NativeProof-'+str(k)+'-'+str(os.getpid()),True)
   try:
    for row in bundle['manifest']:
     dst=R/'saved-native-bundle'/row['state'];dst.parent.mkdir(parents=True,exist_ok=True);c.save_state(row['node'],dst);want=(R/'CANDIDATE_WS.bin').read_bytes()if row['node']==0 else(Path(bundle['directory'])/row['state']).read_bytes();assert dst.read_bytes()==want
     if k==0:manifest.append(dict(row,state_bytes=len(want),state_SHA256=hashlib.sha256(want).hexdigest()))
    c.set(3,1,0);out,status=c.render()
    if k==0:expected=out.copy();sf.write(R/'DETERMINISTIC_NATIVE_ZERO_DEPTH.wav',out,48000,subtype='FLOAT')
    error=float(abs(out-expected).max());assert error<=2e-7;errors.append(error)
   finally:c.close()
  (R/'NATIVE_CANONICAL_COLD_REPLAY_PROOF.json').write_text(json.dumps(dict(two_new_native_zeroDepth_errors=errors,all12_native_resaves_exact=True,native_plugin_manifest=manifest,source_Diva_and_other11_native_unchanged=True,supported_export_pending=True),indent=2)+'\n');assert q.shutil.disk_usage('/workspace').free>192*2**20
  c0=native('Nov4Recovered-Control-'+str(os.getpid()),False);c1=native('Nov4Recovered-Candidate-'+str(os.getpid()),True);archive=Path('/tmp/divalead-Nov4-recovered-OS17-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL60_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(archive)
  with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:c0.close();c1.close();c0=native('Nov4Recovered-ColdControl-'+str(rep)+'-'+str(os.getpid()),False);c1=native('Nov4Recovered-ColdCandidate-'+str(rep)+'-'+str(os.getpid()),True)
    raw0,_=c0.render();old=cascade(raw0);d0=assess(old);anc=cascade(raw0,anchor=True);da=assess(anc);raw1,_=c1.render();new=cascade(raw1,candidate=True);d1=assess(new);captures.append(dict(rep=rep,control=d0,anchor39=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['positive_excess_air_dB']-d0['positive_excess_air_dB'],Air_delta_vs39=d1['positive_excess_air_dB']-da['positive_excess_air_dB']))
    for name,y in[('native-control',raw0),('native-candidate',raw1),('control',old),('anchor39',anc),('candidate',new)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in[('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('ANCHOR39',anc),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(captures,indent=2)+'\n');record('actual_entirely_new12_pairs',completed_pairs=rep+1,latest_gain=captures[-1]['gain'])
  delta=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);aa=np.array([r['Air_delta_vs39']for r in captures]);sem6=float(delta[:6].std(ddof=1)/np.sqrt(6));sem10=float(delta[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guards=all(r['candidate']['original_stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(delta[:6].mean()>max(.0005,3*sem6)and delta[:10].mean()>max(.0005,3*sem10)and min(delta[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guards)
  with tarfile.open(archive)as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
  summary.update(captures=captures,archive_members=members,first6_gain=float(delta[:6].mean()),first6_SEM=sem6,first10_gain=float(delta[:10].mean()),first10_SEM=sem10,cold2_gains=delta[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs39=float(aa[:10].mean()),cold2_Air_delta_vs39=aa[10:].tolist(),first10_TONE_delta=tone,all12_stereo_and_pairedlowmid=guards,robust_improvement=robust)
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('recovered_point_validation_complete_not_adopted',robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in['heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current565_and_recovered_data',error=traceback.format_exc());raise
finally:
 for c in[c0,c1,p,z,t]:
  if c is not None:c.close()
