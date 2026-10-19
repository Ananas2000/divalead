from pathlib import Path
import subprocess,json,hashlib,urllib.request,concurrent.futures,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0]==head
prefix='diva-lead/research/three-held-continuation/after-v61/continued-gain2/'
paths=[prefix+n for n in ['README.md','accepted-gain2/validation.json','CONTINUED_GAIN2_REFERENCE_EDIT_WIP.wav','AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.mp3','AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.wav','three_gain_interior_projection.py','numeric/projection.json']]+['diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json']
def fetch(path):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+path,timeout=90) as response:data=response.read();status=response.status
 assert status==200 and data==(REPO/path).read_bytes(),path
 return dict(path=path,HTTP=status,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),byte_equal=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(fetch,paths))
for name in ['Diva_lead_v61_WIP_checkpoint.zip','diva-lead/v61-wip','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']:
 assert subprocess.check_output(['git','rev-parse',head+':'+name],cwd=REPO)==subprocess.check_output(['git','rev-parse','541e3024dfaf8e7cdfa8386b02474068dc1c8e74:'+name],cwd=REPO)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
def alive(pid,script):
 path=Path('/proc',str(pid));assert str(R/script).encode() in (path/'cmdline').read_bytes()
 assert (path/'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
live=[]
for name,script in [('continuation-state.json','continue_three.py'),('phase-continuation-state.json','continue_phase18.py'),('drift24-continuation-state.json','continue_drift24.py')]:
 state=json.loads((R/name).read_text());assert state['phase']!='failed',state;alive(state['controller_PID'],script);row=dict(state=state)
 if state.get('fit_PID'):
  try:
   p=Path('/proc',str(state['fit_PID']));assert (p/'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
   log=Path(state['fit_log']);modified=datetime.datetime.fromtimestamp(log.stat().st_mtime,datetime.timezone.utc)
   age=(datetime.datetime.now(datetime.timezone.utc)-modified).total_seconds();assert age<300,(name,age)
   row.update(fit_log_bytes=log.stat().st_size,fit_log_modified_UTC=modified.isoformat(),fit_log_age_seconds=age)
  except FileNotFoundError:
   newstate=json.loads((R/name).read_text());assert newstate!=state;row=dict(state=newstate,fit_completed_during_check=True)
 live.append(row)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_main_exact=True,new_research_HTTP_files=files,complete_v61_kit_and_canonical_pointer_unchanged=True,three_live_controllers_and_actual_fresh_fit_logs=live,match_reached=False)
(R/'V61_LATEST_GAIN_CHECKPOINT_STATUS.json').write_text(json.dumps(report,indent=2)+'\n')
print('V61_PUBLIC_LATER_RESEARCH_ALL8_HTTP_FILES_UNCHANGED_KIT_AND_THREE_ACTIVE_CONTROLLERS_PASS',head,flush=True)
