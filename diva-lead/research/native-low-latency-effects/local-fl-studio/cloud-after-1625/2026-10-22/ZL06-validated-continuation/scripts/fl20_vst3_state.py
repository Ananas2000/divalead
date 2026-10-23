"""FL20 VST3 state container, checked against PyFLP's real FL20 fixtures.

This serializes existing FL records and real plugin component state. It does
not synthesize DSP state. New FL GUI loading remains a separate validation.
"""
import struct

CID='ABCDEF019182FAEB5A6C697545717532'

def windows_uid(hex_uid):
    a,b,c,d=[int(hex_uid[k:k+8],16) for k in range(0,32,8)]
    return struct.pack('<IHH',a,b>>16,b&65535)+struct.pack('>II',c,d)

def decode_records(data,version):
    assert struct.unpack_from('<I',data)[0]==version
    out=[];pos=4
    while pos<len(data):
        assert pos+12<=len(data)
        ident,size=struct.unpack_from('<IQ',data,pos);pos+=12
        assert size<=len(data)-pos
        out.append((ident,data[pos:pos+size]));pos+=size
    return out

def encode_records(records,version):
    return struct.pack('<I',version)+b''.join(struct.pack('<IQ',i,len(b))+b for i,b in records)

def vstpreset(component_state):
    assert component_state
    return b'VST3'+struct.pack('<I',1)+CID.encode('ascii')+struct.pack('<q',48+len(component_state))+component_state+b'List'+struct.pack('<I4sqq',1,b'Comp',48,len(component_state))

def read_vstpreset(data):
    assert data[:4]==b'VST3'and struct.unpack_from('<I',data,4)[0]==1
    assert data[8:40].decode('ascii')==CID
    offset=struct.unpack_from('<q',data,40)[0]
    assert data[offset:offset+4]==b'List'
    count=struct.unpack_from('<I',data,offset+4)[0];assert offset+8+count*20==len(data)
    chunks={}
    for k in range(count):
        ident,start,size=struct.unpack_from('<4sqq',data,offset+8+k*20)
        assert start>=48 and start+size<=offset;chunks[ident]=data[start:start+size]
    assert b'Comp'in chunks
    return chunks[b'Comp']

def wrapper(effect_fixture,vst3_fixture,component_state,marker=10):
    effect=decode_records(effect_fixture,10);vst3=decode_records(vst3_fixture,10)
    real_vst3_payload=next(b for i,b in vst3 if i==53)
    real_inner=decode_records(real_vst3_payload,1)
    assert [i for i,b in real_inner]==[1,3]
    inner=encode_records([(i,component_state if i==3 else b)for i,b in real_inner],1)
    desired={50:next(b for i,b in vst3 if i==50),52:windows_uid(CID),53:inner,
             54:b'ZL Equalizer 2',55:rb'C:\Program Files\Common Files\VST3\ZL Equalizer 2.vst3',56:b'ZL Audio'}
    out=[]
    for i,b in effect:
        if i in [51,57]:continue
        out.append((i,desired.get(i,b)))
        if i==50:out.append((52,desired[52]))
    result=encode_records(out,marker)
    assert component_from_wrapper(result,marker)==component_state
    return result

def component_from_wrapper(state,marker=10):
    records=decode_records(state,marker)
    assert next(b for i,b in records if i==52)==windows_uid(CID)
    payload=next(b for i,b in records if i==53)
    inner=decode_records(payload,1)
    return next(b for i,b in inner if i==3)
