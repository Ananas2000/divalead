"""Fully prove a distinct quieter tradeoff; never call it the primary tone winner."""
from pathlib import Path
import datetime,json,os,subprocess,sys,time,traceback
R=Path(__file__).resolve().parent;B=R/'source-post74joint-basis';run=R/'post77-cleaner-hf100-research'
def state(phase,**extra):
 p=R/'post77-cleaner-alternative-state.tmp';p.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,match_reached=False,**extra),indent=2)+'\n');p.replace(R/'post77-cleaner-alternative-state.json')
try:
 while True:
  owner=json.loads((R/'post77-cleaner-hf100-state.json').read_text())
  if owner.get('phase_slot_released'):break
  state('waiting_for_cleaner_search_and_phase_slot_release');time.sleep(5)
 assert owner['phase']=='cleaner_search_finished_releasing_phase_slot',owner
 choicefile=Path('/tmp/divalead-post77-cleaner-hf100/complete-hf-basis/quieter-alternative.json')
 if not choicefile.exists():state('no_separate_quieter_alternative_found');sys.exit(0)
 choice=json.loads(choicefile.read_text());F=R/'post77-cleaner-hf100-alternative-numeric';F.mkdir(exist_ok=False)
 (F/'best.json').write_text(json.dumps(choice,indent=2)+'\n');(F/'history.json').write_text(json.dumps([dict(weighted_score=choice['alternative_baseline_tone_score']),choice],indent=2)+'\n')
 source_report=json.loads((run/'basis/validation.json').read_text());source_report['acceptance_tone_cap']=choice['alternative_tone_cap'];source_report['quieter_alternative_not_a_primary_tone_improvement']=True
 cap=F/'alternative-purpose-source-report.json';cap.write_text(json.dumps(source_report,indent=2)+'\n')
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(B),DIVALEAD_THREE_SOURCE_REPORT=str(cap))
 staging=R/'post77-cleaner-hf100-alternative-proof-staging';final=R/'post74joint-verified-post77-cleaner-hf100-alternative-0001';assert not staging.exists() and not final.exists()
 state('fresh_Diva_Windows_own_NEW_all12cases_proof_of_quieter_tradeoff')
 log=F/'validation.log'
 with log.open('w') as out:completed=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(F),staging.name],env=env,stdout=out,stderr=out)
 if completed.returncode:
  from three_candidate_decision import quality_rejection
  rejected=quality_rejection(log,staging);assert rejected is not None;state('quieter_alternative_rejected_by_actual_quality',decision=rejected);sys.exit(0)
 d=json.loads((staging/'validation.json').read_text())
 # Additional tradeoff bound never changes any original absolute audio guard.
 assert d['tone_score']<choice['alternative_tone_cap'] and d['metrics']['upper_off']<source_report['metrics']['upper_off']-1e-3
 d.update(quieter_alternative_not_claimed_primary_tone_improvement=True,alternative_tone_cap=choice['alternative_tone_cap'],alternative_baseline_tone_score=source_report['tone_score'],all_original_absolute_audio_limits_unchanged=True)
 for k in ['new_source_raw','core_model']:
  assert d[k].startswith(str(staging)+'/');d[k]=str(final)+d[k][len(str(staging)):]
 (staging/'validation.json').write_text(json.dumps(d,indent=2)+'\n')
 (staging/'README_RU.md').write_text('Дополнительный WIP с меньшей энергией между верхними гармониками. Он не объявляется более точным по основной оценке тембра: допускается ограниченный обмен этой оценки на меньший шумовой остаток, в пределах всех исходных абсолютных ограничений и более строгого предела upper-off. Все свежие Diva/Windows/ownNEW/fixture/12 причинных случаев пройдены. Основная точка выбирается отдельно по CURRENT JSON. Совпадение не достигнуто; GUI FL Studio и прослушивание ассистентом не выполнялись.\n')
 staging.rename(final);state('quieter_alternative_fully_proved_not_claimed_primary_winner',validation=str(final/'validation.json'),tone_score=d['tone_score'],upper_off=d['metrics']['upper_off'])
except Exception:state('failed_preserve_results_and_diagnose',error=traceback.format_exc());raise
