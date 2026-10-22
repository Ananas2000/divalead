"""Jointly refit an actual supported95 candidate, then compare fresh whole graphs.

This wrapper holds the four numerical slots and never replaces the incumbent.
No reference sample is used as input, and no source/MIDI changes are introduced.
"""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
candidate_path=Path(sys.argv[1]);ROOT=Path(sys.argv[2]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'paired-isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
trial=json.loads(candidate_path.read_text());assert len(trial['x'])==95 and trial['source_manifest']
start=time.monotonic()
with four_native_slots(ROOT) as state:
    incumbent=json.loads(Path(state['best_candidate']).read_text());assert len(incumbent['x'])==95
    assert incumbent['source_manifest']['source_audio_SHA256']==trial['source_manifest']['source_audio_SHA256']
    assert incumbent['source_manifest']['source_preset_SHA256']==trial['source_manifest']['source_preset_SHA256']
    manifest=trial['source_manifest'];assert hashlib.sha256(Path(manifest['source_audio']).read_bytes()).hexdigest()==manifest['source_audio_SHA256']
    (ROOT/'incumbent.json').write_text(json.dumps(incumbent,indent=2)+'\n')
    (ROOT/'input-candidate.json').write_text(json.dumps(trial,indent=2)+'\n')
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_LBFGS_MAXCALLS=os.environ.get('DIVALEAD_PROFILE_MAXCALLS','6500'),DIVALEAD_LBFGS_MAXITER='50')
    with (ROOT/'refit.log').open('w') as f:
        subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'search_native_joint_EQ_LBFGS.py'),str(ROOT/'input-candidate.json'),str(ROOT/'refit')],
            env=env,stdout=f,stderr=f,check=True)
    fitted=json.loads((ROOT/'refit/full-validated-candidate.json').read_text())
    features=FeaturesOriginal(target);captures={}
    for label,candidate in [('incumbent',incumbent),('profile',fitted)]:
        c=NativeChain(Path(candidate['source_manifest']['native_input']),ROOT.name+'-paired-'+label,fl_graph=True,phase_pair=True)
        rows=[]
        try:
            apply(c,candidate['x'])
            for rep in range(6):
                y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(np.array(candidate['x'])[:28]**2))*.00000025
                p=ROOT/f'{label}-full-{rep}.wav';sf.write(p,y,48000,subtype='FLOAT')
                rows.append(dict(loss=loss,audio=str(p),assessment=features.local.last,native_status=status))
        finally:c.close()
        captures[label]=rows
    old=np.array([r['loss'] for r in captures['incumbent']]);new=np.array([r['loss'] for r in captures['profile']])
    se=float(np.hypot(old.std(),new.std())/np.sqrt(6));robust=float(old.mean()-new.mean())>max(.0005,3*se)
    median=sorted(captures['profile'],key=lambda r:r['loss'])[3]
    result=dict(fitted,loss=float(new.mean()),realization_losses=new.tolist(),realization_standard_deviation=float(new.std()),
        seed_fresh_mean_loss=float(old.mean()),fresh_mean_standard_error=se,robust_improvement=robust,
        recorded_audio=median['audio'],recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],
        source95_profile_vs_incumbent_validated=True,not_automatically_accepted=True,
        source_and_incoming_MIDI_unchanged=True,full_fresh_native_validation_pending=False,full_fresh_native_realizations=6,
        original_reference_match_reached=False)
    (ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'paired-profile-comparison.json').write_text(json.dumps(captures,indent=2)+'\n')
    (ROOT/'completion.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        actual_native95_joint76_profile=True,old_mean=float(old.mean()),new_mean=float(new.mean()),
        robust_improvement=robust,standard_error_of_mean_difference=se,only_three_held_notes=True,
        source_and_incoming_MIDI_unchanged=True,seconds=time.monotonic()-start,match_reached=False),indent=2)+'\n')
    print('ACTUAL_SUPPORTED95_PROFILE_COMPLETE',float(new.mean()),float(old.mean()),robust,flush=True)
