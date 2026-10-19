from pathlib import Path
import subprocess,json,hashlib,urllib.request,concurrent.futures,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0]==head
root='diva-lead/research/three-held-continuation/after-v59/'
names=['README.md','source-wide/history.json','source-drift24-proof/validation.json','source-drift24-proof/parameter-difference.json','source-drift24-proof/Diva_THREE_HELD_BASELINE.h2p','source-drift24-proof/NEW-independent-base-pdc.wav','AB_REFERENCE_V59_DRIFT24_RESEARCH_WIP.wav']
def fetch(name):
 path=root+name
 with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+path,timeout=90) as response:data=response.read();status=response.status
 assert status==200 and data==(REPO/path).read_bytes(),path
 return dict(path=path,HTTP=status,SHA256=hashlib.sha256(data).hexdigest(),bytes=len(data),byte_equal=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,names))
(R/'public-latest-research-verification.json').write_text(json.dumps(dict(commit=head,remote_main_exact=True,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),public_files=rows,v59_ZIP_unchanged=True,match_reached=False),indent=2)+'\n');print('PUBLIC_DRIFT24_RESEARCH_AND_MAIN_BYTE_EXACT_PASS',head,len(rows),flush=True)
