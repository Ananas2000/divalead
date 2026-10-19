"""Test existing dynamic targets on the newer fully proved fine-phase model."""
from pathlib import Path
import os,sys,json,signal,subprocess,datetime,shutil
R=Path(__file__).resolve().parent;T=R/'joint32-power69-combination';T.mkdir(exist_ok=False)
source=R/'verified-joint-phase-0032-fine55';assert (source/'validation.json').exists()
basis=T/'basis';(basis/'analysis').mkdir(parents=True)
for a,b in [(source/'analysis/spectral_model.json',basis/'analysis/spectral_model.json'),(source/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav'),(source/'validation.json',basis/'validation.json'),(R/'baseline/source_manifest.json',basis/'source_manifest.json')]:shutil.copyfile(a,b)
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK='/tmp/divalead-joint32-power69-combination');sys.path.insert(0,str(R))
import fit_three_power69 as f
from project_three_existing_vector import project
import numpy as np
power=json.loads((R/'verified-fine55-power69-combined/numeric-choice.json').read_text());p=np.asarray(power['power_offsets'])
assert np.max(np.abs(np.asarray(power['dynamic_harmonic_parameters']['target_logpower_db_polynomial'])-f.base_target-np.pad(p.reshape(3,23),((0,2),(0,0)))))<1e-12
f.probe(np.zeros(69));trials=[];choices=[]
for fraction in [.25,.5,.75,1.0]:
    _,row,con=f.compute(p*fraction);trials.append(dict(fraction=fraction,tone=row['weighted_score'],minimum_constraint=float(con.min()),feasible=bool(con.min()>=-1e-12)))
    if con.min()>=-1e-12:choices.append((row['weighted_score'],p*fraction))
(T/'fraction-trials.json').write_text(json.dumps(trials,indent=2)+'\n')
point,report=project(p,f.compute,f.lower,f.upper,[list(f.guards).index('whole'),len(f.guards)+1])
(T/'projection.json').write_text(json.dumps(report,indent=2)+'\n')
if point is not None:choices.append((f.compute(point)[1]['weighted_score'],point))
if not choices:print('COMBINED_JOINT32_POWER69_NO_FEASIBLE_POINT',flush=True)
else:
    _,point=min(choices,key=lambda x:x[0]);_,row,con=f.compute(point)
    assert row['weighted_score']<f.rows[0]['weighted_score']-1e-6
    f.probe(point);(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n')
    print('COMBINED_JOINT32_POWER69_NUMERIC_PASS',row['weighted_score'],con.min(),flush=True)
    target=R/'verified-joint32-power69-combined'
    try:
        with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(f.V),target.name],env=os.environ.copy(),stdout=log,stderr=log,check=True,timeout=900)
    except subprocess.CalledProcessError:
        from three_candidate_decision import quality_rejection
        rejection=quality_rejection(T/'validation.log',target)
        if rejection is None:raise
        (T/'decision.json').write_text(json.dumps(rejection,indent=2)+'\n');print('COMBINED_JOINT32_POWER69_FRESH_QUALITY_REJECTED',flush=True)
    else:
        actual=json.loads((target/'validation.json').read_text());print('COMBINED_JOINT32_POWER69_FULL_ACTUAL_PASS',actual['tone_score'],actual['score'],flush=True)
