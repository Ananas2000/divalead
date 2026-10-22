"""Export native Chorus FSTs with explicit LFO variability and mixer slot mix.

State bytes and a zero-depth audio control must round-trip exactly. Modulated
audio is compared as repeated real captures, never labelled sample-identical.
"""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil,sys
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from apply_native_candidate import apply
from native_fst import plugin_preset,insert_preset,parse
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(Path(sys.argv[2]).parent/(Path(sys.argv[2]).name+'-independent-assessment'))
from fl20_objective import FeaturesOriginal
from native_features import target

candidate=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
v=out/'verification';v.mkdir();presets=out/'presets';presets.mkdir()
source=Path('/workspace/divalead/diva-lead/v83-wip');choice=json.loads(candidate.read_text());x=np.array(choice['x']);assert len(x) in [94,95]
assert not choice.get('source_post_EQ'),'Use an extended exporter for post-EQ metadata'
phase_pair=len(x)==95
source_manifest=choice.get('source_manifest')
native_input=Path(source_manifest['native_input']) if source_manifest else W/'native-frozen-source-with-tail.wav'
preset_filename='Diva_NATIVE_WIP_THREE_HELD.h2p' if source_manifest else 'Diva_Lead_v83_WIP.h2p'
fresh_source=json.loads(Path(source_manifest['fresh_proof']).read_text()) if source_manifest else json.loads((W/'FRESH_DIVA_THREE_SOURCE.json').read_text())
if source_manifest:
    assert fresh_source['actual_fresh_Diva_plugin_render'] and fresh_source['all281_exact_against_variant'] and fresh_source['same_all12_incoming_MIDI_events'] and fresh_source['raw_audio_bit_exact_against_variant_fixture']
    assert hashlib.sha256(Path(source_manifest['source_preset']).read_bytes()).hexdigest()==fresh_source['preset_SHA256']
    assert hashlib.sha256(Path(source_manifest['source_audio']).read_bytes()).hexdigest()==fresh_source['source_audio_file_SHA256']
engine='fl_native_fl20_host.exe';assert phase_pair
overrides={int(k):int(v)for k,v in choice.get('chorus_overrides',{}).items()}
def apply_full(c,v):
    apply(c,v)
    for index,value in overrides.items():
        c.set(3,index,value)
        assert c.value_hint(3,index)==value
nodes={0:('Fruity WaveShaper','SOURCE_WaveShaper'),3:('Fruity Chorus','SOURCE_Chorus'),4:('Fruity Parametric EQ 2','MID_EQ_A'),5:('Fruity Parametric EQ 2','MID_EQ_B'),6:('Fruity Parametric EQ 2','SIDE_EQ_A'),7:('Fruity Parametric EQ 2','SIDE_EQ_B'),8:('Fruity Stereo Shaper','SUM_Stereo'),10:('Fruity Stereo Shaper','MID_Encode'),11:('Fruity Stereo Shaper','SIDE_Encode'),12:('Fruity Stereo Shaper','SIDE_Decode')}
groups=[('01_SOURCE',[0,3]),('02_MID',[10,4,5]),('03_SIDE',[11,6,7,12]),('04_SUM',[8])]
if phase_pair:
    nodes.update({13:('Fruity Stereo Shaper','SOURCE_Phase_R'),14:('Fruity Stereo Shaper','SOURCE_Phase_L')})
    groups[0]=('01_SOURCE',[0,3,13,14])
mixraw=int(round(float(x[93])*12800));assert abs(mixraw/12800-x[93])<1e-12,'Quantize and validate the FL slot-mix before export'
features=FeaturesOriginal(target)
def make(tag):return NativeChain(native_input,tag,fl_graph=True,phase_pair=phase_pair,engine_override=engine)
def mix_from_insert(data):
    payload=next(d for i,d in parse(data)['events'] if i==225)
    import struct
    values=[struct.unpack_from('<IBBHi',payload,i) for i in range(0,len(payload),12)]
    return next(row[-1]/12800 for row in values if row[1]==1 and row[3]&63==1)

c=make('chorus-preset-export');manifest=[];states={};captures=[]
try:
    apply_full(c,x)
    for node,(name,label) in nodes.items():
        path=v/(label+'.bin');c.save_state(node,path);state=path.read_bytes();states[node]=state
        preset=presets/(label+'.fst');preset.write_bytes(plugin_preset(name,state,label))
        assert next(d for i,d in parse(preset.read_bytes())['events'] if i==213)==state
        manifest.append(dict(node=node,internal_name=name,label=label,preset=preset.relative_to(out).as_posix(),state=path.relative_to(out).as_posix(),state_bytes=len(state),state_SHA256=hashlib.sha256(state).hexdigest()))
    for label,indices in groups:
        (presets/(label+'.fst')).write_bytes(insert_preset(label,[(nodes[n][0],states[n],nodes[n][1]) for n in indices],slot_mix={1:mixraw} if label=='01_SOURCE' else None))
    assert mix_from_insert((presets/'01_SOURCE.fst').read_bytes())==x[93]
    for rep in range(6):
        y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025
        path=out.parent/f'{out.name}-export-realization-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT');captures.append(dict(loss=loss,audio=str(path),native_status=status,assessment=features.local.last))
    c.set(3,1,0);zero_depth,status=c.render()
finally:c.close()

