"""Try the verified phase-lobe family after each new checked main basis.

Every proposed shape uses the same source and arrays. Main receives only a fresh
Diva/Windows/NEW-independent/12-arbitrary proof, with original limits unchanged.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.sched_setaffinity(0,{4})
from pathlib import Path
import sys,json,copy,hashlib,datetime,time,subprocess,traceback,fcntl,shutil
import numpy as np,soundfile as sf
P=Path(__file__).resolve().parent;W=Path(os.environ.get('DIVALEAD_VALIDATION_WORK','/workspace/divalead-work/all-repository-selection'));ROOT=Path('/workspace/divalead-work/phase-shape-continuation');ROOT.mkdir(exist_ok=True);STATE=W/'phase-shape-continuation-state.json';PY='/workspace/.venvs/divalead/bin/python'
def atomic(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2)+'\n');t.replace(p)
def state(phase,**kw):atomic(STATE,dict(time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_PID=os.getpid(),phase=phase,match_reached=False,automatic_publication=False,**kw))
try:
 lock=(ROOT/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);state('waiting_for_all_verified_plateau_carries')
 while True:
  ready=W/'phase-plateau-ready-state.json'
  if ready.exists():
   d=json.loads(ready.read_text());assert d['phase']=='ready_for_continuation' and d['all9_carry_checks_passed'] and d['global_guards_passed'];break
  if (W/'plateau-all-fitters-state.json').exists():assert json.loads((W/'plateau-all-fitters-state.json').read_text())['phase']!='failed'
  time.sleep(5)
 sys.path.insert(0,str(P));import independent_spectral_plateau as impl
 from replay_spectral_model import kwargs
 import compare_all as a
 hashes={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['independent_spectral_plateau.py','fine_phase_model.py']};source=sf.read(P/'after-core-source/Diva_source.wav')[0];before=sf.read(P/'after-core-source/Diva_before_spectral.wav')[0];settings=json.loads((P.parents[1]/'v53-wip/analysis/selected_candidate.json').read_text())['settings'];rank=json.loads((P/'ranking.json').read_text());original=rank['results'][0]['metrics'];scales=rank['normalizing_errors'];limits=dict(H24=1.,upper_harm=1.01,upper_off=1.01,low_harm=1.01,ERB=1.01,relative_phase=1.005,whole=1.01,envelope=1.01,body=1.03,stereo_phase=1.03,stereo_balance=1.03);index=max([0]+[int(x.name.split('-')[1]) for x in ROOT.glob('round-*')])
 processed=set(json.loads((ROOT/'processed.json').read_text()) if (ROOT/'processed.json').exists() else [])
 while True:
  assert all(hashlib.sha256((P/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items()),'Implementation changed; inspect before resuming shape proposals'
  record=json.loads(Path('/workspace/divalead-work/continuous-refinement/BEST_ACTUAL.json').read_text());path=Path(record['validation']);r=json.loads(path.read_text());assert r['source_updates']=={'OSC:Tune2':24.02} and r['all281_source_verified'] and r['old247_NOT_used_for_changed_source'];assert r['Windows_native_max_error']<2e-7 and r['full_NEW_SOURCE_independent_max_error']<3e-7 and r['spectral_fixture_max_error']<2e-7;assert all(r['metrics'][k]<=original[k]*v for k,v in limits.items());cfg=json.loads(Path(r['core_model']).read_text());digest=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
  if digest in processed:
   state('waiting_for_new_checked_main_basis',last_main_validation=str(path),last_main_score=r['score'],last_round=index);time.sleep(15);continue
  if shutil.disk_usage(ROOT).free<1024**3:state('paused_low_workspace_space',last_main_validation=str(path));break
  index+=1;run=ROOT/('round-'+format(index,'04d'));run.mkdir();atomic(run/'basis-validation.json',r);atomic(run/'basis-model.json',cfg);actual=sf.read(path.parent/'REFERENCE_EDIT_WIP.wav')[0];crest_cap=float(np.sqrt(np.mean((a.wave.features(actual)[2]-a.TC)**2)))*1.001;fine=cfg['fine_phase_harmonic_parameters'];base_pair=(float(fine.get('order_plateau_width',.23)),float(fine.get('order_plateau_strength',0.)));pairs=[]
  for pair in [base_pair,(.23,0.)]+[(width,strength) for width in [.15,.23,.30] for strength in [.25,.5,1.]]:
   if pair not in pairs:pairs.append(pair)
  a.WORK=run;(run/'scores').mkdir();rows=[];best_score=r['score'];best_model=None;best_edit=None;state('numeric_verified_shape_family',round=index,basis_validation=str(path),basis_score=r['score'],profiles=len(pairs))
  for i,(width,strength) in enumerate(pairs):
   model=copy.deepcopy(cfg);model['fine_phase_harmonic_parameters'].update(order_plateau_width=width,order_plateau_strength=strength);model['fine_phase_harmonic_parameters']['law']='Chebyshev degrees0..4 on clamped normalized log2 live carrier; optional harmonic-lobe Hermite warp followed by log-order interpolation; common M/S rotation';full,_=impl.spectral_ms(before,source,48000,8320,model['parameters'],**kwargs(model));edit=a.h.edit_aligned(a.h.align_with_pdc(full,settings,latency=8320))
   if i==0:np.testing.assert_allclose(edit,actual,rtol=0,atol=2e-7)
   scratch=run/'numeric-scratch.wav';sf.write(scratch,edit,48000,subtype='FLOAT');result=a.score(dict(id='shape'+str(i),canonical_path=str(scratch),aliases=[]));m=result['metrics'];value=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS);cr=result['diagnostics']['crest_RMS_db'];feasible=bool(all(m[k]<=original[k]*v for k,v in limits.items()) and cr<=crest_cap and np.max(abs(full))<.99);row=dict(width=width,strength=strength,metrics=m,score=value,crest_RMS_dB=cr,crest_cap_dB=crest_cap,feasible=feasible,numeric_not_actual=True,match_reached=False);rows.append(row);atomic(run/'numeric-history.json',rows)
   if i and feasible and value<best_score-1e-7:best_score=value;best_model=model;best_edit=edit.copy();atomic(run/'selected-numeric-model.json',model)
  (run/'numeric-scratch.wav').unlink(missing_ok=True)
  if best_model is not None:
   fit=run/'actual/frozen-choice';fit.mkdir(parents=True);atomic(fit/'best.json',best_model);sf.write(run/'selected-NUMERIC-NOT-ACTUAL.wav',best_edit,48000,subtype='FLOAT');state('actual_shape_Diva_Windows_NEW_source_and12_arbitrary',round=index,basis_validation=str(path),numeric_score=best_score);name='shape-aux-'+format(index,'04d')+'-53-control';state_name='shape-aux-'+format(index,'04d')
   with (run/'actual-validation.log').open('w') as log:subprocess.run([PY,'-B',str(W/'validate_incoming_snapshot.py'),name,str(fit),state_name,'--no-submit'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True,timeout=1200)
   checked=json.loads((W/(state_name+'-state.json')).read_text());assert checked['phase']=='completed_actual_matched_source_validation';rp=Path(checked['validation']);out=sf.read(rp.parent/'REFERENCE_EDIT_WIP.wav')[0];np.testing.assert_allclose(out,best_edit,rtol=0,atol=2e-7);cr=float(np.sqrt(np.mean((a.wave.features(out)[2]-a.TC)**2)));current=json.loads(Path('/workspace/divalead-work/continuous-refinement/BEST_ACTUAL.json').read_text());accepted=bool(checked['global_guards_passed'] and cr<=crest_cap and checked['score']<current['score']-1e-7);decision=dict(validation=checked['validation'],score=checked['score'],global_guards_passed=checked['global_guards_passed'],actual_crest_RMS_dB=cr,crest_cap_dB=crest_cap,main_actual_score_at_check=current['score'],accepted=accepted,arbitrary_input_verification=checked['arbitrary_input_verification'],match_reached=False);atomic(run/'decision.json',decision)
   if accepted:
    atomic(ROOT/'BEST_ACTUAL.json',dict(validation=checked['validation'],score=checked['score'],match_reached=False));atomic(Path('/workspace/divalead-work/continuous-refinement/INCOMING')/('shape-aux-'+format(index,'04d')+'.json'),dict(validation=checked['validation'],arbitrary_input_verification=checked['arbitrary_input_verification'],match_reached=False))
  else:atomic(run/'decision.json',dict(no_guarded_numeric_shape_improvement=True,match_reached=False))
  processed.add(digest);atomic(ROOT/'processed.json',sorted(processed));state('round_completed',round=index,basis_validation=str(path),basis_score=r['score'],profiles=len(pairs),numeric_improvement=best_model is not None);time.sleep(5)
except BlockingIOError:
 print('Shape controller already running; no duplicate started.')
except Exception:
 state('failed',error=traceback.format_exc());raise
