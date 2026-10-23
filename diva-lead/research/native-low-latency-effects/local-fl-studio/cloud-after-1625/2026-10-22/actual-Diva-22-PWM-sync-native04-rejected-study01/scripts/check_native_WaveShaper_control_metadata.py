"""Actual native DLL regression for newly supported WaveShaper raw controls."""
from pathlib import Path
import copy,datetime,hashlib,json
import numpy as np
from native_chain import NativeChain
from fl20_curve import apply_candidate,curve_metadata,native_dsp_settings_SHA256
from win_vst3 import D

ROOT=D/'native-WaveShaper-control-metadata-01'
ROOT.mkdir(exist_ok=False)
seed=json.loads((D.parent/'FL20_NATIVE_ZL_REBASED_04/verification/candidate.json').read_text())
clients=[]
def make(tag,settings,manual=False):
    c=NativeChain(seed['source_manifest']['native_input'],'WS-control-metadata-'+tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    clients.append(c)
    apply_candidate(c,np.array(settings['x']),seed if manual else settings)
    for k,v in seed['chorus_overrides'].items():c.set(3,int(k),int(v))
    if manual:
        for j,v in enumerate(settings['waveshaper_native_controls']):c.set(0,j,v)
    c.set(3,1,0)
    return c
try:
    original=make('original',seed)
    base,_=original.render()
    fingerprint=native_dsp_settings_SHA256(seed['x'],seed)
    assert fingerprint==seed['native_saved_state_bundle']['settings_SHA256']
    defaults=dict(seed,waveshaper_native_controls=[128,128,128])
    assert native_dsp_settings_SHA256(seed['x'],defaults)==fingerprint
    rows=[]
    for j,values in enumerate([[132,128,128],[128,96,128],[128,128,124]]):
        changed=dict(seed,waveshaper_native_controls=values)
        assert curve_metadata(changed)['waveshaper_native_controls']==values
        assert native_dsp_settings_SHA256(seed['x'],changed)!=fingerprint
        c=make('changed-'+str(j),changed)
        actual=[c.value_hint(0,k)for k in range(3)]
        assert actual==values,(actual,values)
        audio,_=c.render()
        delta=float(abs(audio-base).max())
        assert delta>1e-7,delta
        manual=make('manual-'+str(j),changed,True)
        direct,_=manual.render()
        error=float(abs(direct-audio).max())
        assert error<=2e-7,error
        state=ROOT/f'control-{j}.bin'
        c.save_state(0,state)
        replay=make('replay-'+str(j),changed)
        replay.load_state(0,state)
        replay.save_state(0,ROOT/f'control-{j}-resaved.bin')
        assert state.read_bytes()==(ROOT/f'control-{j}-resaved.bin').read_bytes()
        again,_=replay.render()
        replay_error=float(abs(again-audio).max())
        assert replay_error<=2e-7,replay_error
        rows.append(dict(controls=actual,audio_delta_from_default=delta,metadata_vs_explicit_native_control_max_error=error,saved_state_byte_exact=True,saved_state_audio_max_error=replay_error))
    report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_DLL_execution=True,legacy_settings_fingerprint_preserved=True,explicit_default_controls_preserve_fingerprint=True,modified_controls_not_overwritten_by_old_saved_bundle=True,unchanged_absolute_replay_gate=2e-7,checks=rows,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
    (ROOT/'ACTUAL_NATIVE_CONTROL_METADATA_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ACTUAL_WAVESHAPER_CONTROL_METADATA_PASS',json.dumps(report),flush=True)
finally:
    for c in clients:c.close()
