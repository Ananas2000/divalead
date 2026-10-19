"""Constrained physical-source hypothesis; never mix it into the original family."""
from pathlib import Path
import os,sys,json,signal,subprocess,datetime,traceback
R=Path(__file__).resolve().parent;T=R/'tslop0-research';T.mkdir(exist_ok=False)
state=json.loads((R/'balance-power-continuation-state.json').read_text());pid=state['controller_PID'];assert b'continue_three_balance_power.py' in Path('/proc',str(pid),'cmdline').read_bytes();os.kill(pid,signal.SIGSTOP);table={}
for q in Path('/proc').iterdir():
    if not q.name.isdigit():continue
    try:
        st=(q/'stat').read_text().rsplit(')',1)[1].split();table[int(q.name)]=(int(st[1]),st[19])
    except (FileNotFoundError,ProcessLookupError):pass
ids=[pid]
for parent in ids:
    for child,(ppid,_) in table.items():
        if ppid==parent and child not in ids:ids.append(child)
rows=[]
for p in ids:
    try:os.kill(p,signal.SIGSTOP);rows.append(dict(PID=p,starttime_ticks=table[p][1]))
    except ProcessLookupError:pass
record=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),temporarily_paused_for_three_held_TuneSlop0_research=True,processes=rows)
(T/'paused-balance-power.json').write_text(json.dumps(record,indent=2)+'\n')
def save(phase,**kwargs):
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),coordinator_PID=os.getpid(),phase=phase,source_family='TuneSlop0',only_three_held=True,not_adopted_into_original_source=True,match_reached=False,**kwargs);q=T/'state.tmp';q.write_text(json.dumps(d,indent=2)+'\n');q.replace(T/'state.json')
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
try:
    save('rebuild_matching_own_NEW_and_check_source_all281_12events_and_12_arbitrary_cases')
    with (T/'source-preparation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'prepare_tslop0_source.py')],env=env,stdout=log,stderr=log,check=True,timeout=900)
    B=R/'source-tslop0-basis';assert not (B/'validation.json').exists()
    env.update(DIVALEAD_MODEL_BASE=str(B),DIVALEAD_BASELINE_REPORT=str(B/'preliminary-metrics.json'),DIVALEAD_SELECTION_WORK='/tmp/divalead-tslop0-gains',DIVALEAD_NUMERIC_WORKERS='1',DIVALEAD_MAXITER='36')
    save('fit_existing93_gains_inside_UNCHANGED_original_three_caps',acceptance_tone_cap=json.loads((B/'preliminary-metrics.json').read_text())['acceptance_tone_cap'])
    with (T/'gain-fit.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'fit_three_gains.py')],env=env,stdout=log,stderr=log,check=True,timeout=2400)
    fit=Path(env['DIVALEAD_SELECTION_WORK'])/'complete-joint-source-tslop0-basis'
    if not (fit/'best.json').exists():save('no_feasible_model_found_no_acceptance');raise SystemExit(0)
    choice=json.loads((fit/'best.json').read_text());cap=json.loads((B/'preliminary-metrics.json').read_text())['acceptance_tone_cap']
    if choice['weighted_score']>=cap-1e-6:save('no_feasible_tone_improvement_over_proved_v64',numeric_tone=choice['weighted_score']);raise SystemExit(0)
    env.update(DIVALEAD_THREE_SOURCE_BASIS=str(B),DIVALEAD_THREE_SOURCE_REPORT=str(B/'preliminary-metrics.json'))
    save('fresh_actual_full_source_specific_proof',numeric_tone=choice['weighted_score']);target=R/'tslop0-verified-gain-0001'
    try:
        with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_source_model.py'),str(fit),target.name],env=env,stdout=log,stderr=log,check=True,timeout=900)
    except subprocess.CalledProcessError:
        from three_candidate_decision import quality_rejection
        rejected=quality_rejection(T/'validation.log',target)
        if rejected is None:raise
        (T/'decision.json').write_text(json.dumps(rejected,indent=2)+'\n');save('fresh_quality_rejected',decision=rejected)
    else:
        actual=json.loads((target/'validation.json').read_text());save('source_specific_full_proof_passed',tone_score=actual['tone_score'],score=actual['score'])
except Exception:save('failed',error=traceback.format_exc());raise
finally:
    resumed=[]
    for row in reversed(rows):
        try:
            st=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
            if st[19]!=row['starttime_ticks']:continue
            os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
        except (FileNotFoundError,ProcessLookupError):pass
    record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(T/'paused-balance-power.json').write_text(json.dumps(record,indent=2)+'\n');print('ORIGINAL_BALANCE_POWER_RESUMED',resumed,flush=True)
