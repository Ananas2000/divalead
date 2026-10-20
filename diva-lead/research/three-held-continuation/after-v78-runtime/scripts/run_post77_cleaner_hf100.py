"""Use the phase worker's slot only after its active fit has finished; always release it."""
from pathlib import Path
import datetime,fcntl,json,os,signal,subprocess,sys,time,traceback,shutil
R=Path(__file__).resolve().parent;PY='/workspace/.venvs/divalead/bin/python';B=R/'source-post74joint-basis'
lock=(R/'post77-cleaner-hf100-owner.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
parent=None;start=None
def write(p,d):q=p.with_suffix('.tmp');q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p)
def state(phase,**extra):write(R/'post77-cleaner-hf100-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,phase_parent_PID=parent,phase_parent_starttime=start,phase_parent_temporarily_stopped=parent is not None,only_three_held=True,numeric_workers=1,match_reached=False,**extra))
def proc(pid):
 try:
  p=Path('/proc',str(pid));stat=(p/'stat').read_text().rsplit(')',1)[1].split();cmd=(p/'cmdline').read_bytes().split(b'\0')
  return dict(state=stat[0],ppid=int(stat[1]),start=stat[19],cmd=cmd)
 except FileNotFoundError:return None
def children(pid):return [(int(p.name),d) for p in Path('/proc').iterdir() if p.name.isdigit() and (d:=proc(int(p.name))) is not None and d['ppid']==pid and d['state']!='Z']
try:
 while parent is None:
  state('waiting_for_phase_fit_to_finish_before_using_its_slot')
  d=json.loads((R/'post74joint-phase-state.json').read_text())
  if d['phase']=='fresh_Diva_Windows_own_NEW_12_cases_proof' and shutil.disk_usage(R).free>=384*1048576:
   pid=d['controller_PID'];p=proc(pid);assert p and str(R/'continue_post74joint_phase.py').encode() in p['cmd']
   os.kill(pid,signal.SIGSTOP);after=json.loads((R/'post74joint-phase-state.json').read_text())
   if after['phase']!=d['phase'] or any(any(b'/fit_three_' in x for x in c['cmd']) for _,c in children(pid)):
    os.kill(pid,signal.SIGCONT);time.sleep(3);continue
   parent=pid;start=p['start'];state('phase_fit_finished_waiting_for_its_existing_full_proof')
   while children(parent):time.sleep(3)
   break
  time.sleep(5)
 state('claimed_phase_numeric_slot_after_its_fit_and_proof_finished')
 checked=json.loads(subprocess.check_output([PY,'-B',str(R/'auto_backup_three.py'),'--check-only'],text=True));S=Path(checked['best']).parent;report=json.loads((S/'validation.json').read_text())
 assert report['source_family']=='Post74 joint oscillator-filter'
 run=R/'post77-cleaner-hf100-research';run.mkdir(exist_ok=False);basis=run/'basis';(basis/'analysis').mkdir(parents=True)
 for a,b in [(report['core_model'],basis/'analysis/spectral_model.json'),(S/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav'),(S/'validation.json',basis/'validation.json'),(B/'source_manifest.json',basis/'source_manifest.json')]:shutil.copyfile(a,b)
 scratch=Path('/tmp/divalead-post77-cleaner-hf100');scratch.mkdir(exist_ok=False);write(run/'numeric-location.json',dict(numeric_scratch=str(scratch),baseline=str(basis),only_three_held=True,source_family='Post74 joint oscillator-filter',numeric_workers=1))
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(B),DIVALEAD_THREE_SOURCE_REPORT=str(S/'validation.json'),DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(scratch),DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='18')
 with (run/'fit.log').open('w') as log:
  child=subprocess.Popen([PY,'-B',str(R/'fit_three_hf_cleaner100.py')],env=env,stdout=log,stderr=log)
  state('cleaner_HF100_fit_with_extra_noise_cap',fit_PID=child.pid,fit_log=str(run/'fit.log'),baseline_validation=str(S/'validation.json'));assert child.wait()==0
 fit=scratch/'complete-hf-basis';choice=json.loads((fit/'best.json').read_text());initial=json.loads((fit/'history.json').read_text())[0]['weighted_score']
 if choice['weighted_score']<initial-1e-6:
  target=R/'post74joint-verified-post77-cleaner-hf100-0001';state('fresh_Diva_Windows_own_NEW_all12_cases_proof')
  with (run/'validation.log').open('w') as log:
   result=subprocess.run([PY,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log)
  if result.returncode:
   from three_candidate_decision import quality_rejection
   rejected=quality_rejection(run/'validation.log',target);assert rejected is not None;write(run/'decision.json',rejected)
  else:
   actual=json.loads((target/'validation.json').read_text());write(run/'decision.json',dict(fully_proved=True,tone_score=actual['tone_score'],upper_off=actual['metrics']['upper_off'],extra_noise_cap=choice['extra_cleaner_upper_off_cap'],match_reached=False))
 else:write(run/'decision.json',dict(accepted=False,reason='No strict original-tone improvement within extra noise cap',match_reached=False))
 state('cleaner_search_finished_releasing_phase_slot')
except Exception:
 state('failed_preserve_data_and_release_phase_slot',error=traceback.format_exc());raise
finally:
 if parent is not None:
  p=proc(parent)
  if p and p['start']==start and str(R/'continue_post74joint_phase.py').encode() in p['cmd']:os.kill(parent,signal.SIGCONT)
  parent=None;start=None
  previous=json.loads((R/'post77-cleaner-hf100-state.json').read_text());previous.update(phase_parent_temporarily_stopped=False,phase_slot_released=True);write(R/'post77-cleaner-hf100-state.json',previous)
