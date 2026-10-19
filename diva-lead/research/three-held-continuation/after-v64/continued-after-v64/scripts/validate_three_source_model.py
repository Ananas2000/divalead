"""Fresh Diva/Windows/native/own-NEW proof for a three-held spectral candidate."""
from pathlib import Path
import os,sys,json,subprocess,ctypes,shutil,hashlib,re
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent;B=Path(os.environ.get('DIVALEAD_THREE_SOURCE_BASIS',str(ROOT/'source-drift24-proof')));ANCHOR=ROOT/'baseline';REPO=Path('/workspace/divalead');P=REPO/'diva-lead/research/repository-selection'
sys.path.insert(0,str(P));import compare_all as a
fit=Path(sys.argv[1]);V=ROOT/sys.argv[2];V.mkdir(exist_ok=False);A=V/'analysis';shutil.copytree(B/'analysis',A)
choice=json.loads((fit/'best.json').read_text());cfg=json.loads((A/'spectral_model.json').read_text());previous=json.loads(json.dumps(cfg))
assert choice['feasible_search_guards'] and choice['user_selected_three_baseline']
for field in ['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters']:
 if field in choice:cfg[field]=choice[field]
assert all(cfg[k]==v for k,v in previous.items() if k not in ['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters'])
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
write(A/'spectral_model.json',cfg);c=json.loads((A/'selected_candidate.json').read_text());c['spectral_model']=cfg
for field in ['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters']:c[field]=cfg[field]
write(A/'selected_candidate.json',c)
p=A/'spectral_ms_settings.h';s=p.read_text();values=np.asarray(cfg['hf_matrix_parameters']).reshape(10,10);array='{'+','.join('{'+','.join(format(float(x),'.17g') for x in row)+'}' for row in values)+'}'
s,n=re.subn(r'SMS_HF_PARAMETERS\[10\]\[10\]=\{.*?\};','SMS_HF_PARAMETERS[10][10]='+array+';',s,flags=re.S);assert n==1;p.write_text(s)
values=np.asarray(cfg['harmonic_gain_parameters']).reshape(3,31);array='{'+','.join('{'+','.join(format(float(x),'.17g') for x in row)+'}' for row in values)+'}'
s,n=re.subn(r'SMS_GAIN_PARAMETERS\[3\]\[31\]=\{.*?\};','SMS_GAIN_PARAMETERS[3][31]='+array+';',s,flags=re.S);assert n==1;p.write_text(s)
for field,symbol in [('common_phase_radians','SMS_PHASE_PARAMETERS'),('common_phase_key_slopes','SMS_PHASE_KEY_SLOPES'),('common_phase_key_quadratic','SMS_PHASE_KEY_QUADRATIC')]:
 values=np.asarray(cfg[field]);assert values.shape==(6,)
 array='{'+','.join(format(float(x),'.17g') for x in values)+'}'
 s,n=re.subn(symbol+r'\[6\]=\{.*?\};',symbol+'[6]='+array+';',s,flags=re.S);assert n==1;p.write_text(s)
fine=cfg['fine_phase_harmonic_parameters'];oldfine=previous['fine_phase_harmonic_parameters']
assert all(fine[k]==v for k,v in oldfine.items() if k!='chebyshev_coefficients')
fp=A/'fine_phase_settings.h';fs=fp.read_text();values=np.asarray(fine['chebyshev_coefficients']);assert values.shape==(5,11)
array='{'+','.join('{'+','.join(format(float(x),'.17g') for x in row)+'}' for row in values)+'}'
fs,n=re.subn(r'SMS_FINE_PHASE_TARGET\[5\]\[11\]=\{.*?\};','SMS_FINE_PHASE_TARGET[5][11]='+array+';',fs,flags=re.S);assert n==1;fp.write_text(fs)
balance=cfg['final_stereo_balance'];oldbalance=previous['final_stereo_balance'];balance_fields=['log_side_scale','mid_to_side_real','mid_to_side_imag']
assert all(balance[k]==v for k,v in oldbalance.items() if k not in balance_fields)
assert all(balance[k][7]==0 for k in balance_fields)
bp=A/'spectral_balance_settings.h';bs=bp.read_text()
for field,symbol in [('log_side_scale','SMS_BALANCE_LOG_SCALE'),('mid_to_side_real','SMS_BALANCE_MID_MIX'),('mid_to_side_imag','SMS_BALANCE_MID_IMAG')]:
 values=np.asarray(balance[field]);assert values.shape==(15,)
 array='{'+','.join(format(float(x),'.17g') for x in values)+'}'
 bs,n=re.subn(symbol+r'\[15\]=\{.*?\};',symbol+'[15]='+array+';',bs,flags=re.S);assert n==1
