from pathlib import Path
import hashlib,json,subprocess,urllib.request,concurrent.futures,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0];assert head==remote
names=['Diva_lead_v59_WIP_checkpoint.zip','README.md','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']
prefix='diva-lead/v59-wip/'
names += [prefix+n for n in ['README.md','FL_STUDIO_RU.md','COMPARISON_RU.md','Diva_Lead_v59_WIP.h2p','Diva_THREE_HELD_180BPM.mid','Diva_Lead_Finish_v59_WIP_x64.dll','Diva_Lead_Finish_v59_WIP.fxp','AB_REFERENCE_THREE58_V59_WIP.mp3','AB_REFERENCE_THREE58_V59_WIP.wav','Diva_Lead_v59_REFERENCE_EDIT.wav','Diva_Lead_v59_FULL_180BPM.wav','SHA256SUMS.txt']]
def fetch(name):
 url='https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+name
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'divalead-reproducibility-check'}),timeout=90) as response:
  data=response.read();status=response.status
 assert status==200 and data==(REPO/name).read_bytes(),name
 return dict(path=name,HTTP=status,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),byte_equal=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,names))
proof=dict(checked_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_main_exact=True,public_files=rows,match_reached=False)
(R/'public-v59-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print('PUBLIC_V59_MAIN_AND_HTTP_BYTE_EXACT_PASS',head,len(rows),flush=True)
