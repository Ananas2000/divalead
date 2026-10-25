"""One predeclared independent confirmation of a borderline WS48 screen.

Ten NEW paired native realizations plus TWO new cold native pairs, using the
latest frozen accepted primary/POST. No repeats to chase a passing statistic.
"""
from pathlib import Path
import datetime,hashlib,io,json,os,tarfile,traceback
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects');SOURCE=Path('/tmp/divalead-original-native-WS48-20261025-01');R=Path('/tmp/divalead-WS48-independent12-20261025-01');R.mkdir(exist_ok=False);STATE=N/'ORIGINAL_WS48_INDEPENDENT12_CONFIRMATION.json'
initial=json.loads((SOURCE/'completion.json').read_text());assert initial['robust_improvement'];assert json.loads((N/'zl-stereo-continuation.stop').read_text())['owner']=='original-WS48-confirmation-20261025'
main=json.loads((N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json').read_text());pp=Path('/proc')/str(main['owner']['PID']);assert not pp.exists()or(pp/'stat').read_text().split()[2]=='Z'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());control=prior['native_base'];candidate=json.loads((SOURCE/'NATIVE_CANDIDATE_RESEARCH_ONLY.json').read_text());assert control['source_manifest']==candidate['source_manifest'];assert control['chorus_overrides']==candidate['chorus_overrides'];assert control['x'][:76]==candidate['x'][:76]and control['x'][78:]==candidate['x'][78:]
for name,key in [('PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(R/name).write_bytes(Path(prior[key]).read_bytes())
(R/'FROZEN_LATEST_CONTEXT_BEFORE_CONFIRMATION.json').write_text(json.dumps(dict(prior=prior,primary_SHA256=hashlib.sha256((R/'PRIMARY.bin').read_bytes()).hexdigest(),post_SHA256=hashlib.sha256((R/'POST.bin').read_bytes()).hexdigest(),warm_pairs=10,cold_pairs=2,unchanged_acceptance_floor=.0005,SEM_multiplier=3,not_adopted=True,original_is_the_only_target=True),indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment')
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
 p=STATE.with_suffix('.partial');p.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),original_is_the_only_target=True,only_native_WaveShaper_curve_changed=True,not_adopted=True,reference_match_reached=False,**kw),indent=2)+'\n');p.replace(STATE)
def cascade(raw,p,z):
 p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return out
clients=[];vsts=[]
try:
 c0=native(control,'WS48-confirm-control');c1=native(candidate,'WS48-confirm-candidate');clients=[c0,c1];p0=WinVST3('WS48-confirm-primary-control');z0=WinVST3('WS48-confirm-post-control');p1=WinVST3('WS48-confirm-primary-candidate');z1=WinVST3('WS48-confirm-post-candidate');vsts=[p0,z0,p1,z1];captures=[];members=[]
 with tarfile.open(R/'TWELVE_NEW_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
  for rep in range(12):
   if rep in [10,11]:c0.close();c1.close();c0=native(control,'WS48-confirm-cold-control-'+str(rep));c1=native(candidate,'WS48-confirm-cold-candidate-'+str(rep));clients=[c0,c1]
   raw0,_=c0.render();old=cascade(raw0,p0,z0);d0=assess(old);raw1,_=c1.render();out=cascade(raw1,p1,z1);d1=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
   for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:
    b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');blob=b.getvalue();label=f'{name}-{rep}.wav';info=tarfile.TarInfo(label);info.size=len(blob);tar.addfile(info,io.BytesIO(blob));members.append(dict(name=label,SHA256=hashlib.sha256(blob).hexdigest()))
   if rep==0:
    for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
   record('independent_new_native_confirmation_running',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
 delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:10],ddof=1)/np.sqrt(10));robust=bool(np.mean(delta[:10])>max(.0005,3*sem)and min(delta[10:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
 latest=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert Path(latest['native_ZL_component_state']).read_bytes()==(R/'PRIMARY.bin').read_bytes()and Path(latest['post_ZL_component_state']).read_bytes()==(R/'POST.bin').read_bytes()
 with tarfile.open(R/'TWELVE_NEW_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
  for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 result=dict(initial_fresh6_cold2_passed=True,independent_confirmation_warm_pairs=10,independent_confirmation_cold_pairs=2,first10_mean_improvement=float(np.mean(delta[:10])),first10_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[10:].tolist(),robust_independent_confirmation=robust,control_mean=float(np.mean([r['control']['loss']for r in captures])),candidate_mean=float(np.mean([r['candidate']['loss']for r in captures])),captures=captures,archive_members=members,latest_primary_POST_unchanged_during_confirmation=True,original_is_the_only_target=True,v83_Finish_not_used=True,only_three_held_notes=True,not_adopted=True,reference_match_reached=False)
 (R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('independent_WS48_confirmation_complete_not_adopted',robust_independent_confirmation=robust,mean_gain=result['first10_mean_improvement'],cold2=result['cold2_improvements']);print(json.dumps({k:v for k,v in result.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_nativebase6_and_all_accepted_kits',error=traceback.format_exc());raise
finally:
 for c in clients:c.close()
 for v in vsts:v.close()
