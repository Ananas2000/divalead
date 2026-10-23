"""Independent complete native comparisons after conditional source/EQ profiles."""
from pathlib import Path
import json,os,sys,io,tarfile,hashlib
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate,validate_curve_candidate

ROOT=Path(sys.argv[1]);ROOT.mkdir(exist_ok=False)
incumbent=json.loads(Path(sys.argv[2]).read_text())
proposals=[json.loads(Path(p).read_text())for p in sys.argv[3:]];assert proposals
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal()

def capture(candidate,label,reps=12):
    validate_curve_candidate(candidate);v=np.array(candidate['x'])
    c=NativeChain(candidate['source_manifest']['native_input'],ROOT.name+'-'+label,
                  fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    def configure():
        apply_candidate(c,v,candidate)
        for i,value in candidate['chorus_overrides'].items():c.set(3,int(i),int(value))
    rows=[]
    try:
        configure();y,_=c.render();features.residual(y[:288000]);gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
        v[28:30]=np.clip(v[28:30]+10*np.log10(gain),-18,18);configure()
        archive=ROOT/(label+'-captures.tar.gz')
        with tarfile.open(archive,'w:gz',compresslevel=3)as z:
            for rep in range(reps):
                y,status=c.render();r=features.residual(y[:288000]);loss=float(r@r)+float(np.sum(v[:28]**2))*.00000025
                member=f'{label}-{rep}.wav';blob=io.BytesIO();sf.write(blob,y,48000,format='WAV',subtype='FLOAT');data=blob.getvalue()
                info=tarfile.TarInfo(member);info.size=len(data);z.addfile(info,io.BytesIO(data))
                rows.append(dict(loss=loss,audio_archive=str(archive),archive_member=member,
                    WAV_SHA256=hashlib.sha256(data).hexdigest(),assessment=features.local.last,native_status=status))
    finally:c.close()
    median=sorted(rows,key=lambda row:row['loss'])[len(rows)//2];values=[row['loss']for row in rows]
    with tarfile.open(archive,'r:gz')as z:
        assert len(z.getmembers())==reps
        for row in rows:
            data=z.extractfile(row['archive_member']).read();assert hashlib.sha256(data).hexdigest()==row['WAV_SHA256']
            if row is median:
                audio=ROOT/(label+'-median.wav');audio.write_bytes(data);row['audio']=str(audio)
    median['all_captures_losslessly_saved_and_verified']=True

    result=dict(candidate,x=v.tolist(),loss=float(np.mean(values)),realization_losses=values,
        realization_standard_deviation=float(np.std(values)),recorded_audio=median['audio'],
        recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],
        full_fresh_native_realizations=reps,full_fresh_native_validation_pending=False,
        reference_match_reached=False,actual_FL_GUI_validation_pending=True)
    (ROOT/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('ACTUAL_SUPPORTED_NATIVE_PAIR',label,result['loss'],flush=True);return result

initial_control=capture(incumbent,'selection-control')
checked=[capture(candidate,'selection-proposal-'+str(k))for k,candidate in enumerate(proposals)]
selected=min(checked,key=lambda row:row['loss'])
independent=capture(selected,'independent-selected',24);control=capture(incumbent,'independent-control',24)
sem=float(np.hypot(independent['realization_standard_deviation'],control['realization_standard_deviation'])/np.sqrt(24))
robust=control['loss']-independent['loss']>max(.0005,3*sem)
chosen=independent if robust else control
chosen.update(robust_improvement=bool(robust),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=sem,
              conditional_source_profile_independent_selection_and_holdout=True,
              not_automatically_adopted=not bool(robust),reference_match_reached=False)
(ROOT/'full-validated-candidate.json').write_text(json.dumps(chosen,indent=2)+'\n')
(ROOT/'paired-fresh-control.json').write_text(json.dumps(dict(control=control,selected=independent,
    selection_candidates=checked,SEM=sem,robust_improvement=bool(robust)),indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(proposals=len(proposals),selection_captures_per_path=12,independent_captures_per_path=24,
    independent_selected_mean=independent['loss'],independent_control_mean=control['loss'],SEM=sem,
    robust_improvement=bool(robust),actual_native_DLL_audio=True,match_reached=False),indent=2)+'\n')
