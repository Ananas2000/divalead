"""Freshly prove a frozen feasible checkpoint while the longer numeric search continues."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,sys,time,traceback
R=Path(__file__).resolve().parent;lock=(R/'post81-live-core-checkpoint.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
statepath=R/'post81-live-core-checkpoint-state.json';attempt=0;seen=set()
def state(phase,**kw):
    q=statepath.with_suffix('.tmp');q.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,original_numeric_search_not_stopped=True,match_reached=False,**kw),indent=2)+'\n');q.replace(statepath)
threshold=json.loads(Path('/workspace/divalead/diva-lead/v81-wip/verification/selected_validation.json').read_text())['tone_score']-1e-4
try:
    while True:
        owner=json.loads((R/'source-post81coreprojection-state.json').read_text())
        assert not owner['phase'].startswith('failed'),owner
        path=Path('/tmp/divalead-post81-core147-projection/complete-core-basis/best.json')
        raw=path.read_bytes() if path.exists() else b''
        try:choice=json.loads(raw) if raw else {}
        except json.JSONDecodeError:choice={}
        digest=hashlib.sha256(raw).hexdigest()
        if choice.get('feasible_search_guards') and choice.get('weighted_score',1e9)<threshold and digest not in seen:
            attempt+=1;seen.add(digest);fit=R/('post81-live-core-checkpoint-fit-'+format(attempt,'04d'));fit.mkdir(exist_ok=False)
            (fit/'best.json').write_bytes(raw)
            basis=R/'post81-core147-projection-research/basis/validation.json';report=json.loads(basis.read_text())
            (fit/'history.json').write_text(json.dumps([dict(weighted_score=report['tone_score'])],indent=2)+'\n')
            (fit/'checkpoint-origin.json').write_text(json.dumps(dict(original_best_SHA256=digest,original_numeric_run_still_running=not owner.get('slot_released',True),checkpoint_capture_is_not_optimizer_completion=True),indent=2)+'\n')
            target=R/('post80plate68-verified-core147-live-checkpoint-'+format(attempt,'04d'))
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_THREE_SOURCE_BASIS=str(R/'source-post80plate68-basis'),DIVALEAD_THREE_SOURCE_REPORT=str(basis))
            state('fresh_actual_validation_of_frozen_numeric_checkpoint',target=str(target),numeric_tone=choice['weighted_score'])
            with (fit/'validation.log').open('w') as log:
                result=subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log,timeout=900)
            if result.returncode:
                from three_candidate_decision import quality_rejection
                rejection=quality_rejection(fit/'validation.log',target);assert rejection is not None,'Infrastructure failure in live checkpoint proof'
                (fit/'decision.json').write_text(json.dumps(rejection,indent=2)+'\n');state('checkpoint_rejected_keep_searching',rejection=rejection)
            else:
                actual=json.loads((target/'validation.json').read_text())
                state('frozen_checkpoint_fully_proved_original_search_continues',validation=str(target/'validation.json'),tone_score=actual['tone_score'],score=actual['score']);break
        elif owner.get('slot_released',False):
            state('numeric_search_closed_without_an_additional_eligible_checkpoint');break
        else:state('waiting_for_feasible_improving_core_checkpoint',required_tone_below=threshold)
        time.sleep(3)
except Exception:
    state('failed_preserve_checkpoint_and_diagnose',error=traceback.format_exc());raise
