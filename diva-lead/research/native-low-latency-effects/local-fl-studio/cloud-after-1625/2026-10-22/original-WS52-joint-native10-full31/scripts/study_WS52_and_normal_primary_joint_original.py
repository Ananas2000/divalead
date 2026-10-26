"""NEW candidate: WS48 curve plus a new normal primary-EQ/dynamic refit.

The isolated52curve failed the predeclared first6 gate and was not adopted. A changed
primary is mandatory here; new DSP point requires first6 AND first10 gates,
two positive cold native pairs and all strict original state/stereo checks.
"""
from pathlib import Path
import datetime,gzip,hashlib,io,json,os,struct,tarfile,traceback
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3
from normal_real_ZL_refit import RealPrimaryFit
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');OLD=Path('/workspace/divalead-work/stereo-refinement-20261026/WS52_HIGH_PEAK_STUDY');R=Path('/workspace/divalead-work/stereo-refinement-20261026/WS52_PRIMARY_JOINT_RESEARCH');R.mkdir(exist_ok=False);STATE=N/'ORIGINAL_WS52_PRIMARY_JOINT_STUDY.json'
assert json.loads((N/'zl-stereo-continuation.stop').read_text())['owner']=='LR-lowmid-primary-joint-20261026';main=json.loads((N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json').read_text());mp=Path('/proc')/str(main['owner']['PID']);assert not mp.exists()or(mp/'stat').read_text().split()[2]=='Z'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());control=prior['native_base'];candidate=json.loads((OLD/'NATIVE_CANDIDATE_RESEARCH_ONLY.json').read_text());assert control['source_manifest']==candidate['source_manifest'];assert control['chorus_overrides']==candidate['chorus_overrides'];assert control['x'][:76]==candidate['x'][:76]and control['x'][78:]==candidate['x'][78:]
for name,key in [('CONTROL_PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(R/name).write_bytes(Path(prior[key]).read_bytes())
(R/'FROZEN_SOURCE_AND_LATEST_ORIGINAL_CONTEXT.json').write_text(json.dumps(dict(prior=prior,candidate_native=candidate,curve_alone_not_adopted=True,new_primary_required=True,original_is_the_only_target=True),indent=2)+'\n');os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment')
from fl20_objective import FeaturesOriginal,a
f=FeaturesOriginal();reg=float(np.sum(np.array(control['x'])[:28]**2))*.00000025;ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);np.testing.assert_array_equal(ref,a.REF);freq=np.fft.rfftfreq(len(ref),1/48000);masks=[(freq>=lo)&(freq<hi)for lo,hi in [(300,800),(2000,5000),(5000,10000),(10000,14000)]]
def lr(y):
 p=abs(np.fft.rfft(y,axis=0))**2;return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref)
def assess(y):
 r=f.residual(y[:288000]);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));v=lr(edit);return dict(loss=float(r@r)+reg,assessment=f.local.last,LR_dB=v.tolist(),stereo_preservation_passed=bool(np.sqrt(np.mean((v[1:]-target[1:])**2))<=1.5 and max(abs(v[1:]))<=1.6 and abs(v[0]-target[0])<=3.35))
