"""Check explicit curve replay against its actual saved DLL state, then fresh6+6."""
from pathlib import Path
import hashlib,json,os,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply
from fl20_curve import apply_candidate,FORMAT,curve_metadata

B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=B/'extended-WS-integration-audit-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal

assert json.loads((N/'fl20-corrected-search.pause').read_text())['owner']=='validated-WS-curve-integration'
deadline=time.monotonic()+120
while True:
    state=json.loads((N/'FL20_CORRECTED_SEARCH_CONTROLLER.json').read_text())
    if state['phase']=='paused_by_control_or_actual_disk_reserve':break
    assert time.monotonic()<deadline;time.sleep(1)
experiment=B/'fl20-WS-extended-curve-01'
choice=json.loads((experiment/'full-validated-candidate.json').read_text());assert choice['robust_improvement']
incumbent=json.loads((N/'FL20-corrected/BEST_CANDIDATE.json').read_text())
oldseed=json.loads((experiment/'seed.json').read_text())
assert incumbent['x']==oldseed['x']and incumbent['chorus_overrides']==oldseed['chorus_overrides'],'The current FX improved; re-pair the new curve with that actual current incumbent first'
assert incumbent['source_manifest']==choice['source_manifest']
choice.update(waveshaper_curve_format=FORMAT,not_compatible_with_standard_x95_exporter=False,
              curve_playback_and_export_integration_version=1)
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

features=FeaturesOriginal();results={}
for label,candidate in [('control',incumbent),('extended',choice)]:
    v=np.array(candidate['x']);c=NativeChain(source,ROOT.name+'-fresh-'+label,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    try:
        configure(c,v,candidate);y,_=c.render();features.residual(y[:288000])
        gain=features.local.last['diagnostics']['global_RMS_gain_for_AB'];v[28:30]=np.clip(v[28:30]+10*np.log10(gain),-18,18)
        configure(c,v,candidate);captures=[]
        for rep in range(6):
            y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
            path=ROOT/f'{label}-fresh-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT')
            captures.append(dict(loss=loss,audio=str(path),assessment=features.local.last,native_status=status))
    finally:c.close()
    median=sorted(captures,key=lambda row:row['loss'])[3];values=[row['loss']for row in captures]
    results[label]=dict(candidate,x=v.tolist(),loss=float(np.mean(values)),realization_losses=values,
        realization_standard_deviation=float(np.std(values)),original_reference_assessment=median['assessment'],
        recorded_audio=median['audio'],recorded_render_loss=median['loss'],full_fresh_native_realizations=6,
        full_fresh_native_validation_pending=False,reference_match_reached=False)
control=results['control'];selected=results['extended']
sem=float(np.hypot(control['realization_standard_deviation'],selected['realization_standard_deviation'])/np.sqrt(6))
robust=control['loss']-selected['loss']>max(.0005,3*sem)
selected.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=sem,
                shared_curve_helper_actual_DLL_state_and_audio_verified=True,not_automatically_adopted=True,
                model_family='FL20_corrected_context_supported_native_extended_curve')
(ROOT/'full-validated-candidate.json').write_text(json.dumps(selected,indent=2)+'\n')
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(control=control,selected=selected,SEM=sem),indent=2)+'\n')
proof=dict(actual_saved_curve_and_shared_helper_all12_native_states_byte_exact=checks,
           shared_helper_zero_depth_audio_bit_exact=True,full_native_fresh_control=control['loss'],
           full_native_fresh_extended=selected['loss'],SEM=sem,robust_improvement=bool(robust),
           only_three_held_notes=True,actual_FL_GUI_export_pending=True,reference_match_reached=False)
(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof),flush=True)
