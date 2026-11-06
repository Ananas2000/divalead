"""Validate ONLY the immutable fitted point if the original launch's validation path failed."""
from pathlib import Path
import json
OLD=Path('/tmp/divalead-native12-current580-bothZL109-common-inputs-20261104');summary=json.loads((OLD/'FROZEN_BEFORE_FRESH_VALIDATION.json').read_text());assert summary['sufficient_screen']
import datetime,hashlib,io,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import common109_validation_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;V=Path(__file__).resolve().parent;prior=json.loads((OLD/'PRIOR_COMBINED_CANDIDATE.json').read_text());assert q.seed['native_saved_state_bundle']['settings_SHA256']==prior['native_base']['native_saved_state_bundle']['settings_SHA256'];c=p=z=t=None;cache=threading.local();power=q.a.powers;rows=[];members=[]
for src,dst in [('PRIMARY.bin','PRIMARY.bin'),('POST.bin','POST.bin'),('ANCHOR40_PRIMARY.bin','ANCHOR40_PRIMARY.bin'),('CANDIDATE_PRIMARY.bin','CANDIDATE_PRIMARY.bin'),('CANDIDATE_POST.bin','CANDIDATE_POST.bin'),('FROZEN_BEFORE_FRESH_VALIDATION.json','ORIGINAL_FITTED_POINT.json')]:shutil.copyfile(OLD/src,R/dst)
shutil.copyfile(prior['post_native_trim_state'],R/'TRIM.bin')
def powers(*args,**kw):v=power(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(e[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),frozen_comparator=prior['source_accepted_cohort'],frozen_fit_not_rerun=True,source_MIDI3_ARP_ADSR_native12_trim_unchanged=True,all_control_anchor_candidate_use_same_actual_native_input=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def cascade(raw,label):
 p.load(R/('CANDIDATE_PRIMARY.bin'if label=='candidate'else'ANCHOR40_PRIMARY.bin'if label=='anchor40'else'PRIMARY.bin'));z.load(R/('CANDIDATE_POST.bin'if label=='candidate'else'POST.bin'));t.load(R/'TRIM.bin');mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))

(R/'PREDECLARED_RESUMED_VALIDATION_PROTOCOL.json').write_text(json.dumps(dict(original_frozen_selected_point_unchanged=True,no_training_rerun_or_quality_data_pooling=True,NEW12_all3_cascades_same_native_draw=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Air_first10_and_bothcold_nonincreasing_vs_frozen_current_AND_full40=True,TONEfirst10_nonincreasing=True,all_stereo148_abs16_lowmid325_eachpairedlowmid002=True,original_final_quality_gates_unchanged=True,latest_BEST_revalidation_complete_FL20_export_coldZIP_and_publication_before_adoption=True),indent=2)+'\n')
try:
 record('two_fresh_actual_cold_cascades_before_NEW12');raw,sr=sf.read(OLD/'TRAINING_NATIVE_0.wav',dtype='float32',always_2d=True);expected=None;errs=[]
 for k in range(2):
  p=q.WinVST3('Common109Resume-ColdP-'+str(k));z=q.WinVST3('Common109Resume-ColdZ-'+str(k));t=NativePostTrim(R/'cold-buffers','Common109Resume-ColdT-'+str(k),cleanup_on_close=True)
  for host,path,name in[(p,R/'CANDIDATE_PRIMARY.bin','PRIMARY'),(z,R/'CANDIDATE_POST.bin','POST'),(t,R/'TRIM.bin','TRIM')]:host.load(path);dst=R/f'{k}_{name}_RESAVE.bin';host.save(dst);assert dst.read_bytes()==path.read_bytes()
  out=cascade(raw,'candidate')
  if expected is None:expected=out.copy();sf.write(R/'COLD_CANONICAL_FULL.wav',out,48000,subtype='FLOAT')
  np.testing.assert_allclose(out,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errs.append(float(abs(out-expected).max()));p.close();z.close();t.close();p=z=t=None
 (R/'ACTUAL_TWO_COLD_CASCADE_PROOF.json').write_text(json.dumps(dict(two_fresh_cold_errors=errs,all_component_and_trim_resaves_exact=True,ZL_PDC=0),indent=2)+'\n');c=q.native(q.source['native_input'],'Common109Resume-NEW12-native-'+str(os.getpid()));p=q.WinVST3('Common109Resume-P-'+str(os.getpid()));z=q.WinVST3('Common109Resume-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Common109Resume-T-'+str(os.getpid()),cleanup_on_close=True);archive=Path('/tmp/divalead-common109-resumed-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_COMMON_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(archive)
 with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
  for rep in range(12):
   if rep in[10,11]:c.close();c=q.native(q.source['native_input'],'Common109Resume-ColdNative-'+str(rep)+'-'+str(os.getpid()))
   raw,_=c.render();control=cascade(raw,'control');d0=assess(control);anchor=cascade(raw,'anchor40');da=assess(anchor);candidate=cascade(raw,'candidate');d1=assess(candidate);rows.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
   for name,y in [('native',raw),('control',control),('anchor40',anchor),('candidate',candidate)]:add(tar,f'{name}-{rep}.wav',y)
   if rep==0:
    for name,y in [('NATIVE',raw),('CONTROL',control),('ANCHOR40',anchor),('CANDIDATE',candidate)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
   (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(rows,indent=2)+'\n');record('entirely_new12_common_input_comparisons',completed_pairs=rep+1)
 gain=np.array([d['gain']for d in rows]);air=np.array([d['Air_delta']for d in rows]);aa=np.array([d['Air_delta_vs40']for d in rows]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([d['candidate']['assessment']['tone_score']-d['control']['assessment']['tone_score']for d in rows[:10]]));guards=all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 for d in rows);robust=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guards)
 with tarfile.open(archive)as tar:
  for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 result=dict(rows=rows,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guards,robust_improvement=robust,frozen_comparator=prior['source_accepted_cohort'],original_fitted_point_unchanged=True,not_adopted=True,reference_match_reached=False);(R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('resumed_frozen_point_NEW12_complete_not_adopted',robust_improvement=robust);print(json.dumps({k:v for k,v in result.items()if k not in['rows','archive_members']}),flush=True)
except BaseException:record('failed_preserve_frozen_point_and_current_BEST',error=traceback.format_exc());raise
finally:
 for host in[c,p,z,t]:
  if host is not None:host.close()
