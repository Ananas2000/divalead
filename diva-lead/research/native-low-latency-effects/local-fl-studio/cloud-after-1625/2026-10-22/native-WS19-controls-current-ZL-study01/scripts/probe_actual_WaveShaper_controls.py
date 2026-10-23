"""Measure supplied WaveShaper control ranges and static transfer; no fitting claims."""
from pathlib import Path
import datetime,json
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import curve_bytes
from fl20_curve import apply_candidate
from win_vst3 import D

ROOT=D/'actual-native-WaveShaper-controls-01'
ROOT.mkdir(exist_ok=False)
seed=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text())['native_base']
levels=np.linspace(-.8,.8,65)
block=2048
audio=np.repeat(levels,block)
stereo=np.column_stack([audio,audio]).astype('float32')
src=ROOT/'synthetic-transfer-input.wav'
sf.write(src,stereo,48000,subtype='FLOAT')
c=NativeChain(src,'actual-WaveShaper-control-transfer',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
rows=[]
try:
    apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
    for node in range(1,15):c.bypass(node,True)
    for i,value in enumerate([1,0,1,1,0]):c.gain(i,value)
    c.save_state(0,ROOT/'current-curve-default-controls.bin')
    ranges={str(j):[c.mapped(0,j,m)for m in [0,16384,32768,49152,65536]]for j in range(3)}
    for curve in ['current','identity']:
        state=ROOT/('current-curve-default-controls.bin'if curve=='current'else'identity.bin')
        if curve=='identity':state.write_bytes(curve_bytes(0,0))
        for j in range(3):
            for raw in [0,32,64,96,112,120,124,128,132,136,144,160,192,224,256]:
                c.load_state(0,state)
                c.set(0,j,raw)
                actual=c.value_hint(0,j)
                y,status=c.render()
                plateaus=np.asarray([y[(k+1)*block-512:(k+1)*block].mean(axis=0,dtype=np.float64)for k in range(len(levels))])
                name=f'{curve}-control{j}-raw{raw}'
                rows.append(dict(name=name,curve=curve,control=j,requested_raw=raw,actual_raw=actual,plateaus=plateaus.tolist(),status=status,odd_symmetry_error=float(abs(plateaus+plateaus[::-1]).max())))
                if raw in [0,128,256]:sf.write(ROOT/(name+'.wav'),y,48000,subtype='FLOAT')
            print('CONTROL_TRANSFER_MEASURED',curve,j,flush=True)
    c.bypass(0,True)
    bypassed,_=c.render()
    np.testing.assert_array_equal(bypassed,stereo)
finally:c.close()
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_supplied_native_DLL=True,all_other_nodes_bypassed=True,bypass_input_output_bit_exact=True,synthetic_input_only_no_reference_content=True,midi_to_raw_mapping=ranges,levels=levels.tolist(),rows=rows,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
(ROOT/'ACTUAL_WAVESHAPER_CONTROL_TRANSFERS.json').write_text(json.dumps(report,indent=2)+'\n')
print('WAVESHAPER_CONTROLS_COMPLETE',json.dumps(dict(mapping=ranges,rows=len(rows),output=str(ROOT))),flush=True)
