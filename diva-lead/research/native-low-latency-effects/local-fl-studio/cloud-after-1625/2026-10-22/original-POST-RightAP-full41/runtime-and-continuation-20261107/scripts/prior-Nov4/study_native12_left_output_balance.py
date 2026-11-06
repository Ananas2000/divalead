"""Broad real final L trim/output compensation, original spectral/stereo target only."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import native12_left_output_support as q
from native_post_trim import NativePostTrim
V=Path(__file__).resolve().parent;R=q.ROOT;c=p=z=t=None;cache=threading.local();origpower=q.a.powers;rows=[];captures=[];members=[];inputs=[];middles=[]
shutil.copyfile(q.prior['post_native_trim_state'],R/'CONTROL_TRIM.bin');anchor=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin');shutil.copyfile(anchor,R/'ANCHOR40_PRIMARY.bin');output_gain_id=1891030914
models=[(left,gain)for left in[-.04,-.15,-.3,-.5,-.8,-1.1,-1.4,-1.7]for gain in[0.,.15,.3,.45,.6,.75]]
def powers(*args,**kw):v=origpower(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(e[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),frozen_comparator=q.prior['source_accepted_cohort'],actual_native_host=None if c is None else c.proc.pid,actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],actual_native_trim_host=None if t is None else t.chain.proc.pid,original_is_only_target=True,source_Diva_ARP_ADSR_MIDI3_native12_and_PRIMARY_unchanged=True,only_POST_output_gain_and_final_native_Left_gain_changed=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def configure(left,gain):
 z.load(R/'POST.bin');z.text(output_gain_id,str(gain));t.configure(NativePostTrim.raw_from_dB(left),12800)

def cascade(raw,model=None,anchor=False):
 p.load(R/'ANCHOR40_PRIMARY.bin'if anchor else R/'PRIMARY.bin');mid,_=p.render(raw)
 if model is None:z.load(R/'POST.bin');t.load(R/'CONTROL_TRIM.bin')
 else:configure(model[0],model[1])
 pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def evaluate(k,model):
 left,gain=model;folder=R/('model-'+str(k).zfill(2));folder.mkdir();ds=[]
 for raw,mid in zip(inputs,middles):configure(left,gain);out,_=z.render(mid);out=t.render(out);ds.append(assess(out))
 z.save(folder/'POST.bin');t.save(folder/'TRIM.bin');sf.write(folder/'LAST_ACTUAL_WIP.wav',out,48000,subtype='FLOAT');row=dict(label=folder.name,left_requested_dB=left,POST_Output_Gain_dB=gain,folder=str(folder),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),lowmid_error=float(np.mean([d['lowmid_error']for d in ds])),captures=ds);rows.append(row);(R/'PARTIAL_TRAINING_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_common_input_left_output_grid',model=model,mean_loss=row['loss']);return row

def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(models=models,only_POST_OutputGain_and_final_native_left_trim_changed=True,same3_actual_native_and_PRIMARY_intermediate_inputs_all_training_cases=True,all_candidate_audio_actual_ZL_and_native_DLL=True,training_gain_over0003_Air_nonincreasing_and_original_stereo_guards=True,then_entirely_NEW12_pairs_same_actual_native_input_per_control_anchor_candidate=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Air_first10_AND_bothcold_nonincreasing_vs_current_AND_full40=True,TONEfirst10_nonincreasing=True,all_stereo148_abs16_lowmid325_and_pairedlowmid002=True,latest_BEST_revalidation_full_FL20_export_coldZIP_and_publication_required=True),indent=2)+'\n')
try:
 c=q.native(q.source['native_input'],'Native12LeftOut-native-'+str(os.getpid()));p=q.WinVST3('Native12LeftOut-P-'+str(os.getpid()));z=q.WinVST3('Native12LeftOut-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Native12LeftOut-T-'+str(os.getpid()),cleanup_on_close=True)
 for k in range(3):
  raw,_=c.render();inputs.append(raw);p.load(R/'PRIMARY.bin');mid,_=p.render(raw);middles.append(mid);sf.write(R/f'TRAIN_NATIVE_{k}.wav',raw,48000,subtype='FLOAT')
 for k,m in enumerate(models):evaluate(k,m)
 baseline=rows[0];eligible=[r for r in rows[1:]if r['all_stereo']and r['Air']<=baseline['Air']and all(d['lowmid_error']<=b['lowmid_error']+.02 for d,b in zip(r['captures'],baseline['captures']))];winner=min(eligible,key=lambda r:r['loss'])if eligible else None;ready=bool(winner and baseline['loss']-winner['loss']>.0003);summary=dict(training_cases=len(rows),actual_POST_and_native_trim_renders=3*len(rows),baseline=baseline,winner=winner,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_comparator=q.prior['source_accepted_cohort']);(R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  model=(winner['left_requested_dB'],winner['POST_Output_Gain_dB']);shutil.copyfile(Path(winner['folder'])/'POST.bin',R/'CANDIDATE_POST.bin');shutil.copyfile(Path(winner['folder'])/'TRIM.bin',R/'CANDIDATE_TRIM.bin')
  # Cold component/trim exact resave and same-input reproducibility, unchanged tolerance.
  expect=None;errs=[]
  for k in range(2):
   pp=q.WinVST3('Native12LeftOut-ColdP-'+str(k));zz=q.WinVST3('Native12LeftOut-ColdZ-'+str(k));tt=NativePostTrim(R/'cold-buffers','Native12LeftOut-ColdT-'+str(k),cleanup_on_close=True)
   try:
    for host,path,name in[(pp,R/'PRIMARY.bin','PRIMARY'),(zz,R/'CANDIDATE_POST.bin','POST'),(tt,R/'CANDIDATE_TRIM.bin','TRIM')]:host.load(path);dst=R/f'COLD_{k}_{name}_RESAVE.bin';host.save(dst);assert dst.read_bytes()==path.read_bytes()
    mid,_=pp.render(inputs[0]);out,_=zz.render(mid);out=tt.render(out)
    if k==0:expect=out.copy();sf.write(R/'CANONICAL_COLD_CANDIDATE.wav',out,48000,subtype='FLOAT')
    np.testing.assert_allclose(out,expect,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errs.append(float(abs(out-expect).max()));assert pp.latency()+zz.latency()==0
   finally:pp.close();zz.close();tt.close()
  (R/'ACTUAL_COLD_COMPONENT_TRIM_PROOF.json').write_text(json.dumps(dict(two_cold_actual_chain_errors=errs,all_component_trim_resaves_byte_exact=True,combined_ZL_PDC=0),indent=2)+'\n')
  arc=Path('/tmp/divalead-native12-left-output-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz').symlink_to(arc);c.close();c=q.native(q.source['native_input'],'Native12LeftOut-new12-'+str(os.getpid()))
  with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:c.close();c=q.native(q.source['native_input'],'Native12LeftOut-Cold-'+str(rep)+'-'+str(os.getpid()))
    raw,_=c.render();old=cascade(raw);d0=assess(old);anc=cascade(raw,anchor=True);da=assess(anc);new=cascade(raw,model);d1=assess(new);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
    for name,y in [('native',raw),('control',old),('anchor40',anc),('candidate',new)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in [('NATIVE',raw),('CONTROL',old),('ANCHOR40',anc),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('actual_entirely_NEW12_left_output_comparison',completed_pairs=rep+1)
  gain=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);aa=np.array([r['Air_delta_vs40']for r in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guard=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guard);summary.update(captures=captures,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guard,robust_improvement=robust)
  with tarfile.open(arc)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_left_output_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['baseline','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_best',error=traceback.format_exc());raise
finally:
 for host in[c,p,z,t]:
  if host is not None:host.close()
