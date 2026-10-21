"""Idempotent launcher for this verified native family; respects stop/pause controls."""
from pathlib import Path
import fcntl,json,os,subprocess,time
W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
N.mkdir(exist_ok=True);statefile=N/'NATIVE_SEARCH_CONTROLLER.json'
def identity(pid):
 try:
  v=Path(f'/proc/{pid}/stat').read_text().split()
  if v[2]=='Z':return None
  return dict(PID=pid,starttime=v[21],cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode())
 except FileNotFoundError:return None
with (N/'native-launch.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 if statefile.exists():
  state=json.loads(statefile.read_text());old=state.get('controller')
  if old and identity(old['PID'])==old:
   assert 'continue_native_chorus.py' in old['cmdline'],'An older controller is active; do not launch a duplicate'
   print(json.dumps(dict(already_running=True,controller=old,phase=state['phase'],duplicate_started=False)));raise SystemExit(0)
 assert not (N/'native-search.stop').exists(),'Existing stop control must be inspected'
 assert not (N/'native-search.pause').exists(),'Existing pause control must be inspected'
 priority=json.loads(Path('/workspace/divalead-work/three-held-continuation/native-effects-priority.json').read_text());assert priority['active']
 for name in ['fl_native_chorus_verified_host.exe','fl_native_source_variants_host.exe','native-frozen-source-with-tail.wav','dsp_ippv2_x64.dll','QuickFontCache_x64.dll','freetype_x64.dll']:assert (W/name).is_file(),name
 assert Path('/tmp/.X11-unix/X90').exists(),'Verify and start the Xvfb :90 display before native audio work'
 public=P/'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP/verification/candidate.json'
 candidates=[p for p in [N/'NATIVE_BEST_CANDIDATE.json',N/'NATIVE_PW_PHASE_BEST_CANDIDATE.json',public,*sorted((N/'native-Chorus-completed').glob('*/full-validated-candidate.json'))] if p.is_file()]
 checked=[]
 for path in candidates:
  row=json.loads(path.read_text())
  if len(row.get('x',[])) in [94,95] and row.get('robust_improvement',True) and not row.get('full_fresh_native_validation_pending',False) and not row.get('new_family_full_validation_pending',False) and row.get('full_fresh_native_realizations',0)>=6:
   checked.append((row['loss'],path))
 assert checked,'No fully validated durable native Chorus candidate'
 seed=min(checked,key=lambda pair:pair[0])[1]
 selected=json.loads(seed.read_text());manifest=selected.get('source_manifest')
 if manifest:
  import hashlib,numpy as np,soundfile as sf
  raw=Path(manifest['source_audio']);preset=Path(manifest['source_preset'])
  assert hashlib.sha256(raw.read_bytes()).hexdigest()==manifest['source_audio_SHA256']
  assert hashlib.sha256(preset.read_bytes()).hexdigest()==manifest['source_preset_SHA256']
  y,rate=sf.read(raw,dtype='float32',always_2d=True);assert rate==48000 and y.shape==(288000,2)
  fresh_input=W/'native-selected-source-with-tail.wav';sf.write(fresh_input,np.pad(y,((0,32768),(0,0))),48000,subtype='FLOAT')
  manifest['native_input']=str(fresh_input);selected['source_manifest']=manifest
  seed=N/'NATIVE_STARTUP_SELECTED_CANDIDATE.json';seed.write_text(json.dumps(selected,indent=2)+'\n')
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 with (W/'continue_native_chorus.log').open('a') as log:
  child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(W/'continue_native_chorus.py'),str(seed)],env=env,stdout=log,stderr=log,start_new_session=True)
 deadline=time.monotonic()+15
 while time.monotonic()<deadline:
  assert child.poll() is None,'Inspect continue_native_chorus.log; startup failed'
  if statefile.exists():
   state=json.loads(statefile.read_text())
   if state.get('controller',{}).get('PID')==child.pid:
    print(json.dumps(dict(started=True,controller=state['controller'],phase=state['phase'])));break
  time.sleep(.1)
 else:raise RuntimeError('Controller did not report current readiness')
