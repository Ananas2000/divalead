"""Preserve FL20 FruityWrapper records while replacing an actual VST chunk.

The program bytes must come from the real plugin's effGetChunk. This module
does not synthesize a plugin chunk, parameter table, or any audio.
"""
import struct
def records(state):
    assert state[:4]==struct.pack('<i',8);offset=4;result=[]
    while offset<len(state):
        assert offset+12<=len(state)
        ident,size=struct.unpack_from('<iQ',state,offset);offset+=12
        assert size<=len(state)-offset
        result.append((ident,state[offset:offset+size]));offset+=size
    return result
def envelope(payload):
    assert len(payload)>=21
    assert struct.unpack_from('<i',payload)[0]==-9 and payload[4]==13
    assert struct.unpack_from('<i',payload,5)[0]==-2 and payload[13:21]==bytes(8)
    size=struct.unpack_from('<I',payload,9)[0];assert size==len(payload)-21
    return payload[:21],payload[21:]
def program_chunk(state):
    payloads=[b for ident,b in records(state)if ident==53];assert len(payloads)==1
    return envelope(payloads[0])[1]
def replace_program_chunk(state,actual_plugin_chunk):
    assert actual_plugin_chunk and len(actual_plugin_chunk)<2**32
    out=bytearray(state[:4]);seen=0
    for ident,data in records(state):
        if ident==53:
            header,_=envelope(data);header=bytearray(header)
            struct.pack_into('<I',header,9,len(actual_plugin_chunk));data=bytes(header)+actual_plugin_chunk;seen+=1
        out+=struct.pack('<iQ',ident,len(data))+data
    assert seen==1
    result=bytes(out);assert program_chunk(result)==actual_plugin_chunk
    assert [(i,b)for i,b in records(result)if i!=53]==[(i,b)for i,b in records(state)if i!=53]
    return result
