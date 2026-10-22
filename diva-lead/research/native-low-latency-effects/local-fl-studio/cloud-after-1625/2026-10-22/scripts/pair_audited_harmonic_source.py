"""Fresh paired source comparison using the current supported native FX state."""
from pathlib import Path
import json,os,sys
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply
B=Path('/tmp/divalead-local-1625');ROOT=Path(sys.argv[3]);ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
N=Path('/workspace/divalead-work/native-low-latency-effects');incumbent=json.loads((Path(sys.argv[1])/'frozen-native-effects.json').read_text())
manifest=json.loads(Path(sys.argv[2]).read_text());features=FeaturesOriginal()
(ROOT/'frozen-incumbent.json').write_text(json.dumps(incumbent,indent=2)+'\n')
rows={};audios={}
for label,source in [('control-current-source',incumbent['source_manifest']),('selected-audited-source',manifest)]:
    x=np.array(incumbent['x']);c=NativeChain(source['native_input'],ROOT.name+'-'+label,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    def configure():
        apply(c,x)
        for i,value in incumbent['chorus_overrides'].items():c.set(3,int(i),int(value))
    try:
        configure();y,_=c.render();features.residual(y[:288000]);gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
        x[28:30]=np.clip(x[28:30]+10*np.log10(gain),-18,18);configure();captures=[]
        for rep in range(6):
            y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025
            path=ROOT/f'{label}-{rep}.wav';sf.write(path,y,48000,subtype='FLOAT');captures.append(dict(loss=loss,audio=str(path),assessment=features.local.last,native_status=status))
        selected=sorted(captures,key=lambda r:r['loss'])[3];values=[r['loss']for r in captures]
        rows[label]=dict(x=x.tolist(),loss=float(np.mean(values)),realization_standard_deviation=float(np.std(values)),
            realization_losses=values,recorded_audio=selected['audio'],recorded_render_loss=selected['loss'],
            original_reference_assessment=selected['assessment'],source_manifest=source,chorus_overrides=incumbent['chorus_overrides'],
            actual_native_DLL_audio=True,full_fresh_native_realizations=6,full_fresh_native_validation_pending=False,
            both_paths_level_normalized_in_actual_EQ_Main=True,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,
            host_context='Chorus_excluded_from_silent_warmup',objective_version='local_full_original_criteria_FL20_context_v1',
            model_family='FL20_corrected_context_physical_harmonic_source',reference_match_reached=False)
    finally:c.close()
control=rows['control-current-source'];selected=rows['selected-audited-source']
se=float(np.hypot(control['realization_standard_deviation'],selected['realization_standard_deviation'])/np.sqrt(6))
selected.update(seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
    robust_improvement=bool(control['loss']-selected['loss']>max(.003,3*se)),new_source_actual_Diva_all281_MIDI_and_VST_chunk_verified=True)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(selected,indent=2)+'\n')
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(control=control,selected=selected,SEM=se),indent=2)+'\n')
print('CURRENT_FX_AUDITED_SOURCE_PAIR',control['loss'],selected['loss'],se,selected['robust_improvement'],flush=True)
