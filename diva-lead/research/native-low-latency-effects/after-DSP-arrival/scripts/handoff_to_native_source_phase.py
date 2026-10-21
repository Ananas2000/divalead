from pathlib import Path
import datetime,json,os,signal,subprocess,time
N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects');state=N/'NATIVE_SEARCH_CONTROLLER.json';s=json.loads(state.read_text())
def identity(pid):
 try:
  p=Path(f'/proc/{pid}');f=(p/'stat').read_text().split()
  if f[2]=='Z':return None
  return dict(PID=pid,starttime=f[21],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
 except FileNotFoundError:return None
proof=json.loads((N/'NATIVE_PW_PHASE_BEST_CANDIDATE.json').read_text());assert len(proof['x'])==95 and proof['robust_improvement'] and not proof['new_family_full_validation_pending']
assert s['phase']=='native_Chorus_original_reference_search_running' and not (N/'NATIVE_FINITE_BRANCH.json').exists()
assert identity(s['controller']['PID'])==s['controller'] and identity(s['child']['PID'])==s['child']
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Fresh actual Diva + 16 FST + six full captures proved the PW/phase family better; retire frozen-source plateau cohort',last_old_state=s,new_seed_loss=proof['loss'],new_source_manifest=proof['source_manifest'])
(N/'PW_PHASE_FAMILY_HANDOFF.json').write_text(json.dumps(receipt,indent=2)+'\n')
os.kill(s['controller']['PID'],signal.SIGTERM);os.kill(s['child']['PID'],signal.SIGINT)
deadline=time.monotonic()+90
while identity(s['child']['PID']) is not None:
 assert time.monotonic()<deadline;time.sleep(1)
assert identity(s['controller']['PID']) is None
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'start_native_chorus.py')],check=True)
print('NATIVE_PW_SOURCE_PHASE_COHORT_HANDOFF_COMPLETED')
