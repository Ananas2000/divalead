"""LR-target gradients propose normal saved POST presets; original criterion alone accepts."""
from pathlib import Path
import csv,datetime,hashlib,io,json,os,shutil,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
from scipy.optimize import lsq_linear
import post15_LR_jacobian_support as q
from native_post_trim import NativePostTrim
V=Path(__file__).resolve().parent;R=q.ROOT;c=p=z=t=None;cache=threading.local();power=q.a.powers;rows=[];captures=[];members=[];inputs=[];mids=[]
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');shutil.copyfile(public/'ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin',R/'ANCHOR40_PRIMARY.bin');shutil.copyfile(q.prior['post_native_trim_state'],R/'TRIM.bin')
b=(R/'POST.bin').read_bytes();values={e.attrib['id']:float(e.attrib['value'])for e in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')};ids={r['title']:int(r['id'])for r in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')};specs=[]
for band in[0,1,2,3,5,6]:
 assert values['filter_type'+str(band)]==9 and values['filter_status'+str(band)]==2
 for title,key,step,lo,hi in [('Freq','freq',.035,20,18000),('Q','q',.045,.15,25)]:specs.append(dict(title=title+str(band),value=values[key+str(band)],step=step,log=True,lo=lo,hi=hi))
for title,key,step,lo,hi,log in [('Freq','freq',.035,200,5000,True),('Q','q',.045,.15,25,True),('Gain','gain',.10,-6,3,False)]:specs.append(dict(title=title+'4',value=values[key+'4'],step=step,log=log,lo=lo,hi=hi))
assert len(specs)==15

def powers(*args,**kw):v=power(*args,**kw);cache.power=v[0];return v
q.a.powers=powers
target_overall=float(10*np.log10(np.sum(q.reference[:,0]**2)/np.sum(q.reference[:,1]**2)));target=np.r_[q.reference_LR,target_overall]

def assess(y):
 residual=q.features.residual(y[:288000]);edit=q.a.h.edit_aligned(q.a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));lr=q.lr(edit);overall=float(10*np.log10(np.sum(edit[:,0]**2)/np.sum(edit[:,1]**2)));err=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));v=np.r_[lr,overall]-target;upper=float(np.sqrt(np.mean((lr[1:]-q.reference_LR[1:])**2)));low=abs(float(lr[0]-q.reference_LR[0]));d=dict(loss=float(residual@residual)+q.reg,assessment=q.features.local.last,LR_dB=lr.tolist(),overall_LR_dB=overall,upper_LR_error=upper,lowmid_error=low,Air=float(np.maximum(err[:,4:6,2:],0).mean()),LR_target_RMS=float(np.sqrt(np.mean(v*v))),stereo_preservation_passed=bool(upper<=1.48 and max(abs(lr[1:]))<=1.6 and low<=3.25));return d,np.r_[residual,.5*v/np.sqrt(5)]

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),frozen_comparator=q.prior['source_accepted_cohort'],actual_native_host=None if c is None else c.proc.pid,actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],original_is_only_target=True,LR_extra_residual_for_proposals_only_not_acceptance=True,source_Diva_MIDI3_ARP_ADSR_native12_PRIMARY_trim_unchanged=True,only_existing_POST15_frequency_Q_Left_gain_varied=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def configure(delta):
 z.load(R/'POST.bin')
 for s,unit in zip(specs,delta):
  val=float(np.clip(s['value']*2**(s['step']*unit)if s['log']else s['value']+s['step']*unit,s['lo'],s['hi']))
  if val!=s['value']:z.text(ids[s['title']],format(val,'.12g'))
 t.load(R/'TRIM.bin')

