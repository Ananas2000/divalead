"""Build a complete three-held-note FL package from a fully proved candidate."""
from pathlib import Path
import os,sys,json,re,hashlib,shutil,subprocess,ctypes
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');OLD=REPO/'diva-lead/v71-wip'
S=Path(sys.argv[1]);report=json.loads((S/'validation.json').read_text());A=S/'analysis'
assert report['all_chosen_three_guards_passed'] and report['original_three_held_MIDI_events_unchanged']
family=report.get('source_family','original-user-selected-three');changes=report.get('changed_source_fields',{})
assert (family=='PulseWidth51.90' and changes=={'OSC:PW':51.90}) or (family=='original-user-selected-three' and not changes)
BASE=ROOT/('source-pw5190-basis' if family=='PulseWidth51.90' else 'baseline')
assert report['Windows_native_max_error']<2e-7 and report['full_NEW_SOURCE_independent_max_error']<3e-7 and report['spectral_fixture_max_error']<2e-7
T=Path('/tmp/divalead-v72-build');T.mkdir(exist_ok=False);D=T/'v72-wip';shutil.copytree(OLD,D)
shutil.rmtree(D/'verification');(D/'verification').mkdir();shutil.rmtree(D/'analysis');shutil.copytree(A,D/'analysis')
for p in list(D.iterdir()):
 if not p.is_file():continue
 if p.name.startswith('AB_') or p.name in ['Diva_PERFORMANCE_180BPM.mid','SHA256SUMS.txt']:p.unlink();continue
 if 'v71' in p.name:p.rename(p.with_name(p.name.replace('v71','v72')))
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def win(p):return 'Z:'+str(p).replace('/','\\')
setup=Path('/workspace/divalead-setup');wine=str(setup/'sysroot/usr/lib/wine/wine64');compiler=str(setup/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
env=os.environ.copy();env.update(WINEPREFIX=str(setup/'wine2'),WINEDLLPATH=str(setup/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(setup/'cache'))
cfg=json.loads((A/'spectral_model.json').read_text());candidate=json.loads((A/'selected_candidate.json').read_text());candidate['stage']='v72 three-held WIP; checked source family '+family+'; source changes '+str(changes);write(D/'analysis/selected_candidate.json',candidate)
code=D/'analysis/lead_finish.c';text=code.read_text();assert text.count('0x444c3538')==1;code.write_text(text.replace('0x444c3538','0x444c3732').replace('v58 WIP','v72 WIP'))
p=D/'analysis/vst_program_probe.c';p.write_text(p.read_text().replace('0x444c3538','0x444c3732').replace('v58 WIP','v72 WIP'))
for name in ['verify_release.py','replay_source.py']:
 p=D/'analysis'/name;p.write_text((OLD/'analysis'/name).read_text().replace('v71','v72').replace('V71','V72'))
for src,dst in [(report['source_preset'],'Diva_Lead_v72_WIP.h2p'),(report['new_source_raw'],'Diva_SOURCE_FROZEN_48k.wav'),(report['new_source_before_fixture'],'verification/Before_Spectral.wav'),(report['NEW_independent_prebase'],'verification/NEW_independent_base.wav'),(S/'actual-Windows.wav','verification/Selected_WITH_PDC.wav'),(S/'REFERENCE_EDIT_WIP.wav','verification/Selected_REFERENCE_EDIT.wav'),(S/'Diva_all281.tsv','verification/Diva_all281.tsv'),(S/'Diva.log','verification/Diva_source_render.log'),(S/'arbitrary-input-verification.json','verification/arbitrary_input_verification.json'),(OLD/'Diva_THREE_HELD_180BPM.mid','Diva_THREE_HELD_180BPM.mid')]:shutil.copyfile(src,D/dst)
events=json.loads((BASE/'MIDI_events_48k.json').read_text());assert len(events)==12 and sum(e[1]==144 for e in events)==6
write(D/'verification/MIDI_note_events_48k.json',dict(tempo_BPM=180,division_ticks_per_beat=16000,events=[dict(zip(['frame','status','pitch','velocity'],e)) for e in events],note_on_count=6,incoming_notes_per_phrase=3))
baseline=json.loads((ROOT/'baseline/validation.json').read_text());limits=dict(anchor='User-selected v58 THREE_HELD_RESEARCH',chosen_three_absolute_limits={k:baseline['metrics'][k]*v for k,v in report['guard_limits'].items()},chosen_three_relative_limits=report['guard_limits'],fixed_crest_RMS_dB=report['crest_cap_dB'],old_sixteen_caps_used=False)
write(D/'verification/guard_limits.json',limits);write(D/'verification/selected_validation.json',report);write(D/'verification/user_selected_baseline.json',baseline)
write(D/'verification/selected_proof.json',dict(all_chosen_three_guards_passed=True,crest_RMS_dB=report['crest_RMS_dB'],crest_cap_dB=report['crest_cap_dB'],preset_unchanged=not bool(changes),six_input_notes_unchanged=True,only_Diva_source_change=changes,match_reached=False))
write(D/'render_timing_180BPM.json',dict(tempo_BPM=180,sample_rate=48000,pattern_notes=3,pitches=[41,37,36],durations_beats=[1.5,1.5,1],root_velocities=[96,96,101],repeat_beats=8,repetitions=2,alignment_frames=819,incoming_note_on_count=6))
write(D/'Finish_settings.json',dict(Amount=1,Output_dB=candidate['effect_parameters'][40],spectral_model=cfg,effect_ID='0x444c3732',match_reached=False))
fxp=bytearray((OLD/'Diva_Lead_Finish_v71_WIP.fxp').read_bytes());assert len(fxp)==76;fxp[16:20]=(0x444c3732).to_bytes(4,'big');fxp[64:68]=(0x444c3732).to_bytes(4,'little');(D/'Diva_Lead_Finish_v72_WIP.fxp').write_bytes(bytes(fxp).replace(b'v71',b'v72'))
dll=D/'Diva_Lead_Finish_v72_WIP_x64.dll';subprocess.run([compiler,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp','-Wl,--image-base,0x372720000','-o',str(dll),str(code),'-lm'],check=True)
subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(T/'native_finish.so'),str(D/'analysis/native_finish.c'),'-lm'],check=True)
lib=ctypes.CDLL(str(T/'native_finish.so'));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
raw,rate=sf.read(D/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32');assert rate==48000;np.testing.assert_array_equal(raw,sf.read(BASE/'Diva_source.wav',dtype='float32')[0])
padded=np.pad(raw,((0,12416),(0,0)));inputpath=T/'source-plus-tail.wav';sf.write(inputpath,padded,48000,subtype='FLOAT')
def render(output,block):
 with output.with_suffix('.log').open('w') as log:subprocess.run([wine,'/workspace/divalead-work/fl-v57-build/fx_render_host.exe',win(dll),win(inputpath),win(output),str(block)],env=env,stdout=log,stderr=log,check=True,timeout=150)
fullpath=T/'Windows-with-tail.wav';render(fullpath,512);full=sf.read(fullpath,dtype='float32')[0];previous=sf.read(S/'actual-Windows.wav',dtype='float32')[0];np.testing.assert_allclose(full[:len(raw)],previous,rtol=0,atol=2e-7)
native=np.zeros_like(padded);assert lib.native_render(padded.ctypes.data,native.ctypes.data,len(padded),48000);np.testing.assert_allclose(full,native,rtol=0,atol=2e-7)
sf.write(D/'Diva_Lead_v72_FULL_180BPM.wav',full[12416:12416+len(raw)],48000,subtype='FLOAT')
blocks=[]
for block in [47,127,2048]:
 path=T/('block-'+str(block)+'.wav');render(path,block);error=float(np.max(abs(full-sf.read(path,dtype='float32')[0])));assert error<2e-7;blocks.append(dict(block_size=block,max_error=error))
ref=sf.read(D/'Diva_original_lead_reference.wav')[0];edit=sf.read(S/'REFERENCE_EDIT_WIP.wav')[0];gain=np.sqrt(np.mean(ref*ref)/np.mean(edit*edit));gap=np.zeros((24000,2))
sf.write(D/'AB_REFERENCE_V72_WIP.wav',np.concatenate([ref,gap,edit*gain]),48000,subtype='PCM_24');pair=sf.read(D/'AB_REFERENCE_V72_WIP.wav')[0];sf.write(D/'Diva_Lead_v72_REFERENCE_EDIT.wav',pair[200064:],48000,subtype='PCM_24')
chosen=sf.read(OLD/'Diva_Lead_v71_REFERENCE_EDIT.wav')[0];sf.write(D/'Diva_PREVIOUS_V71_REFERENCE_EDIT.wav',chosen,48000,subtype='PCM_24')
sf.write(D/'AB_REFERENCE_V71_V72_WIP.wav',np.concatenate([ref,gap,chosen,gap,pair[200064:]]),48000,subtype='PCM_24')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(D/'AB_REFERENCE_V71_V72_WIP.wav'),'-codec:a','libmp3lame','-b:a','320k',str(D/'AB_REFERENCE_V71_V72_WIP.mp3')],check=True)
manifest=dict(source_preset='Diva_Lead_v72_WIP.h2p',source_WAV='Diva_SOURCE_FROZEN_48k.wav',before_spectral_WAV='verification/Before_Spectral.wav',NEW_independent_base='verification/NEW_independent_base.wav',source_render_history=report['source_render_history'],source_family=family,changed_source_fields=changes,source_host_C='analysis/diva_source_render_host.c',source_host_C_SHA256=hashlib.sha256((D/'analysis/diva_source_render_host.c').read_bytes()).hexdigest(),spectral_model_SHA256=hashlib.sha256((D/'analysis/spectral_model.json').read_bytes()).hexdigest(),before_latency_frames=8320,total_latency_frames=12416,incoming_notes_per_phrase=3,incoming_note_on_count=6,user_chose_three_by_ear=True,match_reached=False)
for key in ['source_preset','source_WAV','before_spectral_WAV','NEW_independent_base']:manifest[key+'_SHA256']=hashlib.sha256((D/manifest[key]).read_bytes()).hexdigest()
write(D/'source_manifest.json',manifest)
probe=T/'vst_program_probe.exe';subprocess.run([compiler,'-O2','-static-libgcc','-I',str(D/'analysis'),str(D/'analysis/vst_program_probe.c'),'-o',str(probe),'-lm'],check=True)
with (D/'verification/Windows_VST_program_probe.json').open('w') as log:subprocess.run([wine,str(probe),win(dll),win(T/'defaults.chunk'),win(D/'Diva_Lead_Finish_v72_WIP.fxp')],env=env,stdout=log,check=True,timeout=120)
write(D/'verification/release_build_checks.json',dict(release_ID='0x444c3732',image_base='0x372720000',incoming_notes_per_phrase=3,note_on_count=6,Diva_ARP='On',Diva_preset_bytes_equal_user_selected_three=not bool(changes),Diva_MIDI_bytes_equal_user_selected_three=True,only_Diva_parameter_change=changes,Windows_native_max_error=float(np.max(abs(full-native))),released_DLL_matches_selected_waveform_max_error=float(np.max(abs(full[:len(raw)]-previous))),block_checks=blocks,PDC_frames_48k=12416,FL_GUI_tested=False,match_reached=False))
print('V72_THREE_NOTE_BINARY_AUDIO_PACKAGE_BUILT',D,flush=True)
