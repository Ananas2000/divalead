"""Assemble the fully proved v58 and a separately labelled three-held-note trial."""
from pathlib import Path
import sys,json,copy,shutil,subprocess,struct,ctypes,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_architectures as m
import numpy as np,soundfile as sf
ROOT=m.ROOT/'finalists';choice=json.loads((ROOT/'selected.json').read_text())
A=Path(choice['analysis']);S=A.parent;report=json.loads((S/'validation.json').read_text())
D=m.REPO/'diva-lead/v58-wip';assert not D.exists()
shutil.copytree(A,D/'analysis');(D/'verification').mkdir()
T=m.ROOT/'release-build';T.mkdir(exist_ok=False)
timing=json.loads((ROOT/'performance-selection.json').read_text())['timing']
cfg=json.loads((A/'spectral_model.json').read_text())
candidate=json.loads((D/'analysis/selected_candidate.json').read_text())
candidate['source_render_history']=report['source_render_history']
candidate['settings']=timing;m.write(D/'analysis/selected_candidate.json',candidate)
for src,dst in [(ROOT/'source.h2p','Diva_Lead_v58_WIP.h2p'),(ROOT/'raw-selected-Diva.wav','Diva_SOURCE_FROZEN_48k.wav'),(S/'new-source-before-actual.wav','verification/Before_Spectral.wav'),(S/'NEW-independent-base-pdc.wav','verification/NEW_independent_base.wav'),(S/'actual-Windows.wav','verification/Selected_WITH_PDC.wav'),(S/'REFERENCE_EDIT_WIP.wav','verification/Selected_REFERENCE_EDIT.wav'),(ROOT/'fresh-0.tsv','verification/Diva_all281.tsv'),(ROOT/'fresh-0.log','verification/Diva_source_render.log'),(S/'Diva_Lead_Finish_v58_WIP_x64.dll','Diva_Lead_Finish_v58_WIP_x64.dll'),(m.V/'Diva_original_lead_reference.wav','Diva_original_lead_reference.wav'),(m.V/'verification/guard_limits.json','verification/guard_limits.json'),(S/'NEW-independent-base.json','verification/NEW_prebase_rebuild.json')]:
    shutil.copyfile(src,D/dst)
m.write(D/'verification/selected_validation.json',report)
proof=dict(validation='verification/selected_validation.json',score=report['score'],original11_and_fixed_extra_crest_guards_passed=True,crest_RMS_dB=report['crest_RMS_dB'],crest_cap_dB=m.CAP,only_MIDI_velocity_changes=True,preset_unchanged57=True,match_reached=False)
m.write(D/'verification/selected_proof.json',proof)
m.write(D/'verification/HF_selection_proof.json',json.loads((ROOT/'HF-selection-proof.json').read_text()))
m.write(D/'render_timing_180BPM.json',timing)
m.write(D/'Finish_settings.json',dict(Amount=1,Output_dB=candidate['effect_parameters'][40],spectral_model=cfg,effect_ID='0x444c3538',match_reached=False))
events=json.loads((ROOT/'MIDI-events.json').read_text())
def vlq(n):
    parts=[n&127];n>>=7
    while n:parts.append(128|(n&127));n>>=7
    return bytes(reversed(parts))
def midi(path,notes):
    track=bytearray(b'\x00\xff\x51\x03'+(333333).to_bytes(3,'big')+b'\x00\xff\x58\x04\x04\x02\x18\x08');previous=0
    for frame,status,pitch,velocity in notes:
        track+=vlq(frame-previous)+bytes([status,pitch,velocity]);previous=frame
    track+=b'\x00\xff\x2f\x00'
    path.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,16000)+b'MTrk'+struct.pack('>I',len(track))+track)
midi(D/'Diva_PERFORMANCE_180BPM.mid',events)
m.write(D/'verification/MIDI_note_events_48k.json',dict(tempo_BPM=180,division_ticks_per_beat=16000,events=[dict(zip(['frame','status','pitch','velocity'],e)) for e in events],DAW_import_may_quantize=True))
fxp=bytearray((m.V/'Diva_Lead_Finish_v57_WIP.fxp').read_bytes());assert len(fxp)==76
assert int.from_bytes(fxp[16:20],'big')==int.from_bytes(fxp[64:68],'little')==0x444c3537
fxp[16:20]=(0x444c3538).to_bytes(4,'big');fxp[64:68]=(0x444c3538).to_bytes(4,'little')
(D/'Diva_Lead_Finish_v58_WIP.fxp').write_bytes(bytes(fxp).replace(b'v57',b'v58'))
for file in ['verify_release.py','vst_program_probe.c']:
    p=D/'analysis'/file;p.write_text(p.read_text().replace('v57','v58').replace('V57','V58').replace('0x444c3537','0x444c3538'))
