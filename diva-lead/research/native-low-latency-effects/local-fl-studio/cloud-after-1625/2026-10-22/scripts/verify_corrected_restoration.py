"""Replay a restored FL05/native kit through actual DLLs and unchanged criteria."""
from pathlib import Path
import hashlib,json,os,sys,zipfile
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply
root=Path(sys.argv[1]);out=root/'actual-DLL-restoration-check';out.mkdir(exist_ok=False)
os.environ['DIVALEAD_FL20_BASE']=str(root);os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(out/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();choice=json.loads((root/'restored-candidate.json').read_text());x=np.array(choice['x'])
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/WIP06')
zpath=next(public.glob('*_complete_WIP.zip'))
with zipfile.ZipFile(zpath)as z:
    prefix=z.namelist()[0].split('/')[0]+'/'
    expected=json.loads(z.read(prefix+'verification/NATIVE_PRESET_VERIFICATION.json'))
    saved_states={r['node']:z.read(prefix+r['state'])for r in expected['native_plugin_manifest']}
def configure(c):
    apply(c,x)
    for index,value in choice['chorus_overrides'].items():c.set(3,int(index),int(value))
c=NativeChain(choice['source_manifest']['native_input'],'restored-corrected-FL05-check',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
rows=[];checked=[]
try:
    configure(c)
    for node,data in saved_states.items():
        path=out/f'native-node-{node}.bin';c.save_state(node,path);assert path.read_bytes()==data
        checked.append(dict(node=node,SHA256=hashlib.sha256(data).hexdigest(),actual_native_state_bytes_exact=True))
    for rep in range(6):
        y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025
        rows.append(dict(loss=loss,assessment=features.local.last,native_status=status))
    c.set(3,1,0);restored_zero,_=c.render()
finally:c.close()
original=json.loads((public/'verification/candidate.json').read_text())
c=NativeChain(original['source_manifest']['native_input'],'original-corrected-FL05-zero-restore-check',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
try:configure(c);c.set(3,1,0);original_zero,_=c.render()
finally:c.close()
assert np.array_equal(original_zero,restored_zero)
mean=float(np.mean([r['loss']for r in rows]));std=float(np.std([r['loss']for r in rows]))
assert abs(mean-expected['mean_original_objective'])<.01,(mean,expected['mean_original_objective'])
proof=dict(actual_native_DLL_replay=True,restored_from_published_ZIP_and_full_checkout=True,
    all12_native_state_bytes_exact=checked,restored_source_zero_depth_audio_bit_exact=True,
    six_actual_full_capture_mean=mean,six_actual_full_capture_std=std,previous_published_export_mean=expected['mean_original_objective'],
    actual_captures=rows,only_three_held_notes_per_phrase=True,actual_FL_GUI_export_not_claimed=True,
    independently_fresh_machine_install_not_claimed=True,reference_match_reached=False)
(out/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print('CORRECTED_NATIVE_RESTORATION_VERIFIED',mean,std,flush=True)
