"""Package actual native states plus the official zero-latency ZL VST3 WIP."""
from pathlib import Path
import csv,gzip,hashlib,json,os,shutil,struct,subprocess,zipfile
import numpy as np
import soundfile as sf
from native_fst import parse,event,container,text
from fl20_curve import apply_candidate
from native_chain import NativeChain
from fl20_diva_wrapper import program_chunk
from fl20_vst3_state import wrapper,component_from_wrapper,vstpreset,read_vstpreset,decode_records,encode_records
from win_vst3 import D,WinVST3

B=D.parent;BASE=B/'FL20_NATIVE_17_WIP';ROOT=B/'FL20_ZL_13_WIP';LABEL='Diva_ZL_13_WIP'
STUDY=D/'ZL-auto-export-input-13';root_source=Path('/tmp/divalead-native-effects/pyflp-source/tests/assets/plugins')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(B/'ZL13-export-assessment')
from fl20_objective import FeaturesOriginal
f=FeaturesOriginal()
def read(p):return json.loads(Path(p).read_text())
choice=read(STUDY/'candidate-research-only.json');seed=choice['native_base'];assert choice['robust_improvement_over_allpass']
BASE=Path(choice.get('native_base_export_directory',str(BASE)))
assert BASE.is_dir()and(BASE/'Diva_NATIVE_17_WIP.flp').is_file()
assert not ROOT.exists();shutil.copytree(BASE,ROOT)
for p in ROOT.glob('*.mp3'):p.unlink()
old=ROOT/'Diva_NATIVE_17_WIP.flp';old.rename(ROOT/(LABEL+'.flp'))
for name in ['README_RU.md','FL_STUDIO_RU.md','SHA256SUMS.txt']: (ROOT/name).unlink()
v=ROOT/'verification';presets=ROOT/'presets'
(v/'candidate.json').rename(v/'native-base-candidate.json')
(v/'NATIVE_PRESET_VERIFICATION.json').rename(v/'NATIVE_BASE_PRESET_VERIFICATION.json')
shutil.copyfile(seed['source_manifest']['native_input'],v/'NATIVE_SOURCE_WITH_TAIL.wav')
component=Path(choice['native_ZL_component_state']).read_bytes()
(v/'ZL_component.bin').write_bytes(component)
(presets/'ZL_13_WIP.vstpreset').write_bytes(vstpreset(component))
assert read_vstpreset((presets/'ZL_13_WIP.vstpreset').read_bytes())==component
raw=(STUDY/'ZL_joint_parameters.tsv').read_text();(v/'ZL_parameters.tsv').write_text('\n'.join(line+'\"\"'if line.endswith('\t')else line for line in raw.splitlines())+'\n')
shutil.copyfile(D/'OFFICIAL_DOWNLOADS.json',v/'OFFICIAL_DOWNLOADS.json')
shutil.copyfile(D/'ZL-allpass-original-reference-01/REAL_VST3_HOST_AUDIT.json',v/'REAL_VST3_HOST_AUDIT.json')
shutil.copyfile(STUDY/'completion.json',v/'ZL_JOINT_completion.json');shutil.copyfile(STUDY/'CANONICAL_COMPONENT_REPLAY_PROOF.json',v/'ZL_CANONICAL_COMPONENT_REPLAY_PROOF.json')
effect=parse((root_source/'xfer-djmfilter.fst').read_bytes());synth=parse((root_source/'fruity-wrapper.fst').read_bytes())
effect_state=next(b for i,b in effect['events']if i==213);synth_state=next(b for i,b in synth['events']if i==213)
assert encode_records(decode_records(effect_state,10),10)==effect_state
assert encode_records(decode_records(synth_state,10),10)==synth_state
state10=wrapper(effect_state,synth_state,component,10);state8=wrapper(effect_state,synth_state,component,8)
shell=next(b for i,b in effect['events']if i==212)
def plugin_events(track,slot,state):
    b=bytearray(shell);struct.pack_into('<II',b,0,track,slot);struct.pack_into('<II',b,44,1000,700)
    return [(201,('Fruity Wrapper\0').encode('utf-16-le')),(212,bytes(b)),(203,('ZL 13 WIP\0').encode('utf-16-le')),
        (155,bytes(4)),(128,b'HQV\0'),(213,state)]
fst=container(0x30,event(199,b'20.8.4.2576\0')+b''.join(event(i,b)for i,b in plugin_events(0,0,state10)))
(presets/'SUM_ZL_13_WIP.fst').write_bytes(fst)

def add_sum_slot(data,is_project):
    p=parse(data);events=p['events'];out=[];armed=False;inserted=False;changed=[]
    if is_project:
        sum_index=max(k for k,(i,b)in enumerate(events)if i==204 and b.decode('utf-16-le').rstrip('\0')=='04_SUM')
    else:sum_index=-1
    for k,(i,b)in enumerate(events):
        if k==sum_index:armed=True
        if not is_project:armed=True
        if armed and not inserted and i==98 and b==struct.pack('<H',1):
            out.extend(plugin_events(4 if is_project else 1,1,state8 if is_project else state10));inserted=True
        if i==225:
            a=bytearray(b)
            for off in range(0,len(a),12):
                _,param,kind,track,value=struct.unpack_from('<IBBHi',a,off)
                if kind==31 and (track&63)==1 and ((track>>6)&127)==(4 if is_project else 1) and param in [0,1]:
                    new=1 if param==0 else 12800
                    if value!=new:changed.append(dict(param=param,track=track,before=value,after=new))
                    struct.pack_into('<i',a,off+8,new)
            b=bytes(a)
        out.append((i,b))
    assert inserted and any(r['param']==0 for r in changed),changed
    result=container(p['format'],b''.join(event(i,b)for i,b in out),p['channels'])
    q=parse(result)
    assert [b for i,b in events if i in [224,235]]==[b for i,b in q['events']if i in [224,235]]
    oldstates=[b for i,b in events if i==213];newstates=[b for i,b in q['events']if i==213]
    assert newstates[:-1]==oldstates and component_from_wrapper(newstates[-1],8 if is_project else 10)==component
    return result,changed