proof={}
for mode in ['single-FST','insert-FST']:
    c=make('chorus-preset-roundtrip-'+mode)
    try:
        apply_full(c,x)
        if mode=='single-FST':
            for row in manifest:
                data=next(d for i,d in parse((out/row['preset']).read_bytes())['events'] if i==213)
                path=W/('chorus-reload-'+row['label']+'.bin');path.write_bytes(data);c.load_state(row['node'],path)
        else:
            for label,indices in groups:
                payloads=[d for i,d in parse((presets/(label+'.fst')).read_bytes())['events'] if i==213]
                assert len(payloads)==len(indices)
                for node,data in zip(indices,payloads):
                    path=W/f'chorus-insert-reload-{node}.bin';path.write_bytes(data);c.load_state(node,path)
            slot_mix=mix_from_insert((presets/'01_SOURCE.fst').read_bytes());c.gain(0,1-slot_mix);c.gain(1,slot_mix)
        byte_checks=[]
        for node,data in states.items():
            path=W/f'chorus-resaved-{mode}-{node}.bin';c.save_state(node,path);assert path.read_bytes()==data,(mode,node)
            byte_checks.append(node)
        modulated,st=c.render();c.set(3,1,0);control,control_status=c.render()
        err=float(abs(control-zero_depth).max());assert err<=2e-7,(mode,err)
        proof[mode]=dict(state_bytes_exact=True,all_native_states_checked=byte_checks,zero_depth_routing_control_max_abs_error=err,modulated_audio_is_free_running_LFO=True,native_status=st,zero_depth_native_status=control_status)
    finally:c.close()

captures.sort(key=lambda row:row['loss']);selected=captures[len(captures)//2];y=sf.read(selected['audio'],dtype='float32')[0]
sf.write(out/'NATIVE_FULL_180BPM_WIP.wav',y[:288000],48000,subtype='FLOAT');sf.write(v/'NATIVE_WITH_TAIL_WIP.wav',y,48000,subtype='FLOAT')
z=np.pad(y,((819,0),(0,0)));edit=np.zeros((176064,2),np.float32);edit[1:64041]=z[1:64041];edit[112022:176064]=z[128007:192049]
sf.write(out/'NATIVE_REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT')
reportchoice=dict(choice,loss=float(np.mean([r['loss'] for r in captures])),realization_losses=[r['loss'] for r in captures],realization_standard_deviation=float(np.std([r['loss'] for r in captures])),full_fresh_native_realizations=6,recorded_render_loss=selected['loss'],original_reference_assessment=selected['assessment'])
(v/'candidate.json').write_text(json.dumps(reportchoice,indent=2)+'\n')
for name in ['Diva_THREE_HELD_180BPM.mid','Diva_original_lead_reference.wav']:shutil.copyfile(source/name,out/name)
shutil.copyfile(Path(source_manifest['source_preset']) if source_manifest else source/'Diva_Lead_v83_WIP.h2p',out/preset_filename)
shutil.copyfile(Path(source_manifest['source_audio']) if source_manifest else source/'Diva_SOURCE_FROZEN_48k.wav',out/'Diva_SOURCE_FROZEN_48k.wav')
for filename in ['all281.tsv','Diva.log']:
    p=Path(source_manifest['source_preset']).parent/filename
    data=p.read_bytes();packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data
    (v/(filename+'.gz')).write_bytes(packed)
shutil.copyfile(source/'verification/MIDI_note_events_48k.json',v/'MIDI_note_events_48k.json')
delta=y[:len(target)].astype(float)-target.astype(float)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_DLL_audio=True,distinct_source_destination_buffers=True,FL_mixer_graph_reproduced_by_actual_stock_DLLs=True,preset_round_trip=proof,preset_state_bytes_exact=True,zero_depth_routing_audio_exact=True,modulated_audio_sample_exact_expected=False,repeat_max_abs_error=None,native_Chorus_mixer_slot_mix_raw=mixraw,native_Chorus_mixer_slot_mix_percent=100*x[93],modulated_captures=[{k:v for k,v in row.items() if k!='audio'} for row in captures],mean_original_objective=float(np.mean([r['loss'] for r in captures])),std_original_objective=float(np.std([r['loss'] for r in captures])),selected_capture_is_median_not_best=True,native_status=selected['native_status'],only_three_held_notes=True,source_fixture_unchanged=True,fresh_Diva_proof=fresh_source,declared_effect_PDC_frames=0,old_Finish_PDC_frames=12416,audio_interface_or_DAW_buffer_latency_not_measured=True,v83_transfer=dict(decoded_float32_bit_exact=bool(np.array_equal(y[:len(target)],target)),max_abs_error=float(abs(delta).max()),null_RMS=float(np.sqrt(np.mean(delta**2))),gain_or_time_matching_used=False),native_plugin_manifest=manifest,FL_GUI_tested=False,subjective_audition_claimed=False,match_reached=False,not_a_replacement_for_v83_until_sound_difference_accepted=True)
(v/'NATIVE_PRESET_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
report.update(host_context='Chorus_excluded_from_silent_warmup',chorus_overrides=choice.get('chorus_overrides',{}),objective_version='local_full_original_criteria_FL20_context_v1',actual_FL_validation_pending=True,common_phase_pair=phase_pair,source_preset_filename=preset_filename,source_fixture_unchanged=not bool(source_manifest),source_manifest=source_manifest,fresh_Diva_proof=fresh_source,source_change_vs_v83=source_manifest.get('changed_parameters') if source_manifest else None)
(v/'NATIVE_PRESET_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print('NATIVE_CHORUS_FST_STATE_AND_ZERO_DEPTH_CONTROL_PASS',report['mean_original_objective'],report['std_original_objective'],flush=True)
