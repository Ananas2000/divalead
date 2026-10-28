"""Independent fresh12 comparison; clarify a missing numeric-only stereo guard."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import Direct404_vs372_paired_lowmid_support as q
from native_post_trim import NativePostTrim
from fl20_curve import native_dsp_settings_SHA256
R=q.ROOT;STATE=q.STATE;n=p=z=t=None;cache=threading.local();oldpowers=q.a.powers;captures=[];members=[]
assert q.prior['source_accepted_cohort']==404
assert native_dsp_settings_SHA256(q.seed['x'],q.seed)==q.seed['native_saved_state_bundle']['settings_SHA256']
control=q.A/'stereo-continuous87/cohort-0372/candidate-component.bin';(R/'CONTROL372_PRIMARY.bin').write_bytes(control.read_bytes());candidate=R/'PRIMARY.bin'
def powers(*args,**kw):
 v=oldpowers(*args,**kw);cache.power=v[0];return v
q.a.powers=powers
def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(e[:,4:6,2:],0).mean());v=np.array(d['LR_dB']);d['original_stereo_preservation_passed']=bool(np.sqrt(np.mean((v[1:]-q.reference_LR[1:])**2))<=1.48 and max(abs(v[1:]))<=1.6 and abs(v[0]-q.reference_LR[0])<=3.25);return d
def cascade(raw,component):
 p.load(component);z.load(R/'POST.bin');mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],actual_native_host=None if n is None else n.proc.pid,actual_trim_host=None if t is None else t.chain.proc.pid,reference_match_reached=False,not_a_new_candidate=True,**kw);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(s,indent=2)+'\n');tmp.replace(STATE)
def add(tar,name,audio):
 b=io.BytesIO();sf.write(b,audio,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();entry=tarfile.TarInfo(name);entry.size=len(blob);tar.addfile(entry,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(candidate404_vs_direct_previous372_not403=True,new10warm_and2cold_native=True,first6ANDfirst10_gain_over_max0005_3SEM=True,bothcold_positive=True,each_pair_lowmid_error_increase_at_most002=True,absolute_upper148_abs16_lowmid325_unchanged=True,first10_Air_and_bothcold_increase_at_most002=True,source281_3held_ARP_ADSR_native12_POST_trim_unchanged=True,primary404_only=True,earlier403_violation_and_description_correction_disclosed=True),indent=2)+'\n')
try:
 assert shutil.disk_usage('/workspace').free>128*2**20 and shutil.disk_usage('/tmp').free>96*2**20
 p=q.WinVST3('Direct404audit-'+str(os.getpid())+'-primary');z=q.WinVST3('Direct404audit-'+str(os.getpid())+'-post');t=NativePostTrim(R/'buffers','Direct404audit-'+str(os.getpid())+'-trim',cleanup_on_close=True);t.load(q.prior['post_native_trim_state']);n=q.native(q.source['native_input'],'Direct404audit-'+str(os.getpid())+'-native');record('fresh12_direct404_vs372_stricter_stereo_audit')
 with tarfile.open(R/'ALL12_NATIVE_CONTROL372_CANDIDATE404_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
  for rep in range(12):
   if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'Direct404audit-'+str(os.getpid())+'-cold-'+str(rep))
   raw,_=n.render();a=cascade(raw,R/'CONTROL372_PRIMARY.bin');da=assess(a);b=cascade(raw,candidate);db=assess(b);captures.append(dict(rep=rep,control372=da,candidate404=db,improvement=da['loss']-db['loss'],air_increase=db['positive_excess_air_dB']-da['positive_excess_air_dB'],paired_lowmid_error_delta=db['lowmid_error']-da['lowmid_error']))
   for label,y in [('native',raw),('control372',a),('candidate404',b)]:add(tar,f'{label}-{rep}.wav',y)
   if rep==0:
    for label,y in [('NATIVE_INPUT',raw),('CONTROL372',a),('CANDIDATE404',b)]:sf.write(R/(label+'_00.wav'),y,48000,subtype='FLOAT')
   record('fresh12_direct404_vs372_audit_in_progress',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
 p.save(R/'CANDIDATE404_RESAVED.bin');assert(R/'CANDIDATE404_RESAVED.bin').read_bytes()==candidate.read_bytes();d=np.array([x['improvement']for x in captures]);air=np.array([x['air_increase']for x in captures]);low=np.array([x['paired_lowmid_error_delta']for x in captures]);sem6=float(d[:6].std(ddof=1)/np.sqrt(6));sem10=float(d[:10].std(ddof=1)/np.sqrt(10));guard=bool(all(x['candidate404']['original_stereo_preservation_passed']for x in captures)and max(low)<=.02);passed=bool(d[:6].mean()>max(.0005,3*sem6)and d[:10].mean()>max(.0005,3*sem10)and min(d[10:])>0 and air[:10].mean()<=.02 and max(air[10:])<=.02 and guard)
 with tarfile.open(R/'ALL12_NATIVE_CONTROL372_CANDIDATE404_WAVs.tar.gz')as tar:
  for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate404_direct_stricter_requalification_passed=passed,first6_mean_improvement=float(d[:6].mean()),first6_SEM=sem6,first10_mean_improvement=float(d[:10].mean()),first10_SEM=sem10,cold2_improvements=d[10:].tolist(),first10_air_increase=float(air[:10].mean()),cold2_air_increases=air[10:].tolist(),max_paired_lowmid_error_delta=float(max(low)),all12_absolute_and_paired_stereo_guards=guard,state_resave_exact=True,ZL_PDC_frames=0,captures=captures,archive_members=members,not_a_new_candidate=True,not_adopted=True,reference_match_reached=False);(R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('direct404_vs372_stricter_audit_complete',candidate404_direct_stricter_requalification_passed=passed);print(json.dumps({k:v for k,v in result.items()if k not in['captures','archive_members']}),flush=True)
except BaseException:record('audit_failed_no_accepted_state_mutation',error=traceback.format_exc());raise
finally:
 for c in[n,p,z,t]:
  if c is not None:c.close()
