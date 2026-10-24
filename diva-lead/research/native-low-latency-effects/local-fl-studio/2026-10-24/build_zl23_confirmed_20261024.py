"""Embed the existing cloud-confirmed component in the working FL20 project."""
from pathlib import Path
import struct,json,hashlib
import cloud_native_fst as f
R=Path(__file__).resolve().parent.parent;S=R/'sessions/2026-10-24';U=S/'ZL23_upstream/FL20_ZL_23_WIP'
old=(U/'verification/ZL_component.bin').read_bytes();new=(S/'ZL23_CONFIRMED_INPUT.bin').read_bytes()
def patch(payload):
    assert payload.count(old)==1
    o=4;out=payload[:4];changed=0
    while o<len(payload):
        ident,n=struct.unpack_from('<iQ',payload,o);o+=12;v=payload[o:o+n];o+=n
        if ident==53:
            assert v.endswith(old);header=v[:-len(old)]
            assert struct.unpack_from('<Q',header,len(header)-8)[0]==len(old)
            v=header[:-8]+struct.pack('<Q',len(new))+new;changed+=1
        out+=struct.pack('<iQ',ident,len(v))+v
    assert changed==1 and o==len(payload);return out
def build(src,dest):
    p=f.parse(src.read_bytes());events=[];count=0
    for ident,v in p['events']:
        if ident==213 and old in v:v=patch(v);count+=1
        events.append(f.event(ident,v))
    assert count==1
    dest.write_bytes(f.container(p['format'],b''.join(events),p['channels']))
    check=f.parse(dest.read_bytes());assert sum(new in b for i,b in check['events']if i==213)==1
build(U/'Diva_ZL_23_WIP.flp',S/'Diva_ZL23_CONFIRMED_LOCAL.flp')
build(U/'presets/SUM_ZL_23_WIP.fst',S/'SUM_ZL23_CONFIRMED_LOCAL.fst')
report=dict(source_commit='05150a2a8e990b65e0c58c00cfc487689e34bde5',source_cloud_confirmed_component_sha256=hashlib.sha256(new).hexdigest(),only_component_changed=True,all_native_states_and_Diva_and_notes_unchanged=True,new_search_candidate=False,actual_FL26_validation_pending=True)
(S/'CONFIRMED_LOCAL_BUILD.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
