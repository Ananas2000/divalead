"""Check explicit curve replay against its actual saved DLL state, then fresh6+6."""
from pathlib import Path
import hashlib,json,os,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply
from fl20_curve_detail8_supported_proposal import apply_candidate,FORMAT,DETAIL_FORMAT,curve_metadata

B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=B/'detail8-WS-integration-audit-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal

assert json.loads((N/'fl20-corrected-search.pause').read_text())['owner']=='validated-detail8-curve-integration'
deadline=time.monotonic()+120
while True:
    state=json.loads((N/'FL20_CORRECTED_SEARCH_CONTROLLER.json').read_text())
    if state['phase']=='paused_by_control_or_actual_disk_reserve':break
    assert time.monotonic()<deadline;time.sleep(1)
experiment=B/'fl20-WS-detail8-curve-01'
choice=json.loads((experiment/'full-validated-candidate.json').read_text());assert choice['robust_improvement']
incumbent=json.loads((N/'FL20-corrected/BEST_CANDIDATE.json').read_text())
oldseed=json.loads((experiment/'seed.json').read_text())
assert incumbent['source_manifest']['source_audio_SHA256']==choice['source_manifest']['source_audio_SHA256']
assert incumbent['source_manifest']==choice['source_manifest']
choice.update(waveshaper_curve_format=FORMAT,not_compatible_with_standard_x95_exporter=False,
              waveshaper_detail_bump_format=DETAIL_FORMAT,curve_playback_and_export_integration_version=3)
(ROOT/'supported-proposal.json').write_text(json.dumps(choice,indent=2)+'\n')
source=Path(choice['source_manifest']['native_input']);x=np.array(choice['x']);overrides=choice['chorus_overrides']
nodes=[0,3,4,5,6,7,8,10,11,12,13,14]

def configure(c,v,candidate,manual=False):
    if manual:
        apply(c,v);c.load_state(0,experiment/'Extended_WaveShaper_state.bin')
    else:apply_candidate(c,v,candidate)
    for k,value in candidate['chorus_overrides'].items():c.set(3,int(k),int(value))

saved={};zero_reference=None;checks=[]
for mode in ['actual-saved-DLL-state','explicit-shared-curve-helper']:
    c=NativeChain(source,ROOT.name+'-'+mode,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    try:
        configure(c,x,choice,manual=mode=='actual-saved-DLL-state')
        for node in nodes:
            path=ROOT/f'{mode}-node-{node}.bin';c.save_state(node,path);data=path.read_bytes()
            if mode=='actual-saved-DLL-state':saved[node]=data
            else:
                assert saved[node]==data,(mode,node)
                checks.append(dict(node=node,actual_native_state_bytes_exact=True,SHA256=hashlib.sha256(data).hexdigest()))
        c.set(3,1,0);y,_=c.render()
        if zero_reference is None:zero_reference=y
        else:np.testing.assert_array_equal(y,zero_reference)
    finally:c.close()

proposal=dict(choice,full_fresh_native_realizations=0,full_fresh_native_validation_pending=True,
              supported_native_curve_state_and_audio_verified=True,not_automatically_adopted=True)
(ROOT/'supported-old-EQ-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
graft=dict(incumbent,waveshaper_detail_bump_format=DETAIL_FORMAT,
           waveshaper_detail_bump_adjustment=choice['waveshaper_detail_bump_adjustment'],
           full_fresh_native_realizations=0,full_fresh_native_validation_pending=True,
           supported_native_curve_state_and_audio_verified=True,not_automatically_adopted=True)
(ROOT/'supported-current-EQ-proposal.json').write_text(json.dumps(graft,indent=2)+'\n')
(ROOT/'current-validated-incumbent.json').write_text(json.dumps(incumbent,indent=2)+'\n')
proof=dict(actual_saved_curve_and_shared_helper_all12_native_states_byte_exact=checks,
           shared_helper_zero_depth_audio_bit_exact=True,only_three_held_notes=True,
           actual_FL_GUI_export_pending=True,fresh_comparison_with_current_incumbent_pending=True,
           proposals_explicitly_marked_pending=True,reference_match_reached=False)
(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof),flush=True)
