"""Freeze and freshly reproduce the last complete Finish sound before migration.

This is a check of the OLD target, not a native-FL render or a matching claim.
"""
from pathlib import Path
import concurrent.futures, datetime, hashlib, json, os, re, subprocess
import numpy as np
import soundfile as sf

W=Path(__file__).resolve().parent
P=Path('/workspace/divalead/diva-lead/v83-wip')
S=Path('/workspace/divalead-setup')
compiler=S/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix'
host=W/'v83-target-fx-host.exe'
subprocess.run([str(compiler),'-O3','-I'+str(P/'analysis'),'-o',str(host),
                str(P/'analysis/fx_render_host.c'),'-lm'],check=True)
env=os.environ.copy()
env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),
           WINEDEBUG='-all',XDG_CACHE_HOME=str(S/'cache'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def win(p):return 'Z:'+str(p).replace('/','\\')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw,rate=sf.read(P/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32',always_2d=True)
assert rate==48000 and raw.shape==(288000,2)
assert hashlib.sha256(raw.tobytes()).hexdigest()=='930f9f9261d8c55a18bf04570f772a99e6379ce6b30692b9dffc18b3fe47faea'
delay=12416
sf.write(W/'v83-target-source-with-tail.wav',np.pad(raw,((0,delay),(0,0))),rate,subtype='FLOAT')
impulse=np.zeros((rate*3,2),np.float32);impulse[rate,0]=.1
sf.write(W/'v83-target-test-impulse.wav',impulse,rate,subtype='FLOAT')
settings=json.loads((P/'Finish_settings.json').read_text())
def render(pair):
    label,inputname=pair;out=W/(label+'-fresh-Windows.wav');log=W/(label+'-fresh-Windows.log')
    args=[str(S/'sysroot/usr/lib/wine/wine64'),str(host),win(P/'Diva_Lead_Finish_v83_WIP_x64.dll'),
          win(W/inputname),win(out),'512','1',str(settings['Output_dB'])]
    with log.open('w') as f:subprocess.run(args,env=env,stdout=f,stderr=f,check=True,timeout=180)
    y,sr=sf.read(out,dtype='float32',always_2d=True);assert sr==rate and np.isfinite(y).all()
    return label,y,log.read_text()
with concurrent.futures.ThreadPoolExecutor(2) as pool:
    results={name:(y,log) for name,y,log in pool.map(render,[('v83-source','v83-target-source-with-tail.wav'),('v83-impulse','v83-target-test-impulse.wav')])}
y,log=results['v83-source'];assert 'latency=12416' in log,log
target,sr=sf.read(P/'Diva_Lead_v83_FULL_180BPM.wav',dtype='float32',always_2d=True)
full=y[delay:delay+len(raw)];assert full.shape==target.shape
null=full-target;error=float(abs(null).max());assert error<2e-7,error
pdctarget=sf.read(P/'verification/Selected_WITH_PDC.wav',dtype='float32',always_2d=True)[0]
pdc_error=float(abs(y[:len(raw)]-pdctarget).max());assert pdc_error<2e-7,pdc_error
sf.write(W/'v83-target-fresh-FULL.wav',full,rate,subtype='FLOAT')
sf.write(W/'v83-target-reproduction-NULL.wav',null,rate,subtype='FLOAT')
imp,implog=results['v83-impulse'];aligned_imp=imp[delay:]
threshold=max(float(abs(aligned_imp).max())*1e-6,1e-12)
before=aligned_imp[:rate]
events=np.flatnonzero(np.max(abs(before),axis=1)>threshold)
timing=json.loads((P/'render_timing_180BPM.json').read_text())
assert timing['pattern_notes']==3 and timing['incoming_note_on_count']==6 and timing['pitches']==[41,37,36]
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 target_complete_release='v83-wip',target_full=str(P/'Diva_Lead_v83_FULL_180BPM.wav'),
 target_edit=str(P/'Diva_Lead_v83_REFERENCE_EDIT.wav'),target_full_file_SHA256=digest(P/'Diva_Lead_v83_FULL_180BPM.wav'),
 target_edit_file_SHA256=digest(P/'Diva_Lead_v83_REFERENCE_EDIT.wav'),source_file_SHA256=digest(P/'Diva_SOURCE_FROZEN_48k.wav'),
 source_preset_SHA256=digest(P/'Diva_Lead_v83_WIP.h2p'),MIDI_SHA256=digest(P/'Diva_THREE_HELD_180BPM.mid'),
 source_decoded_float32_SHA256=hashlib.sha256(raw.tobytes()).hexdigest(),
 reference_decoded_float64_SHA256=hashlib.sha256(sf.read(P/'Diva_original_lead_reference.wav',dtype='float64')[0].tobytes()).hexdigest(),
 three_held_notes_preserved=True,note_on_count=6,Finish_amount=1,Finish_output_dB=settings['Output_dB'],
 sample_rate=rate,reported_latency_frames=delay,reported_latency_ms=1000*delay/rate,
 fresh_Windows_full_target_max_abs_error=error,fresh_Windows_PDC_target_max_abs_error=pdc_error,
 full_target_bit_exact_decoded=bool(np.array_equal(full,target)),
 null_RMS=float(np.sqrt(np.mean(null.astype('float64')**2))),
 zero_latency_aligned_impulse_has_pre_input_output=bool(len(events)),
 zero_latency_aligned_impulse_pre_input_peak=float(abs(before).max()),
 pre_input_detection_threshold=threshold,
 pre_input_first_offset_frames=int(events[0]-rate) if len(events) else None,
 caution='Pre-input response concerns this impulse and latency-subtracted old Finish. No claim about perceptual audibility or a native approximation is made.',
 native_FL_audio_render_tested=False,native_migration_match_verified=False,original_reference_match_reached=False)
assert report['reference_decoded_float64_SHA256']=='450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c'
(W/'V83_MIGRATION_TARGET_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
