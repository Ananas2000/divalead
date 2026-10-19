"""Project a completed near-feasible fine-phase point; preserve running fits."""
from pathlib import Path
import os,sys,json,signal,subprocess,datetime
R=Path(__file__).resolve().parent;T=R/'joint30-fine55-projection';T.mkdir(exist_ok=False)
source=R/'joint-phase-continuation/round-0030-fine55'
assert (source/'numeric/complete-fine_phase-basis/optimizer.json').exists()
seed=json.loads((source/'numeric/complete-fine_phase-basis/latest_center.json').read_text())
(T/'seed.json').write_text(json.dumps(seed,indent=2)+'\n')
state=json.loads((R/'balance-power-continuation-state.json').read_text());pid=state['controller_PID']
assert b'continue_three_balance_power.py' in Path('/proc',str(pid),'cmdline').read_bytes()
os.kill(pid,signal.SIGSTOP);table={}
for q in Path('/proc').iterdir():
    if not q.name.isdigit():continue
    try:
        st=(q/'stat').read_text().rsplit(')',1)[1].split();table[int(q.name)]=(int(st[1]),st[19])
    except (FileNotFoundError,ProcessLookupError):pass
ids=[pid]
for parent in ids:
    for child,(ppid,_) in table.items():
        if ppid==parent and child not in ids:ids.append(child)
paused=[]
for p in ids:
    try:os.kill(p,signal.SIGSTOP);paused.append(dict(PID=p,starttime_ticks=table[p][1]))
    except ProcessLookupError:pass
record=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),temporary_numeric_slot_pause=True,processes=paused)
(T/'paused-balance-power.json').write_text(json.dumps(record,indent=2)+'\n')
try:
    os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MODEL_BASE=str(source/'basis'),DIVALEAD_SELECTION_WORK='/tmp/divalead-joint30-fine55-projection');sys.path.insert(0,str(R))
    import fit_three_fine55 as f
    from project_three_existing_vector import project
    import numpy as np
    assert seed['baseline_model_SHA256']==f.baseline_hash
    f.probe(np.zeros(55))
    point,report=project(seed['fine_phase_offsets'],f.compute,f.lower,f.upper,[list(f.guards).index('whole'),len(f.guards)+1])
    (T/'projection.json').write_text(json.dumps(report,indent=2)+'\n')
    if point is None:print('JOINT30_FINE55_NO_FEASIBLE_PROJECTED_POINT',report,flush=True)
    else:
        _,row,con=f.compute(point);assert row['weighted_score']<f.rows[0]['weighted_score']-1e-6;f.probe(point)
        (f.V/'history.json').write_text(json.dumps(f.rows,indent=2)+'\n');(f.V/'optimizer.json').write_text(json.dumps(report,indent=2)+'\n')
        print('JOINT30_FINE55_PROJECTED_NUMERIC_PASS',row['weighted_score'],con.min(),flush=True)
        target=R/'verified-joint30-fine55-projection'
        try:
            with (T/'validation.log').open('w') as log:subprocess.run([sys.executable,'-B',str(R/'validate_three_model.py'),str(f.V),target.name],env=os.environ.copy(),stdout=log,stderr=log,check=True,timeout=900)
        except subprocess.CalledProcessError:
            from three_candidate_decision import quality_rejection
            rejection=quality_rejection(T/'validation.log',target)
            if rejection is None:raise
            (T/'decision.json').write_text(json.dumps(rejection,indent=2)+'\n');print('JOINT30_FINE55_FRESH_QUALITY_REJECTED',flush=True)
        else:
            actual=json.loads((target/'validation.json').read_text());print('JOINT30_FINE55_PROJECTED_FULL_ACTUAL_PASS',actual['tone_score'],actual['score'],flush=True)
finally:
    resumed=[]
    for row in reversed(paused):
        try:
            st=Path('/proc',str(row['PID']),'stat').read_text().rsplit(')',1)[1].split()
            if st[19]!=row['starttime_ticks']:continue
            os.kill(row['PID'],signal.SIGCONT);resumed.append(row['PID'])
        except (FileNotFoundError,ProcessLookupError):pass
    record.update(resumed_PIDs=resumed,resumed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());(T/'paused-balance-power.json').write_text(json.dumps(record,indent=2)+'\n');print('ORIGINAL_BALANCE_POWER_RESUMED',resumed,flush=True)
