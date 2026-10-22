"""Read the actual saved FLP: six notes, routing, native state and slot mix."""
from pathlib import Path
import hashlib, json, struct, sys
import cloud_native_fst as f
root=Path(__file__).resolve().parent.parent
session=root/'sessions/2026-10-22'
path=Path(sys.argv[1]) if len(sys.argv)>1 else session/'Diva_NATIVE_LOCAL_01_WIP.flp'
data=path.read_bytes();p=f.parse(data);ev=p['events']
states=[b for i,b in ev if i==213]
wanted=[]
for name in ('01_SOURCE','02_MID','03_SIDE','04_SUM'):
    wanted += [b for i,b in f.parse((session/'input/presets'/(name+'.fst')).read_bytes())['events'] if i==213]
native=states[-12:]
routes=[b for i,b in ev if i==235]
notes=[]
for i,b in ev:
    if i!=224:continue
    assert len(b)%24==0
    for o in range(0,len(b),24):
        pos,flags,ch,length,key,group,*rest=struct.unpack_from('<IHHIHH8B',b,o)
        notes.append(dict(position_ticks=pos,channel=ch,length_ticks=length,key=key,velocity=rest[5],pan=rest[4]))
params={}
for i,b in ev:
    if i==225:
        for o in range(0,len(b),12):
            zero,ident,kind,track,value=struct.unpack_from('<IBBHi',b,o)
            if kind==31:params[(track>>6)&127,track&63,ident]=value
track_params=[]
for idx in range(1,5):
    track_params.append(dict(insert=idx,enabled=[params.get((idx,s,0)) for s in range(10)],mix=[params.get((idx,s,1)) for s in range(10)],volume=params.get((idx,0,192)),pan=params.get((idx,0,193)),stereo_separation=params.get((idx,0,194))))
route_report=[]
for idx,b in enumerate(routes[:5]):
    enabled=[j for j,v in enumerate(b) if v]
    levels={j:params.get((idx,0,64+j),12800) for j in enabled}
    route_report.append(dict(insert=idx,enabled_flags=enabled,send_levels=levels,audible_destinations=[j for j in enabled if levels[j]!=0]))
report=dict(file=path.name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),ppq=p['ppq'],tempo_bpm=struct.unpack('<I',next(b for i,b in ev if i==156))[0]/1000,notes=notes,native_payloads_exact=[a==b for a,b in zip(native,wanted)],routes=route_report,mixer=track_params)
out=path.with_suffix('.verification.json');out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
