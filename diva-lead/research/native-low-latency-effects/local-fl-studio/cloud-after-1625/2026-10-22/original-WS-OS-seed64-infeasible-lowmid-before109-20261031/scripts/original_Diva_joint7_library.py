"""Actual Diva tone screen scored ONLY against uploaded original, never v83.

Three held notes/internal ARP/ADSR untouched. Current real native06 and both
official zero-PDC ZLs remain fixed. Every actual281 parameter/MIDI event is
audited, and positive screens need fresh6/cold2 plus a supported full export.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,shutil,subprocess,tarfile,threading,traceback
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import D,S,WinVST3,win
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=Path('/tmp/divalead-original-Diva-joint7-20261025-01');ROOT.mkdir(exist_ok=False)
STATE=N/'ORIGINAL_DIVA_JOINT7_STUDY.json';OWNER='original-reference-tone-finite-20261025'
prior=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];source=seed['source_manifest'];baseline_dir=Path(source['source_preset']).parent;preset=Path(source['source_preset']).read_text();baseline_raw,sr=sf.read(source['source_audio'],dtype='float32',always_2d=True);assert sr==48000
(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
for name,key in [('PRIMARY.bin','native_ZL_component_state'),('POST.bin','post_ZL_component_state')]:(ROOT/name).write_bytes(Path(prior[key]).read_bytes())
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal();reg=float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
reference_path=Path('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav');assert hashlib.sha256(reference_path.read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f'
reference,sr=sf.read(reference_path,always_2d=True);np.testing.assert_array_equal(reference,a.REF)
frequency=np.fft.rfftfreq(len(reference),1/48000);bands=[(300,800),(2000,5000),(5000,10000),(10000,14000)];masks=[(frequency>=lo)&(frequency<hi)for lo,hi in bands]
def lr(y):
 p=abs(np.fft.rfft(y,axis=0))**2;return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])

reference_LR=lr(reference)
HARMONIC_CACHE=threading.local()
HARMONIC_WEIGHTS=np.maximum(a.h.HT,1e-5)**.5;HARMONIC_WEIGHTS[:,0]=0;HARMONIC_WEIGHTS/=HARMONIC_WEIGHTS.sum()
original_harmonic_error_function=a.h.harmonic_errors
def cache_actual_harmonic_error(y):
 result=original_harmonic_error_function(y);HARMONIC_CACHE.vector=(np.asarray(result['harmonic_errors_db'])*np.sqrt(HARMONIC_WEIGHTS)).ravel();return result
a.h.harmonic_errors=cache_actual_harmonic_error

def assess(y):
 residual=features.residual(y[:288000]);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));balance=lr(edit);upper=float(np.sqrt(np.mean((balance[1:]-reference_LR[1:])**2)));low=abs(float(balance[0]-reference_LR[0]))
 return dict(loss=float(residual@residual)+reg,assessment=features.local.last,LR_dB=balance.tolist(),upper_LR_error=upper,lowmid_error=low,stereo_preservation_passed=bool(upper<=1.5 and max(abs(balance[1:]))<=1.6 and low<=3.35))
def parameters(path):return {int(r['index']):r for r in csv.DictReader(Path(path).open(),delimiter='\t')}
original=parameters(baseline_dir/'all281.tsv');assert len(original)==281
expected_notes=[s for s in(baseline_dir/'Diva.log').read_text().splitlines()if s.startswith('NOTE ')];assert len(expected_notes)==12
plugin=Path('/workspace/attachments/6a76beaa-924d-4f2e-8491-512d9b487af2/Diva(x64).vst3');host=Path('/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe');assert plugin.is_file()and host.is_file()
env=dict(os.environ,WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def record(phase,**kw):
 state=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(ROOT),cases=len(rows),actual_native_hosts=[c.proc.pid for c,p,z in clients],actual_ZL_hosts=[x.child.pid for c,p,z in clients for x in [p,z]],original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,only_three_held_notes=True,ARP_ADSR_MIDI_unchanged=True,native06_and_both_ZL_components_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(STATE)
def patched(values):
 section=None;used=set();lines=[]
 for line in preset.splitlines():
  if line.startswith('#cm='):section=line[4:]
  if '='in line and not line.startswith('#'):
   key=line.split('=',1)[0]
   if(section,key)in values:line=key+'='+str(values[(section,key)]);used.add((section,key))
  lines.append(line)
 assert used==set(values);return '\n'.join(lines)+'\n'
def actual_Diva(state,out):
 out.mkdir();commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(out/'all281.tsv'),'save '+win(out/'Diva_VST_chunk.bin'),'render '+win(out/'Diva_source.wav'),'quit']
 with(out/'Diva.log').open('w')as log:subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),str(host),win(plugin),win(state)],input='\n'.join(commands)+'\n',text=True,stdout=log,stderr=log,env=env,check=True,timeout=120)
 log=(out/'Diva.log').read_text();assert 'ERROR 'not in log;assert[s for s in log.splitlines()if s.startswith('NOTE ')]==expected_notes
 raw,rate=sf.read(out/'Diva_source.wav',dtype='float32',always_2d=True);assert rate==48000 and raw.shape==baseline_raw.shape
 return raw,parameters(out/'all281.tsv')
def native(input_path,tag):
 c=NativeChain(input_path,tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 return c
def cascade(raw,p,z):
 p.load(ROOT/'PRIMARY.bin');z.load(ROOT/'POST.bin');middle,_=p.render(raw);out,_=z.render(middle);assert p.latency()+z.latency()==0;return out
def evaluate(case,reps=4,existing=None):
 label,values,allowed=case
 if existing is None:
  assert shutil.disk_usage('/tmp').free>128*2**20,'Preserve study and all accepted kits at observed storage reserve'
  folder=ROOT/label;folder.mkdir();h2p=folder/'Diva.h2p';h2p.write_text(patched(values));raw,actual=actual_Diva(h2p,folder/'actual-Diva');changed={i for i in original if actual[i]['normalized']!=original[i]['normalized']};assert changed==allowed,(label,changed,allowed)
  if label=='unchanged-control':np.testing.assert_array_equal(raw,baseline_raw)
 else:
  folder=Path(existing['source_audio']).parent.parent;h2p=folder/'Diva.h2p';raw,_=sf.read(existing['source_audio'],dtype='float32',always_2d=True);actual=parameters(folder/'actual-Diva/all281.tsv');changed={i for i in original if actual[i]['normalized']!=original[i]['normalized']}
 c,p,z=pool.get()
 try:
  padded=ROOT/('worker-'+str(c.proc.pid)+'-regenerable-native-input.wav');sf.write(padded,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT');c.load_input(padded);captures=[];audio=[];harmonic_vectors=[]
  for rep in range(reps):
   current,status=c.render();out=cascade(current,p,z);captures.append(assess(out));audio.append(out);harmonic_vectors.append(HARMONIC_CACHE.vector.copy())
  median=int(np.argsort([r['loss']for r in captures])[len(captures)//2]);selected=folder/'SELECTED_FULL_NATIVE_TWO_ZL_WIP.wav'
  if existing is None:sf.write(selected,audio[median],48000,subtype='FLOAT')
  row=dict(label=label,harmonic_residual_vector=np.mean(harmonic_vectors,axis=0).tolist(),loss=float(np.mean([r['loss']for r in captures])),realization_losses=[r['loss']for r in captures],all_stereo_preservation_passed=all(r['stereo_preservation_passed']for r in captures),source_preset=str(h2p),source_audio=str(folder/'actual-Diva/Diva_source.wav'),source_VST_chunk=str(folder/'actual-Diva/Diva_VST_chunk.bin'),selected_full_audio=str(selected),changed_parameters={actual[i]['name']:dict(before=original[i],after=actual[i])for i in sorted(changed)},all281_audited=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_ADSR_unchanged=True,assessment=captures[median],original_is_the_only_target=True,reference_match_reached=False)
  if existing is None:
   (folder/'ACTUAL_DIVA_AND_FULL_CHAIN_VERIFICATION.json').write_text(json.dumps(row,indent=2)+'\n')
   with mutex:rows.append(row);record('actual_Diva_original_target_tone_screen',latest=label,latest_mean=row['loss'],best_mean=min(r['loss']for r in rows))
  return row
 finally:pool.put((c,p,z))
def add(tar,name,y,members):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');b=f.getvalue();info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
