"""One four-worker controller for real low-latency native Chorus/EQ renders.

Every accepted family is validated on fresh whole-chain captures. Numbered
releases remain unchanged. Files with stop/pause names control this process.
"""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,signal,subprocess,sys,time,traceback
W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation');P=Path('/workspace/divalead')
PY='/workspace/.venvs/divalead/bin/python';STATE=N/'NATIVE_SEARCH_CONTROLLER.json';STOP=N/'native-search.stop';PAUSE=N/'native-search.pause'
lock=(N/'native-search-controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def read(p):
 for attempt in range(5):
  try:return json.loads(Path(p).read_text())
  except json.JSONDecodeError:
   if attempt==4:raise
   time.sleep(.05)
def identity(pid):
 try:
  fields=Path(f'/proc/{pid}/stat').read_text().split()
  if fields[2]=='Z':return None
  return dict(PID=pid,starttime=fields[21],cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode())
 except FileNotFoundError:return None
def state(phase,**fields):
 data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller=identity(os.getpid()),phase=phase,model_family='native_Chorus_and_EQ_three_held',only_three_held_notes=True,native_DLL_audio=True,numeric_workers=4,old_Finish_controllers_not_started=True,free_running_Chorus_validated_over_repeated_real_captures=True,match_reached=False,**fields)
 tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(STATE)
def run(script,args,log):
 with Path(log).open('w') as f:subprocess.run([PY,'-B',str(W/script),*map(str,args)],env=env,stdout=f,stderr=f,check=True)
def publish(candidate,tag):
 kit=W/(tag+'-checkpoint-WIP')
 run('export_native_chorus_checkpoint.py',[candidate,kit],W/(tag+'-export.log'))
 run('verify_fst_with_pyflp.py',[kit],W/(tag+'-parse.log'))
 run('complete_native_checkpoint.py',[kit],W/(tag+'-guide.log'))
 run('verify_native_latency_blocks.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],W/(tag+'-latency.log'))
 run('assess_native_reference.py',[kit/'verification/NATIVE_WITH_TAIL_WIP.wav'],W/(tag+'-reference.log'))
 shutil.copyfile(W/'reference-assessment/COMPARISON.json',kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json')
 proof=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json');assert proof['preset_state_bytes_exact'] and proof['zero_depth_routing_audio_exact']
 actual=read(kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json')[-1];expected=read(kit/'verification/candidate.json')['original_reference_assessment'];assert abs(actual['tone_score']-expected['tone_score'])<2e-5
 run('publish_native_progress.py',[kit],W/(tag+'-Git.log'))
 return kit
best_path=Path(sys.argv[1]);best=read(best_path);assert len(best['x'])==94
session=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');child=None
try:
 source=P/'diva-lead/v83-wip/Diva_SOURCE_FROZEN_48k.wav';source_hash='7a852ee05341c77708faced2e554c3f45080a691b5f001322221ec5cd9bf027e'
 assert read(R/'native-effects-priority.json')['active']
 generation=0
 while not STOP.exists():
  while PAUSE.exists() or shutil.disk_usage('/workspace').free<64*1024**2 or shutil.disk_usage('/tmp').free<512*1024**2:
   if STOP.exists():break
   state('paused_by_control_file_or_actual_disk_limit',best_candidate=str(best_path),best_loss=best['loss'],root_free_MiB=shutil.disk_usage('/workspace').free/1024**2,tmp_free_MiB=shutil.disk_usage('/tmp').free/1024**2);time.sleep(10)
  if STOP.exists():break
  assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
  (N/'NATIVE_BEST_CANDIDATE.json').write_text(json.dumps(best,indent=2)+'\n')
  public=P/'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP/verification/candidate.json'
  if public.exists() and best['loss']<read(public)['loss']*.99:
   tag=f'chorus-{session}-{generation:04d}'
   state('verifying_native_Chorus_checkpoint_for_Git',generation=generation,best_candidate=str(best_path),best_loss=best['loss'])
   publish(best_path,tag)
  generation+=1;tag=f'chorus-{session}-{generation:04d}';root=W/tag
  script='search_native_chorus_controls.py' if generation%2 else 'search_native_chorus.py'
  seed=W/(tag+'-seed.json');seed.write_text(json.dumps(best,indent=2)+'\n')
  e=env.copy();e['DIVALEAD_CHORUS_GENERATION']=str(generation)
  log=(W/(tag+'.log')).open('w');child=subprocess.Popen([PY,'-B',str(W/script),str(seed),str(root)],env=e,stdout=log,stderr=log)
  while child.poll() is None:
   progress=read(root/'search-state.json') if (root/'search-state.json').exists() else None
   state('native_Chorus_original_reference_search_running',generation=generation,search_kind=script,child=identity(child.pid),search_root=str(root),best_candidate=str(best_path),best_loss=best['loss'],progress=progress)
   if (root/'best.json').exists():
    (N/'NATIVE_LIVE_TRAINING_CANDIDATE.json').write_text(json.dumps(dict(candidate=read(root/'best.json'),not_accepted_until_fresh_full_validation=True),indent=2)+'\n')
   if STOP.exists():child.send_signal(signal.SIGINT);child.wait(timeout=90);break
   time.sleep(10)
  log.close()
  if STOP.exists():break
  assert child.returncode==0
  got=read(root/'full-validated-candidate.json')
  if got.get('robust_improvement') and got['loss']<best['loss']:
   best=got;best_path=root/'full-validated-candidate.json'
  # All completed experiment metadata is small and durable; training WAVs stay temporary.
  dest=N/'native-Chorus-completed'/tag;dest.mkdir(parents=True,exist_ok=True)
  for name in ['completion.json','full-validated-candidate.json','paired-fresh-control.json','heldout-prefix-validation.json']:
   if (root/name).is_file():shutil.copyfile(root/name,dest/name)
 state('stopped_by_control_file',best_candidate=str(best_path),best_loss=best['loss'])
except BaseException:
 state('failed_preserve_files_and_diagnose',best_candidate=str(best_path),best_loss=best['loss'],error=traceback.format_exc());raise
