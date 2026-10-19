from pathlib import Path
import json,hashlib,subprocess,urllib.request,concurrent.futures,datetime,os
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0];assert head==remote
paths=['diva-lead/research/three-held-continuation/after-v59/hf-continuation-0001/'+n for n in ['README.md','validation.json','AFTER_V59_HF_0001_REFERENCE_EDIT.wav','AB_REFERENCE_V59_HF0001_RESEARCH_WIP.wav']]
def fetch(name):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+name,timeout=90) as r:data=r.read();status=r.status
 assert status==200 and data==(REPO/name).read_bytes(),name
 return dict(path=name,HTTP=status,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),byte_equal=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,paths))
for name in ['Diva_lead_v59_WIP_checkpoint.zip','diva-lead/v59-wip/Diva_Lead_Finish_v59_WIP_x64.dll','diva-lead/v59-wip/Diva_Lead_v59_WIP.h2p','diva-lead/v59-wip/Diva_THREE_HELD_180BPM.mid']:
 assert subprocess.check_output(['git','rev-parse',head+':'+name],cwd=REPO)==subprocess.check_output(['git','rev-parse','09ca93b5b3ff4621afc94cb17e86b34df53a3ecd:'+name],cwd=REPO)
live=[]
for file in ['continuation-state.json','drift24-continuation-state.json']:
 state=json.loads((R/file).read_text());assert state['phase']!='failed';pid=state['controller_PID'];cmd=Path('/proc',str(pid),'cmdline').read_bytes();assert str(R).encode() in cmd and Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
 fit=state.get('fit_PID')
 if fit:assert Path('/proc',str(fit),'stat').read_text().rsplit(')',1)[1].split()[0]!='Z'
 logfile=Path(state.get('fit_log',R/'controller.log'));live.append(dict(state=state,fit_log_bytes=logfile.stat().st_size,fit_log_modified_UTC=datetime.datetime.fromtimestamp(logfile.stat().st_mtime,datetime.timezone.utc).isoformat()))
report=dict(commit=head,remote_main_exact=True,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),public_new_HF_files=results,previous_v59_kit_objects_unchanged=True,live_three_note_controllers=live,match_reached=False)
(R/'FINAL_CHECKPOINT_STATUS.json').write_text(json.dumps(report,indent=2)+'\n');print('FINAL_CHECKPOINT_PUBLIC_HF_AND_MAIN_AND_TWO_LIVE_THREE_CONTROLLERS_PASS',head,flush=True)
