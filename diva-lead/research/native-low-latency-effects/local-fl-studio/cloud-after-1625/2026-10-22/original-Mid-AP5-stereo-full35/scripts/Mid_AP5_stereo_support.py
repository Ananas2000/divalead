from pathlib import Path
H=Path(__file__).resolve().parent
"""New hypothesis: common stereo phase correction scored ONLY against original.
Actual native training inputs and actual official ZL DSP; unchanged objective.
No new Diva instances/GUI exports, reference samples never enter synthesis.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,struct,tarfile,threading,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3,D
A=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');OLD=Path('/workspace/divalead-work/pc-stereo-20261024')
ROOT=H/'MID_AP5_STEREO_ORIGINAL';ROOT.mkdir(exist_ok=False)
STATE=N/'ORIGINAL_MID_AP5_STEREO_ORIGINAL_STUDY.json';OWNER='post-joint11-finite-parallel-20261026';STOP=N/'zl-stereo-continuation.stop'
prior=json.loads((OLD/'stereo-continuous87/BEST_CANDIDATE.json').read_text())
seed=prior['native_base'];BASE=Path(prior['native_base_export_directory']);manifest=json.loads((BASE/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest']
for name,source in [('PRIMARY.bin',prior['native_ZL_component_state']),('CONTROL_POST.bin',prior['post_ZL_component_state'])]:(ROOT/name).write_bytes(Path(source).read_bytes())
(ROOT/'PRIOR_CONFIRMED.json').write_text(json.dumps(prior,indent=2)+'\n')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal();reg=float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def values(path):
 b=Path(path).read_bytes();x=ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]])
 return {p.attrib['id']:float(p.attrib['value'])for p in x.find('Para')}
original=values(ROOT/'CONTROL_POST.bin');assert all(original['filter_status'+str(k)]==2 for k in range(5))
specs=[]
for k in range(4):
 specs += [dict(title='Freq'+str(k),key='freq'+str(k),step=.12,lo=30.,hi=18000.,log=True),dict(title='Q'+str(k),key='q'+str(k),step=.18,lo=.15,hi=25.,log=True)]
specs += [dict(title='Gain4',key='gain4',step=.5,lo=-6.,hi=6.,log=False),dict(title='Freq4',key='freq4',step=.12,lo=300.,hi=2500.,log=True),dict(title='Q4',key='q4',step=.18,lo=.15,hi=25.,log=True)]
origin={p['key']:original[p['key']]for p in specs}
ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);freqs=np.fft.rfftfreq(len(ref),1/48000)
bands=[(40,300),(300,800),(800,2000),(2000,5000),(5000,10000),(10000,14000)];masks=[(freqs>=lo)&(freqs<hi)for lo,hi in bands]
def lr(edit):
 p=abs(np.fft.rfft(edit,axis=0))**2
 return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref)
def assessment(y):
 residual=features.residual(y);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));balance=lr(edit);high=float(np.sqrt(np.mean((balance[3:]-target[3:])**2)))
 return dict(loss=float(residual@residual)+reg,assessment=features.local.last,LR_dB=balance.tolist(),lowmid_error=abs(float(balance[1]-target[1])),bass_error=abs(float(balance[0]-target[0])),upper_error=high,upper_stereo_guard=bool(high<=1.5 and np.max(np.abs(balance[3:]))<=1.6))
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def state(phase,**extra):
 p=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),owner=OWNER,phase=phase,root=str(ROOT),cases=len(rows),real_VST3_hosts=[c.child.pid for c in clients],only_three_held_notes=True,source_native_primary_unchanged=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra);tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(STATE)
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
 for row in manifest:
  p=BASE/row['state'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['state_SHA256'];c.load_state(row['node'],p)
 return c
def configure(c,settings):
 c.load(ROOT/'CONTROL_POST.bin')
 if settings is not None:
  for p in specs:c.text(params[p['title']],format(settings[p['key']],'.12g'))
def evaluate(case,phase=0,keep=True):
 label,settings=case;c=pool.get()
 try:
  configure(c,settings);out,status=c.render(input_file=ROOT/f'primary-{phase}.f32');row=dict(label=label,settings=settings,**assessment(out),VST3_status=status);assert c.latency()==0
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put(c)
def wave(y):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');return f.getvalue()
def add(tar,name,y,members):
 b=wave(y);info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()))
assert prior['native_base_export_directory'].endswith('_10')
(ROOT/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(existing_POST_four_AllPass_freqQ_and_LeftPeak_freqQgain_only=True,all_filter_modes_types_statuses_unchanged=True,extra_per_pair_lowmid_error_not_worse_over_dB=.02,actual_primary_and_native10_frozen=True,BOTH_first6_and_first10=True,warm10_cold2=True,floor=.0005,SEM_multiplier=3,latest_context_match_required_before_adoption=True),indent=2)+'\n')
