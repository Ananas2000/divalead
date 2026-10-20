"""Repair completed directions in one already idle main slot; leave handoff ownership intact."""
from pathlib import Path
import datetime,fcntl,json,os,subprocess,sys,traceback
R=Path(__file__).resolve().parent
lock=(R/'core-projection-idle-owner.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def proc(pid):
 try:
  p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split()
  return dict(PID=pid,state=s[0],ppid=int(s[1]),start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
 except FileNotFoundError:return None
def children(pid):
 return [d for p in Path('/proc').iterdir() if p.name.isdigit() and (d:=proc(int(p.name))) and d['ppid']==pid and d['state']!='Z']
def state(phase,**kw):
 p=R/'source-post81coreprojection-state.json';q=p.with_suffix('.tmp')
 q.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,CPU_slot='main',numeric_workers=1,main_capacity_reserved=2,slot_released=phase!='projecting_completed_core_in_idle_main_slot',only_three_held=True,match_reached=False,**kw),indent=2)+'\n');q.replace(p)
try:
 handoff=json.loads((R/'post80-source-handoff-state.json').read_text())
 assert handoff['phase']=='waiting_for_current_previous_source_fits_to_finish'
 main=handoff['stopped_parents']['main'];p=proc(main['PID'])
 assert p and p['start']==main['starttime_ticks'] and p['state']=='T' and not children(p['PID'])
 assert json.loads((R/'post81-core147-idle-main-state.json').read_text())['idle_main_slot_released']
 assert json.loads((R/'active-three-source-family.json').read_text())['source_family']=='Post74 joint oscillator-filter'
 state('projecting_completed_core_in_idle_main_slot',old_main_still_owned_by_handoff=main)
 assert proc(main['PID'])['state']=='T' and not children(main['PID'])
 with (R/'post81-core-projection-idle-fit.log').open('w') as log:
  subprocess.run([sys.executable,'-B',str(R/'fit_post81_core147_projection.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True,timeout=7200)
 decision=json.loads((R/'post81-core147-projection-research/decision.json').read_text())
 state('completed_strict_core_projection_release_idle_main',decision=decision)
except Exception:
 state('failed_preserve_projection_and_release_idle_main',error=traceback.format_exc());raise
finally:
 # The handoff owns the old stopped main. Never resume or retire it here.
 current=R/'source-post81coreprojection-state.json'
 if current.exists():
  d=json.loads(current.read_text());d['slot_released']=True;current.write_text(json.dumps(d,indent=2)+'\n')
 with (R/'post81-projection-release-bootstrap.log').open('w') as log:
  result=subprocess.run([sys.executable,'-B',str(R/'start_three_services.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdout=log,stderr=log)
 if result.returncode:raise RuntimeError('Projection released its slot, but startup needs diagnosis; see post81-projection-release-bootstrap.log')
 print('IDLE_MAIN_CORE_PROJECTION_RELEASED_WITH_HANDOFF_PARENT_OWNERSHIP_PRESERVED',flush=True)
