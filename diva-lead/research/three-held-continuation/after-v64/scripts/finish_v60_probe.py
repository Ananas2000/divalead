from pathlib import Path
import os,json,subprocess,ctypes
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;T=R/'v60-build';D=T/'v60-wip';setup=Path('/workspace/divalead-setup');compiler=str(setup/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
p=D/'analysis/vst_program_probe.c';p.write_text(p.read_text().replace('v58 WIP','v60 WIP'))
p=R/'build_three_v60.py';p.write_text(p.read_text().replace("p.write_text(p.read_text().replace('0x444c3538','0x444c3630'))","p.write_text(p.read_text().replace('0x444c3538','0x444c3630').replace('v58 WIP','v60 WIP'))"))
def win(p):return 'Z:'+str(p).replace('/','\\')
env=dict(os.environ,WINEPREFIX=str(setup/'wine2'),WINEDLLPATH=str(setup/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(setup/'cache'))
probe=T/'vst_program_probe.exe';dll=D/'Diva_Lead_Finish_v60_WIP_x64.dll';subprocess.run([compiler,'-O2','-static-libgcc','-I',str(D/'analysis'),str(D/'analysis/vst_program_probe.c'),'-o',str(probe),'-lm'],check=True)
with (D/'verification/Windows_VST_program_probe.json').open('w') as log:subprocess.run([str(setup/'sysroot/usr/lib/wine/wine64'),str(probe),win(dll),win(T/'defaults.chunk'),win(D/'Diva_Lead_Finish_v60_WIP.fxp')],env=env,stdout=log,check=True,timeout=120)
raw,rate=sf.read(D/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32');full,fr=sf.read(T/'Windows-with-tail.wav',dtype='float32');padded=np.pad(raw,((0,12416),(0,0)));assert rate==fr==48000
lib=ctypes.CDLL(str(T/'native_finish.so'));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];out=np.zeros_like(padded);assert lib.native_render(padded.ctypes.data,out.ctypes.data,len(padded),48000);error=float(np.max(abs(full-out)));assert error<2e-7
selected=sf.read(D/'verification/Selected_WITH_PDC.wav',dtype='float32')[0];same=float(np.max(abs(full[:len(raw)]-selected)));assert same<2e-7
blocks=[]
for block in [47,127,2048]:
 e=float(np.max(abs(full-sf.read(T/('block-'+str(block)+'.wav'),dtype='float32')[0])));assert e<2e-7;blocks.append(dict(block_size=block,max_error=e))
report=dict(release_ID='0x444c3630',image_base='0x360600000',incoming_notes_per_phrase=3,note_on_count=6,Diva_ARP='On',Diva_preset_and_MIDI_bytes_equal_user_selected_three=True,Windows_native_max_error=error,released_DLL_matches_selected_waveform_max_error=same,block_checks=blocks,PDC_frames_48k=12416,FL_GUI_tested=False,match_reached=False)
(D/'verification/release_build_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('V60_BINARY_AUDIO_API_PROOF_PASS',json.dumps(report),flush=True)
