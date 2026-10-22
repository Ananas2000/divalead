"""Measure native declared PDC, causality and host block-size sensitivity."""
from pathlib import Path
import json,subprocess,sys
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from apply_native_candidate import apply
choice=json.loads(Path(sys.argv[1]).read_text());x=choice['x'];dest=Path(sys.argv[2]);assert not choice.get('source_post_EQ')
overrides=choice.get('chorus_overrides',{})
def apply_full(c,v):
    apply(c,v)
    for index,value in overrides.items():c.set(3,int(index),int(value))
chorus=len(x)>=94;phase_pair=len(x)==95
native_input=Path(choice.get('source_manifest',{}).get('native_input',str(W/'native-frozen-source-with-tail.wav')))
cc='/workspace/divalead-setup/sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
rows=[];reference=None
for block in [128,512,1024]:
    engine=f'FL20-context-checked-block-{block}.exe'
    defines=['-DCOMMON_PHASE_PAIR'] if phase_pair else []
    subprocess.run([cc,'-O3','-static-libgcc','-Wl,--no-insert-timestamp','-DFL_PRESET_GRAPH',*defines,f'-DBLOCK={block}','-o',str(W/engine),'/tmp/divalead-local-1625/tools/fl_native_fl20_host.c','-lole32','-luuid','-lm'],check=True)
    c=NativeChain(native_input,f'native-block-{block}',fl_graph=True,phase_pair=phase_pair,engine_override=engine)
    try:
        apply_full(c,x)
        if chorus:c.set(3,1,0)
        y,status=c.render()
    finally:c.close()
    if reference is None:reference=y
    error=float(abs(y-reference).max());rows.append(dict(block=block,native_status=status,max_error_from_block128=error,null_RMS=float(np.sqrt(np.mean((y-reference).astype(float)**2)))))
impulse=np.zeros((48000,2),np.float32);impulse[8192]=[.1,.073]
path=W/'native-live-latency-input.wav';sf.write(path,impulse,48000,subtype='FLOAT')
c=NativeChain(path,'native-live-latency-output',fl_graph=True,phase_pair=phase_pair,engine_override='fl_native_fl20_host.exe')
try:apply_full(c,x);y,status=c.render()
finally:c.close()
envelope=abs(y).max(axis=1);nz=np.flatnonzero(envelope>1e-6)
assert len(nz) and nz[0]>=8192
report=dict(block_size_cases=rows,block_size_sample_exact=all(r['max_error_from_block128']==0 for r in rows),block_invariance_within_2e_6=all(r['max_error_from_block128']<=2e-6 for r in rows),input_impulse_frame=8192,output_first_over_1e_6_frame=int(nz[0]),output_peak_frame=int(envelope.argmax()),first_response_delay_frames=int(nz[0]-8192),pre_input_max_abs=float(envelope[:8192].max()),no_pre_input_response=True,native_status=status,declared_effect_PDC_frames=0,old_Finish_PDC_frames=12416,not_a_DAW_or_audio_interface_latency_test=True,FL_GUI_tested=False)
report.update(host_context='Chorus_excluded_from_silent_warmup',chorus_overrides=overrides,block_comparison_Chorus_depth_zero_control=chorus,impulse_used_full_working_Chorus_modulation=chorus,free_running_LFO_audio_not_claimed_block_identical=chorus)
dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
