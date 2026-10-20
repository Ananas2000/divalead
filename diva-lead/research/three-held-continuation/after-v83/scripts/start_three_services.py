"""Idempotent startup for the existing prepared three-held environment."""
from pathlib import Path
import os,sys,json,subprocess,datetime,fcntl
R=Path(__file__).resolve().parent;PY='/workspace/.venvs/divalead/bin/python'
assert str(Path(sys.executable).resolve())==str(Path(PY).resolve())
lock=(R/'service-start.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
def live(name):
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            cmd=(p/'cmdline').read_bytes().split(b'\0');st=(p/'stat').read_text().rsplit(')',1)[1].split()
            same_script=str(R/name).encode() in cmd or (name.encode() in cmd and (p/'cwd').resolve()==R)
            if st[0]!='Z' and cmd[0]==PY.encode() and same_script and not any(v in cmd for v in [b'--check-only',b'--once']):found.append(int(p.name))
        except (FileNotFoundError,ProcessLookupError):pass
    return found
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MIN_FREE_MIB='512')
preference=R/'active-three-source-family.json'
family=json.loads(preference.read_text())['source_family'] if preference.exists() else 'original-user-selected-three'
families={'original-user-selected-three':['continue_three.py','continue_three_joint_phase.py','continue_three_balance_power.py'],'PulseWidth51.90':['continue_pw5190_main.py','continue_pw5190_phase.py','continue_pw5190_balance.py'],'Post74 joint oscillator-filter':['continue_post74joint_main.py','continue_post74joint_phase.py','continue_post74joint_balance.py'],'Post80 Plate2 damping68':['continue_post80plate68_main.py','continue_post80plate68_phase.py','continue_post80plate68_balance.py']}
assert family in families
fit_reserve=512 if family=='original-user-selected-three' else 256
env['DIVALEAD_MIN_FREE_MIB']=str(fit_reserve)
cohort=families[family]
opposite=[script for k,v in families.items() if k!=family for script in v]
assert not any(live(name) for name in opposite),'Another source cohort remains live; use the idle handoff before starting replacements'
subprocess.run([PY,'-B',str(R/cohort[0]),'--check-only'],env=env,check=True)
subprocess.run([PY,'-B',str(R/'auto_backup_three.py'),'--check-only'],env=env,check=True)
assert not live('continue_phase18.py'),'Retired phase18 controller is live; diagnose before starting a duplicate phase worker'
assert not live('continue_drift24.py'),'Retired Drift controller is live; diagnose CPU slots before starting a replacement'
temporarily_owned=any(live(n) for n in ['run_tslop0_research.py','run_source_pan64.py','run_source_current65.py','run_pw5190_source_preparation.py','run_pw5190_balance_repair.py','run_pw5190_gain_research.py','run_pw5190_accuracy_probe.py','run_pw5190_coupled135.py','combine_fine55_power69.py','prove_joint30_fine55_projection.py','run_source_post74_probe.py','run_source_post74joint_probe.py','run_source_post74proof.py','run_source_post74fit.py','run_source_post74blend.py','run_source_post77_probe.py','run_post77_coupled135.py','run_source_post78_shapes.py','run_source_post78_dual.py','run_source_post80_plate.py','run_source_post80_plate2.py','run_source_post80plateproof.py','run_source_post80platefit.py','run_post81_core147.py'])
projection_state=R/'source-post81coreprojection-state.json'
projection_data=json.loads(projection_state.read_text()) if projection_state.exists() else {}
projection_live=bool(live('run_post81_core_projection.py'))
projection_owned=bool(projection_live and projection_data.get('CPU_slot','balance')=='balance' and not projection_data.get('slot_released',True))
temporarily_owned=temporarily_owned or projection_owned
phase_slot_owned=bool(live('run_cleaner_hf100.py') or live('run_post77_cleaner_hf100.py'))
main_slot_owned=False
if projection_live and projection_data.get('CPU_slot')=='main' and not projection_data.get('slot_released',True):main_slot_owned=True
idle_owner=R/'post81-core147-idle-main-state.json'
if live('run_post81_core147_idle_main.py') and idle_owner.exists():
    held=json.loads(idle_owner.read_text()).get('stopped_handoff')
    if held:
        try:
            fields=Path('/proc',str(held['PID']),'stat').read_text().rsplit(')',1)[1].split()
            main_slot_owned=main_slot_owned or (fields[0]=='T' and fields[19]==held['starttime_ticks'])
        except FileNotFoundError:pass
rows=[]
for script,logname in list(zip(cohort,['main-service.log','joint-phase-service.log','balance-power-service.log']))+[('auto_backup_three.py','auto-backup-controller.log')]:
    found=live(script)
    assert len(found)<=1,(script,found)
    if found:rows.append(dict(script=script,existing_PIDs=found,newly_started=False));continue
    if (script==cohort[0] and main_slot_owned) or (script==cohort[2] and temporarily_owned) or (script==cohort[1] and phase_slot_owned):
        rows.append(dict(script=script,temporarily_owned_CPU_slot=True,newly_started=False));continue
    with (R/logname).open('a') as log:
        p=subprocess.Popen([PY,'-B',str(R/script)],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    rows.append(dict(script=script,PID=p.pid,newly_started=True))
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_family=family,services=rows,numeric_budget='2+1+1',fit_operational_reserve_MiB=fit_reserve,only_three_held=True,match_reached=False)
(R/'service-start-last.json').write_text(json.dumps(report,indent=2)+'\n');print('THREE_HELD_SERVICES_CHECKED_AND_STARTED_WHERE_ABSENT',json.dumps(report),flush=True)
