from pathlib import Path
import json, os, subprocess, time
import numpy as np
import soundfile as sf

W=Path(__file__).resolve().parent
class NativeChain:
    def __init__(self,input_path,tag='native-chain',fl_graph=False,engine_override=None,comb_stack=False):
        self.output=W/(tag+'-render.wav');self.logpath=W/(tag+'-host.log')
        rows=json.loads((W/'staged-plugin-manifest.json').read_text())
        paths={x['name']:Path(x['staged']) for x in rows}
        names=['Fruity WaveShaper_x64.dll','Fruity Parametric EQ 2_x64.dll',
               'Fruity Parametric EQ 2_x64.dll','Fruity Chorus_x64.dll']+[
               'Fruity Parametric EQ 2_x64.dll']*4+['Fruity Stereo Shaper_x64.dll','Fruity Soft Clipper_x64.dll']
        if fl_graph:names+=['Fruity Stereo Shaper_x64.dll']*3
        if comb_stack:
            assert fl_graph
            names+=['Fruity Chorus_x64.dll']
        setup=Path('/workspace/divalead-setup');env=os.environ.copy()
        env.update(WINEPREFIX=str(W/'wine'),WINEDLLPATH=str(setup/'sysroot/usr/lib/x86_64-linux-gnu/wine'),
                   WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(W/'cache'))
        self.log=self.logpath.open('w')
        def win(p):return 'Z:'+str(Path(p).resolve()).replace('/','\\')
        engine=engine_override or ('fl_native_comb_host.exe' if comb_stack else 'fl_native_fl_graph_host.exe' if fl_graph else 'fl_native_chain_host.exe')
        argv=[str(setup/'sysroot/usr/lib/wine/wine64'),str(W/engine),
              win(input_path),win(self.output)]+[win(paths[x]) for x in names]
        self.proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,
                                   text=True,bufsize=1,env=env)
        self.pending=[];self.commands=[]
        self.ready=self._line('READY')
        if fl_graph:
            half=int(round(12800*np.log(2)/np.log(3)))
            for node,values in [(10,[half]*4),(11,[-half,half,-half,half]),(12,[0,12800,-12800,0])]:
                for i,value in enumerate(values):self.set(node,i,value)
    def _line(self,prefix):
        while True:
            line=self.proc.stdout.readline()
            if not line:raise RuntimeError(f'Native host exited {self.proc.poll()}: {self.logpath.read_text()[-2000:]}')
            if line.startswith(prefix):return line.strip()
    def set(self,node,index,value):self.pending.append(f'S {node} {index} {int(value)}')
    def gain(self,index,value):self.pending.append(f'G {index} {float(value):.17g}')
    def bypass(self,node,disabled=True):self.pending.append(f'B {node} {int(disabled)}')
    def _send(self,last):
        commands=self.pending+[last];self.pending=[];self.commands+=commands
        self.proc.stdin.write('\n'.join(commands)+'\n');self.proc.stdin.flush()
    def render(self):
        self._send('R');status=self._line('DONE')
        y,sr=sf.read(self.output,dtype='float32',always_2d=True)
        assert sr==48000 and np.isfinite(y).all()
        return y,status
    def mapped(self,node,index,midi):
        self._send(f'H {node} {index} {int(midi)}');return int(self._line('MAPPED').split()[-1])
    def value_hint(self,node,index):
        self._send(f'V {node} {index}');return int(self._line('VALUE').split()[-1])
    def save_state(self,node,dest):
        self._send(f'D {node} Z:'+str(Path(dest).resolve()).replace('/','\\'))
        line=self._line('STATE_SAVED');assert line.endswith(' 1'),line
    def load_state(self,node,src):
        self._send(f'L {node} Z:'+str(Path(src).resolve()).replace('/','\\'))
        line=self._line('STATE_LOADED');assert line.endswith(' 1'),line
    def load_input(self,src):
        self._send('I Z:'+str(Path(src).resolve()).replace('/','\\'))
        return self._line('INPUT_LOADED')
    def automate(self,events):
        self.pending.append('TCLEAR')
        for frame,node,index,value in events:self.pending.append(f'T {int(frame)} {int(node)} {int(index)} {int(value)}')
    def close(self):
        if self.proc.poll() is None:
            self._send('Q');self._line('CLOSED_OK');self.proc.wait(timeout=20)
        self.log.close();assert self.proc.returncode==0

if __name__=='__main__':
    src,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_SOURCE_FROZEN_48k.wav',dtype='float32',always_2d=True)
    padded=np.pad(src,((0,32768),(0,0)));sf.write(W/'native-frozen-source-with-tail.wav',padded,sr,subtype='FLOAT')
    c=NativeChain(W/'native-frozen-source-with-tail.wav','native-chain-first')
    print(c.ready,flush=True)
    y,a=c.render();y2,b=c.render()
    print('FLAT',a,'raw_max_error',float(abs(y-padded).max()),'repeat_max_error',float(abs(y-y2).max()),flush=True)
    c.set(3,11,1);c.gain(0,.7);c.gain(1,.5)
    z,d=c.render();z2,e=c.render()
    print('CHORUS',d,'repeat_max_error',float(abs(z-z2).max()),flush=True)
    mappings={}
    for node,index in [(1,0),(1,7),(1,14),(1,21),(1,28),(3,0),(3,1),(3,2),(3,3),(3,6),(3,9),(3,10),(8,4),(8,5)]:
        vals=[c.mapped(node,index,v) for v in [0,16384,32768,49152,65536]]
        mappings[f'{node}:{index}']=vals;print('MAP',node,index,vals,flush=True)
    c.close()
    (W/'NATIVE_CHAIN_FIRST_CHECKS.json').write_text(json.dumps(dict(flat_raw_max_error=float(abs(y-padded).max()),flat_repeat_max_error=float(abs(y-y2).max()),chorus_repeat_max_error=float(abs(z-z2).max()),mappings=mappings,native_chain_rendered=True),indent=2)+'\n')