ref=sf.read(D/'Diva_original_lead_reference.wav')[0];gap=np.zeros((24000,2))
def level(edit):return edit*np.sqrt(np.mean(ref*ref)/np.mean(edit*edit))
edit=sf.read(D/'verification/Selected_REFERENCE_EDIT.wav')[0]
sf.write(D/'AB_REFERENCE_V58_WIP.wav',np.concatenate([ref,gap,level(edit)]),48000,subtype='PCM_24')
decoded=sf.read(D/'AB_REFERENCE_V58_WIP.wav')[0]
sf.write(D/'Diva_Lead_v58_REFERENCE_EDIT.wav',decoded[200064:],48000,subtype='PCM_24')
v57=sf.read(m.V/'Diva_Lead_v57_REFERENCE_EDIT.wav')[0]
sf.write(D/'AB_REFERENCE_V57_V58_WIP.wav',np.concatenate([ref,gap,v57,gap,decoded[200064:]]),48000,subtype='PCM_24')
def windows_render(rawfile,output,block=512,log=None):
    with (log or output.with_suffix('.log')).open('w') as f:
        subprocess.run([m.WINE,str(m.B/'fl-v57-build/fx_render_host.exe'),m.win(D/'Diva_Lead_Finish_v58_WIP_x64.dll'),m.win(rawfile),m.win(output),str(block)],env=m.env,stdout=f,stderr=f,check=True,timeout=150)
