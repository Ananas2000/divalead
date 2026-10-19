"""Combine two fully proved three-held changes, then re-prove the actual result."""
from pathlib import Path
import os,sys,json,shutil,time,subprocess,datetime
R=Path(__file__).resolve().parent;T=R/'coupled-hf15-fine55';T.mkdir(exist_ok=False)
G=R/'verified-cont-0015-hf';P=R/'verified-fine55-preview-0001'
def state(phase,**kw):
 p=T/'state.json';q=p.with_suffix('.tmp');q.write_text(json.dumps(dict(phase=phase,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),match_reached=False,**kw),indent=2)+'\n');q.replace(p)
while not (G/'validation.json').exists():
 current=json.loads((R/'continuation-state.json').read_text());assert current['phase']!='failed',current
 if current['phase']=='waiting_for_changed_proved_three_basis' or ('fit_log' in current and 'round-0015-' not in current['fit_log']):
  state('HF15_did_not_produce_completed_proof_combination_not_attempted');raise SystemExit(0)
 state('waiting_for_full_HF15_proof');time.sleep(10)
assert (P/'validation.json').exists();basis=T/'basis';(basis/'analysis').mkdir(parents=True)
for a,b in [(P/'analysis/spectral_model.json',basis/'analysis/spectral_model.json'),(P/'validation.json',basis/'validation.json'),(P/'REFERENCE_EDIT_WIP.wav',basis/'REFERENCE_EDIT_WIP.wav'),(R/'baseline/source_manifest.json',basis/'source_manifest.json')]:shutil.copyfile(a,b)
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(basis),DIVALEAD_SELECTION_WORK=str(T/'numeric'))
sys.path.insert(0,str(R));state('recompute_fine55_basis_and_HF15_combination')
import fit_three_hf_fixed_anchor as f
from three_hf_interior_projection import project_hf
import numpy as np
cfgG=json.loads((G/'analysis/spectral_model.json').read_text());cfgP=json.loads((P/'analysis/spectral_model.json').read_text())
for field in cfgG:
 if field not in ['hf_matrix_parameters','fine_phase_harmonic_parameters']:assert cfgG[field]==cfgP[field],field
point=np.asarray(cfgG['hf_matrix_parameters'])-np.asarray(cfgP['hf_matrix_parameters']);assert np.max(abs(point))<=.10000000001
f.probe(np.zeros(100));_,seed,con=f.compute(point);seed['HF_offsets']=point.tolist()
(T/'unrepaired-combination.json').write_text(json.dumps(seed,indent=2)+'\n')
point,projection=project_hf(seed,f.compute,f.lower,f.upper,f.guards);(T/'projection.json').write_text(json.dumps(projection,indent=2)+'\n')
if point is None:state('no_feasible_combination_original_guards_unchanged');raise SystemExit(0)
_,row,con=f.compute(point)
if row['weighted_score']>=f.rows[0]['weighted_score']-1e-6:state('no_numeric_improvement_over_fine55',tone=row['weighted_score']);raise SystemExit(0)
f.probe(point);(f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(dict(method='two fully proved changes coupled through existing HF coefficients, with unchanged fixed quality limits',projection=projection,requires_fresh_actual_proof=True,match_reached=False),indent=2)+'\n')
state('fresh_Diva_Windows_matching_NEW_all12_cases',numeric_tone=row['weighted_score'])
with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(f.V),'verified-coupled-hf15-fine55'],env=os.environ.copy(),stdout=log,stderr=log,check=True,timeout=900)
report=json.loads((R/'verified-coupled-hf15-fine55/validation.json').read_text());old=json.loads((P/'validation.json').read_text());state('full_actual_proof_passed',tone=report['tone_score'],score=report['score'],improved_over_fine55_actual=report['tone_score']<old['tone_score']-1e-6)
print('COUPLED_HF15_FINE55_FULL_ACTUAL_PROOF_PASS',report['tone_score'],report['score'],flush=True)
