"""Freeze the user's preferred three-held-note source and prove its own NEW base."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,ctypes,shutil
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,soundfile as sf
REPO=Path('/workspace/divalead');BASE=Path('/workspace/divalead-work');ROOT=Path(__file__).resolve().parent
P=REPO/'diva-lead/research/repository-selection';R=REPO/'diva-lead/v58-wip';Q=R/'THREE_HELD_RESEARCH';V=ROOT/'baseline';V.mkdir(exist_ok=False)
sys.path.insert(0,str(P));import compare_all as common
common.WORK=V;(V/'scores').mkdir()
SETUP=Path('/workspace/divalead-setup');WINE=str(SETUP/'sysroot/usr/lib/wine/wine64');COMPILER=str(SETUP/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
env=os.environ.copy();env.update(WINEPREFIX=str(SETUP/'wine2'),WINEDLLPATH=str(SETUP/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(SETUP/'cache'))
def win(p):return 'Z:'+str(p).replace('/','\\')
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
shutil.copytree(R/'analysis',V/'analysis');A=V/'analysis'
preset=V/'Diva_THREE_HELD_BASELINE.h2p';shutil.copyfile(Q/'Diva_THREE_HELD_RESEARCH.h2p',preset)
rawpath=V/'Diva_source.wav';dump=V/'Diva_all281.tsv'
cmd='\n'.join(['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(dump),'render '+win(rawpath),'quit'])+'\n'
(V/'Diva_commands.txt').write_text(cmd)
with (V/'Diva.log').open('w') as log:
 subprocess.run([WINE,str(BASE/'current-source-history-probe/diva_performance_history.exe'),r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(preset)],input=cmd,text=True,env=env,stdout=log,stderr=log,check=True,timeout=90)
dry,sr=sf.read(rawpath,dtype='float32');assert sr==48000
np.testing.assert_array_equal(dry,sf.read(Q/'Diva_THREE_HELD_SOURCE_48k.wav',dtype='float32')[0]);assert dump.read_bytes()==(Q/'Diva_all281.tsv').read_bytes()
events=[list(map(int,s.split()[1:])) for s in (V/'Diva.log').read_text().splitlines() if s.startswith('NOTE ')]
assert events==json.loads((Q/'MIDI_events_48k.json').read_text()) and sum(e[1]==144 for e in events)==6
write(V/'MIDI_events_48k.json',events)
c=json.loads((A/'selected_candidate.json').read_text());c['settings']=dict(alignment_frames=819,repeat=8,pattern_notes=3,root_velocities=[96,96,101],incoming_note_count=6)
c['stage']='User-selected three-held-note source, frozen v58 Finish baseline'
c['source_fields'].update(json.loads((Q/'source_selection.json').read_text())['fields'])
c['source_render_history'].update(source_samples_SHA256=hashlib.sha256(dry.tobytes()).hexdigest(),target_MIDI_events_unchanged=True,user_selected_three_held=True,incoming_note_on_count=6,incoming_notes_per_phrase=3,relative_to='user-selected v58 THREE_HELD_RESEARCH',only_MIDI_velocity_changes=False,same_as_v58_sixteen_MIDI=False,same_as_user_selected_three_held_MIDI=True)
write(A/'selected_candidate.json',c)
native=V/'native_finish.so';subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(native),str(A/'native_finish.c'),'-lm'],check=True)
lib=ctypes.CDLL(str(native));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
y=np.zeros_like(dry);assert lib.native_render(dry.ctypes.data,y.ctypes.data,len(dry),48000)
actualpath=V/'actual-Windows.wav'
with (V/'Windows.log').open('w') as log:
 subprocess.run([WINE,str(BASE/'fl-v57-build/fx_render_host.exe'),win(R/'Diva_Lead_Finish_v58_WIP_x64.dll'),win(rawpath),win(actualpath),'512'],env=env,stdout=log,stderr=log,check=True,timeout=150)
actual=sf.read(actualpath,dtype='float32')[0];np.testing.assert_allclose(actual,y,rtol=0,atol=2e-7)
edit=common.h.edit_aligned(common.h.align_with_pdc(actual.astype('float64'),c['settings'],latency=12416));sf.write(V/'REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT')
published=sf.read(Q/'Diva_THREE_HELD_REFERENCE_EDIT.wav')[0];gain=np.sqrt(np.mean(common.REF**2)/np.mean(edit**2));np.testing.assert_allclose(edit*gain,published,rtol=0,atol=1.2e-7)
measured=common.score(dict(id='user-chosen-three',canonical_path=str(V/'REFERENCE_EDIT_WIP.wav'),aliases=[]));scales=json.loads((P/'ranking.json').read_text())['normalizing_errors'];score=sum(common.WEIGHTS[k]*measured['metrics'][k]/scales[k] for k in common.WEIGHTS)
assert abs(score-json.loads((Q/'verification.json').read_text())['score'])<1e-6
write(V/'measurements.json',measured)
print('USER_CHOSEN_THREE_BASELINE_ACTUAL_DIVA_WINDOWS_AND_PUBLISHED_AB_EXACT',score,flush=True)
preA=V/'before-analysis';shutil.copytree(A,preA);code=preA/'lead_finish.c';s=code.read_text()
needle='double spectral_output[2];sms_push(&s->spectral,&s->color.tracker,corrected,spectral_output);corrected[0]=spectral_output[0];corrected[1]=spectral_output[1];';assert s.count(needle)==1;s=s.replace(needle,'/* pre-STFT proof only */')
needle='s->effect.initialDelay=s->fir.latency+(int)llround(s->rate*(4096./48000)/8)*8;';assert s.count(needle)==1;s=s.replace(needle,'s->effect.initialDelay=s->fir.latency;');code.write_text(s)
for output,args in [(V/'before.so',['gcc','-O3','-shared','-fPIC',str(preA/'native_finish.c'),'-lm']),(V/'before.dll',[COMPILER,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp',str(code),'-lm'])]:subprocess.run(args+['-o',str(output)],check=True)
beforepath=V/'Diva_before_spectral.wav'
with (V/'before-Windows.log').open('w') as log:subprocess.run([WINE,str(BASE/'fl-v57-build/fx_render_host.exe'),win(V/'before.dll'),win(rawpath),win(beforepath),'512'],env=env,stdout=log,stderr=log,check=True,timeout=150)
prelib=ctypes.CDLL(str(V/'before.so'));prelib.native_render.argtypes=lib.native_render.argtypes;before=np.zeros_like(dry);assert prelib.native_render(dry.ctypes.data,before.ctypes.data,len(dry),48000)
np.testing.assert_allclose(before,sf.read(beforepath,dtype='float32')[0],rtol=0,atol=2e-7)
sys.path.insert(0,str(BASE));script=(BASE/'v247_fine_source_independent_base.py').read_text()
for needle,value in {"ROOT/'v246-fine-source-validation/raw-selected-Diva.wav'":'Path('+repr(str(rawpath))+')',"ROOT/'v246-fine-source-validation/analysis/selected_candidate.json'":'Path('+repr(str(A/'selected_candidate.json'))+')',"ROOT/'v247-independent-base-pdc.wav'":'Path('+repr(str(V/'NEW-independent-base-pdc.wav'))+')',"ROOT/'v247-independent-base.json'":'Path('+repr(str(V/'NEW-independent-base.json'))+')',"ROOT/'v246-fine-source-validation/before-spectral-actual.wav'":'Path('+repr(str(beforepath))+')'}.items():
 assert needle in script;script=script.replace(needle,value)
script='from pathlib import Path\n'+script;(V/'own_NEW_rebuild_cloud.py').write_text(script);exec(compile(script,'THREE_HELD_OWN_NEW','exec'),{'__name__':'three_held_own_NEW'})
sys.path.insert(0,str(A));from independent_spectral_ms import spectral_ms
cfg=json.loads((A/'spectral_model.json').read_text())
kwargs=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])
errors={}
for label,path,tolerance in [('own_NEW',V/'NEW-independent-base-pdc.wav',3e-7),('before_fixture',beforepath,2e-7)]:
 ind,extra=spectral_ms(sf.read(path)[0],dry.astype('float64'),48000,8320,cfg['parameters'],**kwargs)
 errors[label]=float(np.max(abs(actual[extra:]-ind[:-extra])));np.testing.assert_allclose(actual[extra:],ind[:-extra],rtol=0,atol=tolerance)
manifest=dict(source_preset=str(preset),source_WAV=str(rawpath),before_spectral_WAV=str(beforepath),NEW_independent_base=str(V/'NEW-independent-base-pdc.wav'),source_render_history=c['source_render_history'],user_selected_three_held=True,source_fields=c['source_fields'],match_reached=False)
for key in ['source_preset','source_WAV','before_spectral_WAV','NEW_independent_base']:manifest[key+'_SHA256']=hashlib.sha256(Path(manifest[key]).read_bytes()).hexdigest()
write(V/'source_manifest.json',manifest)
report=dict(score=score,metrics=measured['metrics'],crest_RMS_dB=measured['diagnostics']['crest_RMS_db'],Windows_native_max_error=float(np.max(abs(actual-y))),full_NEW_SOURCE_independent_max_error=errors['own_NEW'],spectral_fixture_max_error=errors['before_fixture'],user_chose_this_source_by_ear=True,original_three_held_unchanged=True,all281_source_verified=True,fresh_raw_equal_published_source=True,own_NEW_prebase_rebuilt_for_this_three_held_source=True,old_sixteen_source_bases_NOT_used=True,source_preset=str(preset),new_source_raw=str(rawpath),new_source_before_fixture=str(beforepath),NEW_independent_prebase=str(V/'NEW-independent-base-pdc.wav'),core_model=str(A/'spectral_model.json'),source_render_history=c['source_render_history'],match_reached=False)
write(V/'validation.json',report)
harm=common.h.harmonic_errors(edit)['harmonic_errors_db'];weights=np.mean(abs(np.asarray(harm)),axis=0)
write(V/'harmonic_diagnostics.json',dict(errors_db=harm,mean_absolute_error_per_order_db=weights.tolist(),body_errors_db=measured['diagnostics']['common_metrics']['body_errors_db']))
print('THREE_HELD_OWN_NEW_FULL_PROOF_PASS',json.dumps(report),flush=True)
