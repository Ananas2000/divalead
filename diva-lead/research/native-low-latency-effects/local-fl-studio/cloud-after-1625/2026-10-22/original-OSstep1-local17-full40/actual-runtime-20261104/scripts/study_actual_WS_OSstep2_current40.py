"""Actual GUI oversampling step2, all curve points and other DSP unchanged."""
from pathlib import Path
import datetime,hashlib,io,json,os,struct,tarfile,threading,traceback
import numpy as np,soundfile as sf
import WS_OSstep2_current40_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;U=Path(__file__).resolve().parent;prior=q.prior;assert prior['full_public_kit_directory']=='ZL-WIP40';(U/'WS_NATIVE_OVERSAMPLING_CURRENT40').symlink_to(R,target_is_directory=True);src=Path('/tmp/divalead-WS-native12-OSstep2-GUI-20261104/after.bin');b=src.read_bytes();old=(Path(q.seed['native_saved_state_bundle']['directory'])/'verification/SOURCE_WaveShaper.bin').read_bytes();assert struct.unpack_from('<I',b,16)[0]==131073;assert [k for k in range(len(b))if b[k]!=old[k]]==[18];(R/'GUI_OSSTEP2_NATIVE_STATE.bin').write_bytes(b)
cache=threading.local();power=q.a.powers;clients=[];c0=c1=p=z=t=None;captures=[];members=[]
def powers(*args,**kw):v=power(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(e[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def native(tag,on):
 c=q.native(q.source['native_input'],tag)
 if on:c.load_state(0,R/'GUI_OSSTEP2_NATIVE_STATE.bin')
 return c

def cascade(raw):
 p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),actual_native_hosts=[c.proc.pid for c in[c0,c1]if c],actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],original_is_only_target=True,only_three_held_notes=True,only_GUI_Oversampling_offset_flag_changed=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def pair(rep):
 a,_=c0.render();out0=cascade(a);d0=assess(out0);b,_=c1.render();out1=cascade(b);d1=assess(out1);return dict(rep=rep,control=d0,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air']),[a,b,out0,out1]

def add(tar,name,y):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');blob=f.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(actual_GUI_hint='Oversampling factor',flag_uint32_offset16_before65537_after131073=True,all233curve_points_and_other_header_bytes_identical=True,first6_training_pairs_screen_mean_gain_over0003=True,training_Air_mean_nonincreasing=True,then12_entirely_new_pairs=True,final_first6AND10_gain_over_max0005_3SEM=True,bothcold_positive=True,final_Air_first10_and_bothcold_nonincreasing=True,TONEfirst10_nonincreasing=True,all_stereo148_abs16_lowmid325_pairedlowmid002=True,full_supported_export_latest_context_and_cold_ZIP_required=True),indent=2)+'\n')
try:
 c0=native('Native12OSstep2-control-'+str(os.getpid()),False);c1=native('Native12OSstep2-candidate-'+str(os.getpid()),True);p=q.WinVST3('Native12OSstep2-primary-'+str(os.getpid()));z=q.WinVST3('Native12OSstep2-post-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Native12OSstep2-trim-'+str(os.getpid()),cleanup_on_close=True);t.load(prior['post_native_trim_state']);rows=[]
 for k in range(6):
  row,audios=pair(k);rows.append(row)
  if k==0:
   for name,y in zip(['TRAIN_NATIVE_CONTROL','TRAIN_NATIVE_CANDIDATE','TRAIN_CONTROL','TRAIN_CANDIDATE'],audios):sf.write(R/(name+'.wav'),y,48000,subtype='FLOAT')
  record('actual_GUI_Oversampling_training_pairs',completed_pairs=k+1,latest_gain=row['gain'])
 ready=bool(np.mean([r['gain']for r in rows])>.0003 and np.mean([r['Air_delta']for r in rows])<=0 and all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in rows));summary=dict(training_pairs=rows,training_mean_gain=float(np.mean([r['gain']for r in rows])),training_mean_Air_delta=float(np.mean([r['Air_delta']for r in rows])),sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False);(R/'FROZEN_BEFORE_NEW_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  c0.close();c1.close();c0=native('Native12OSstep2-new12-control-'+str(os.getpid()),False);c1=native('Native12OSstep2-new12-candidate-'+str(os.getpid()),True);archive=Path('/tmp/divalead-native12-Native12OSstep2-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz').symlink_to(archive)
  with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:c0.close();c1.close();c0=native('Native12OSstep2-cold-control-'+str(rep)+'-'+str(os.getpid()),False);c1=native('Native12OSstep2-cold-candidate-'+str(rep)+'-'+str(os.getpid()),True)
    row,audios=pair(rep);captures.append(row)
    for name,y in zip(['native-control','native-candidate','control','candidate'],audios):add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in zip(['NATIVE_CONTROL','NATIVE_CANDIDATE','CONTROL','CANDIDATE'],audios):sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('new12_actual_GUI_Oversampling_validation',completed_pairs=rep+1)
  gain=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guard=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and tone<=0 and guard);summary.update(captures=captures,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_TONE_delta=tone,all12_stereo_pairedlowmid=guard,robust_improvement=robust)
  with tarfile.open(archive)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 dst=R/'ACTUAL_OSSTEP2_WS_RESAVED.bin';c1.save_state(0,dst);assert dst.read_bytes()==b;summary['actual_GUI_state_resave_byte_exact']=True;(R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_GUI_Oversampling_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in['training_pairs','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_latest_numeric_and_base40',error=traceback.format_exc());raise
finally:
 for host in[c0,c1,p,z,t]:
  if host is not None:host.close()
