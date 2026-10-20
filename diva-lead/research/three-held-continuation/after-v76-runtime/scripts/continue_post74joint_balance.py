"""Alternate42 existing final-balance and69 dynamic-target values of the exact selected three-held source.

No Git writes and no automatic assistant messages. Published releases remain
immutable. All search limits stay anchored to the original preferred source.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,fcntl,datetime,traceback,shutil
ROOT=Path(__file__).resolve().parent;B=ROOT/'source-post74joint-basis';WORK=ROOT/'post74joint-live-balance';WORK.mkdir(exist_ok=True)
MIN_FREE_MIB=int(os.environ.get('DIVALEAD_MIN_FREE_MIB','1024'))
PY=sys.executable;STATE=ROOT/'post74joint-balance-state.json'
def write(p,x):
 q=p.with_suffix('.tmp');q.write_text(json.dumps(x,indent=2)+'\n');q.replace(p)
def state(phase,**kw):write(STATE,dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_PID=os.getpid(),phase=phase,user_selected_three=True,existing_balance42_or_power69=True,numeric_workers=1,automatic_Git_publication=False,match_reached=False,source_family='Post74 joint oscillator-filter',**kw))
anchor=json.loads((ROOT/'baseline/validation.json').read_text())
def checked(path):
 r=json.loads(path.read_text());assert r['source_family']=='Post74 joint oscillator-filter' and r['changed_source_fields']=={'OSC:PW':51.91,'OSC:OscMix':5.71,'VCF1:Res':12.13,'VCF1:Freq':144.16};assert r['all_chosen_three_guards_passed'] and r['original_three_held_MIDI_events_unchanged']
 assert r['Windows_native_max_error']<2e-7 and r['full_NEW_SOURCE_independent_max_error']<3e-7 and r['spectral_fixture_max_error']<2e-7
 assert Path(r['source_preset']).read_bytes()==(B/'Diva_THREE_HELD_BASELINE.h2p').read_bytes()
 assert hashlib.sha256(Path(r['new_source_raw']).read_bytes()).digest()==hashlib.sha256((B/'Diva_source.wav').read_bytes()).digest()
 assert Path(r['NEW_independent_prebase']).read_bytes()==(B/'NEW-independent-base-pdc.wav').read_bytes()
 assert all(r['metrics'][k]<=anchor['metrics'][k]*limit for k,limit in r['guard_limits'].items())
 assert r['crest_RMS_dB']<=anchor['crest_RMS_dB']*1.001 and r['score']<=anchor['score']*1.0001
 cases=json.loads((path.parent/'arbitrary-input-verification.json').read_text())['arbitrary_input_no_MIDI_cases']
 assert len(cases)==12 and {x['sample_rate'] for x in cases}=={44100,48000,96000,192000} and all(x['causal_prefix_equal'] and x['independent_max_error']<2e-10 for x in cases)
 assert (path.parent/'Diva_all281.tsv').read_bytes()==(B/'Diva_all281.tsv').read_bytes()
 events=[list(map(int,line.split()[1:])) for line in (path.parent/'Diva.log').read_text().splitlines() if line.startswith('NOTE ')]
 assert events==json.loads((B/'MIDI_events_48k.json').read_text())
 return r
def available():
 choices=[]
 for path in ROOT.glob('post74joint-verified-*/validation.json'):
  try:r=checked(path)
  except json.JSONDecodeError:
   if time.time()-path.stat().st_mtime<2:continue
   raise
  choices.append((r['tone_score'],path,r))
 assert choices
 return min(choices,key=lambda v:v[0])
if '--check-only' in sys.argv:
 tone,path,r=available();print(json.dumps(dict(tone_score=tone,score=r['score'],validation=str(path),all_three_source_hashes_and_full_proofs_and_12_cases_checked=True,old_sixteen_source_rejected=True,match_reached=False),indent=2));raise SystemExit(0)
lock=(ROOT/'post74joint-balance.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 if '--wait-for-current-fits' in sys.argv:
  watched=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    cmd=(p/'cmdline').read_bytes().replace(b'\x00',b' ').decode()
    if cmd.startswith('/workspace/.venvs/divalead/bin/python ') and any(str(ROOT/name) in cmd for name in ['fit_three_hf_fixed_anchor.py','fit_three_gains.py']):watched.append(int(p.name))
   except (FileNotFoundError,ProcessLookupError):pass
  while watched:
   alive=[]
   for pid in watched:
    try:
     fields=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
     if fields[0]!='Z':alive.append(pid)
    except FileNotFoundError:pass
   watched=alive
   if watched:state('waiting_for_current_three_fit_completion',fit_PIDs=watched);time.sleep(15)
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(B))
 seenpath=WORK/'attempted.json';seen=json.loads(seenpath.read_text()) if seenpath.exists() else []
 if not seenpath.exists():
  write(seenpath,seen)
 while True:
  tone,path,report=available();env['DIVALEAD_THREE_SOURCE_REPORT']=str(path);write(ROOT/'POST74JOINT_BALANCE_BEST_ACTUAL.json',dict(validation=str(path),tone_score=tone,score=report['score'],source='Post74 joint oscillator-filter three-held',all_chosen_three_guards_passed=True,match_reached=False))
  digest=hashlib.sha256(Path(report['core_model']).read_bytes()).hexdigest();order=['balance42','power69'] if len(seen)%2==0 else ['power69','balance42'];kind=next((k for k in order if digest+':'+k not in seen),None)
  if kind is None:state('waiting_for_changed_proved_three_basis',best_validation=str(path),tone_score=tone,score=report['score']);time.sleep(15);continue
  if shutil.disk_usage(ROOT).free<MIN_FREE_MIB*1024**2:state('paused_low_workspace_space',best_validation=str(path),minimum_free_MiB=MIN_FREE_MIB);time.sleep(15);continue
  index=max([0]+[int(p.name.split('-')[1]) for p in WORK.glob('round-*') if p.is_dir() and p.name.split('-')[1].isdigit()])+1;run=WORK/('round-'+format(index,'04d')+'-'+kind);basis=run/'basis';(basis/'analysis').mkdir(parents=True)
  shutil.copyfile(report['core_model'],basis/'analysis/spectral_model.json');shutil.copyfile(path.parent/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav');shutil.copyfile(path,basis/'validation.json');shutil.copyfile(B/'source_manifest.json',basis/'source_manifest.json')
  scratch=Path('/tmp/divalead-post74joint-live-balance')/run.name;scratch.mkdir(parents=True,exist_ok=False)
  runenv=dict(env,DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(scratch),DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='36')
  write(run/'numeric-location.json',dict(numeric_scratch=str(scratch),temporary=True,baseline=str(basis),only_three_held=True))
  script=ROOT/('fit_three_balance42.py' if kind=='balance42' else 'fit_three_power69.py')
  with (run/'fit.log').open('w') as log:
   proc=subprocess.Popen([PY,'-B',str(script)],env=runenv,stdin=subprocess.DEVNULL,stdout=log,stderr=log,close_fds=True)
   state('three_'+kind+'_fit',fit_PID=proc.pid,fit_log=str(run/'fit.log'),best_validation=str(path),tone_score=tone,score=report['score']);code=proc.wait()
  assert code==0,('fit failed',code)
  fit=scratch/('complete-balance42-basis' if kind=='balance42' else 'complete-power69-basis');choice=json.loads((fit/'best.json').read_text());initial=json.loads((fit/'history.json').read_text())[0]['weighted_score']
  if choice['weighted_score']<initial-1e-6:
   target=ROOT/('post74joint-verified-live-balance-'+format(index,'04d')+'-'+kind)
   state('fresh_Diva_Windows_own_NEW_12_cases_proof',fit=str(fit),numeric_tone_score=choice['weighted_score'])
   try:
    with (run/'validation.log').open('w') as log:subprocess.run([PY,'-B',str(ROOT/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log,check=True,timeout=900)
   except subprocess.CalledProcessError:
    from three_candidate_decision import quality_rejection
    rejected=quality_rejection(run/'validation.log',target)
    if rejected is None:raise
    write(run/'decision.json',rejected);seen.append(digest+':'+kind);write(seenpath,seen)
    state('candidate_rejected_by_fresh_actual_metrics',fit=str(fit),best_validation=str(path),continued=True);continue
   result=checked(target/'validation.json');write(run/'decision.json',dict(validation=str(target/'validation.json'),accepted=result['tone_score']<tone-1e-6,tone_score=result['tone_score'],score=result['score'],match_reached=False))
  seen.append(digest+':'+kind);write(seenpath,seen)
except Exception:
 state('failed',error=traceback.format_exc());raise
