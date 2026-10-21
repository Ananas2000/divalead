"""Export real native states and FSTs, then render them in a fresh DLL host.

This verifies preset bytes and native-DSP round trips, NOT FL Studio GUI loading
and NOT equality with v83 or the original recording.
"""
from pathlib import Path
import datetime,hashlib,json,shutil,sys
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from apply_native_candidate import apply
from native_fst import plugin_preset,insert_preset,parse

candidate=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
v=out/'verification';v.mkdir();presets=out/'presets';presets.mkdir()
source=Path('/workspace/divalead/diva-lead/v83-wip')
x=json.loads(candidate.read_text())['x']
nodes={0:('Fruity WaveShaper','SOURCE_WaveShaper'),4:('Fruity Parametric EQ 2','MID_EQ_A'),5:('Fruity Parametric EQ 2','MID_EQ_B'),6:('Fruity Parametric EQ 2','SIDE_EQ_A'),7:('Fruity Parametric EQ 2','SIDE_EQ_B'),8:('Fruity Stereo Shaper','SUM_Stereo'),10:('Fruity Stereo Shaper','MID_Encode'),11:('Fruity Stereo Shaper','SIDE_Encode'),12:('Fruity Stereo Shaper','SIDE_Decode')}
groups=[('01_SOURCE',[0]),('02_MID',[10,4,5]),('03_SIDE',[11,6,7,12]),('04_SUM',[8])]
def configure(c):
 for n in [1,2,3,9]:c.bypass(n,True)
 for i,value in enumerate([1,0,1,1,1]):c.gain(i,value)

c=NativeChain(W/'native-frozen-source-with-tail.wav','checkpoint-export',fl_graph=True)
try:
 apply(c,x);y,status=c.render();repeat,_=c.render();repeat_error=float(abs(y-repeat).max());assert repeat_error<=2e-7
 states={};manifest=[]
 for node,(name,label) in nodes.items():
  state=v/(label+'.bin');c.save_state(node,state);b=state.read_bytes();states[node]=b
  path=presets/(label+'.fst');path.write_bytes(plugin_preset(name,b,label))
  parsed=parse(path.read_bytes());payload=[d for i,d in parsed['events'] if i==213];assert payload==[b]
  manifest.append(dict(node=node,internal_name=name,label=label,preset=path.relative_to(out).as_posix(),state=state.relative_to(out).as_posix(),state_SHA256=hashlib.sha256(b).hexdigest(),state_bytes=len(b)))
 for label,indices in groups:
  (presets/(label+'.fst')).write_bytes(insert_preset(label,[(nodes[n][0],states[n],nodes[n][1]) for n in indices]))
finally:c.close()

proof={}
for mode in ['single-FST','insert-FST']:
 c=NativeChain(W/'native-frozen-source-with-tail.wav','checkpoint-roundtrip-'+mode,fl_graph=True)
 try:
  configure(c)
  if mode=='single-FST':
   for row in manifest:
    state=next(d for i,d in parse((out/row['preset']).read_bytes())['events'] if i==213)
    path=W/('reload-'+row['label']+'.bin');path.write_bytes(state);c.load_state(row['node'],path)
  else:
   for label,indices in groups:
    states=[d for i,d in parse((presets/(label+'.fst')).read_bytes())['events'] if i==213]
    assert len(states)==len(indices)
    for node,b in zip(indices,states):
     path=W/f'reload-insert-{node}.bin';path.write_bytes(b);c.load_state(node,path)
  actual,st=c.render();error=float(abs(actual-y).max());assert error<=2e-7,(mode,error)
  proof[mode]=dict(max_abs_error=error,native_status=st,fresh_native_instances=True)
 finally:c.close()

sf.write(out/'NATIVE_FULL_180BPM_WIP.wav',y[:288000],48000,subtype='FLOAT')
sf.write(v/'NATIVE_WITH_TAIL_WIP.wav',y,48000,subtype='FLOAT')
z=np.pad(y,((819,0),(0,0)));edit=np.zeros((176064,2),np.float32);edit[1:64041]=z[1:64041];edit[112022:176064]=z[128007:192049]
sf.write(out/'NATIVE_REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT')
shutil.copyfile(candidate,v/'candidate.json')
for name in ['Diva_Lead_v83_WIP.h2p','Diva_THREE_HELD_180BPM.mid','Diva_SOURCE_FROZEN_48k.wav','Diva_original_lead_reference.wav']:
 shutil.copyfile(source/name,out/name)
target=sf.read(source/'Diva_Lead_v83_FULL_180BPM.wav',dtype='float32')[0]
error=y[:len(target)].astype(float)-target.astype(float)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_DLL_audio=True,distinct_source_destination_buffers=True,FL_mixer_graph_reproduced_by_actual_stock_DLLs=True,preset_round_trip=proof,repeat_max_abs_error=repeat_error,native_status=status,only_three_held_notes=True,source_fixture_unchanged=True,fresh_Diva_proof=json.loads((W/'FRESH_DIVA_THREE_SOURCE.json').read_text()),declared_effect_PDC_frames=0,old_Finish_PDC_frames=12416,audio_interface_or_DAW_buffer_latency_not_measured=True,v83_transfer=dict(decoded_float32_bit_exact=bool(np.array_equal(y[:len(target)],target)),max_abs_error=float(abs(error).max()),null_RMS=float(np.sqrt(np.mean(error**2))),gain_or_time_matching_used=False),native_plugin_manifest=manifest,FL_GUI_tested=False,subjective_audition_claimed=False,match_reached=False,not_a_replacement_for_v83_until_sound_difference_accepted=True)
(v/'NATIVE_PRESET_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
