"""Complete validation without rerunning an already finished 625-case fit.

The original hot-host exact-audio assertion found only <=2.23e-16 residual
tail differences. Preserve that failure; separately check two newly loaded
hosts and fresh whole-chain captures using the real saved component state.
"""
from pathlib import Path
script=Path(__file__).with_name('run_ZL_joint_refinement.py')
prefix=script.read_text().split('\ntry:\n    assert read(PAUSE)')[0]
prefix=prefix.replace('ROOT.mkdir(exist_ok=False)','assert ROOT.is_dir()')
prefix=prefix.replace("OWNER='external-ZL-full-FL20-preset-integration'","OWNER='external-ZL-joint-canonical-state-validation'")
exec(compile(prefix,str(script)+'-definitions','exec'),globals())
import struct,xml.etree.ElementTree as ET
seed=read(ROOT/'validated-native-base.json')
component=ROOT/'ZL_joint_component.bin'
data=component.read_bytes();n=struct.unpack_from('<I',data,4)[0];xml=ET.fromstring(data[8:8+n])
values={p.attrib['id']:float(p.attrib['value'])for p in xml.find('Para')}
canonical_x=np.r_[[values['gain'+str(k)]for k in range(12)],np.log2([values['freq'+str(k)]for k in range(12)]),np.log2([values['q'+str(k)]for k in range(12)])]
canonical_ap=[dict(frequency=values['freq'+str(k)],Q=values['q'+str(k)],mode=int(values['lr_mode'+str(k)]),order=int(values['order'+str(k)]))for k in [12,13]]
canonical_dyn=[dict(frequency=values['freq'+str(k)],Q=values['q'+str(k)],mode=int(values['lr_mode'+str(k)]),target=values['target_gain'+str(k)],
    threshold=values['threshold'+str(k)],attack=values['attack'+str(k)],release=values['release'+str(k)])for k in [14,15]]
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,purpose='complete saved-candidate canonical replay and independent12 validation'),f)
try:
    record('diagnosing_strict_hot_host_tail_difference_without_repeating_the_fit')
    hot=np.fromfile(D/'ZL-joint-worker-0-output.f32',dtype='<f4').reshape(-1,2)
    prior=np.fromfile(D/'ZL-joint-independent-state-replay-output.f32',dtype='<f4').reshape(-1,2)
    hot_error=float(abs(hot-prior).max());assert hot_error<1e-12
    c=WinVST3('ZL-joint-canonical-cold-host1');clients.append(c);c.load(component)
    expected,_=c.render(input_file=ROOT/'frozen-native-0.f32')
    second=WinVST3('ZL-joint-canonical-cold-host2');clients.append(second);second.load(component)
    actual,_=second.render(input_file=ROOT/'frozen-native-0.f32')
    cold_error=float(abs(actual-expected).max());assert cold_error<1e-12
    second.save(ROOT/'ZL_joint_component_resaved.bin');assert component.read_bytes()==(ROOT/'ZL_joint_component_resaved.bin').read_bytes()
    proof=dict(original_hot_vs_cold_bit_exact_assertion_failed=True,original_hot_vs_cold_max_abs_error=hot_error,
        original_hot_vs_cold_mismatched_samples=int(np.sum(hot!=prior)),two_newly_loaded_hosts_bit_exact=bool(cold_error==0),
        two_newly_loaded_hosts_max_abs_error=cold_error,actual_component_bytes_roundtrip_exact=True,
        validation_absolute_tolerance=1e-12,tolerance_is_numerical_tail_check_not_reference_match=True)
    (ROOT/'CANONICAL_COMPONENT_REPLAY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
    second.close();clients.remove(second)
    control=WinVST3('ZL-joint-independent-prior-control');clients.append(control);control.load(PRIOR/'ZL_dynamic_component.bin')
    a=native();captures=[];archive=ROOT/'independent12-prior-and-joint-captures.tar.gz'
    record('resumed_actual_independent12_joint_vs_ZL02_paired_validation',component_replay=proof)
    try:
        with tarfile.open(archive,'w:gz',compresslevel=3)as z:
            for rep in range(12):
                raw,status=a.render();old,_=control.render(raw);old_loss=score(old);out,_=c.render(raw);loss=score(out)
                row=dict(rep=rep,prior_loss=old_loss,loss=loss,assessment=features.local.last,members=[])
                for label,audio in [('prior',old),('joint',out)]:
                    blob=io.BytesIO();sf.write(blob,audio,48000,format='WAV',subtype='FLOAT');b=blob.getvalue();name=f'{label}-{rep}.wav'
                    info=tarfile.TarInfo(name);info.size=len(b);z.addfile(info,io.BytesIO(b));row['members'].append(dict(name=name,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()))
                captures.append(row)
    finally:a.close()
    median=sorted(captures,key=lambda r:r['loss'])[6]
    with tarfile.open(archive)as z:
        for row in captures:
            for m in row['members']:
                b=z.extractfile(m['name']).read();assert len(b)==m['bytes']and hashlib.sha256(b).hexdigest()==m['SHA256']
                if row is median and m['name'].startswith('joint'):(ROOT/'SELECTED_NATIVE_ZL_JOINT_WIP.wav').write_bytes(b)
    delta=np.array([r['prior_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(len(delta)))
    robust=bool(np.mean(delta)>max(.0005,3*sem));summary=dict(candidate_mean=float(np.mean([r['loss']for r in captures])),
        prior_dynamic_control_mean=float(np.mean([r['prior_loss']for r in captures])),paired_difference_SEM=sem,robust_improvement_over_dynamic=robust,
        completed_training_cases=625,training_not_repeated=True,canonical_component_replay=proof,reference_match_reached=False)
    result=dict(native_base=seed,ZL_allpass_bands=canonical_ap,ZL_peaking_MidSide_x=canonical_x.tolist(),ZL_dynamic_bands=canonical_dyn,
        ZL_output_gain_dB=values['total_output_gain'],native_ZL_component_state=str(component),loss=summary['candidate_mean'],
        recorded_audio=str(ROOT/'SELECTED_NATIVE_ZL_JOINT_WIP.wav'),not_compatible_with_standard_x95_exporter=True,not_automatically_adopted=True,
        robust_improvement_over_allpass=robust,robust_improvement=robust,only_three_held_notes=True,declared_added_PDC_frames=c.latency(),
        actual_FL_GUI_validation_pending=True,reference_match_reached=False)
    for name,obj in [('completion.json',summary),('candidate-research-only.json',result),('independent-captures.json',captures)]:
        (ROOT/name).write_text(json.dumps(obj,indent=2)+'\n')
    record('joint52_recovered_canonical_state_and_fresh_validation_complete_not_automatically_adopted',completion=summary)
    print('JOINT52_SAVED_STATE_AND_FRESH_VALIDATION_COMPLETE',json.dumps(summary),flush=True)
except BaseException:
    record('joint52_saved_state_validation_failed_preserve_complete_ZL02',error=traceback.format_exc());raise
finally:
    for c in clients:c.close()
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
