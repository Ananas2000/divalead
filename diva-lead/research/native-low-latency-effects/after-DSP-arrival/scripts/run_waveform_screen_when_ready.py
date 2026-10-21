from pathlib import Path
import json,os,subprocess,time
N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects');deadline=time.monotonic()+55
while time.monotonic()<deadline:
 s=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text())
 if s.get('phase')=='native_Chorus_original_reference_search_running' and s.get('generation',0)>=5 and not (N/'NATIVE_FINITE_BRANCH.json').exists():
  pid=s['child']['PID'];children=subprocess.check_output(['ps','-o','args=','--ppid',str(pid)],text=True)
  if children.count('fl_native_common_phase_host.exe')==4:
   e=os.environ.copy();e.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'probe_Diva_waveforms_native.py')],env=e,check=True);raise SystemExit(0)
 time.sleep(1)
print('WAVEFORM_SCREEN_WAIT_BOUNDARY_NOT_REACHED_NO_MUTATIONS')
