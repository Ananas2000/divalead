from pathlib import Path
import os,subprocess,json,sys,datetime
R=Path(__file__).resolve().parent;env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(R/'phase18-basis'),DIVALEAD_SELECTION_WORK=str(R/'phase18-numeric'),DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='36')
def save(phase,**kw):
 p=R/'phase18-state.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(dict(phase=phase,PID=os.getpid(),UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),incoming_notes_per_phrase=3,ARP_unchanged=True,automatic_Git_publication=False,match_reached=False,**kw),indent=2)+'\n');t.replace(p)
try:
 save('phase18_fit')
 with (R/'phase18-fit.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'fit_three_phase18.py')],env=env,stdout=log,stderr=log,check=True)
 fit=R/'phase18-numeric/complete-phase-phase18-basis';choice=json.loads((fit/'best.json').read_text());initial=json.loads((fit/'history.json').read_text())[0]['weighted_score']
 if choice['weighted_score']<initial-1e-6:
  save('fresh_Diva_Windows_own_NEW_and_12_cases',numeric_tone=choice['weighted_score'])
  with (R/'phase18-validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(fit),'verified-phase18-0001'],env=env,stdout=log,stderr=log,check=True,timeout=900)
  report=json.loads((R/'verified-phase18-0001/validation.json').read_text());save('full_actual_proof_passed',tone_score=report['tone_score'],score=report['score'])
 else:save('no_accepted_improvement',initial_tone=initial,selected_tone=choice['weighted_score'])
except Exception:
 import traceback;save('failed',error=traceback.format_exc());raise
