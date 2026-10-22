"""Compare fresh VST block/warmup protocols to the existing real-FL raw capture.
This diagnoses host differences; no time-shifted source is promoted as a preset.
"""
from pathlib import Path
import os,subprocess,json,concurrent.futures
import numpy as np,soundfile as sf
from local_native_chain import ROOT,SESSION,W
OUT=SESSION/'host-block-diagnostic';OUT.mkdir(exist_ok=True)
y,sr=sf.read(SESSION/'renders/FL_DIVA_CHANNEL03_SOURCE.wav',always_2d=True);assert sr==48000
windows=[(1000,23000),(25000,47000),(49000,63000),(129000,151000),(153000,175000),(177000,191000)]
def rel(p):return os.path.relpath(p,ROOT)
def run(b):
    exe=W/f'diva_block_{b}.exe'
    p=subprocess.run(['gcc','-O2','-static',f'-DDIVA_BLOCK={b}','-o',str(exe),str(W/'diva_source_render_host.c')],capture_output=True,text=True);assert p.returncode==0,p.stderr
    rows=[]
    for mode,warm in [('same-count',128),('same-total-frames',max(1,round(66048/b)-1))]:
        tag=f'block{b}-{mode}';raw=OUT/(tag+'.wav');cmd=['pattern 3 0 8','velocities 96 96 101',f'warmblocks {warm}','preludes 0','render '+rel(raw),'quit']
        p=subprocess.run([str(exe),r'C:\Program Files\VstPlugins\Diva(x64).dll',rel(SESSION/'input/Diva_NATIVE_WIP_THREE_HELD.h2p')],cwd=ROOT,input='\n'.join(cmd)+'\n',capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=60);(OUT/(tag+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout
        x,_=sf.read(raw,always_2d=True);n=min(192000,len(y),len(x));x=x[:n];z=y[:n];g=float(np.sum(x*z)/np.sum(x*x));parts=[]
        for lo,hi in windows:
            a=x[lo:hi];v=z[lo:hi];sg=np.sum(a*v)/np.sum(a*a);parts.append(dict(start=lo,gain=float(sg),residual=float(np.sqrt(np.mean((v-sg*a)**2)/np.mean(v*v)))))
        rows.append(dict(block=b,warm_blocks=warm,warm_frames=(warm+1)*b,mode=mode,amplitude_fit=g,residual=float(np.sqrt(np.mean((z-g*x)**2)/np.mean(z*z))),parts=parts,raw_file=rel(raw),not_a_candidate=True))
    return rows
with concurrent.futures.ThreadPoolExecutor(4)as ex:rows=[r for rr in ex.map(run,[16,32,64,128,256,512,1024])for r in rr]
rows.sort(key=lambda r:r['residual']);(OUT/'RESULTS.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{k:r[k]for k in('block','mode','residual','amplitude_fit')}for r in rows]),flush=True)
