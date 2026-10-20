"""Bounded one-worker HF refinement of a separately fully proved physical source."""
from pathlib import Path
import datetime,json,os,shutil,subprocess,sys
R=Path(__file__).resolve().parent;S=R/'source-post74joint-basis';run=R/'source-post74joint-HF100';run.mkdir(exist_ok=False)
report=json.loads((S/'validation.json').read_text());assert report['all_chosen_three_guards_passed'] and report['all12_implementation_cases_passed']
assert report['source_family']=='Post74 joint oscillator-filter'
basis=run/'basis';(basis/'analysis').mkdir(parents=True)
for a,b in [(report['core_model'],basis/'analysis/spectral_model.json'),(S/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav'),(S/'source_manifest.json',basis/'source_manifest.json')]:shutil.copyfile(a,b)
report['acceptance_tone_cap']=report['tone_score'];(basis/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
scratch=Path('/tmp/divalead-post74joint-HF100');scratch.mkdir(exist_ok=False)
(run/'numeric-location.json').write_text(json.dumps(dict(numeric_scratch=str(scratch),baseline=str(basis),source_family=report['source_family'],numeric_workers=1,only_three_held=True),indent=2)+'\n')
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(S),DIVALEAD_THREE_SOURCE_REPORT=str(basis/'validation.json'),DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(scratch),DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='18')
subprocess.run([sys.executable,'-B',str(R/'fit_three_hf_fixed_anchor.py'),'--check-only'],env=env,check=True)
subprocess.run([sys.executable,'-B',str(R/'fit_three_hf_fixed_anchor.py')],env=env,check=True)
fit=scratch/'complete-hf-basis';choice=json.loads((fit/'best.json').read_text());initial=json.loads((fit/'history.json').read_text())[0]['weighted_score'];decision=dict(numeric_seed_tone=initial,numeric_best_tone=choice['weighted_score'],match_reached=False,source_family=report['source_family'])
if choice['weighted_score']<initial-1e-6:
 target=R/'post74joint-verified-HF100-0001'
 with (run/'validation.log').open('w') as log:result=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log)
 if result.returncode:
  from three_candidate_decision import quality_rejection
  rejected=quality_rejection(run/'validation.log',target);assert rejected is not None;decision.update(rejected)
 else:
  report=json.loads((target/'validation.json').read_text());decision.update(fully_proved=True,validation=str(target/'validation.json'),tone_score=report['tone_score'],score=report['score'])
else:decision.update(accepted=False,reason='No strict numerical improvement on this source')
(run/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')
out=Path('/tmp/divalead-source-post74fit');out.mkdir(exist_ok=False);(out/'completed.json').write_text(json.dumps(dict(trials=1,best=report,decision=decision,match_reached=False),indent=2)+'\n')
print('FINITE_POST74_SOURCE_FINISH_REFINEMENT_COMPLETE',decision,flush=True)
