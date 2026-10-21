"""Measure native declared PDC, causality and host block-size sensitivity."""
from pathlib import Path
import json,subprocess,sys
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from apply_native_candidate import apply
x=json.loads(Path(sys.argv[1]).read_text())['x'];dest=Path(sys.argv[2])
cc='/workspace/divalead-setup/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
rows=[];reference=None
for block in [128,512,1024]:
    engine=f'native-block-{block}.exe'
    subprocess.run([cc,'-O3','-static-libgcc','-Wl,--no-insert-timestamp','-DFL_PRESET_GRAPH',f'-DBLOCK={block}','-o',str(W/engine),str(W/'fl_native_chain_host.c'),'-lole32','-luuid','-lm'],check=True)
    c=NativeChain(W/'native-frozen-source-with-tail.wav',f'native-block-{block}',fl_graph=True,engine_override=engine)
    try:apply(c,x);y,status=c.render()
    finally:c.close()
    if reference is None:reference=y
    error=float(abs(y-reference).max());rows.append(dict(block=block,native_status=status,max_error_from_block128=error,null_RMS=float(np.sqrt(np.mean((y-reference).astype(float)**2)))))
impulse=np.zeros((48000,2),np.float32);impulse[8192]=[.1,.073]
path=W/'native-live-latency-input.wav';sf.write(path,impulse,48000,subtype='FLOAT')
c=NativeChain(path,'native-live-latency-output',fl_graph=True)
try:apply(c,x);y,status=c.render()
finally:c.close()
envelope=abs(y).max(axis=1);nz=np.flatnonzero(envelope>1e-6)
assert len(nz) and nz[0]>=8192
report=dict(block_size_cases=rows,block_size_sample_exact=all(r['max_error_from_block128']==0 for r in rows),block_invariance_within_2e_6=all(r['max_error_from_block128']<=2e-6 for r in rows),input_impulse_frame=8192,output_first_over_1e_6_frame=int(nz[0]),output_peak_frame=int(envelope.argmax()),first_response_delay_frames=int(nz[0]-8192),pre_input_max_abs=float(envelope[:8192].max()),no_pre_input_response=True,native_status=status,declared_effect_PDC_frames=0,old_Finish_PDC_frames=12416,not_a_DAW_or_audio_interface_latency_test=True,FL_GUI_tested=False)
dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
