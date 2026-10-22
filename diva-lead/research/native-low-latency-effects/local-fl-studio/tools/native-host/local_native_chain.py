"""Local Windows runner for the original native FL research host."""
from pathlib import Path
import json,subprocess,time,os,sys
import numpy as np,soundfile as sf
W=Path(__file__).resolve().parent
ROOT=W.parent.parent
SESSION=ROOT/'sessions/2026-10-22'
FX=Path('C:/Program Files/Image-Line/FL Studio 20/Plugins/Fruity/Effects')

class NativeChain:
    def __init__(self,input_path,tag='native-local'):
        self.output=SESSION/'renders'/(tag+'.wav')
        self.logpath=SESSION/'renders'/(tag+'.log')
        names=['Fruity WaveShaper','Fruity Parametric EQ 2','Fruity Parametric EQ 2','Fruity Chorus']+['Fruity Parametric EQ 2']*4+['Fruity Stereo Shaper','Fruity Soft Clipper']+['Fruity Stereo Shaper']*5
        self.log=self.logpath.open('w')
        def relative(p):return os.path.relpath(p,ROOT)
        argv=[str(W/'fl_native_common_phase_host.exe'),relative(input_path),relative(self.output)]+[str(FX/n/(n+'_x64.dll'))for n in names]
        self.proc=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1,creationflags=subprocess.CREATE_NO_WINDOW)
        self.pending=[];self.commands=[];self.ready=self._line('READY')
    def _line(self,prefix):
        while True:
            line=self.proc.stdout.readline()
            if not line:raise RuntimeError(f'Native host exited {self.proc.poll()}: {self.logpath.read_text()[-3000:]}')
            if line.startswith(prefix):return line.strip()
    def send(self,last):
        c=self.pending+[last];self.pending=[];self.commands+=c
        self.proc.stdin.write('\n'.join(c)+'\n');self.proc.stdin.flush()
    def set(self,node,index,value):self.pending.append(f'S {node} {index} {int(value)}')
    def gain(self,index,value):self.pending.append(f'G {index} {float(value):.17g}')
    def bypass(self,node,value=True):self.pending.append(f'B {node} {int(value)}')
    def load_state(self,node,path):
        self.send(f'L {node} '+os.path.relpath(path,ROOT));line=self._line('STATE_LOADED');assert line.endswith(' 1'),line
    def save_state(self,node,path):
        self.send(f'D {node} '+os.path.relpath(path,ROOT));line=self._line('STATE_SAVED');assert line.endswith(' 1'),line
    def render(self):
        self.send('R');status=self._line('DONE');x,sr=sf.read(self.output,dtype='float32',always_2d=True);assert sr==48000 and np.isfinite(x).all();return x,status
    def load_input(self,path):
        self.send('I '+os.path.relpath(path,ROOT));return self._line('INPUT_LOADED')
    def value_hint(self,node,index):
        self.send(f'V {node} {index}');return int(self._line('VALUE').split()[-1])
    def close(self):
        if self.proc.poll() is None:self.send('Q');self._line('CLOSED_OK');self.proc.wait(timeout=20)
        self.log.close();assert self.proc.returncode==0
    def checkpoint(self):
        names={0:'SOURCE_WaveShaper',3:'SOURCE_Chorus',4:'MID_EQ_A',5:'MID_EQ_B',6:'SIDE_EQ_A',7:'SIDE_EQ_B',8:'SUM_Stereo',10:'MID_Encode',11:'SIDE_Encode',12:'SIDE_Decode',13:'SOURCE_Phase_R',14:'SOURCE_Phase_L'}
        for node,name in names.items():self.load_state(node,ROOT/'divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP/verification'/(name+'.bin'))
        for node in(1,2,9):self.bypass(node)
        self.gain(0,1-4923/12800);self.gain(1,4923/12800)
        self.gain(2,1);self.gain(3,1);self.gain(4,1)

if __name__=='__main__':
    c=NativeChain(SESSION/'renders/FL_DIVA_SOURCE_CURRENT.wav','OFFLINE_NATIVE_VALIDATION')
    print(c.ready,flush=True);c.checkpoint();x,s=c.render();print(s,flush=True);c.close()
