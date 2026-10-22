"""Change explicit saved FLP fields; retain MIDI, VST chunk, routing and FX shell."""
from pathlib import Path
import argparse,struct,json,hashlib
import cloud_native_fst as f
root=Path(__file__).resolve().parent.parent;session=root/'sessions/2026-10-22'
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--volume',type=int,required=True);p.add_argument('--eq-directory');a=p.parse_args()
assert 0<=a.volume<=12800 and Path(a.name).name==a.name and a.name.endswith('.flp')
base=session/'Diva_NATIVE_LOCAL_01_WIP.flp';parsed=f.parse(base.read_bytes());ev=parsed['events'];native_index=-13;channel=-1;out=[];changes=[]
state_map={5:'MID_EQ_A',6:'MID_EQ_B',8:'SIDE_EQ_A',9:'SIDE_EQ_B',11:'SUM_Stereo'}
native_total=sum(i==213 for i,b in ev);assert native_total==13
seen=0
for ident,data in ev:
    if ident==64:channel=struct.unpack('<H',data)[0]
    if ident==219 and channel==1:
        old=struct.unpack_from('<I',data,4)[0];b=bytearray(data);struct.pack_into('<I',b,4,a.volume);data=bytes(b);changes.append(dict(channel_volume_before=old,after=a.volume))
    if ident==213:
        index=seen-1;seen+=1
        if a.eq_directory and index in state_map:
            name=state_map[index];data=(root/a.eq_directory/(name+'.bin')).read_bytes();changes.append(dict(native_index=index,state=name,sha256=hashlib.sha256(data).hexdigest()))
    out.append(f.event(ident,data))
dest=session/a.name;dest.write_bytes(f.container(parsed['format'],b''.join(out),parsed['channels']));dest.with_suffix('.changes.json').write_text(json.dumps(dict(base=base.name,file=dest.name,changes=changes),indent=2),encoding='utf-8');print(str(dest))
