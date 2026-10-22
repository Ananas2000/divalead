"""Compare actual post-LR research graphs with the latest supported incumbent.

This deliberately does not migrate research metadata or write a project.
Selection uses12 fresh native captures per path; independent holdout uses24.
"""
from pathlib import Path
import json,os,sys,subprocess
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate,validate_curve_candidate
ROOT=Path(sys.argv[1]);ROOT.mkdir(exist_ok=False)
incumbent=json.loads(Path(sys.argv[2]).read_text());proposals=[json.loads(Path(p).read_text())for p in sys.argv[3:]]
assert proposals
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal()
FREQ=np.array([80,250,800,2000,5000,9000,14000],float)
RAW=np.rint(np.log(FREQ/20)/np.log(1000)*65536).astype(int)
def parts(candidate):
    base=dict(candidate);post=base.get('post_LR_EQ_and_SS_controls')
    if post is None and base.get('post_LR_EQ_gains')is not None:post=[*base['post_LR_EQ_gains'],0.,0.,0.,0.]
    if post is not None:
        assert len(post)==20 and np.isfinite(post).all()
        assert np.array_equal(candidate['post_LR_EQ_frequencies_Hz'],FREQ)
        assert candidate['post_LR_EQ_bandwidth_raw']==9830
        assert candidate['not_compatible_with_standard_x95_exporter']
        base['not_compatible_with_standard_x95_exporter']=False
    validate_curve_candidate(base);return base,None if post is None else np.array(post)
def configure(c,v,candidate,post):
    base,_=parts(candidate);apply_candidate(c,v,base)
    for k,value in candidate['chorus_overrides'].items():c.set(3,int(k),int(value))
    if post is None:return
    for node,offset,main in [(1,0,14),(2,7,15)]:
        c.bypass(node,False)
        for band in range(7):
            c.set(node,band,int(round(post[offset+band]*100)));c.set(node,7+band,int(RAW[band]))
            c.set(node,14+band,9830);c.set(node,21+band,6);c.set(node,28+band,0)
        c.set(node,35,int(round(post[main]*100)))
    for node,values in [(15,[0,12800,0,0,round(post[16]*1000),round(post[17]*1000)]),(16,[0,0,12800,0,round(post[18]*1000),round(post[19]*1000)])]:
        for i,value in enumerate(values):c.set(node,i,int(value))
def capture(candidate,label,reps):
    _,post=parts(candidate);v=np.array(candidate['x'])
    assert candidate['source_manifest']['source_audio_SHA256']==incumbent['source_manifest']['source_audio_SHA256']
    c=NativeChain(candidate['source_manifest']['native_input'],ROOT.name+'-'+label,fl_graph=True,phase_pair=True,
        side_phase_pair=post is not None,engine_override='fl_native_fl20_postLR_host.exe'if post is not None else'fl_native_fl20_host.exe')
    rows=[]
    try:
        configure(c,v,candidate,post);y,_=c.render();features.residual(y[:288000]);gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
        v[28:30]=np.clip(v[28:30]+10*np.log10(gain),-18,18);configure(c,v,candidate,post)
        for rep in range(reps):
            y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
            path=ROOT/f'{label}-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT')
            rows.append(dict(loss=loss,audio=str(path),assessment=features.local.last,native_status=status))
    finally:c.close()
    median=sorted(rows,key=lambda row:row['loss'])[reps//2];values=[r['loss']for r in rows]
    result=dict(candidate,x=v.tolist(),loss=float(np.mean(values)),realization_losses=values,
        realization_standard_deviation=float(np.std(values)),recorded_audio=median['audio'],recorded_render_loss=median['loss'],
        original_reference_assessment=median['assessment'],full_fresh_native_realizations=reps,
        full_fresh_native_validation_pending=False,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
    (ROOT/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n');print('ACTUAL_POST_LR_CURRENT_COMPARISON',label,result['loss'],flush=True);return result
control_selection=capture(incumbent,'selection-control',12)
checked=[capture(p,'selection-proposal-'+str(k),12)for k,p in enumerate(proposals)]
selected=min(checked,key=lambda r:r['loss'])
independent=capture(selected,'independent-selected',24);control=capture(incumbent,'independent-control',24)
sem=float(np.hypot(independent['realization_standard_deviation'],control['realization_standard_deviation'])/np.sqrt(24))
robust=control['loss']-independent['loss']>max(.0005,3*sem)
chosen=independent if robust else control
chosen.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=sem,
    research_graph_not_automatically_adopted=True,reference_match_reached=False)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(chosen,indent=2)+'\n')
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(control=control,selected=independent,SEM=sem,
    selection_candidates=checked,robust_improvement=bool(robust)),indent=2)+'\n')
restored=Path('/tmp/divalead-local-1625/corrected-restoration-WIP13-local4-check')
restored_proof=restored/'actual-DLL-restoration-check/PROOF.json'
if restored.exists()and not restored_proof.exists():
    subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(restored/'verify_corrected_restoration.py'),str(restored)],check=True)
restored_verified=bool(restored_proof.exists()and json.loads(restored_proof.read_text()).get('actual_native_DLL_replay'))
(ROOT/'completion.json').write_text(json.dumps(dict(proposals=len(proposals),selection_captures_per_path=12,
    independent_captures_per_path=24,independent_selected_mean=independent['loss'],independent_control_mean=control['loss'],
    SEM=sem,robust_improvement=bool(robust),published_WIP13_restored_actual_native_replay_verified=restored_verified,
    new_graph_export_integration_still_pending=True,match_reached=False),indent=2)+'\n')
