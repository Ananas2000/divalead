"""Rebuild a packaged Windows x64 Finish effect from its supplied C sources."""
import argparse,json,shutil,subprocess
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('release',type=Path,help='Directory such as diva-lead/v57-wip')
p.add_argument('--compiler',help='Windows gcc or a MinGW x64 cross compiler')
p.add_argument('--output',type=Path)
p.add_argument('--image-base',help='Optional preferred PE image base, e.g. 0x35fa60000')
a=p.parse_args();release=a.release.resolve()
compiler=a.compiler or shutil.which('x86_64-w64-mingw32-gcc')
if not compiler:p.error('Specify --compiler with a Windows x64 MinGW gcc executable')
existing=list(release.glob('Diva_Lead_Finish_*_x64.dll'))
if a.output is None and len(existing)!=1:p.error('Specify --output for the new DLL')
out=a.output.resolve() if a.output else existing[0]
source=release/'analysis/lead_finish.c'
if not source.is_file():p.error('Missing analysis/lead_finish.c')
out.parent.mkdir(parents=True,exist_ok=True)
flags=[]
if a.image_base:
 try:base=int(a.image_base,0)
 except ValueError:p.error('Invalid --image-base integer')
 if not 0<=base<2**64:p.error('PE image base is outside uint64')
 flags=['-Wl,--image-base,'+hex(base)]
subprocess.run([compiler,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp',*flags,'-o',str(out),str(source),'-lm'],check=True)
print(json.dumps(dict(output=str(out),bytes=out.stat().st_size,FL_GUI_validation_claimed=False)))
