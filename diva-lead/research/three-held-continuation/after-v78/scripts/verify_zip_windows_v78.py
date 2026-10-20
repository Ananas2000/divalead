from pathlib import Path
import os,subprocess,json
import soundfile as sf,numpy as np
R=Path(__file__).resolve().parent;T=Path('/tmp/divalead-v78-build');D=Path('/tmp/divalead-v78-clean-extraction/v78-wip');setup=Path('/workspace/divalead-setup')
def win(p):return 'Z:'+str(p).replace('/','\\')
env=dict(os.environ,WINEPREFIX=str(setup/'wine2'),WINEDLLPATH=str(setup/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(setup/'cache'))
raw,sr=sf.read(D/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32');assert sr==48000
path=T/'zip-source-plus-tail.wav';sf.write(path,np.pad(raw,((0,12416),(0,0))),sr,subtype='FLOAT')
out=T/'clean-ZIP-Windows.wav'
with (T/'clean-ZIP-Windows.log').open('w') as log:subprocess.run([str(setup/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/fl-v57-build/fx_render_host.exe',win(D/'Diva_Lead_Finish_v78_WIP_x64.dll'),win(path),win(out),'127'],env=env,stdout=log,stderr=log,check=True,timeout=150)
a,sr=sf.read(out,dtype='float32');b,br=sf.read(D/'Diva_Lead_v78_FULL_180BPM.wav',dtype='float32');assert sr==br==48000
np.testing.assert_array_equal(a[12416:12416+len(raw)],b)
p=T/'clean-ZIP-Windows-proof.json';p.write_text(json.dumps(dict(clean_ZIP_actual_DLL_loaded=True,full_WAV_sample_exact=True,block_size=127,sample_rate=48000,PDC_frames=12416,FL_GUI_tested=False),indent=2)+'\n');print(p.read_text())
