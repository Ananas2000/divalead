"""Change one human-readable Diva value inside its saved FLP VST state."""
from pathlib import Path
import json,hashlib,struct
import cloud_native_fst as f
ROOT=Path(__file__).resolve().parent.parent;S=ROOT/'sessions/2026-10-22'
src=S/'Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp';p=f.parse(src.read_bytes());out=[];seen=0
for i,b in p['events']:
    if i==213 and seen==0:
        assert b.count(b'ModDpt=-68.00')==1
        b=b.replace(b'ModDpt=-68.00',b'ModDpt=-58.00')
        o=4
        while o<len(b):
            ident,n=struct.unpack_from('<iQ',b,o);o+=12;v=b[o:o+n];o+=n
            if ident==53:
                j=v.index(b'/*@Meta');preset=v[j:].rstrip(b'\0')
                (S/'Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.h2p').write_bytes(preset)
        assert o==len(b)
    if i==213:seen+=1
    out.append(f.event(i,b))
dest=S/'Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.flp';dest.write_bytes(f.container(p['format'],b''.join(out),p['channels']))
assert len(src.read_bytes())==dest.stat().st_size
report=dict(base=src.name,file=dest.name,change=dict(parameter_index=171,name='VCA1: ModDepth',before=-68,after=-58,normalized=.21),channel_volume_raw=11148,other_native_states_preserved=True,actual_FL_validation_pending=True,match_reached=False,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
dest.with_suffix('.changes.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
