"""Changed MIDI requires a fresh own independent pre-STFT base, not old247."""
from pathlib import Path
import sys,json,shutil,subprocess,ctypes,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_architectures as m
import numpy as np,soundfile as sf
ROOT=m.ROOT/'finalists';selected=json.loads((ROOT/'selected.json').read_text())
A=Path(selected['analysis']);V=A.parent
dry=np.ascontiguousarray(sf.read(ROOT/'raw-selected-Diva.wav',dtype='float32')[0])
before_A=V/'before-analysis';shutil.copytree(A,before_A)
code=before_A/'lead_finish.c';text=code.read_text()
line='double spectral_output[2];sms_push(&s->spectral,&s->color.tracker,corrected,spectral_output);corrected[0]=spectral_output[0];corrected[1]=spectral_output[1];'
assert text.count(line)==1;text=text.replace(line,'/* pre-STFT source proof: spectral stage omitted */')
needle='s->effect.initialDelay=s->fir.latency+(int)llround(s->rate*(4096./48000)/8)*8;'
assert text.count(needle)==1;text=text.replace(needle,'s->effect.initialDelay=s->fir.latency;');code.write_text(text)
compiler=str(m.SETUP/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
for output,args in [(V/'before.so',['gcc','-O3','-shared','-fPIC',str(before_A/'native_finish.c'),'-lm']),
                    (V/'before.dll',[compiler,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp',str(code),'-lm'])]:
    subprocess.run(args+['-o',str(output)],check=True,timeout=120)
lib=ctypes.CDLL(str(V/'before.so'));lib.native_render.argtypes=m.LIB.native_render.argtypes
before=np.zeros_like(dry);assert lib.native_render(dry.ctypes.data,before.ctypes.data,len(dry),48000)
before_path=V/'new-source-before-actual.wav'
with (V/'before-Windows.log').open('w') as log:
    subprocess.run([m.WINE,str(m.B/'fl-v57-build/fx_render_host.exe'),m.win(V/'before.dll'),m.win(ROOT/'raw-selected-Diva.wav'),m.win(before_path),'512'],env=m.env,stdout=log,stderr=log,check=True,timeout=150)
actual_before=sf.read(before_path,dtype='float32')[0]
np.testing.assert_allclose(before,actual_before,rtol=0,atol=2e-7)
print('CHANGED_MIDI_BEFORE_WINDOWS_NATIVE_PASS',float(np.max(abs(before-actual_before))),flush=True)
sys.path.insert(0,str(m.B))
script=(m.B/'v247_fine_source_independent_base.py').read_text()
replacements={"ROOT/'v246-fine-source-validation/raw-selected-Diva.wav'":'Path('+repr(str(ROOT/'raw-selected-Diva.wav'))+')',
              "ROOT/'v246-fine-source-validation/analysis/selected_candidate.json'":'Path('+repr(str(A/'selected_candidate.json'))+')',
              "ROOT/'v247-independent-base-pdc.wav'":'Path('+repr(str(V/'NEW-independent-base-pdc.wav'))+')',
              "ROOT/'v247-independent-base.json'":'Path('+repr(str(V/'NEW-independent-base.json'))+')',
              "ROOT/'v246-fine-source-validation/before-spectral-actual.wav'":'Path('+repr(str(before_path))+')'}
for needle,value in replacements.items():
    assert needle in script,needle
    script=script.replace(needle,value)
script='from pathlib import Path\n'+script
(V/'rebuild-own-NEW-base-cloud.py').write_text(script)
exec(compile(script,'CHANGED_MIDI_OWN_NEW_PREBASE','exec'),{'__name__':'changed_MIDI_own_NEW'})
sys.path.insert(0,str(A));from independent_spectral_ms import spectral_ms
cfg=json.loads((A/'spectral_model.json').read_text())
kwargs=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])
actual=sf.read(V/'actual-Windows.wav',dtype='float32')[0]
errors={}
for label,path,tolerance in [('own_NEW',V/'NEW-independent-base-pdc.wav',3e-7),('before_fixture',before_path,2e-7)]:
    independent,extra=spectral_ms(sf.read(path)[0],dry.astype('float64'),48000,8320,cfg['parameters'],**kwargs)
    error=float(np.max(abs(actual[extra:]-independent[:-extra])))
    np.testing.assert_allclose(actual[extra:],independent[:-extra],rtol=0,atol=tolerance)
    errors[label]=error
edit=m.common.h.edit_aligned(m.common.h.align_with_pdc(actual.astype('float64'),m.TIMING,latency=12416))
sf.write(V/'REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT')
m.common.WORK=ROOT
measured=m.common.score(dict(id='actual-Windows-final',canonical_path=str(V/'REFERENCE_EDIT_WIP.wav'),aliases=[]))
score=sum(m.common.WEIGHTS[k]*measured['metrics'][k]/m.SCALES[k] for k in m.common.WEIGHTS)
from search_global_guards import ORIGINAL53_LIMITS
original=json.loads((m.P/'ranking.json').read_text())['results'][0]['metrics']
assert all(measured['metrics'][k]<=original[k]*v for k,v in ORIGINAL53_LIMITS.items())
crest=measured['diagnostics']['crest_RMS_db'];assert crest<=m.CAP
baseline=json.loads((m.V/'verification/selected_validation.json').read_text())
assert score<baseline['score']
history=json.loads((m.V/'source_manifest.json').read_text())['source_render_history']
history.update(target_MIDI_events_unchanged=False,source_samples_SHA256=hashlib.sha256(dry.tobytes()).hexdigest(),timing_and_pitches_unchanged=True,only_MIDI_velocity_changes=True)
report=dict(score=score,baseline_v57_score=baseline['score'],metrics=measured['metrics'],crest_RMS_dB=crest,crest_cap_dB=m.CAP,source_preset=str(ROOT/'source.h2p'),new_source_raw=str(ROOT/'raw-selected-Diva.wav'),new_source_before_fixture=str(before_path),NEW_independent_prebase=str(V/'NEW-independent-base-pdc.wav'),core_model=str(A/'spectral_model.json'),source_updates=baseline['source_updates'],source_render_history=history,all281_source_verified=True,fresh_raw_samples_and_dump_equal_selected_source=True,preset_bytes_and_all281_unchanged57=True,MIDI_preSTFT_processing_unchanged53=False,only_MIDI_velocity_changes=True,old247_NOT_used_for_changed_source=True,own_NEW_prebase_built_from_this_new_raw=True,Windows_native_max_error=selected['Windows_native_max_error'],full_NEW_SOURCE_independent_max_error=errors['own_NEW'],spectral_fixture_max_error=errors['before_fixture'],before_Windows_native_max_error=float(np.max(abs(before-actual_before))),fixed_original11_and_crest_passed=True,match_reached=False)
m.write(V/'validation.json',report)
print('FINALIST_OWN_NEW_FULL_INDEPENDENT_PASS',json.dumps(report),flush=True)
