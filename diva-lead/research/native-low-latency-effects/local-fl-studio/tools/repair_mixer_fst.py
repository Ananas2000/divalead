"""Repair cloud mixer presets against a real FL Studio 20.0.3 export.

Native DSP state bytes remain unchanged. Event 98 terminates a slot block.
"""
from pathlib import Path
import json
import struct
import cloud_native_fst as f

root = Path(__file__).resolve().parent.parent
session = root / 'sessions/2026-10-22'
source = session / 'input/presets'
dest = session / 'compatible-presets'
dest.mkdir(exist_ok=True)
reference = f.parse((session / 'GUI_TWO_EFFECTS_REFERENCE.fst').read_bytes())
ref_events = dict(reference['events'])
wrapper = ref_events[212]
report = []
for name in ('01_SOURCE', '02_MID', '03_SIDE', '04_SUM'):
    parsed = f.parse((source / (name + '.fst')).read_bytes())
    ev = parsed['events']
    plugins = []
    for i, (ident, data) in enumerate(ev):
        if ident == 201:
            state = next(b for j, b in ev[i+1:] if j == 213)
            plugins.append((data, state))
    controls = bytearray(ref_events[225])
    for offset in range(0, len(controls), 12):
        _, ident, _, track, value = struct.unpack_from('<IBBHi', controls, offset)
        slot = track & 63
        if ident == 0:
            value = int(slot < len(plugins))
        elif ident == 1:
            value = 4923 if name == '01_SOURCE' and slot == 1 else 12800
        struct.pack_into('<i', controls, offset + 8, value)
    payload = f.event(199, ref_events[199]) + f.event(159, ref_events[159])
    payload += f.event(28, ref_events[28]) + f.event(37, ref_events[37])
    payload += f.text(204, name) + f.event(236, ref_events[236])
    for slot in range(10):
        if slot < len(plugins):
            internal, state = plugins[slot]
            slot_wrapper = bytearray(wrapper)
            struct.pack_into('<I', slot_wrapper, 4, slot)
            payload += f.event(201, internal) + f.event(212, bytes(slot_wrapper))
            payload += f.event(155, ref_events[155]) + f.event(128, ref_events[128])
            payload += f.event(213, state)
        payload += f.event(98, struct.pack('<H', slot))
    payload += f.event(225, bytes(controls))
    result = f.container(64, payload, channels=2)
    (dest / (name + '.fst')).write_bytes(result)
    check = f.parse(result)
    assert [b for i,b in check['events'] if i == 213] == [b for _,b in plugins]
    report.append({'file':name+'.fst', 'plugins':[a.decode('utf-16-le').rstrip('\0') for a,_ in plugins], 'native_payloads_preserved':True})
(dest / 'REPAIR_VERIFICATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