def evaluate(label,delta,keep=True,phases=range(3)):
 ds=[];features=[]
 for k in phases:
  configure(delta);out,_=z.render(mids[k]);out=t.render(out);d,f=assess(out);ds.append(d);features.append(f)
 row=dict(label=label,delta=list(map(float,delta)),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),LR_target_RMS=float(np.mean([d['LR_target_RMS']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),captures=ds,proposal_features=np.mean(features,axis=0).tolist())
 if keep:
  folder=R/label;folder.mkdir();z.save(folder/'POST.bin');sf.write(folder/'LAST_ACTUAL_FULL_WIP.wav',out,48000,subtype='FLOAT');rows.append(row);(R/'PARTIAL_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_POST15_LR_derivative_or_joint',label=label,loss=row['loss'],LR=row['LR_target_RMS'])
 return row

def cascade(raw,label,delta=None):
 p.load(R/('ANCHOR40_PRIMARY.bin'if label=='anchor40'else'PRIMARY.bin'));mid,_=p.render(raw);configure(np.zeros(15)if delta is None else delta);out,_=z.render(mid);return t.render(out)

def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(specs=specs,only_existing_POST15_changed=True,three_common_native_AND_PRIMARY_inputs_all_training_models=True,original_scalar_metric_plus_LR_vector_for_proposals_only=True,all_final_acceptance_uses_unchanged_original_criterion=True,derivative30_then5_joint_models=True,additional2_unseen_gain_over0003=True,final_NEW12_shared_native_input_per_control_anchor_candidate=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Air_first10_bothcold_nonincreasing_vs_current_AND_full40=True,TONE_nonincreasing=True,all_stereo148_abs16_lowmid325_pairedlowmid002=True,LR_error_cannot_increase_training_and_final=True,cold_component_replay_latest_BEST_and_full_FL20_export_required=True),indent=2)+'\n')
try:
 c=q.native(q.source['native_input'],'Post15LR-native-'+str(os.getpid()));p=q.WinVST3('Post15LR-P-'+str(os.getpid()));z=q.WinVST3('Post15LR-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Post15LR-T-'+str(os.getpid()),cleanup_on_close=True)
 for k in range(5):raw,_=c.render();inputs.append(raw);p.load(R/'PRIMARY.bin');mid,_=p.render(raw);mids.append(mid);sf.write(R/f'TRAIN_NATIVE_{k}.wav',raw,48000,subtype='FLOAT')
 baseline=evaluate('baseline',np.zeros(15));derivatives={}
 for j in range(15):
  derivatives[j]={}
  for sign in[-1,1]:d=np.zeros(15);d[j]=sign;derivatives[j][sign]=evaluate('derivative-'+str(j)+'-'+str(sign),d)
 f0=np.array(baseline['proposal_features']);J=np.column_stack([(np.array(derivatives[j][1]['proposal_features'])-np.array(derivatives[j][-1]['proposal_features']))/2 for j in range(15)]);np.savez_compressed(R/'POST15_ACTUAL_FEATURE_JACOBIAN.npz',J=J,baseline=f0);direction=lsq_linear(np.r_[J,np.eye(15)*.025],np.r_[-f0,np.zeros(15)],bounds=(-1.5,1.5),tol=1e-9).x
 for fraction in[.125,.25,.5,.75,1.]:evaluate('joint-'+str(fraction),direction*fraction)
 valid=[r for r in rows[1:]if r['label'].startswith('joint-')and r['all_stereo']and r['Air']<=baseline['Air']and r['LR_target_RMS']<=baseline['LR_target_RMS']];winner=min(valid,key=lambda r:r['loss'])if valid else None;held=[];ready=False
 if winner:
  for k in[3,4]:b=evaluate('held-control',np.zeros(15),False,[k]);d=evaluate('held-candidate',winner['delta'],False,[k]);held.append(dict(input=k,control=b,candidate=d,gain=b['loss']-d['loss']))
  ready=bool(baseline['loss']-winner['loss']>.0003 and np.mean([r['gain']for r in held])>.0003 and all(r['candidate']['all_stereo']and r['candidate']['Air']<=r['control']['Air']+.02 for r in held))
 summary=dict(training_cases=len(rows),actual_training_POST_nativeTrim_DSP=3*len(rows),baseline=baseline,winner=winner,heldout=held,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_comparator=q.prior['source_accepted_cohort']);(R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  configure(winner['delta']);z.save(R/'CANDIDATE_POST.bin');z.load(R/'CANDIDATE_POST.bin');z.save(R/'CANDIDATE_POST_RESAVED.bin');assert(R/'CANDIDATE_POST_RESAVED.bin').read_bytes()==(R/'CANDIDATE_POST.bin').read_bytes();c.close();c=q.native(q.source['native_input'],'Post15LR-new12-'+str(os.getpid()));arc=Path('/tmp/divalead-post15LR-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(arc)
  with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:c.close();c=q.native(q.source['native_input'],'Post15LR-Cold-'+str(rep)+'-'+str(os.getpid()))
    raw,_=c.render();old=cascade(raw,'control');d0,_=assess(old);anc=cascade(raw,'anchor40');da,_=assess(anc);new=cascade(raw,'candidate',winner['delta']);d1,_=assess(new);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
    for name,y in [('native',raw),('control',old),('anchor40',anc),('candidate',new)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in [('NATIVE',raw),('CONTROL',old),('ANCHOR40',anc),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('actual_NEW12_POST15_LR_shared_inputs',completed_pairs=rep+1)
  delta=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);aa=np.array([r['Air_delta_vs40']for r in captures]);s6=float(delta[:6].std(ddof=1)/np.sqrt(6));s10=float(delta[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guard=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);LRok=bool(np.mean([r['candidate']['LR_target_RMS']-r['control']['LR_target_RMS']for r in captures[:10]])<=0);robust=bool(delta[:6].mean()>max(.0005,3*s6)and delta[:10].mean()>max(.0005,3*s10)and min(delta[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guard and LRok);summary.update(captures=captures,archive_members=members,first6_gain=float(delta[:6].mean()),first6_SEM=s6,first10_gain=float(delta[:10].mean()),first10_SEM=s10,cold2_gains=delta[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guard,LR_target_preserved=LRok,robust_improvement=robust)
  with tarfile.open(arc)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_POST15_LR_jacobian_complete_not_adopted',robust_improvement=summary['robust_improvement']);print(json.dumps({k:v for k,v in summary.items()if k not in['baseline','winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_BEST',error=traceback.format_exc());raise
finally:
 for host in[c,p,z,t]:
  if host is not None:host.close()
