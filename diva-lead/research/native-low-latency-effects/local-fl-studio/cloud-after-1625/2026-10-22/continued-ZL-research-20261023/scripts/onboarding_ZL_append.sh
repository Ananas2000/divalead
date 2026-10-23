
# Official external VST3 runtime. Historical Finish checks above are readiness
# fixtures, not the current production effect chain. Existing setup is intact.
cd /workspace/divalead
zl_python=/workspace/.venvs/divalead/bin/python
zl_runtime=/tmp/divalead-local-1625/internet-plugins-runtime-1.4.1
zl_scripts=diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/external-plugins-20261023-02/scripts
if [ ! -x "$zl_runtime/vst3_effect_host.exe" ]; then
  if [ -e "$zl_runtime" ]; then
    echo 'Incomplete external ZL runtime exists; preserve it and choose a new destination.' >&2
    exit 1
  fi
  PYTHONDONTWRITEBYTECODE=1 "$zl_python" "$zl_scripts/setup_ZL_runtime.py" --destination "$zl_runtime"
fi
PYTHONPATH="$zl_runtime" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 "$zl_python" - <<'ZL_ACTUAL_CHECK'
from pathlib import Path
import hashlib,json,numpy as np
from win_vst3 import WinVST3,D
binary=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22')
state=public/'ZL-WIP03/verification/ZL_component.bin'
c=WinVST3('startup-ZL14-real-component-check')
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
print('OFFICIAL_ZL14_ACTUAL_VST3_STATE_AND_ZERO_ADDED_BUFFER_PASS')
ZL_ACTUAL_CHECK
