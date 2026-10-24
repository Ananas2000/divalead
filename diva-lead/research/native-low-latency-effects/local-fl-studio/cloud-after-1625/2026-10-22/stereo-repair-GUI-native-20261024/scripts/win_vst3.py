"""Control the real official Windows VST3 through a separate Wine host."""
from pathlib import Path
import os,subprocess,select,time
import numpy as np

D=Path(__file__).resolve().parent
S=Path('/workspace/divalead-setup')
PLUGIN=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
def win(p):return 'Z:'+str(Path(p).resolve()).replace('/','\\')

class WinVST3:
    def __init__(self,tag):
        self.log=(D/(tag+'-host.log')).open('w')
        self.out=D/(tag+'-output.f32');self.input=D/(tag+'-input.f32')
        env=dict(os.environ,WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),
                 WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
        self.child=subprocess.Popen([str(S/'sysroot/usr/lib/wine/wine64'),str(D/'vst3_effect_host.exe'),win(PLUGIN)],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=False,env=env,bufsize=0)
        self.buffer=b'';self._until('READY ',45)

    def _until(self,prefix,timeout=30):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            while b'\n'in self.buffer:
                line,self.buffer=self.buffer.split(b'\n',1);line=line.decode(errors='replace').rstrip('\r')
                self.log.write(line+'\n');self.log.flush()
                if line.startswith('ERROR '):raise RuntimeError(line)
                if line.startswith(prefix):return line
            remaining=deadline-time.monotonic()
            if remaining<=0:break
            ready,_,_=select.select([self.child.stdout],[],[],min(remaining,.5))
            if ready:
                data=os.read(self.child.stdout.fileno(),65536)
                if not data:raise RuntimeError(f'VST3 host exited {self.child.poll()}')
                self.buffer+=data
            elif self.child.poll()is not None:raise RuntimeError(f'VST3 host exited {self.child.returncode}')
        raise TimeoutError('VST3 host did not return '+prefix)

    def command(self,text,prefix,timeout=30):
        self.child.stdin.write((text+'\n').encode());self.child.stdin.flush()
        return self._until(prefix,timeout)
    def set(self,id,value):return self.command(f'set {int(id)} {float(value):.17g}','SET ')
    def text(self,id,value):return self.command(f'text {int(id)} {value}','SET ')
    def dump(self,path):self.command('dump '+win(path),'DUMP ')
    def save(self,path):self.command('save '+win(path),'SAVED ')
    def load(self,path):return self.command('load '+win(path),'LOADED ')
    def block(self,n):self.command('block '+str(n),'BLOCK ')
    def latency(self):return int(self.command('latency','LATENCY ').split()[1])
    def render(self,y=None,input_file=None):
        if input_file is None:
            np.asarray(y,dtype='<f4').tofile(self.input);input_file=self.input
        status=self.command('render '+win(input_file)+' '+win(self.out),'DONE ',60)
        result=np.fromfile(self.out,dtype='<f4').reshape(-1,2).copy()
        return result,status
    def close(self):
        if self.child.poll()is None:
            try:self.child.stdin.write(b'quit\n');self.child.stdin.flush();self.child.wait(timeout=10)
            except (BrokenPipeError,subprocess.TimeoutExpired):self.child.terminate();self.child.wait(timeout=10)
        self.log.close()
