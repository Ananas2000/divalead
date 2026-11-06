"""Actual Preamp/Mix/Post native controls in accepted canonical oversampled context."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import native12_controls_support as q
from native_post_trim import NativePostTrim
from fl20_curve import native_dsp_settings_SHA256
V=Path(__file__).resolve().parent;R=q.ROOT;assert q.prior['full_public_kit_directory']=='ZL-WIP40';c=p=z=t=None;cache=threading.local();origpower=q.a.powers;rows=[];captures=[];members=[]
base_state=Path(q.seed['native_saved_state_bundle']['directory'])/'verification/SOURCE_WaveShaper.bin';assert q.seed['waveshaper_native_controls']==[128,128,128];shutil.copyfile(base_state,R/'BASE_WS.bin')
anchor=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin');shutil.copyfile(anchor,R/'ANCHOR40_PRIMARY.bin')
controls=[[128,128,128]]+[[128+d,128,128]for d in[-4,-2,-1,1,2,4]]+[[128,m,128]for m in[127,126,124]]+[[128,128,g]for g in[127,126]]+[[127,127,128],[129,126,127],[130,124,126],[126,126,128]]
def powers(*args,**kw):v=origpower(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(e[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),frozen_comparator=q.prior['source_accepted_cohort'],actual_native_host=None if c is None else c.proc.pid,actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],actual_native_trim_host=None if t is None else t.chain.proc.pid,source_Diva_ARP_ADSR_MIDI3_other11_native_bothZL_trim_unchanged=True,only_WS_Preamp_Mix_Post_changed=True,original_is_only_target=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def configure(vals):
 c.load_state(0,R/'BASE_WS.bin')
 for j,value in enumerate(vals):c.set(0,j,value)

def cascade(raw,anchor=False):
 p.load(R/'ANCHOR40_PRIMARY.bin'if anchor else R/'PRIMARY.bin');z.load(R/'POST.bin');mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def evaluate(label,vals):
 folder=R/label;folder.mkdir();configure(vals);state=folder/'WS_NATIVE.bin';c.save_state(0,state);ds=[]
 for k in range(3):
  raw,_=c.render();out=cascade(raw);ds.append(assess(out))
  if k==0:sf.write(folder/'FIRST_NATIVE.wav',raw,48000,subtype='FLOAT');sf.write(folder/'FIRST_FULL_WIP.wav',out,48000,subtype='FLOAT')
 trial=dict(q.seed,waveshaper_native_controls=vals);row=dict(label=label,controls=vals,state=str(state),state_SHA256=hashlib.sha256(state.read_bytes()).hexdigest(),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),three_real_native_draw_metrics=ds,only_first_draw_native_and_full_WAV_retained=True,supported_settings_SHA256=native_dsp_settings_SHA256(trial['x'],trial));rows.append(row);(R/'PARTIAL_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_native_WS_controls_case_completed',label=label,mean_loss=row['loss'],Air=row['Air']);return row

def fresh(row):
 c.load_state(0,row['state']);ds=[]
 for k in range(6):raw,_=c.render();ds.append(assess(cascade(raw)))
 return dict(label=row['label'],loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),captures=ds)

def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(raw_controls=controls,native_canonical_OSstep1_local17_parent_fixed=True,supported_controls_fingerprinted_no_stale_bundle=True,training3_draws_per_control_and_first_draw_WAV_saved=True,top3_fresh6_then_NEW12=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Air_first10_and_bothcold_nonincreasing_vs_current_and_full40=True,TONEfirst10_nonincreasing=True,all_stereo148_abs16_lowmid325_and_pairedlowmid002=True,all12_resaves_and_two_native_zeroDepth_cold_same_state_replays_required=True,latest_BEST_revalidation_supported_full_FL20_export_coldZIP_and_publication_before_adoption=True),indent=2)+'\n')
try:
 c=q.native(q.source['native_input'],'Native12Controls-'+str(os.getpid()));p=q.WinVST3('Native12Controls-P-'+str(os.getpid()));z=q.WinVST3('Native12Controls-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Native12Controls-T-'+str(os.getpid()),cleanup_on_close=True);t.load(q.prior['post_native_trim_state'])
 for k,vals in enumerate(controls):evaluate('control-'+str(k).zfill(2),vals)
 base=rows[0];candidates=sorted([r for r in rows[1:]if r['all_stereo']and r['state_SHA256']!=base['state_SHA256']],key=lambda r:r['loss'])[:3];control=fresh(base);ranked=[dict(model=row,fresh=fresh(row))for row in candidates];valid=[r for r in ranked if r['fresh']['all_stereo']and r['fresh']['Air']<=control['Air']];winner=min(valid,key=lambda r:r['fresh']['loss'])if valid else None;ready=bool(winner and control['loss']-winner['fresh']['loss']>.0003);summary=dict(training_cases=len(rows),actual_training_native_renders=3*len(rows),fresh_control=control,fresh_ranked=ranked,winner=winner,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_comparator=q.prior['source_accepted_cohort']);(R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  selected=winner['model'];shutil.copyfile(selected['state'],R/'CANDIDATE_WS.bin');newseed=dict(q.seed,waveshaper_native_controls=selected['controls'],native_saved_state_bundle=None);(R/'CANDIDATE_SUPPORTED_NATIVE_METADATA.json').write_text(json.dumps(newseed,indent=2)+'\n')
  # Cold actual preset/generator check, with every other saved native state fixed.
  expected=None;errs=[]
  for k in range(2):
   nc=q.native(q.source['native_input'],'Native12Controls-ColdProof-'+str(k)+'-'+str(os.getpid()))
   try:
    nc.load_state(0,R/'CANDIDATE_WS.bin')
    for row in q.seed['native_saved_state_bundle']['manifest']:
     path=R/'saved-native-bundle'/row['state'];path.parent.mkdir(parents=True,exist_ok=True);nc.save_state(row['node'],path);want=(R/'CANDIDATE_WS.bin').read_bytes()if row['node']==0 else(Path(q.seed['native_saved_state_bundle']['directory'])/row['state']).read_bytes();assert path.read_bytes()==want
    nc.set(3,1,0);out,_=nc.render()
    if k==0:expected=out.copy()
    np.testing.assert_array_equal(out,expected);errs.append(float(abs(out-expected).max()))
   finally:nc.close()
  nc=q.native(q.source['native_input'],'Native12Controls-NoBundle-'+str(os.getpid()))
  try:q.apply_candidate(nc,np.array(q.seed['x']),newseed);dst=R/'GENERATED_NO_BUNDLE_WS.bin';nc.save_state(0,dst);assert dst.read_bytes()==(R/'CANDIDATE_WS.bin').read_bytes()
  finally:nc.close()
  (R/'COLD_NATIVE_EXPORT_PROOF.json').write_text(json.dumps(dict(two_actual_zeroDepth_errors=errs,generator_without_bundle_byte_exact=True,all12_saved_state_resaves_exact=True),indent=2)+'\n')
  c.close();c=q.native(q.source['native_input'],'Native12Controls-new12-'+str(os.getpid()));arc=Path('/tmp/divalead-native12-controls-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL60_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(arc)
  with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:c.close();c=q.native(q.source['native_input'],'Native12Controls-Cold-'+str(rep)+'-'+str(os.getpid()))
    configure([128]*3);raw0,_=c.render();old=cascade(raw0);d0=assess(old);anc=cascade(raw0,anchor=True);da=assess(anc);c.load_state(0,R/'CANDIDATE_WS.bin');raw1,_=c.render();new=cascade(raw1);d1=assess(new);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
    for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('anchor40',anc),('candidate',new)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('ANCHOR40',anc),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(captures,indent=2)+'\n');record('actual_entirely_NEW12_native_controls',completed_pairs=rep+1)
  gain=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);aa=np.array([r['Air_delta_vs40']for r in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guard=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guard);summary.update(captures=captures,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guard,robust_improvement=robust)
  with tarfile.open(arc)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_native_controls_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['fresh_control','fresh_ranked','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_best',error=traceback.format_exc());raise
finally:
 for host in[c,p,z,t]:
  if host is not None:host.close()
