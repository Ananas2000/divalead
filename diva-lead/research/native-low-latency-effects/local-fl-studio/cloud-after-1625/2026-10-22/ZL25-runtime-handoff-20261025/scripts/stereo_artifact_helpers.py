"""Change only the primary VST3 state in already-validated two-ZL FL artifacts."""
import struct
from native_fst import parse,event,container
from fl20_vst3_state import decode_records,encode_records,component_from_wrapper
def replace_primary(data,old,new):
 p=parse(data);events=[];count=0
 for ident,b in p['events']:
  if ident==213 and old in b:
   marker=struct.unpack_from('<I',b)[0];outer=decode_records(b,marker);out=[]
   for key,payload in outer:
    if key==53:
     inner=decode_records(payload,1);assert sum(i==3 and value==old for i,value in inner)==1
     payload=encode_records([(i,new if i==3 else value)for i,value in inner],1)
    out.append((key,payload))
   b=encode_records(out,marker);assert component_from_wrapper(b,marker)==new;count+=1
  events.append((ident,b))
 assert count==1
 result=container(p['format'],b''.join(event(i,b)for i,b in events),p['channels']);q=parse(result)
 assert[b for i,b in p['events']if i in [224,235]]==[b for i,b in q['events']if i in [224,235]]
 before=[b for i,b in p['events']if i==213];after=[b for i,b in q['events']if i==213];assert len(before)==len(after)
 assert sum(a!=b for a,b in zip(before,after))==1
 return result
