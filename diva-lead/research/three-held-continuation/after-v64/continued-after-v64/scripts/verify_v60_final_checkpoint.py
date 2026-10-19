from pathlib import Path
import subprocess,json,hashlib,urllib.request,concurrent.futures,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0]==head
prefix='diva-lead/research/three-held-continuation/after-v60/continued-after-v60/'
paths=[prefix+n for n in ['README.md','accepted-gain4/validation.json','CONTINUED_GAIN4_REFERENCE_EDIT_WIP.wav','AB_REFERENCE_V60_CONTINUED_GAIN4_WIP.wav','rounds/phase2/decision.json','three_candidate_decision.py']]
paths.append('diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json')
def fetch(path):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+path,timeout=90) as response:data=response.read();status=response.status
 assert status==200 and data==(REPO/path).read_bytes(),path
 return dict(path=path,HTTP=status,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),byte_equal=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(fetch,paths))
for name in ['Diva_lead_v60_WIP_checkpoint.zip','diva-lead/v60-wip/Diva_Lead_Finish_v60_WIP_x64.dll','diva-lead/v60-wip/Diva_Lead_v60_WIP.h2p','diva-lead/v60-wip/Diva_THREE_HELD_180BPM.mid']:
 assert subprocess.check_output(['git','rev-parse',head+':'+name],cwd=REPO)==subprocess.check_output(['git','rev-parse','e07a638a2c59a98261397f40d7bc2b659343d573:'+name],cwd=REPO)
live=[]
for name in ['continuation-state.json','phase-continuation-state.json','drift24-continuation-state.json']:
 state=json.loads((R/name).read_text());assert state['phase']!='failed',state
 pid=state['controller_PID'];assert str(R).encode() in Path('/proc',str(pid),'cmdline').read_bytes();assert Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
 row=dict(state=state)
 if state.get('fit_PID'):
  p=state['fit_PID'];assert Path('/proc',str(p),'stat').read_text().rsplit(')',1)[1].split()[0]!='Z';log=Path(state['fit_log']);row.update(fit_log_bytes=log.stat().st_size,fit_log_modified_UTC=datetime.datetime.fromtimestamp(log.stat().st_mtime,datetime.timezone.utc).isoformat())
 live.append(row)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_main_exact=True,new_public_files=files,complete_v60_kit_unchanged=True,three_note_controllers=live,match_reached=False)
(R/'V60_FINAL_CHECKPOINT_STATUS.json').write_text(json.dumps(report,indent=2)+'\n');print('V60_PUBLIC_AND_LATER_RESEARCH_AND_THREE_LIVE_CONTROLLERS_PASS',head,flush=True)
