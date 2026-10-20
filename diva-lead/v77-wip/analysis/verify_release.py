"""Verify the self-contained v77 assets and independent saved-NEW replay."""
from pathlib import Path
import json,hashlib,struct,sys
import numpy as np,soundfile as sf
from independent_spectral_ms import spectral_ms

A=Path(__file__).resolve().parent;D=A.parent
manifest=json.loads((D/'source_manifest.json').read_text())
for key in ['source_preset','source_WAV','before_spectral_WAV','NEW_independent_base']:
 path=D/manifest[key];assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest[key+'_SHA256'],key
cfg=json.loads((A/'spectral_model.json').read_text())
assert hashlib.sha256((A/'spectral_model.json').read_bytes()).hexdigest()==manifest['spectral_model_SHA256']
dry,sr=sf.read(D/manifest['source_WAV'],dtype='float32');assert sr==48000 and dry.shape==(288000,2)
assert hashlib.sha256(dry.tobytes()).hexdigest()==manifest['source_render_history']['source_samples_SHA256']
kwargs=dict(sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])
actual=sf.read(D/'verification/Selected_WITH_PDC.wav')[0]
errors={}
for label,key,tolerance in [('saved_own_NEW','NEW_independent_base',3e-7),('before_spectral_fixture','before_spectral_WAV',2e-7)]:
 independent,extra=spectral_ms(sf.read(D/manifest[key])[0],dry.astype('float64'),48000,8320,cfg['parameters'],**kwargs)
 error=float(np.max(abs(actual[extra:]-independent[:-extra])));assert error<tolerance,(label,error);errors[label]=error
ab,sr=sf.read(D/'AB_REFERENCE_V77_WIP.wav');edit,er=sf.read(D/'Diva_Lead_v77_REFERENCE_EDIT.wav');ref,rr=sf.read(D/'Diva_original_lead_reference.wav')
assert sr==er==rr==48000 and len(ab)==376128 and len(edit)==len(ref)==176064
np.testing.assert_array_equal(ab[:176064],ref);np.testing.assert_array_equal(ab[200064:],edit);assert np.max(abs(ab[176064:200064]))==0
raw_edit=sf.read(D/'verification/Selected_REFERENCE_EDIT.wav')[0];gain=float(np.sqrt(np.mean(ref*ref)/np.mean(raw_edit*raw_edit)))
assert np.max(abs(edit-raw_edit*gain))<1.2e-7
full,fr=sf.read(D/'Diva_Lead_v77_FULL_180BPM.wav');assert fr==48000 and full.shape==(288000,2)
np.testing.assert_allclose(full[:len(actual)-12416],actual[12416:],rtol=0,atol=2e-7)
# Parse the actual standard MIDI file, then convert its encoded tempo/ticks to
# rounded48000Hz sample frames. This catches omitted swing or offset events.
data=(D/'Diva_THREE_HELD_180BPM.mid').read_bytes();assert data[:4]==b'MThd'
length,format_,tracks,division=struct.unpack('>IHHH',data[4:14]);assert (length,format_,tracks,division)==(6,0,1,16000)
assert data[14:18]==b'MTrk';track_size=int.from_bytes(data[18:22],'big');track=data[22:];assert len(track)==track_size
offset=ticks=0;tempo=500000;events=[]
def read_vlq():
 global offset
 value=0
 for _ in range(4):
  byte=track[offset];offset+=1;value=(value<<7)|(byte&127)
  if byte<128:return value
 raise AssertionError('Invalid MIDI VLQ')
while offset<len(track):
 ticks+=read_vlq();status=track[offset];offset+=1
 if status==255:
  kind=track[offset];offset+=1;n=read_vlq();payload=track[offset:offset+n];offset+=n
  if kind==81:tempo=int.from_bytes(payload,'big')
  if kind==47:break
 else:
  assert status in [128,144];pitch,velocity=track[offset:offset+2];offset+=2
  frame=int(np.floor(ticks/division*(tempo/1e6)*48000+.5));events.append(dict(frame=frame,status=status,pitch=pitch,velocity=velocity))
expected=json.loads((D/'verification/MIDI_note_events_48k.json').read_text())['events'];assert len(events)==12 and events==expected
assert [e['pitch'] for e in events if e['status']==144]==[41,37,36]*2
logged=[tuple(map(int,line.split()[1:])) for line in (D/'verification/Diva_source_render.log').read_text().splitlines() if line.startswith('NOTE ')]
assert [(x['frame'],x['status'],x['pitch'],x['velocity']) for x in events]==logged
report=json.loads((D/'verification/selected_validation.json').read_text());limits=json.loads((D/'verification/guard_limits.json').read_text())
assert all(report['metrics'][k]<=v for k,v in limits['chosen_three_absolute_limits'].items())
proof=json.loads((D/'verification/selected_proof.json').read_text());assert proof['crest_RMS_dB']<=limits['fixed_crest_RMS_dB']
cases=json.loads((D/'verification/arbitrary_input_verification.json').read_text())['arbitrary_input_no_MIDI_cases'];assert len(cases)==12 and {x['sample_rate'] for x in cases}=={44100,48000,96000,192000} and all(x['causal_prefix_equal'] and x['independent_max_error']<2e-10 for x in cases)
if (D/'SHA256SUMS.txt').exists():
 for line in (D/'SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
print(json.dumps(dict(source_and_model_hashes_checked=True,source_decoded_samples_SHA256_checked=True,independent_errors=errors,independent_preSTFT_base_rebuilt_now=False,saved_matching_NEW_base_used=True,MIDI_all12_events_match_actual_host_log=True,reference_edit_equals_AB_second_exactly=True,full_WAV_PDC_prefix_checked=True,chosen_three_guards_and_fixed_crest_passed=True,arbitrary_cases_recorded=12,FL_GUI_tested=False,match_reached=False),indent=2))
