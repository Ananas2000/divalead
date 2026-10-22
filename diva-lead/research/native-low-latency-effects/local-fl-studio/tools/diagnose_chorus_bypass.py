"""Build a diagnostic FLP with only Chorus bypassed; leave the source unchanged."""
from pathlib import Path
import struct,json,sys
import cloud_native_fst as f
ROOT=Path(__file__).resolve().parent.parent;S=ROOT/'sessions/2026-10-22'
src=S/'Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp';p=f.parse(src.read_bytes());out=[];changes=0
for i,b in p['events']:
    if i==225:
        b=bytearray(b)
        for o in range(0,len(b),12):
            _,ident,kind,track,value=struct.unpack_from('<IBBHi',b,o)
            if kind==31 and (track>>6)&127==1 and track&63==1 and ident==0:
                struct.pack_into('<i',b,o+8,0);changes+=1
        b=bytes(b)
    out.append(f.event(i,b))
assert changes==1
dest=S/'Diva_NATIVE_DIAG_NO_CHORUS.flp';dest.write_bytes(f.container(p['format'],b''.join(out),p['channels']))
sys.path.insert(0,str(ROOT/'tools/native-host'))
from local_native_chain import NativeChain
c=NativeChain(S/'renders/DIVA_FRESH_DIRECT.wav','DIAG_OFFLINE_NO_CHORUS');c.checkpoint();c.gain(0,1);c.gain(1,0);c.bypass(3,True);_,status=c.render();c.close()
print(json.dumps(dict(project=dest.name,change='Chorus slot bypass only',native=status,not_promoted=True)))
