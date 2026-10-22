"""Render the installed Diva VST2 with the exact supplied h2p and six-note protocol."""
from pathlib import Path
import subprocess,os,json,time,argparse
W=Path(__file__).resolve().parent;ROOT=W.parent.parent;SESSION=ROOT/'sessions/2026-10-22'
p=argparse.ArgumentParser();p.add_argument('--preset',default='sessions/2026-10-22/input/Diva_NATIVE_WIP_THREE_HELD.h2p');p.add_argument('--tag',default='DIVA_FRESH_DIRECT');a=p.parse_args();assert Path(a.tag).name==a.tag
commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0',f'dump sessions/2026-10-22/{a.tag}_ALL281.tsv',f'save sessions/2026-10-22/{a.tag}.vstchunk',f'render sessions/2026-10-22/renders/{a.tag}.wav','quit']
start=time.monotonic()
p=subprocess.run([str(W/'diva_source_render_host.exe'),r'C:\Program Files\VstPlugins\Diva(x64).dll',a.preset],cwd=ROOT,input='\n'.join(commands)+'\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,timeout=90)
(SESSION/(a.tag+'.log')).write_text(p.stdout,encoding='utf-8');print(p.stdout[-2500:]);print(dict(returncode=p.returncode,seconds=time.monotonic()-start));assert p.returncode==0