flp=ROOT/(LABEL+'.flp');original=flp.read_bytes();data,controls=add_sum_slot(original,True);flp.write_bytes(data)
sumfile=presets/'04_SUM.fst';data,sum_controls=add_sum_slot(sumfile.read_bytes(),False);sumfile.write_bytes(data)
source_state=next(b for i,b in parse(flp.read_bytes())['events']if i==213)
assert program_chunk(source_state)==(v/'Diva_VST_chunk.bin').read_bytes()
manifest=read(v/'NATIVE_BASE_PRESET_VERIFICATION.json')['native_plugin_manifest']
c=NativeChain(v/'NATIVE_SOURCE_WITH_TAIL.wav','ZL13-export-actual-native',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
z=WinVST3('ZL13-export-actual-VST3');rows=[]
try:
    apply_candidate(c,np.array(seed['x']),seed)
    for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
    for row in manifest:c.load_state(row['node'],ROOT/row['state'])
    z.load(v/'ZL_component.bin')
    for rep in range(6):
        raw,status=c.render();y,zstatus=z.render(raw);r=f.residual(y[:288000]);loss=float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
        path=D/f'ZL13-export-capture-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT')
        rows.append(dict(loss=loss,path=str(path),assessment=f.local.last,native_status=status,VST3_status=zstatus))
    assert z.latency()==0
    impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];response,_=z.render(impulse)
    nz=np.flatnonzero(np.max(abs(response),axis=1)>1e-9);assert nz[0]==4096 and not np.any(response[:4096])
    impulse_proof=dict(declared_PDC_frames=0,first_response_delay_frames=0,peak_delay_frames=int(np.max(abs(response),axis=1).argmax())-4096,pre_input_audio_zero=True)
finally:c.close();z.close()
median=sorted(rows,key=lambda r:r['loss'])[3];audio=sf.read(median['path'],dtype='float32')[0]
sf.write(ROOT/'NATIVE_FULL_180BPM_WIP.wav',audio[:288000],48000,subtype='FLOAT');sf.write(v/'NATIVE_WITH_TAIL_WIP.wav',audio,48000,subtype='FLOAT')
aligned=np.pad(audio,((819,0),(0,0)));edit=np.zeros((176064,2),np.float32)
edit[1:64041]=aligned[1:64041];edit[112022:176064]=aligned[128007:192049]
sf.write(ROOT/'NATIVE_REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT')
ref=sf.read(ROOT/'Diva_original_lead_reference.wav',dtype='float64')[0]
rms=lambda y:float(np.sqrt(np.mean(y*y)))
gain=rms(ref)/rms(edit);ab=np.concatenate([ref,np.zeros((24000,2)),edit*gain]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
working=D/'ZL13_AB-working.wav';sf.write(working,ab,48000,subtype='FLOAT')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(working),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_REFERENCE_ZL13_WIP.mp3')],check=True)
working.unlink()
(v/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','ZL13 WIP'],starts_seconds=[0,4.168],candidate_RMS_gain=gain,common_peak_safety_gain=safety,only_AB_level_normalized=True),indent=2)+'\n')
report=dict(version='ZL13',only_three_held_notes_per_phrase=True,new_effect='official ZL Equalizer 2 v1.4.1 Windows x64 VST3',
    full_native_graph_and_actual_VST3_rendered=True,mean_original_objective=float(np.mean([r['loss']for r in rows])),std_original_objective=float(np.std([r['loss']for r in rows])),
    fresh_full_captures=rows,chosen_capture_is_median=True,all12_native_states_preserved=True,native_plugin_manifest=manifest,
    real_VST3_component_state_in_project_and_two_FSTs=True,VST3_state_format_based_on_real_FL2084_fixture=True,
    six_held_note_blocks_unchanged=True,all_existing_routes_unchanged=True,changed_mixer_controls=controls,SUM_FST_controls=sum_controls,
    ZL_dynamic_bands=choice['ZL_dynamic_bands'],ZL_impulse=impulse_proof,actual_FL_GUI_validation_pending=True,reference_match_reached=False,old_high_latency_Finish_not_used=True,
    base_native_report='NATIVE_BASE_PRESET_VERIFICATION.json',old_FLp_integration_report_scope='FLP_VERIFICATION.json describes preserved native base before adding new SUM slot')
(v/'ZL_FULL_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
result=dict(choice,loss=report['mean_original_objective'],recorded_audio=str(ROOT/'NATIVE_FULL_180BPM_WIP.wav'),exported_project=str(flp),
    topology='FL20 native 12 effects followed by actual ZL Equalizer 2 on SUM slot2',not_compatible_with_standard_x95_exporter=True,
    use_extended_ZL_exporter_and_replay=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(v/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
print('ACTUAL_FULL_ZL13_FLP_FST_VSTPRESET_EXPORT_PASS',report['mean_original_objective'],flush=True)
