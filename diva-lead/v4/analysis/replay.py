"""Replay the fixed eight-attack test phrase in the user's VST2 Diva engine."""
from pathlib import Path
import argparse,json,os,shutil,subprocess
import numpy as np
import soundfile as sf

base=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--plugin',required=True,type=Path)
p.add_argument('--host',type=Path,default=Path(__file__).with_name('diva_host.exe'))
p.add_argument('--output',type=Path,default=base/'Diva_replay.wav')
p.add_argument('--wine',help='Wine executable on Linux; not used on Windows')
p.add_argument('--prefix',type=Path,default=base/'analysis/wine-prefix')
p.add_argument('--wine-dll-dir',type=Path)
p.add_argument('--wineserver',type=Path)
a=p.parse_args()
def winpath(path):
    path=path.resolve()
    return str(path) if os.name=='nt' else 'Z:'+str(path).replace('/','\\')

timing=json.loads((base/'render_timing.json').read_text())
env=os.environ.copy();env.pop('GH_TOKEN',None);env.pop('GITHUB_TOKEN',None)
env['WINEDEBUG']='-all'
if os.name=='nt':command=[str(a.host.resolve())]
else:
    wine=a.wine or shutil.which('wine64') or shutil.which('wine')
    if not wine:raise SystemExit('Install Wine or pass --wine.')
    env['WINEPREFIX']=str(a.prefix.resolve())
    if a.wine_dll_dir:env['WINEDLLPATH']=str(a.wine_dll_dir.resolve())
    if a.wineserver:env['WINESERVER']=str(a.wineserver.resolve())
    command=[wine,str(a.host.resolve())]
command += [winpath(a.plugin),winpath(base/'Diva_Lead_Reference_v4_DRY.h2p')]
protocol=('pattern 8 0 7\n'
          f'timing {timing["swing_fraction"]:.12g} {timing["gate_fraction"]:.12g}\n'
          'velocities 100 100 100\n'
          f'render {winpath(a.output)}\nquit\n')
r=subprocess.run(command,input=protocol,text=True,stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT,env=env,timeout=120)
if r.returncode or 'RENDER ' not in r.stdout:
    raise SystemExit('Host failed; last output:\n'+r.stdout[-2000:])
x,sr=sf.read(a.output,always_2d=True)
assert sr==48000 and x.shape==(192000,2) and np.all(np.isfinite(x))
assert .005<float(abs(x).max())<1
print(json.dumps({'sample_rate':sr,'frames':len(x),'peak':float(abs(x).max()),
                  'output':str(a.output.resolve())},indent=2))