raw=sf.read(D/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32')[0]
padded=np.pad(raw,((0,12416),(0,0)));padded_path=T/'source-plus-tail.wav';sf.write(padded_path,padded,48000,subtype='FLOAT')
full_path=T/'Windows-with-tail.wav';windows_render(padded_path,full_path)
full=sf.read(full_path,dtype='float32')[0]
np.testing.assert_allclose(full[:len(raw)],sf.read(D/'verification/Selected_WITH_PDC.wav',dtype='float32')[0],rtol=0,atol=2e-7)
sf.write(D/'Diva_Lead_v58_FULL_180BPM.wav',full[12416:12416+len(raw)],48000,subtype='FLOAT')
block_checks=[]
for block in [47,127,2048]:
    path=T/('block-'+str(block)+'.wav');windows_render(padded_path,path,block)
    error=float(np.max(abs(full-sf.read(path,dtype='float32')[0])));assert error<2e-7
    block_checks.append(dict(block_size=block,Windows_max_error=error))
lib=ctypes.CDLL(str(S/'native_finish.so'));lib.native_render.argtypes=m.LIB.native_render.argtypes
native=np.zeros_like(padded);assert lib.native_render(padded.ctypes.data,native.ctypes.data,len(padded),48000)
np.testing.assert_allclose(full,native,rtol=0,atol=2e-7)
# Best held-note source is a separately marked comparison, rendered through
# the same final v58 effect. It was screened with v57; do not reuse that score.
Q=D/'THREE_HELD_RESEARCH';Q.mkdir()
held=m.ROOT/'arp-refinement/best-three-arp'
held_selection=json.loads((held/'selection.json').read_text())
shutil.copyfile(held/'source.h2p',Q/'Diva_THREE_HELD_RESEARCH.h2p')
held_dump=Q/'Diva_all281.tsv';held_raw=Q/'Diva_THREE_HELD_SOURCE_48k.wav'
cmd=m.commands('three-arp',m.TIMING,held_raw,held_dump,held_selection['root_velocities'])
(Q/'Diva_commands.txt').write_text(cmd)
with (Q/'Diva_source_render.log').open('w') as log:
    subprocess.run([m.WINE,str(m.HOST),m.win(m.PLUGIN),m.win(Q/'Diva_THREE_HELD_RESEARCH.h2p')],input=cmd,text=True,env=m.env,stdout=log,stderr=log,check=True,timeout=90)
held_audio=sf.read(held_raw,dtype='float32')[0]
np.testing.assert_array_equal(held_audio,sf.read(held/'raw-Diva.wav',dtype='float32')[0])
assert held_dump.read_bytes()==(held/'all281.tsv').read_bytes()
held_events=[list(map(int,line.split()[1:])) for line in (Q/'Diva_source_render.log').read_text().splitlines() if line.startswith('NOTE ')]
assert len(held_events)==12 and [e[2] for e in held_events if e[1]==144]==[41,37,36]*2
midi(Q/'Diva_THREE_HELD_180BPM.mid',held_events);m.write(Q/'MIDI_events_48k.json',held_events)
held_pad=np.pad(held_audio,((0,12416),(0,0)));hp=T/'held-plus-tail.wav';sf.write(hp,held_pad,48000,subtype='FLOAT')
ho=T/'held-Windows-with-tail.wav';windows_render(hp,ho)
ha=sf.read(ho,dtype='float32')[0];hn=np.zeros_like(held_pad);assert lib.native_render(held_pad.ctypes.data,hn.ctypes.data,len(hn),48000)
np.testing.assert_allclose(ha,hn,rtol=0,atol=2e-7)
sf.write(Q/'Diva_THREE_HELD_FULL_180BPM.wav',ha[12416:12416+len(held_audio)],48000,subtype='FLOAT')
he=m.common.h.edit_aligned(m.common.h.align_with_pdc(ha[:len(held_audio)].astype('float64'),m.TIMING,latency=12416))
hefile=Q/'Diva_THREE_HELD_REFERENCE_EDIT.wav';sf.write(hefile,he,48000,subtype='FLOAT')
m.common.WORK=ROOT;hr=m.common.score(dict(id='three-held-final-v58',canonical_path=str(hefile),aliases=[]))
hr['score']=sum(m.common.WEIGHTS[k]*hr['metrics'][k]/m.SCALES[k] for k in m.common.WEIGHTS)
hr.update(incoming_notes_per_phrase=3,note_on_count=6,effect='same v58 DLL',Windows_native_max_error=float(np.max(abs(ha-hn))),fresh_Diva_raw_and_all281_equal_screened_source=True,independent_NEW_for_this_three_note_control_rebuilt=False,better_than_v58=False,match_reached=False)
m.write(Q/'verification.json',hr);m.write(Q/'source_selection.json',held_selection)
sf.write(D/'AB_REFERENCE_V58_THREE_HELD_WIP.wav',np.concatenate([ref,gap,decoded[200064:],gap,level(he)]),48000,subtype='PCM_24')
# The saved research edit is level matched globally, like the corresponding A/B.
sf.write(hefile,level(he),48000,subtype='PCM_24')
source_manifest=dict(source_preset='Diva_Lead_v58_WIP.h2p',source_WAV='Diva_SOURCE_FROZEN_48k.wav',before_spectral_WAV='verification/Before_Spectral.wav',NEW_independent_base='verification/NEW_independent_base.wav',source_updates=report['source_updates'],source_updates_relative57={},source_render_history=report['source_render_history'],source_host_C='analysis/diva_source_render_host.c',source_host_C_SHA256=hashlib.sha256((D/'analysis/diva_source_render_host.c').read_bytes()).hexdigest(),spectral_model_SHA256=hashlib.sha256((D/'analysis/spectral_model.json').read_bytes()).hexdigest(),before_latency_frames=8320,total_latency_frames=12416,only_MIDI_velocity_changes_relative57=True,match_reached=False)
for key in ['source_preset','source_WAV','before_spectral_WAV','NEW_independent_base']:
    source_manifest[key+'_SHA256']=hashlib.sha256((D/source_manifest[key]).read_bytes()).hexdigest()
m.write(D/'source_manifest.json',source_manifest)
checks=dict(effect_ID='0x444c3538',default_Amount=1,default_Output_dB=candidate['effect_parameters'][40],PDC_frames_48k=12416,full_processed_frames=288000,Windows_native_with_tail_max_error=float(np.max(abs(full-native))),block_size_checks=block_checks,own_NEW_rebuilt_for_changed_MIDI=True,fresh_Diva_twice_exact=True,three_note_control_fresh_Diva_and_Windows_verified=True,baseline_v57_score=report['baseline_v57_score'],v58_score=report['score'],three_note_same_v58_DSP_score=hr['score'],FL_Studio_GUI_tested=False,match_reached=False)
m.write(D/'verification/release_build_checks.json',checks)
compiler=str(m.SETUP/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
probe=T/'vst_program_probe.exe';subprocess.run([compiler,'-O2','-static-libgcc','-I',str(D/'analysis'),str(D/'analysis/vst_program_probe.c'),'-lm','-o',str(probe)],check=True,timeout=120)
with (D/'verification/Windows_VST_program_probe.json').open('w') as f:
    subprocess.run([m.WINE,str(probe),m.win(D/'Diva_Lead_Finish_v58_WIP_x64.dll'),m.win(T/'defaults.chunk'),m.win(D/'Diva_Lead_Finish_v58_WIP.fxp')],env=m.env,stdout=f,check=True,timeout=120)
print('V58_PACKAGE_AUDIO_API_BLOCKS_COMPLETE',json.dumps(checks),flush=True)
