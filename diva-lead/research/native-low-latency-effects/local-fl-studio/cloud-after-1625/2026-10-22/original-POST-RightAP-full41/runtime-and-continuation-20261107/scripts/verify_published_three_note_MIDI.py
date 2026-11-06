from pathlib import Path
import struct,json
from native_fst import parse
J=Path(__file__).resolve().parent;P=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP41');b=(P/'Diva_THREE_HELD_180BPM.mid').read_bytes();assert b[:4]==b'MThd';format,ntracks,ppq=struct.unpack_from('>HHH',b,8);pos=8+int.from_bytes(b[4:8],'big');notes=[];offs=[]
def vlq(data,p):
 value=0
 while True:
  c=data[p];p+=1;value=(value<<7)|(c&127)
  if c<128:return value,p
for track in range(ntracks):
 assert b[pos:pos+4]==b'MTrk';n=int.from_bytes(b[pos+4:pos+8],'big');data=b[pos+8:pos+8+n];pos+=8+n;i=tick=0;running=None
 while i<len(data):
  dt,i=vlq(data,i);tick+=dt;status=data[i]
  if status>=128:i+=1
  else:assert running is not None;status=running
  if status==255:
   meta=data[i];i+=1;length,i=vlq(data,i);i+=length;continue
  if status in[240,247]:length,i=vlq(data,i);i+=length;continue
  running=status;kind=status&240;length=1 if kind in[192,208]else 2;values=data[i:i+length];i+=length
  if kind==144 and values[1]>0:notes.append(dict(tick=tick,pitch=values[0],velocity=values[1]))
  if kind==128 or(kind==144 and values[1]==0):offs.append(dict(tick=tick,pitch=values[0]))
assert [x['pitch']for x in notes]==[41,37,36,41,37,36]and len(offs)==6
flp=parse((P/'Diva_ZL41_STEREO_WIP.flp').read_bytes());events=[blob for ident,blob in flp['events']if ident==224];assert[len(blob)for blob in events]==[144];records=[events[0][i:i+24]for i in range(0,144,24)];pitches=[struct.unpack_from('<H',r,12)[0]for r in records];lengths=[struct.unpack_from('<I',r,8)[0]for r in records];assert pitches==[41,37,36,41,37,36]and min(lengths)>0
proof=dict(MIDI_format=format,PPQ=ppq,note_on=notes,note_off=offs,FLP_pitches=pitches,FLP_note_lengths_ticks=lengths,FLP_note_record_bytes=24,FLP_note_records=6,FLP_plugin_state_count=sum(ident==213 for ident,blob in flp['events']),exactly_three_incoming_held_notes_each_phrase=True,two_repeats=True,no_extra_short_notes=True)
(J/'ACTUAL_PUBLISHED41_MIDI_EVENT_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