bp.write_text(bs)
dynamic=cfg['dynamic_harmonic_parameters'];olddynamic=previous['dynamic_harmonic_parameters']
assert all(dynamic[k]==v for k,v in olddynamic.items() if k!='target_logpower_db_polynomial')
dp=A/'spectral_dynamic_settings.h';ds=dp.read_text();values=np.asarray(dynamic['target_logpower_db_polynomial']);assert values.shape==(5,23)
array='{'+','.join('{'+','.join(format(float(x),'.17g') for x in row)+'}' for row in values)+'}'
ds,n=re.subn(r'SMS_DYNAMIC_TARGET\[5\]\[23\]=\{.*?\};','SMS_DYNAMIC_TARGET[5][23]='+array+';',ds,flags=re.S);assert n==1;dp.write_text(ds)
setup=Path('/workspace/divalead-setup');wine=str(setup/'sysroot/usr/lib/wine/wine64');compiler=str(setup/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
env=os.environ.copy();env.update(WINEPREFIX=str(setup/'wine2'),WINEDLLPATH=str(setup/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(setup/'cache'))
def win(p):return 'Z:'+str(p).replace('/','\\')
native=V/'native_finish.so';dll=V/'research-finish.dll'
subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(native),str(A/'native_finish.c'),'-lm'],check=True)
subprocess.run([compiler,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp','-o',str(dll),str(A/'lead_finish.c'),'-lm'],check=True)
rawpath=V/'Diva_source.wav';dump=V/'Diva_all281.tsv'
cmd='\n'.join(['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(dump),'render '+win(rawpath),'quit'])+'\n'
with (V/'Diva.log').open('w') as log:subprocess.run([wine,'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(B/'Diva_THREE_HELD_BASELINE.h2p')],input=cmd,text=True,env=env,stdout=log,stderr=log,check=True,timeout=90)
raw,rate=sf.read(rawpath,dtype='float32');assert rate==48000;np.testing.assert_array_equal(raw,sf.read(B/'Diva_source.wav',dtype='float32')[0]);assert dump.read_bytes()==(B/'Diva_all281.tsv').read_bytes()
events=[list(map(int,x.split()[1:])) for x in (V/'Diva.log').read_text().splitlines() if x.startswith('NOTE ')]
assert events==json.loads((B/'MIDI_events_48k.json').read_text());write(V/'MIDI_events_48k.json',events)
with (V/'Windows.log').open('w') as log:subprocess.run([wine,'/workspace/divalead-work/fl-v57-build/fx_render_host.exe',win(dll),win(rawpath),win(V/'actual-Windows.wav'),'512'],env=env,stdout=log,stderr=log,check=True,timeout=150)
actual=sf.read(V/'actual-Windows.wav',dtype='float32')[0];lib=ctypes.CDLL(str(native));lib.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];out=np.zeros_like(raw);assert lib.native_render(raw.ctypes.data,out.ctypes.data,len(raw),48000);np.testing.assert_allclose(actual,out,rtol=0,atol=2e-7)
sys.path.insert(0,str(A));from independent_spectral_ms import spectral_ms
kwargs=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])
errors={}
for label,path,tolerance in [('own_NEW',B/'NEW-independent-base-pdc.wav',3e-7),('before_fixture',B/'Diva_before_spectral.wav',2e-7)]:
 ind,extra=spectral_ms(sf.read(path)[0],raw.astype('float64'),48000,8320,cfg['parameters'],**kwargs);error=float(np.max(abs(actual[extra:]-ind[:-extra])));np.testing.assert_allclose(actual[extra:],ind[:-extra],rtol=0,atol=tolerance);errors[label]=error
edit=a.h.edit_aligned(a.h.align_with_pdc(actual.astype('float64'),dict(alignment_frames=819),latency=12416));sf.write(V/'REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT');a.WORK=V;(V/'scores').mkdir();measured=a.score(dict(id='actual-three',canonical_path=str(V/'REFERENCE_EDIT_WIP.wav'),aliases=[]))
base=json.loads((ANCHOR/'validation.json').read_text());source_basis_report=json.loads(Path(os.environ.get('DIVALEAD_THREE_SOURCE_REPORT',str(B/'validation.json'))).read_text());scales=json.loads((P/'ranking.json').read_text())['normalizing_errors'];standard=sum(a.WEIGHTS[k]*measured['metrics'][k]/scales[k] for k in a.WEIGHTS)
tone_weights=choice['tone_focused_weights'];tone=sum(tone_weights[k]*measured['metrics'][k]/scales[k] for k in tone_weights)
assert all(measured['metrics'][k]<=base['metrics'][k]*limit for k,limit in choice['guard_limits'].items())
crest=measured['diagnostics']['crest_RMS_db'];assert crest<=choice['fixed_crest_cap_dB'];assert standard<=base['score']*1.0001
assert tone<source_basis_report.get('acceptance_tone_cap',json.loads((fit/'history.json').read_text())[0]['weighted_score'])-1e-6
assert np.max(np.abs(actual))<.99
family=source_basis_report.get('source_family','Drift24')
report=dict(score=standard,tone_score=tone,baseline_score=base['score'],metrics=measured['metrics'],crest_RMS_dB=crest,crest_cap_dB=choice['fixed_crest_cap_dB'],guard_limits=choice['guard_limits'],all_chosen_three_guards_passed=True,Windows_native_max_error=float(np.max(abs(actual-out))),full_NEW_SOURCE_independent_max_error=errors['own_NEW'],spectral_fixture_max_error=errors['before_fixture'],same_user_selected_Diva_preset_raw_and_all281=False,same_checked_Drift24_source_raw_and_all281=family=='Drift24',same_checked_source_family_raw_and_all281=True,source_family=family,changed_source_fields=source_basis_report.get('changed_source_fields',{'OSC:Drift':24.0}),original_three_held_MIDI_events_unchanged=True,source_preset=str(B/'Diva_THREE_HELD_BASELINE.h2p'),new_source_raw=str(rawpath),new_source_before_fixture=str(B/'Diva_before_spectral.wav'),NEW_independent_prebase=str(B/'NEW-independent-base-pdc.wav'),core_model=str(A/'spectral_model.json'),source_render_history=source_basis_report['source_render_history'],all281_source_verified=True,old_sixteen_NEW_bases_NOT_used=True,match_reached=False)
write(V/'numeric-choice.json',choice)
with (V/'arbitrary-input-verification.json').open('w') as log:subprocess.run([sys.executable,'-B',str(A/'verify_spectral.py')],stdout=log,env=env,check=True,timeout=300)
cases=json.loads((V/'arbitrary-input-verification.json').read_text())['arbitrary_input_no_MIDI_cases'];assert len(cases)==12 and all(x['causal_prefix_equal'] and x['independent_max_error']<2e-10 for x in cases)
write(V/'validation.json',report)
print('THREE_HELD_SOURCE_FAMILY_CANDIDATE_ACTUAL_FULL_PROOF_PASS',family,json.dumps(report),flush=True)
