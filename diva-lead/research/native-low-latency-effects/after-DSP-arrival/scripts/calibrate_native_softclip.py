"""Inspect actual Soft Clipper knob units without assuming VST scales."""
from pathlib import Path
import json
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-post-softclip-units-01';ROOT.mkdir(exist_ok=False)
rows=[]
with four_native_slots(ROOT) as state:
    seed=json.loads(Path(state['best_candidate']).read_text())
    c=NativeChain(Path(seed['source_manifest']['native_input']),ROOT.name,fl_graph=True,phase_pair=True)
    try:
        apply(c,seed['x'])
        for index in [0,1]:
            default=c.value_hint(9,index)
            rows.append(dict(parameter=index,default_raw=default))
            for value in [0,8192,16384,24576,32768,40960,49152,57344,65536]:
                raw=c.mapped(9,index,value);rows.append(dict(parameter=index,MIDI_scaled=value,actual_native_raw=raw))
            c.set(9,index,default)
    finally:c.close()
    (ROOT/'MAPPING.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'actual-native-units.log').write_bytes(c.logpath.read_bytes())
print('NATIVE_SOFTCLIP_UNITS',json.dumps(rows),flush=True)
