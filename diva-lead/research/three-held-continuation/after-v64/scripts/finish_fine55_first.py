from pathlib import Path
import os,sys,json,time,datetime,subprocess,signal,traceback,fcntl
R=Path(__file__).resolve().parent;T=R/'fine55-first';lock=(T/'finish.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def save(phase,**kw):
 p=T/'state.json';q=p.with_suffix('.tmp');q.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),coordinator_PID=os.getpid(),phase=phase,incoming_notes_per_phrase=3,automatic_Git_publication=False,match_reached=False,**kw),indent=2)+'\n');q.replace(p)
launch=json.loads((T/'launch.json').read_text());pid=launch['PID']
try:
 while True:
  try:
   stat=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
   if stat[0]=='Z':break
  except FileNotFoundError:break
  save('three_held_fine55_fit',fit_PID=pid,fit_log=str(T/'fit.log'),source_basis=launch['basis']);time.sleep(10)
 fit=T/'numeric/complete-fine_phase-basis';assert (fit/'optimizer.json').exists(),'fit did not finish normally'
 best=json.loads((fit/'best.json').read_text());first=json.loads((fit/'history.json').read_text())[0]
 if best['weighted_score']<first['weighted_score']-1e-6:
  save('fresh_Diva_Windows_matching_NEW_and_12_cases',numeric_tone=best['weighted_score'])
  try:
   with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(fit),'verified-fine55-0001'],stdout=log,stderr=log,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),check=True,timeout=900)
  except subprocess.CalledProcessError:
   from three_candidate_decision import quality_rejection
   rejected=quality_rejection(T/'validation.log',R/'verified-fine55-0001')
   if rejected is None:raise
   (T/'decision.json').write_text(json.dumps(rejected,indent=2)+'\n');save('candidate_rejected_by_fresh_quality',decision=rejected)
  else:
   actual=json.loads((R/'verified-fine55-0001/validation.json').read_text());save('full_actual_proof_passed',tone_score=actual['tone_score'],score=actual['score'],validation=str(R/'verified-fine55-0001/validation.json'))
 else:save('no_accepted_numerical_improvement',initial_tone=first['weighted_score'],selected_tone=best['weighted_score'])
except Exception:save('failed',error=traceback.format_exc());raise
finally:
 record=json.loads((R/'phase18-paused-for-fine55.json').read_text());resumed=[]
 for row in reversed(record['processes']):
  try:
   stat=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
   assert stat[19]==row['starttime_ticks']
   os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
  except FileNotFoundError:pass
 record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(R/'phase18-paused-for-fine55.json').write_text(json.dumps(record,indent=2)+'\n')
 print('FINE55_FINISHED_AND_PHASE18_WORK_RESUMED',resumed,flush=True)