def native(seed,tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 return c
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),original_is_the_only_target=True,v83_Finish_not_used=True,normal_native_WS52_and_ZL_primary_joint_fit=True,source_Diva_MIDI_ARP_ADSR_routing_POST_unchanged=True,not_adopted=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def cascade(raw,p,z,primary):
 p.load(primary);z.load(R/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return out
def add(tar,name,y,members):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');b=f.getvalue();info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
fit=None;ns=[];zs=[]
try:
 record('capture_three_NEW_control_and_candidate_native_realizations');c0=native(control,'WS52Joint-control-training');c1=native(candidate,'WS52Joint-candidate-training');ns=[c0,c1];p=WinVST3('WS52Joint-control-primary-training');z=WinVST3('WS52Joint-control-post-training');zs=[p,z];controls=[]
 for phase in range(3):
  raw,_=c0.render();out=cascade(raw,p,z,R/'CONTROL_PRIMARY.bin');controls.append(assess(out));sf.write(R/f'TRAINING_CONTROL_{phase}.wav',out,48000,subtype='FLOAT');raw,_=c1.render();raw.astype('<f4').tofile(R/f'frozen-native-{phase}.f32');sf.write(R/f'TRAINING_CANDIDATE_NATIVE_{phase}.wav',raw,48000,subtype='FLOAT')
 for c in ns:c.close()
 for c in zs:c.close()
 ns=[];zs=[];fit=RealPrimaryFit(R,R/'CONTROL_PRIMARY.bin',R/'POST.bin',assess,record);baseline,current=fit.fit(sweeps=3);held=[fit.evaluate(('new-heldout-'+str(k),current['x']),k,False)for k in [1,2]];p,z=fit.clients[0];fit.configure(p,current['x']);p.save(R/'CANDIDATE_PRIMARY_RESEARCH_ONLY.bin');primary_changed=(R/'CANDIDATE_PRIMARY_RESEARCH_ONLY.bin').read_bytes()!=(R/'CONTROL_PRIMARY.bin').read_bytes();mid,_=p.render(input_file=R/'frozen-native-0.f32');z.load(R/'POST.bin');out,_=z.render(mid);sf.write(R/'SELECTED_TRAINING_WIP.wav',out,48000,subtype='FLOAT');(R/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(fit.rows).encode(),mtime=0));control_mean=float(np.mean([r['loss']for r in controls]));ready=bool(primary_changed and control_mean-float(np.mean([h['loss']for h in held]))>.0003 and all(h['stereo_preservation_passed']for h in held))
 summary=dict(training_cases=len(fit.rows),control_mean=control_mean,initial_candidate_native_old_primary=baseline,training_candidate=current,heldout=held,new_primary_changed=primary_changed,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,only_three_held_notes=True,curve_alone_not_adopted=True,new_DSP_point_is_curve_plus_new_primary=True,not_adopted=True,reference_match_reached=False);(R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n');fit.close();fit=None
 if ready:
  record('first6_AND_first10_plus_two_cold_new_DSP_confirmation');c0=native(control,'WS52Joint-control-validation');c1=native(candidate,'WS52Joint-candidate-validation');ns=[c0,c1];p0=WinVST3('WS52Joint-control-primary');z0=WinVST3('WS52Joint-control-post');p1=WinVST3('WS52Joint-candidate-primary');z1=WinVST3('WS52Joint-candidate-post');zs=[p0,z0,p1,z1];captures=[];members=[]
  with tarfile.open(R/'TWELVE_NEW_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in [10,11]:c0.close();c1.close();c0=native(control,'WS52Joint-cold-control-'+str(rep));c1=native(candidate,'WS52Joint-cold-candidate-'+str(rep));ns=[c0,c1]
    raw0,_=c0.render();old=cascade(raw0,p0,z0,R/'CONTROL_PRIMARY.bin');d0=assess(old);raw1,_=c1.render();out=cascade(raw1,p1,z1,R/'CANDIDATE_PRIMARY_RESEARCH_ONLY.bin');d1=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
    for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('new_DSP_point_confirmation_running',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  delta=np.array([r['improvement']for r in captures]);sem6=float(np.std(delta[:6],ddof=1)/np.sqrt(6));sem10=float(np.std(delta[:10],ddof=1)/np.sqrt(10));robust=bool(np.mean(delta[:6])>max(.0005,3*sem6)and np.mean(delta[:10])>max(.0005,3*sem10)and min(delta[10:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  with tarfile.open(R/'TWELVE_NEW_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem6,first10_mean_improvement=float(np.mean(delta[:10])),first10_SEM=sem10,required_first6=max(.0005,3*sem6),required_first10=max(.0005,3*sem10),cold2_improvements=delta[10:].tolist(),robust_improvement=robust);choice=dict(prior,native_base=candidate,native_ZL_component_state=str(R/'CANDIDATE_PRIMARY_RESEARCH_ONLY.bin'),loss=float(np.mean([r['candidate']['loss']for r in captures[:10]])),not_adopted_until_supported_export=True);(R/'COMBINED_CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(choice,indent=2)+'\n')
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_WS48_normal_primary_joint_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members','initial_candidate_native_old_primary','training_candidate','heldout']}),flush=True)
except BaseException:record('failed_preserve_current_WIP30_and_nativebase09',error=traceback.format_exc());raise
finally:
 if fit is not None:fit.close()
 for c in ns:c.close()
 for c in zs:c.close()
