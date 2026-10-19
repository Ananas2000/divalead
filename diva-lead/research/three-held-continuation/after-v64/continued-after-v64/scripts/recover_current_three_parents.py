"""One-time handoff for two live parents loaded before quality rejection recovery.

Fresh environment starts already load the corrected controller code. No Git writes.
"""
from pathlib import Path
import os,sys,json,hashlib,time,subprocess,datetime
from three_candidate_decision import quality_rejection
R=Path(__file__).resolve().parent
watch=[dict(PID=78627,script='continue_three.py',state='continuation-state.json',work='continuation'),dict(PID=80265,script='continue_drift24.py',state='drift24-continuation-state.json',work='drift24-continuation')]
def alive(pid,script):
 try:return str(R/script).encode() in Path('/proc',str(pid),'cmdline').read_bytes() and Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
 except (FileNotFoundError,ProcessLookupError):return False
def save(rows):
 p=R/'current-three-parent-handoff-state.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),one_time_current_instance_only=True,automatic_Git_publication=False,controllers=rows),indent=2)+'\n');t.replace(p)
while watch:
 states=[];remaining=[]
 for item in watch:
  if alive(item['PID'],item['script']):states.append(dict(item,phase='original_parent_still_working'));remaining.append(item);continue
  state=json.loads((R/item['state']).read_text())
  if alive(state.get('controller_PID',0),item['script']):states.append(dict(item,phase='already_replaced_by_new_controller',new_PID=state['controller_PID']));continue
  error=state.get('error','');found=None
  for log in sorted((R/item['work']).glob('round-*/validation.log'),reverse=True):
   run=log.parent
   if str(run/'numeric') not in error:continue
   parts=run.name.split('-');target=R/(('drift24-' if item['script']=='continue_drift24.py' else '')+'verified-cont-'+parts[1]+'-'+parts[2]);rejected=quality_rejection(log,target)
   if rejected:found=(run,rejected);break
  if found is None:states.append(dict(item,phase='requires_manual_diagnosis',error=error));continue
  run,rejected=found;(run/'decision.json').write_text(json.dumps(rejected,indent=2)+'\n')
  seenpath=R/item['work']/'attempted.json';seen=json.loads(seenpath.read_text());kind=run.name.rsplit('-',1)[1];key=hashlib.sha256((run/'basis/analysis/spectral_model.json').read_bytes()).hexdigest()+':'+kind
  if key not in seen:seen.append(key);seenpath.write_text(json.dumps(seen,indent=2)+'\n')
  with (R/(item['script']+'.recovered.log')).open('ab') as output:proc=subprocess.Popen([sys.executable,'-B',str(R/item['script'])],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdin=subprocess.DEVNULL,stdout=output,stderr=output,start_new_session=True,close_fds=True)
  states.append(dict(item,phase='known_quality_rejection_preserved_and_parent_restarted',new_PID=proc.pid))
 watch=remaining;save(states)
 if watch:time.sleep(15)
