"""Fresh paired stock-clipper control with BOTH paths normalized in native routing."""
from pathlib import Path
import json,os
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
ROOT=W/'native-post-softclip-screen-01'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'normalized-paired-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
seed=json.loads((ROOT/'seed.json').read_text());best=json.loads((ROOT/'full-validated-candidate.json').read_text())
features=FeaturesOriginal(target);target_rms=float(np.sqrt(np.mean(target.astype(float)**2)));rows={}
with four_native_slots(ROOT/'normalized-paired'):
    c=NativeChain(Path(seed['source_manifest']['native_input']),'native-postclip-level-control',fl_graph=True,phase_pair=True)
    try:
        for label,row,enabled in [('bypass',seed,False),('clipper',best,True)]:
            apply(c,row['x'])
            if enabled:
                extension=best['post_clip_extension'];c.bypass(9,False);c.set(9,0,extension['threshold_raw']);c.set(9,1,160)
            captures=[];measurements=[]
            for rep in range(2):
                y,status=c.render();measurements.append(float(np.sqrt(np.mean(y[:len(target)].astype(float)**2))))
            gain=target_rms/float(np.mean(measurements));assert .01<gain<1.87;c.gain(2,gain)
            for rep in range(6):
                y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(np.array(row['x'])[:28]**2))*.00000025
                captures.append(dict(loss=loss,assessment=features.local.last,native_status=status))
            rows[label]=dict(native_SUM_fader_gain=gain,native_SUM_fader_dB=float(20*np.log10(gain)),captures=captures,
                mean_loss=float(np.mean([r['loss'] for r in captures])),std_loss=float(np.std([r['loss'] for r in captures])))
    finally:c.close()
old=rows['bypass'];new=rows['clipper'];se=float(np.hypot(old['std_loss'],new['std_loss'])/np.sqrt(6))
robust=old['mean_loss']-new['mean_loss']>max(.0005,3*se)
report=dict(both_paths_level_normalized_by_actual_native_mixer_gain=True,captures_per_path=6,
    rows=rows,standard_error_of_mean_difference=se,robust_improvement=bool(robust),only_three_held_notes=True,match_reached=False)
(ROOT/'FRESH_BOTH_LEVEL_NORMALIZED_CONTROL.json').write_text(json.dumps(report,indent=2)+'\n')
print('POSTCLIP_BOTH_LEVELS_FRESH',old['mean_loss'],new['mean_loss'],robust,flush=True)
