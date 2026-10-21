"""Small original writer/reader for native-plugin and mixer-insert FL presets.

This serializes FL's event container; all effect payloads MUST come from the
actual native DLL's SaveRestoreState. It does not implement any audio effect.
Format facts were checked against existing FST samples using PyFLP separately.
"""
import struct

def varint(n):
    assert n>=0
    result=bytearray()
    while n>=128:result.append((n&127)|128);n>>=7
    result.append(n);return bytes(result)

def event(identifier,payload):
    assert 0<=identifier<256
    if identifier<192:
        expected=1 if identifier<64 else 2 if identifier<128 else 4
        assert len(payload)==expected
        return bytes([identifier])+payload
    return bytes([identifier])+varint(len(payload))+payload

def text(identifier,value):return event(identifier,(value+'\0').encode('utf-16-le'))
def version():return event(199,b'20.8.4.2576\0')

def container(fmt,payload,channels=1):
    return struct.pack('<4sIh2H4sI',b'FLhd',6,fmt,channels,96,b'FLdt',len(payload))+payload

def wrapper(width=640,height=360):
    # Visible, threaded native effect, hide generic settings; no demo/license bit.
    b=bytearray(52);struct.pack_into('<II',b,4,1,2)
    struct.pack_into('<H',b,16,0x141)
    struct.pack_into('<II',b,44,width,height)
    return event(212,bytes(b))

def plugin_events(internal_name,state,display_name=None):
    return text(201,internal_name)+wrapper()+text(203,display_name or internal_name)+event(213,state)

def plugin_preset(name,state,display_name=None):
    return container(0x30,version()+plugin_events(name,state,display_name))

def insert_preset(label,plugins):
    """plugins = [(internal_name, saved_native_state_bytes, display_label), ...].

    Preset contains no routing, so routing must be set explicitly in FL.
    All slot mixes and faders are unity, pan/separation and built-in EQ neutral.
    """
    assert 1<=len(plugins)<=10
    p=version()+event(159,struct.pack('<I',2576))+event(37,b'\x01')
    p+=text(204,label)+event(236,struct.pack('<III',0,0x4c,0))
    values=[];track=0x2000  # ordinary insert ID0 in exported preset
    for slot in range(10):
        p+=event(98,struct.pack('<H',slot))
        if slot<len(plugins):p+=plugin_events(*plugins[slot])
        values.extend([(0,slot,int(slot<len(plugins))),(1,slot,12800)])
    values.extend((ident,0,val) for ident,val in [
        (192,12800),(193,0),(194,0),(208,0),(209,0),(210,0),
        (216,5777),(217,33145),(218,55825),(224,17500),(225,17500),(226,17500)])
    p+=event(225,b''.join(struct.pack('<IBBHi',0,ident,31,track+slot,val) for ident,slot,val in values))
    return container(0x40,p,18)

def parse(data):
    """Return exact payload bytes, rejecting truncated or inconsistent events."""
    magic,size,fmt,channels,ppq,chunk,n=struct.unpack_from('<4sIh2H4sI',data)
    assert magic==b'FLhd' and size==6 and chunk==b'FLdt' and n==len(data)-22
    i=22;events=[]
    while i<len(data):
        ident=data[i];i+=1
        if ident<192:length=1 if ident<64 else 2 if ident<128 else 4
        else:
            length=0;bits=0
            while True:
                assert i<len(data) and bits<=28
                v=data[i];i+=1;length|=(v&127)<<bits;bits+=7
                if v<128:break
        assert length<=len(data)-i
        events.append((ident,data[i:i+length]));i+=length
    return dict(format=fmt,channels=channels,ppq=ppq,events=events)
