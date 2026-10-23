from pathlib import Path
import hashlib,json,numpy as np
from win_vst3 import WinVST3,D
binary=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22')
state=public/'ZL-WIP17/verification/ZL_component.bin'
c=WinVST3('startup-ZL17-current-context-check')
try:
    c.load(state)
    impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073]
    y,status=c.render(impulse);assert np.isfinite(y).all()and not np.any(y[:4096])
    assert c.latency()==0 and np.flatnonzero(np.max(abs(y),axis=1)>1e-9)[0]==4096
    c.save(D/'startup-component-resaved.bin')
    assert (D/'startup-component-resaved.bin').read_bytes()==state.read_bytes()
    receipt=dict(actual_official_VST3_execution=True,component_roundtrip_byte_exact=True,declared_PDC_frames=0,
                 impulse_added_delay_frames=0,not_a_FL_GUI_or_ASIO_test=True,reference_match_reached=False)
    (D/'STARTUP_ACTUAL_ZL_PROOF.json').write_text(json.dumps(receipt,indent=2)+'\n')
finally:c.close()
print('OFFICIAL_ZL17_ACTUAL_VST3_STATE_AND_ZERO_ADDED_BUFFER_PASS')
