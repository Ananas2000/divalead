"""Repair completed core-search directions strictly inside all original guards."""
from pathlib import Path
import datetime,importlib.util,json,os,shutil,subprocess,sys,time
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np
R=Path(__file__).resolve().parent;RUN=R/'post81-core147-projection-research';RUN.mkdir(exist_ok=False)
prior=R/'post81-core147-research';basis=RUN/'basis';shutil.copytree(prior/'basis',basis)
scratch=Path('/tmp/divalead-post81-core147-projection');scratch.mkdir(exist_ok=False)
source=R/'source-post80plate68-basis';report=json.loads((basis/'validation.json').read_text())
assert report['source_family']=='Post80 Plate2 damping68'
os.environ.update(DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(scratch))
(RUN/'numeric-location.json').write_text(json.dumps(dict(numeric_scratch=str(scratch),baseline=str(basis),source_family=report['source_family'],numeric_workers=1,only_three_held=True),indent=2)+'\n')
spec=importlib.util.spec_from_file_location('post81_projection_frozen_core',R/'fit_three_core147_fixed_anchor.py')
fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(fit)
fit.probe(np.zeros(147));baseline=fit.best
old_scratch=Path(json.loads((prior/'numeric-location.json').read_text())['numeric_scratch'])
history=json.loads((old_scratch/'complete-core-basis/history.json').read_text())
seeds=sorted([row for row in history if row['weighted_score']<baseline-1e-6 and row['minimum_constraint']>=-.05],key=lambda row:row['weighted_score'])[:3]
from project_three_existing_vector import project
attempts=[];started=time.monotonic()
for row in seeds:
    point,diagnostic=project(row['core_offsets'],fit.compute,fit.lower,fit.upper,[list(fit.guards).index('whole'),len(fit.guards)+2],max_turns=5)
    attempts.append(dict(seed_center=row['center'],seed_numeric_tone=row['weighted_score'],projection=diagnostic))
    if point is not None:
        value=fit.compute(point)
        if value[1]['weighted_score']<fit.best:fit.probe(point)
    (RUN/'projection-attempts.json').write_text(json.dumps(attempts,indent=2)+'\n')
(fit.V/'history.json').write_text(json.dumps(fit.rows,indent=2)+'\n')
(fit.V/'optimizer.json').write_text(json.dumps(dict(elapsed_seconds=time.monotonic()-started,source_completed_history=str(old_scratch/'complete-core-basis/history.json'),projection_attempts=attempts,original_guards_not_loosened=True,original_three_held=True,requires_fresh_actual_proof=True,match_reached=False),indent=2)+'\n')
decision=dict(numeric_baseline_tone=baseline,numeric_best_tone=fit.best,projection_attempts=len(attempts),full_proof_completed=False,match_reached=False)
if fit.best<report['tone_score']-1e-6:
    env=dict(os.environ,DIVALEAD_THREE_SOURCE_BASIS=str(source),DIVALEAD_THREE_SOURCE_REPORT=str(basis/'validation.json'))
    target=R/'post80plate68-verified-core147-projection-0001'
    with (RUN/'validation.log').open('w') as log:
        result=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit.V),target.name],env=env,stdout=log,stderr=log,timeout=900)
    if result.returncode:
        from three_candidate_decision import quality_rejection
        rejection=quality_rejection(RUN/'validation.log',target);assert rejection is not None,'Infrastructure failure in core projection proof'
        decision.update(rejection)
    else:
        actual=json.loads((target/'validation.json').read_text());decision.update(full_proof_completed=True,validation=str(target/'validation.json'),tone_score=actual['tone_score'],score=actual['score'])
else:decision.update(accepted=False,reason='No projected improvement inside all original guards')
(RUN/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')
out=Path('/tmp/divalead-source-post81coreprojection');out.mkdir(exist_ok=False)
(out/'completed.json').write_text(json.dumps(dict(trials=len(attempts),best=decision,match_reached=False),indent=2)+'\n')
print('COMPLETED_CORE_DIRECTIONS_REPROJECTED_WITHOUT_LOOSENING_GUARDS',json.dumps(decision),flush=True)
