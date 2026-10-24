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

_FL20_INSERT_SHELL = {
    199: bytes.fromhex('32302e302e332e35333200'),
    159: bytes.fromhex('14020000'),
    28: bytes.fromhex('03'),
    37: bytes.fromhex('01'),
    236: bytes.fromhex('000000004c00000000000000'),
    212: bytes.fromhex('01000000010000000200000000000000400100000000000000000000000000000000000000000000000000008002000068010000'),
    155: bytes.fromhex('00000000'),
    128: bytes.fromhex('48515600'),
    225: bytes.fromhex('00000000001f40200100000000000000011f40200032000000000000001f41200100000000000000011f41203b13000000000000001f42200100000000000000011f42200032000000000000001f43200100000000000000011f43200032000000000000001f44200000000000000000011f44200032000000000000001f45200000000000000000011f45200032000000000000001f46200000000000000000011f46200032000000000000001f47200000000000000000011f47200032000000000000001f48200000000000000000011f48200032000000000000001f49200000000000000000011f49200032000000000000c01f40200032000000000000c11f40200000000000000000c21f40200000000000000000d01f40200000000000000000d11f40200000000000000000d21f40200000000000000000d81f40209116000000000000d91f40207981000000000000da1f402011da000000000000e01f40205c44000000000000e11f40205c44000000000000e21f40205c440000'),
}

def insert_preset(label,plugins,slot_mix=None):
    """Native mixer FST using the verified real FL Studio20.0.3 slot shell.

    Event98 terminates each slot. Wrapper DWORD at offset4 is its zero-based
    slot index. All DSP payloads stay verbatim. Routing is not in this preset.
    """
    assert 1<=len(plugins)<=10
    slot_mix=slot_mix or {}
    assert all(0<=int(k)<len(plugins) and 0<=int(v)<=12800 for k,v in slot_mix.items())
    shell=_FL20_INSERT_SHELL;controls=bytearray(shell[225])
    for offset in range(0,len(controls),12):
        _,ident,kind,track,value=struct.unpack_from('<IBBHi',controls,offset)
        slot=track&63
        if ident==0:value=int(slot<len(plugins))
        elif ident==1:value=int(slot_mix.get(slot,12800))
        struct.pack_into('<i',controls,offset+8,value)
    p=b''.join(event(i,shell[i]) for i in [199,159,28,37])+text(204,label)+event(236,shell[236])
    for slot in range(10):
        if slot<len(plugins):
            internal,state,_=plugins[slot];wrapper_data=bytearray(shell[212]);struct.pack_into('<I',wrapper_data,4,slot)
            p+=text(201,internal)+event(212,bytes(wrapper_data))+event(155,shell[155])+event(128,shell[128])+event(213,state)
        p+=event(98,struct.pack('<H',slot))
    p+=event(225,bytes(controls))
    return container(0x40,p,2)

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
