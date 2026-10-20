"""Verify actual retained-source workflow and repeatable startup without duplicates."""
from pathlib import Path
import datetime,json,os,subprocess,time
R=Path(__file__).resolve().parent;PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
reports=[]
while True:
    path=R/'source-post81coreprojection-state.json'
    owner=json.loads(path.read_text()) if path.exists() else {}
    if owner.get('phase','').startswith('failed'):raise RuntimeError(owner)
    if owner.get('slot_released',True):
        process=Path('/proc',str(owner.get('PID',0)))
        try:
            status=(process/'stat').read_text().rsplit(')',1)[1].split()[0]
            command=(process/'cmdline').read_bytes().split(b'\0')
            still_releasing=status!='Z' and str(R/'run_post81_core_projection.py').encode() in command
        except FileNotFoundError:still_releasing=False
        if not still_releasing:break
    time.sleep(5)
for index in range(2):
    with (R/('post81-bootstrap-readiness-'+str(index)+'.log')).open('w') as log:
        subprocess.run([PY,'-B',str(R/'start_three_services.py')],env=env,stdout=log,stderr=log,check=True)
    d=json.loads((R/'service-start-last.json').read_text())
    assert len(d['services'])==4 and all(not row['newly_started'] and len(row.get('existing_PIDs',[]))==1 for row in d['services'])
    reports.append(d)
assert reports[0]['services']==reports[1]['services']
family=json.loads((R/'active-three-source-family.json').read_text())['source_family']
prefix={'Post80 Plate2 damping68':'post80plate68','Post74 joint oscillator-filter':'post74joint'}[family]
states=[]
for role in ['main','phase','balance']:
    state=json.loads((R/(prefix+'-'+role+'-state.json')).read_text());assert state['phase']!='failed'
    pid=state['controller_PID'];p=Path('/proc',str(pid));command=(p/'cmdline').read_bytes().split(b'\0')
    assert str(R/('continue_'+prefix+'_'+role+'.py')).encode() in command
    status=(p/'stat').read_text().rsplit(')',1)[1].split();assert status[0] not in ['Z','T']
    states.append(dict(role=role,state=state,process_state=status[0],starttime_ticks=status[19]))
complete=json.loads(Path('/workspace/divalead/diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
proof=json.loads((R/('public-'+complete['version'].split('-')[0]+'-verification.json')).read_text())
assert proof['remote_exact'] and proof['all_older_numbered_releases_unchanged']
core=json.loads((R/'post81-core-validator-regression.json').read_text())
assert core['fresh_Diva_Windows_native_own_NEW_and_all12_cases_passed']
out=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_family=family,current_complete_release=complete['version'],current_complete_public_receipt=proof['commit'],idempotent_startup_twice_no_new_services=True,existing_service_reports=reports,actual_parent_states=states,full_real_Diva_and_Windows_clean_ZIP_DLL_workflow_verified=True,core_validator_actual_fresh_regression_passed=True,fresh_task_restore_tested=False,FL_GUI_tested=False,subjective_audition_performed=False,match_reached=False)
(R/'post81-runtime-readiness.json').write_text(json.dumps(out,indent=2)+'\n');print('ACTUAL_FULL_WORKFLOW_AND_TWO_IDEMPOTENT_STARTUPS_PASS',family,flush=True)
