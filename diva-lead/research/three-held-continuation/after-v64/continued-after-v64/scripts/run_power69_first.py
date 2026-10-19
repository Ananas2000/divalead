"""Bounded original-three adaptive-power study, numerical scratch on tmp."""
from pathlib import Path
import os,sys,json,subprocess,shutil,signal,datetime,traceback
R=Path(__file__).resolve().parent;T=R/'power69-first';S=R/'verified-balance42-0001';basis=T/'basis-balance42';(basis/'analysis').mkdir(parents=True,exist_ok=False)
for a,b in [(S/'analysis/spectral_model.json',basis/'analysis/spectral_model.json'),(S/'validation.json',basis/'validation.json'),(S/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav'),(R/'baseline/source_manifest.json',basis/'source_manifest.json')]:shutil.copyfile(a,b)
state=json.loads((R/'drift24-continuation-state.json').read_text());pid=state['controller_PID'];assert b'continue_drift24.py' in Path('/proc',str(pid),'cmdline').read_bytes();os.kill(pid,signal.SIGSTOP);table={}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   st=(p/'stat').read_text().rsplit(')',1)[1].split();table[int(p.name)]=(int(st[1]),st[19])
  except (FileNotFoundError,ProcessLookupError):pass
ids=[pid]
for parent in ids:
 for child,(ppid,_) in table.items():
  if ppid==parent and child not in ids:ids.append(child)
rows=[]
for p in ids:
 try:os.kill(p,signal.SIGSTOP);rows.append(dict(PID=p,starttime_ticks=table[p][1]))
 except (FileNotFoundError,ProcessLookupError):pass
record=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_family_temporarily_paused='Drift24; all work retained',processes=rows)
(T/'paused-drift24.json').write_text(json.dumps(record,indent=2)+'\n')
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK='/tmp/divalead-power69-from-balance42',DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='36')
def save(phase,**kw):
 p=T/'state.json';q=p.with_suffix('.tmp');q.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,match_reached=False,automatic_Git_publication=False,**kw),indent=2)+'\n');q.replace(p)
try:
 save('checked_zero_and_two_nonzero_then_power69_fit',source_basis=str(S))
 with (T/'fit.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'fit_three_power69.py')],env=env,stdout=log,stderr=log,check=True)
 fit=Path(env['DIVALEAD_SELECTION_WORK'])/'complete-power69-basis-balance42';best=json.loads((fit/'best.json').read_text());first=json.loads((fit/'history.json').read_text())[0]
 if best['weighted_score']<first['weighted_score']-1e-6:
  save('fresh_Diva_Windows_matching_NEW_and_all12_cases',numeric_tone=best['weighted_score'])
  try:
   with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(fit),'verified-power69-0001'],env=env,stdout=log,stderr=log,check=True,timeout=900)
  except subprocess.CalledProcessError:
   from three_candidate_decision import quality_rejection
   rejected=quality_rejection(T/'validation.log',R/'verified-power69-0001')
   if rejected is None:raise
   (T/'decision.json').write_text(json.dumps(rejected,indent=2)+'\n');save('candidate_rejected_by_fresh_quality',decision=rejected)
  else:
   actual=json.loads((R/'verified-power69-0001/validation.json').read_text());save('full_actual_proof_passed',tone_score=actual['tone_score'],score=actual['score'])
 else:save('no_accepted_numerical_improvement',initial_tone=first['weighted_score'],selected_tone=best['weighted_score'])
except Exception:save('failed',error=traceback.format_exc());raise
finally:
 resumed=[]
 for row in reversed(record['processes']):
  try:
   st=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
   if st[19]!=row['starttime_ticks']:continue
   os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
  except (FileNotFoundError,ProcessLookupError):pass
 record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(T/'paused-drift24.json').write_text(json.dumps(record,indent=2)+'\n');print('POWER69_DONE_DRIFT_WORK_RESUMED',resumed,flush=True)
