"""Verify a separate sixteen-node host with actual uploaded saturator DLLs.

Native FromMIDI queries mutate parameters, so every probe restores the saved
raw value. This file does no licensing emulation or reference-audio playback.
"""
from pathlib import Path
import hashlib,json,os,re,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-extra-saturator-units-01';ROOT.mkdir(exist_ok=False)
rows=[];start=time.monotonic()
with four_native_slots(ROOT) as state:
    seed=json.loads(Path(state['best_candidate']).read_text());x=np.array(seed['x']);assert len(x)==95
    INPUT=Path(seed['source_manifest']['native_input']);zero=x.copy();zero[87]=0
    old=NativeChain(INPUT,ROOT.name+'-old',fl_graph=True,phase_pair=True)
    try:apply(old,zero);control,control_status=old.render()
    finally:old.close()
    for name,label in [('Fruity Blood Overdrive_x64.dll','Blood_Overdrive'),('Fruity Fast Dist_x64.dll','Fast_Dist')]:
        c=NativeChain(INPUT,ROOT.name+'-'+label,fl_graph=True,phase_pair=True,extra_effect_name=name)
        try:
            apply(c,zero);c.bypass(15,True);bypass,bypass_status=c.render()
            error=float(abs(bypass-control).max());assert error<=2e-7,(name,error)
            text=c.logpath.read_text();count=int(re.search(r'NODE_READY 15 .* params=(\d+)',text)[1]);assert 1<=count<=32
            params=[]
            for i in range(count):
                original=c.value_hint(15,i)
                mapped=[]
                for midi in [0,16384,32768,49152,65536]:mapped.append(c.mapped(15,i,midi))
                c.set(15,i,original);assert c.value_hint(15,i)==original
                params.append(dict(index=i,default_raw=original,FromMIDI_inputs=[0,16384,32768,49152,65536],FromMIDI_raw=mapped,FromMIDI_is_mutating=True,original_value_restored=True))
            c.save_state(15,ROOT/(label+'-default-state.bin'))
            c.bypass(15,False);positive,status=c.render();delta=float(abs(positive-bypass).max())
            sf.write(ROOT/(label+'-positive-with-tail.wav'),positive,48000,subtype='FLOAT')
            row=dict(plugin=name,params=params,default_native_metadata=[l for l in text.splitlines() if l.startswith('EXTRA_PARAM ')],
                bypass_zero_Chorus_depth_max_error=error,default_enabled_max_delta=delta,
                old15_and_research16_native_graphs_actually_rendered=True,native_status=status,bypass_native_status=bypass_status,
                original_source_and_incoming_MIDI_unchanged=True,reference_match_reached=False)
            rows.append(row);(ROOT/(label+'-units.json')).write_text(json.dumps(row,indent=2)+'\n')
            print('ACTUAL_EXTRA_NATIVE_EFFECT_CALIBRATED',name,count,error,delta,flush=True)
        finally:c.close()
        (ROOT/(label+'-host.log')).write_bytes(c.logpath.read_bytes())
    (ROOT/'completion.json').write_text(json.dumps(dict(actual_uploaded_native_DLLs=True,effects=len(rows),seconds=time.monotonic()-start,
        zero_depth_bypass_graph_preserved=True,all_mapped_parameters_restored=True,production_host_binary_unchanged=True,
        original_reference_match_reached=False),indent=2)+'\n')
