"""Fresh supplied Diva tone variants into fixed actual native+official ZL.

Every actual281 parameter and incoming MIDI event is audited. No source or
main preset is replaced; a positive screen still needs a new supported export.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,shutil,subprocess,tarfile,threading,traceback
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import D,S,WinVST3,win
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'Diva-tone-actual-current-ZL-rebase02-01'
main_control=json.loads((N/'FL20_ZL_CONTINUOUS_CONTROLLER.json').read_text());main_proc=Path('/proc')/str(main_control['owner']['PID'])
assert not main_proc.exists()or(main_proc/'stat').read_text().split()[2]=='Z','Use a graceful finite main handoff for full source studies; avoid competing /tmp buffers'
assert shutil.disk_usage('/tmp').free>=350*2**20,'Reserve350MiB for full source study captures before starting'
ROOT.mkdir(exist_ok=False)
STATE=N/'ACTUAL_DIVA_TONE_CURRENT_ZL_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();prior=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];manifest=seed['source_manifest'];baseline_dir=Path(manifest['source_preset']).parent;preset=Path(manifest['source_preset']).read_text();baseline_raw,sr=sf.read(manifest['source_audio'],dtype='float32');assert sr==48000
component=ROOT/'UNCHANGED_ZL_COMPONENT.bin';component.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
expected=[line for line in(baseline_dir/'Diva.log').read_text().splitlines()if line.startswith('NOTE ')];assert len(expected)==12
def parameters(path):return {int(r['index']):r for r in csv.DictReader(Path(path).open(),delimiter='\t')}
original=parameters(baseline_dir/'all281.tsv');assert len(original)==281
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
env=dict(os.environ,WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_native_hosts=[c.proc.pid for c,z in clients],actual_VST3_hosts=[z.child.pid for c,z in clients],actual_Diva_plugin=str(Path('/workspace/attachments/6a76beaa-924d-4f2e-8491-512d9b487af2/Diva(x64).vst3')),only_three_held_notes=True,ARP_clock_envelopes_MIDI_unchanged=True,native_and_ZL_settings_unchanged=True,main_candidate_not_modified=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def patched(values):
 section=None;used=set();out=[]
 for line in preset.splitlines():
  if line.startswith('#cm='):section=line[4:]
  if '='in line and not line.startswith('#'):
   key=line.split('=',1)[0]
   if(section,key)in values:line=key+'='+str(values[(section,key)]);used.add((section,key))
  out.append(line)
 assert used==set(values);return '\n'.join(out)+'\n'
def run_Diva(state,out,label):
 out.mkdir();commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(out/'all281.tsv'),'save '+win(out/'Diva_VST_chunk.bin'),'render '+win(out/'Diva_source.wav'),'quit']
 with(out/'Diva.log').open('w')as log:subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(state)],input='\n'.join(commands)+'\n',text=True,stdout=log,stderr=log,env=env,check=True,timeout=120)
 log=(out/'Diva.log').read_text();assert 'ERROR 'not in log;assert[line for line in log.splitlines()if line.startswith('NOTE ')]==expected
 raw,rate=sf.read(out/'Diva_source.wav',dtype='float32');assert rate==48000 and raw.shape==baseline_raw.shape
 return raw,parameters(out/'all281.tsv')
def score(y):
 r=features.residual(y[:288000]);return float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
def evaluate(case,reps=4):
 label,values,allowed=case;folder=ROOT/label;folder.mkdir();h2p=folder/'Diva.h2p';h2p.write_text(patched(values));raw,actual=run_Diva(h2p,folder/'actual-Diva',label);changed={i for i in original if actual[i]['normalized']!=original[i]['normalized']};assert changed==allowed,(label,changed,allowed)
 if label=='unchanged-control':np.testing.assert_array_equal(raw,baseline_raw)
 padded=folder/'source-with-tail.wav';sf.write(padded,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT');c,z=pool.get()
 try:
  c.load_input(padded);losses=[];assessments=[];audio=[]
  for rep in range(reps):
   native,status=c.render();out,zstatus=z.render(native);losses.append(score(out));assessments.append(features.local.last);audio.append(out)
  median=int(np.argsort(losses)[len(losses)//2]);selected=folder/'SELECTED_FULL_NATIVE_ZL_WIP.wav';sf.write(selected,audio[median],48000,subtype='FLOAT');assert z.latency()==0
  row=dict(label=label,loss=float(np.mean(losses)),realization_losses=losses,source_preset=str(h2p),source_audio=str(folder/'actual-Diva/Diva_source.wav'),source_VST_chunk=str(folder/'actual-Diva/Diva_VST_chunk.bin'),native_input=str(padded),selected_full_audio=str(selected),changed_parameters={actual[i]['name']:dict(before=original[i],after=actual[i])for i in sorted(changed)},all281_audited=True,only_requested_source_parameters_changed=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_envelopes_unchanged=True,assessment=assessments[median],reference_match_reached=False)
  (folder/'ACTUAL_DIVA_AND_FULL_CHAIN_VERIFICATION.json').write_text(json.dumps(row,indent=2)+'\n')
  with mutex:rows.append(row);record('actual_Diva_tone_candidates_with_fixed_native_and_ZL',latest_label=label,latest_mean=row['loss'],best_training_mean=min(r['loss']for r in rows))
  return row
 finally:pool.put((c,z))
try:
 record('starting_actual_fresh_Diva_tone_screen_no_main_changes')
 for k in range(2):
  c=NativeChain(manifest['native_input'],f'actual-Diva-tone-current-ZL-native-{k}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
  for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
  z=WinVST3(f'actual-Diva-tone-current-ZL-VST3-{k}');z.load(component);clients.append((c,z));pool.put((c,z))
 cases=[('unchanged-control',{},set())]
 for value in [4.8,5.5,5.9,6.1,6.5,6.8,7.2,7.8]:cases.append((f'OscMix-{value:g}',{('OSC','OscMix'):value},{96}))
 for value in [51.66,51.81,52.01,52.16]:cases.append((f'PW-{value:g}',{('OSC','PW'):value},{90}))
 for value in [.75,.9,1.1,1.25]:cases.append((f'PW-KeyFollow2-{value:g}',{('OSC','PWMDpt'):value},{108}))
 for value in [143.6,143.9,144.4,144.7]:cases.append((f'VCF-frequency-{value:g}',{('VCF1','Freq'):value},{148}))
 for value in [11.13,13.13]:cases.append((f'VCF-resonance-{value:g}',{('VCF1','Res'):value},{149}))
 control=evaluate(cases[0],12)
 with concurrent.futures.ThreadPoolExecutor(2)as executor:list(executor.map(evaluate,cases[1:]))
 (ROOT/'ALL_TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
 finalists=[]
 for row in sorted((r for r in rows if r['label']!='unchanged-control'),key=lambda r:r['loss'])[:3]:
  c,z=clients[0];c.load_input(row['native_input']);losses=[]
  for rep in range(12):raw,_=c.render();out,_=z.render(raw);losses.append(score(out))
  finalists.append(dict(row,independent_finalist_mean=float(np.mean(losses)),independent_finalist_losses=losses))
 winner=min(finalists,key=lambda r:r['independent_finalist_mean']);c0,z0=clients[0];c1,z1=clients[1];c0.load_input(control['native_input']);c1.load_input(winner['native_input']);captures=[];audio=[];record('twelve_new_actual_source_control_candidate_full_chain_pairs',selected_case=winner['label'])
 for rep in range(12):
  raw0,_=c0.render();old,_=z0.render(raw0);loss0=score(old);raw1,_=c1.render();out,_=z1.render(raw1);loss1=score(out);captures.append(dict(rep=rep,base_loss=loss0,loss=loss1,assessment=features.local.last));audio.append((old,out));record('twelve_new_actual_source_control_candidate_full_chain_pairs',selected_case=winner['label'],completed_pairs=rep+1)
 # Independently reload the actual saved Diva chunk, audit all parameters and raw audio.
 fresh,actual=run_Diva(Path(winner['source_VST_chunk']),ROOT/'selected-source-cold-chunk-replay','cold-selected');selected_raw,_=sf.read(winner['source_audio'],dtype='float32');np.testing.assert_array_equal(fresh,selected_raw);assert actual==parameters(Path(winner['source_audio']).parent/'all281.tsv');assert(ROOT/'selected-source-cold-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(winner['source_VST_chunk']).read_bytes()
 delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(12));robust=bool(np.mean(delta)>max(.0005,3*sem));archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';members=[]
 with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
  for rep,pair in enumerate(audio):
   for label,y in zip(['control','candidate'],pair):
    out=io.BytesIO();sf.write(out,y,48000,format='WAV',subtype='FLOAT');blob=out.getvalue();name=f'{label}-{rep}.wav';entry=tarfile.TarInfo(name);entry.size=len(blob);tar.addfile(entry,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
 with tarfile.open(archive)as tar:
  for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 median=sorted(range(12),key=lambda k:captures[k]['loss'])[6];sf.write(ROOT/'SELECTED_COMBINED_WIP.wav',audio[median][1],48000,subtype='FLOAT')
 summary=dict(cohort='actual-Diva-tone-with-current-ZL-rebase02',training_cases=len(rows),current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,only_three_held_notes=True,source_Diva_tone_parameters_tested=True,native_and_ZL_settings_unchanged=True,all281_and_all12_MIDI_events_audited_for_all_cases=True,selected_source_cold_effSetChunk_all281_audio_effGetChunk_byte_exact=True,selected_case=winner['label'],selected_changes=winner['changed_parameters'],requires_latest_main_revalidation_and_supported_source_export=True,not_automatically_adopted_into_main=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,captures=captures,archive_members=members)
 (ROOT/'SELECTED_SOURCE_RESEARCH_ONLY.json').write_text(json.dumps(winner,indent=2)+'\n');(ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('actual_Diva_tone_screen_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print('ACTUAL_DIVA_TONE_CONTEXT_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 record('failed_keep_all_prior_main_and_source_fixtures',error=traceback.format_exc());raise
finally:
 for c,z in clients:c.close();z.close()
