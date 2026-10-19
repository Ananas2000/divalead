from pathlib import Path
import os,sys,json,shutil,subprocess,signal,datetime
R=Path(__file__).resolve().parent;T=R/'balance42-first';T.mkdir(exist_ok=False);S=R/'verified-cont-0031-hf';basis=T/'basis';(basis/'analysis').mkdir(parents=True)
for a,b in [(S/'analysis/spectral_model.json',basis/'analysis/spectral_model.json'),(S/'validation.json',basis/'validation.json'),(S/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav'),(R/'baseline/source_manifest.json',basis/'source_manifest.json')]:shutil.copyfile(a,b)
state=json.loads((R/'drift24-continuation-state.json').read_text());pid=state['controller_PID'];assert b'continue_drift24.py' in Path('/proc',str(pid),'cmdline').read_bytes();os.kill(pid,signal.SIGSTOP);table={}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   st=(p/'stat').read_text().rsplit(')',1)[1].split();table[int(p.name)]=(int(st[1]),st[19],st[0])
  except (FileNotFoundError,ProcessLookupError):pass
ids=[pid]
for parent in ids:
 for child,(ppid,_,_) in table.items():
  if ppid==parent and child not in ids:ids.append(child)
rows=[]
for p in ids:
 try:os.kill(p,signal.SIGSTOP);rows.append(dict(PID=p,starttime_ticks=table[p][1],cmdline=Path('/proc',str(p),'cmdline').read_bytes().replace(b'\0',b' ').decode()))
 except (FileNotFoundError,ProcessLookupError):pass
(T/'paused-drift24.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),saved_state=state,processes=rows,resume_after_experiment=True),indent=2)+'\n')
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK='/tmp/divalead-balance42-numeric',DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='28')
try:
 with (T/'check.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'fit_three_balance42.py'),'--check-only'],env=env,stdout=log,stderr=log,check=True)
 with (T/'fit.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'fit_three_balance42.py')],env=env,stdout=log,stderr=log,check=True)
 fit=Path('/tmp/divalead-balance42-numeric/complete-balance42-basis');seed=json.loads((fit/'best.json').read_text());first=json.loads((fit/'history.json').read_text())[0]
 if seed['weighted_score']<first['weighted_score']-1e-6:
  with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(fit),'verified-balance42-0001'],env=env,stdout=log,stderr=log,check=True,timeout=900)
  actual=json.loads((R/'verified-balance42-0001/validation.json').read_text());result=dict(phase='full_actual_proof_passed',tone_score=actual['tone_score'],score=actual['score'])
 else:result=dict(phase='no_accepted_numerical_improvement',tone_score=seed['weighted_score'],initial_tone_score=first['weighted_score'])
 (T/'result.json').write_text(json.dumps(dict(result,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),match_reached=False),indent=2)+'\n');print('THREE_BALANCE42_COMPLETED',result,flush=True)
except Exception:
 import traceback;(T/'failure.log').write_text(traceback.format_exc());raise
finally:
 record=json.loads((T/'paused-drift24.json').read_text());resumed=[]
 for row in reversed(record['processes']):
  try:
   st=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
   if st[19]!=row['starttime_ticks']:continue
   os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
  except (FileNotFoundError,ProcessLookupError):pass
 record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(T/'paused-drift24.json').write_text(json.dumps(record,indent=2)+'\n')
 print('DRIFT24_RESUMED_AFTER_BALANCE42',resumed,flush=True)
