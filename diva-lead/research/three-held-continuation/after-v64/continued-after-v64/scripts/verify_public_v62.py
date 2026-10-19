from pathlib import Path
import subprocess,json,hashlib,urllib.request,concurrent.futures,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0]==head
prefix='diva-lead/v62-wip/'
paths=['Diva_lead_v62_WIP_checkpoint.zip','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']+[prefix+n for n in ['README.md','FL_STUDIO_RU.md','Diva_Lead_Finish_v62_WIP_x64.dll','Diva_Lead_Finish_v62_WIP.fxp','Diva_Lead_v62_WIP.h2p','Diva_THREE_HELD_180BPM.mid','AB_REFERENCE_V61_V62_WIP.mp3','AB_REFERENCE_V61_V62_WIP.wav','Diva_Lead_v62_REFERENCE_EDIT.wav','Diva_Lead_v62_FULL_180BPM.wav','COMPARISON_RU.md']]+['diva-lead/research/three-held-continuation/after-v62/README.md','diva-lead/research/three-held-continuation/after-v62/accepted-gain14/validation.json']
def fetch(path):
 with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+path,timeout=90) as response:data=response.read();status=response.status
 assert status==200 and data==(REPO/path).read_bytes(),path
 return dict(path=path,HTTP=status,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),byte_equal=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(fetch,paths))
for name in ['Diva_lead_v61_WIP_checkpoint.zip','diva-lead/v61-wip/Diva_Lead_Finish_v61_WIP_x64.dll','diva-lead/v61-wip/Diva_Lead_v61_WIP.h2p','diva-lead/v61-wip/Diva_THREE_HELD_180BPM.mid']:
 assert subprocess.check_output(['git','rev-parse',head+':'+name],cwd=REPO)==subprocess.check_output(['git','rev-parse','541e3024dfaf8e7cdfa8386b02474068dc1c8e74:'+name],cwd=REPO)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_main_exact=True,new_public_files=files,complete_v61_kit_unchanged=True,FL_GUI_tested=False,match_reached=False)
(R/'public-v62-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('V62_PUBLIC_MAIN_AND_ALL15_HTTP_ASSETS_BYTE_EXACT_AND_V61_IMMUTABLE_PASS',head,flush=True)
