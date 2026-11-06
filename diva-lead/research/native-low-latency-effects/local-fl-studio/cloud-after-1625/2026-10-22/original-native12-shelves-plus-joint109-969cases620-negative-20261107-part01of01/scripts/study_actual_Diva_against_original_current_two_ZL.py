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
ROOT=Path('/tmp/divalead-original-target-Diva-tone-20261025-01');ROOT.mkdir(exist_ok=False)
STATE=N/'ACTUAL_DIVA_ORIGINAL_TARGET_TWO_ZL_STUDY.json';OWNER='original-reference-tone-finite-20261025'
stop=json.loads((N/'zl-stereo-continuation.stop').read_text());assert stop['owner']==OWNER
main=json.loads((N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json').read_text());mp=Path('/proc')/str(main['owner']['PID']);assert not mp.exists()or(mp/'stat').read_text().split()[2]=='Z'
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
  padded=ROOT/('worker-'+str(c.proc.pid)+'-regenerable-native-input.wav');sf.write(padded,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT');c.load_input(padded);captures=[];audio=[]
  for rep in range(reps):
   current,status=c.render();out=cascade(current,p,z);captures.append(assess(out));audio.append(out)
  median=int(np.argsort([r['loss']for r in captures])[len(captures)//2]);selected=folder/'SELECTED_FULL_NATIVE_TWO_ZL_WIP.wav'
  if existing is None:sf.write(selected,audio[median],48000,subtype='FLOAT')
  row=dict(label=label,loss=float(np.mean([r['loss']for r in captures])),realization_losses=[r['loss']for r in captures],all_stereo_preservation_passed=all(r['stereo_preservation_passed']for r in captures),source_preset=str(h2p),source_audio=str(folder/'actual-Diva/Diva_source.wav'),source_VST_chunk=str(folder/'actual-Diva/Diva_VST_chunk.bin'),selected_full_audio=str(selected),changed_parameters={actual[i]['name']:dict(before=original[i],after=actual[i])for i in sorted(changed)},all281_audited=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_ADSR_unchanged=True,assessment=captures[median],original_is_the_only_target=True,reference_match_reached=False)
  if existing is None:
   (folder/'ACTUAL_DIVA_AND_FULL_CHAIN_VERIFICATION.json').write_text(json.dumps(row,indent=2)+'\n')
   with mutex:rows.append(row);record('actual_Diva_original_target_tone_screen',latest=label,latest_mean=row['loss'],best_mean=min(r['loss']for r in rows))
  return row
 finally:pool.put((c,p,z))
def add(tar,name,y,members):
 f=io.BytesIO();sf.write(f,y,48000,format='WAV',subtype='FLOAT');b=f.getvalue();info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
try:
 record('starting_fresh_actual_Diva_with_original_only_objective')
 for k in range(2):
  c=native(source['native_input'],'OriginalTarget-Diva-native-'+str(k));p=WinVST3('OriginalTarget-Diva-primary-'+str(k));z=WinVST3('OriginalTarget-Diva-post-'+str(k));clients.append((c,p,z));pool.put((c,p,z))
 cases=[('unchanged-control',{},set())]
 for v in [5.8,6.2,6.8,7.2]:cases.append((f'OscMix-{v:g}',{('OSC','OscMix'):v},{96}))
 for v in [51.76,51.86,51.96,52.06]:cases.append((f'PW-{v:g}',{('OSC','PW'):v},{90}))
 for v in [.5,1.5]:cases.append((f'PW-KeyFollow2-{v:g}',{('OSC','PWMDpt'):v},{108}))
 for v in [143.6,144.7]:cases.append((f'Cutoff-{v:g}',{('VCF1','Freq'):v},{148}))
 for v in [10.5,13.8]:cases.append((f'Resonance-{v:g}',{('VCF1','Res'):v},{149}))
 for v in [20,30]:cases.append((f'Drift-{v:g}',{('OSC','Drift'):v},{134}))
 for v in [.6,1.6]:cases.append((f'PlateWet-{v:g}',{('Plate2','Wet'):v},{235}))
 for v in [-62,-54]:cases.append((f'VCA-ModDepth-{v:g}',{('VCA1','ModDpt'):v},{171}))
 control=evaluate(cases[0],8)
 with concurrent.futures.ThreadPoolExecutor(2)as executor:list(executor.map(evaluate,cases[1:]))
 (ROOT/'ALL_TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
 allowed=sorted([r for r in rows if r['label']!='unchanged-control'and r['all_stereo_preservation_passed']],key=lambda r:r['loss'])[:3];finalists=[]
 for row in allowed:finalists.append(evaluate(('fresh-finalist-'+row['label'],{},set()),8,existing=row))
 (ROOT/'FRESH_FINALISTS.json').write_text(json.dumps(finalists,indent=2)+'\n')
 winner=min(finalists,key=lambda r:r['loss'])if finalists else control
 ready=bool(winner is not control and control['loss']-winner['loss']>.0003 and winner['all_stereo_preservation_passed'])
 frozen=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),winner=winner,training_control_mean=control['loss'],sufficient_screen=ready,original_is_the_only_target=True,not_adopted=True);(ROOT/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(frozen,indent=2)+'\n')
 summary=dict(training_cases=len(rows),training_control_mean=control['loss'],training_best=winner,robust_improvement=False,sufficient_screen=ready,all281_and_all12_events_audited=True,source_changed_only_as_recorded=True,native06_and_both_ZL_unchanged=True,original_is_the_only_target=True,v83_Finish_not_used=True,only_three_held_notes=True,not_adopted=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
 if ready:
  record('frozen_actual_Diva_candidate_fresh6_plus_two_cold_full_chain_pairs',winner=winner['label'])
  candidate_raw,_=sf.read(winner['source_audio'],dtype='float32',always_2d=True);candidate_input=ROOT/'selected-source-with-tail.wav';sf.write(candidate_input,np.pad(candidate_raw,((0,32768),(0,0))),48000,subtype='FLOAT')
  c0,p0,z0=clients[0];c1,p1,z1=clients[1];c0.load_input(source['native_input']);c1.load_input(candidate_input);captures=[];members=[]
  with tarfile.open(ROOT/'EIGHT_FRESH_NATIVE_AND_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(8):
    if rep in [6,7]:
     c0.close();c1.close();c0=native(source['native_input'],'OriginalTarget-Diva-cold-control-'+str(rep));c1=native(candidate_input,'OriginalTarget-Diva-cold-candidate-'+str(rep));clients[0]=(c0,p0,z0);clients[1]=(c1,p1,z1)
    raw0,_=c0.render();old=cascade(raw0,p0,z0);r0=assess(old);raw1,_=c1.render();out=cascade(raw1,p1,z1);r1=assess(out);captures.append(dict(rep=rep,control=r0,candidate=r1,improvement=r0['loss']-r1['loss']))
    for label,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:add(tar,f'{label}-{rep}.wav',y,members)
    if rep==0:
     for label,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(ROOT/(label+'_00.wav'),y,48000,subtype='FLOAT')
  cold,actual=actual_Diva(Path(winner['source_VST_chunk']),ROOT/'selected-source-cold-chunk-replay');np.testing.assert_array_equal(cold,candidate_raw);assert actual==parameters(Path(winner['source_audio']).parent/'all281.tsv');assert(ROOT/'selected-source-cold-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(winner['source_VST_chunk']).read_bytes()
  delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  with tarfile.open(ROOT/'EIGHT_FRESH_NATIVE_AND_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in members:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,selected_source_cold_chunk_all281_audio_and_chunk_bytes_exact=True)
  (ROOT/'SELECTED_SOURCE_RESEARCH_ONLY.json').write_text(json.dumps(winner,indent=2)+'\n')
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('actual_original_target_Diva_screen_complete_not_adopted',robust_improvement=summary['robust_improvement'],selected=winner['label'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members','training_best']}),flush=True)
except BaseException:record('failed_preserve_previous_accepted_kit',error=traceback.format_exc());raise
finally:
 for c,p,z in clients:c.close();p.close();z.close()
