"""Profile a physical source change with actual native EQ re-optimization.

Screening a source under fixed FX can miss a better joint solution. This trial
does not replace the running incumbent without a paired original-reference win.
"""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,time
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply

ROOT=W/'native-Diva-cutoff148-profile-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'paired-isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
N=Path('/workspace/divalead-work/native-low-latency-effects');S=Path('/workspace/divalead-setup')
V=Path('/workspace/divalead/diva-lead/v83-wip')
case=W/'native-Diva-sync-PW-fine-screen-01/cutoff-148'
source=N/'source-bases/PW-keyfollow-depth-1-cutoff148';source.mkdir(exist_ok=False)
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
def params(p):
    return {int(v[0]):dict(normalized=float(v[1]),name=v[2],display=v[3]) for v in
            (line.split('\t') for line in p.read_text().splitlines()[1:])}

with four_native_slots(ROOT) as state:
    incumbent=json.loads(Path(state['best_candidate']).read_text());assert len(incumbent['x'])==95
    (ROOT/'incumbent.json').write_text(json.dumps(incumbent,indent=2)+'\n')
    for name in ['Diva.h2p','Diva_source.wav','all281.tsv','Diva.log','verification.json']:
        shutil.copyfile(case/name,source/name)
    original=params(V/'verification/Diva_all281.tsv');new=params(source/'all281.tsv')
    changed={i for i in original if original[i]['normalized']!=new[i]['normalized']};assert changed=={108,148}
    fresh=ROOT/'fresh-Diva';fresh.mkdir()
    commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0',
              'dump '+win(fresh/'all281.tsv'),'render '+win(fresh/'Diva_source.wav'),'quit']
    env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),
        WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    with (fresh/'Diva.log').open('w') as f:
        subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',
            r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(source/'Diva.h2p')],
            input='\n'.join(commands)+'\n',text=True,env=env,stdout=f,stderr=f,check=True,timeout=120)
    text=(fresh/'Diva.log').read_text();assert 'ERROR ' not in text
    events=[list(map(int,line.split()[1:])) for line in text.splitlines() if line.startswith('NOTE ')]
    expected=[[e[k] for k in ['frame','status','pitch','velocity']] for e in json.loads((V/'verification/MIDI_note_events_48k.json').read_text())['events']]
    assert events==expected and (fresh/'all281.tsv').read_bytes()==(source/'all281.tsv').read_bytes()
    a,rate=sf.read(source/'Diva_source.wav',dtype='float32');b,rate2=sf.read(fresh/'Diva_source.wav',dtype='float32')
    assert rate==rate2==48000;np.testing.assert_array_equal(a,b)
    proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_fresh_Diva_plugin_render=True,
        preset=str(source/'Diva.h2p'),preset_SHA256=hashlib.sha256((source/'Diva.h2p').read_bytes()).hexdigest(),
        source_audio=str(source/'Diva_source.wav'),source_audio_file_SHA256=hashlib.sha256((source/'Diva_source.wav').read_bytes()).hexdigest(),
        decoded_float32_SHA256=hashlib.sha256(a.astype('<f4').tobytes()).hexdigest(),
        raw_audio_bit_exact_against_variant_fixture=True,all281_exact_against_variant=True,
        same_all12_incoming_MIDI_events=True,only_three_held_notes_per_phrase=True,
        only_changed_parameters_vs_v83=sorted(changed),frames=len(a),sample_rate=rate,reference_match_reached=False)
    (source/'FRESH_DIVA_SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
    padded=ROOT/'source-with-tail.wav';sf.write(padded,np.pad(a,((0,32768),(0,0))),48000,subtype='FLOAT')
    manifest=dict(source_preset=str(source/'Diva.h2p'),source_audio=str(source/'Diva_source.wav'),native_input=str(padded),
        source_preset_SHA256=proof['preset_SHA256'],source_audio_SHA256=proof['source_audio_file_SHA256'],
        changed_parameters={new[i]['name']:dict(before=original[i],after=new[i]) for i in sorted(changed)},
        all281_audited=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_and_envelopes_unchanged=True,
        proof=str(source/'verification.json'),fresh_proof=str(source/'FRESH_DIVA_SOURCE_PROOF.json'))
    seed=dict(incumbent,source_manifest=manifest,not_accepted_source_profile_trial=True)
    seedpath=ROOT/'source-refit-seed.json';seedpath.write_text(json.dumps(seed,indent=2)+'\n')
    env.update(DIVALEAD_LBFGS_MAXCALLS='4000',DIVALEAD_LBFGS_MAXITER='40')
    with (ROOT/'refit.log').open('w') as f:
        subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(W/'search_native_source_LBFGS.py'),str(seedpath),str(ROOT/'refit')],
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
    old=np.array([r['loss'] for r in captures['incumbent']]);newloss=np.array([r['loss'] for r in captures['profile']])
    se=float(np.hypot(old.std(),newloss.std())/np.sqrt(6));robust=float(old.mean()-newloss.mean())>max(.0005,3*se)
    median=sorted(captures['profile'],key=lambda r:r['loss'])[3]
    result=dict(fitted,loss=float(newloss.mean()),realization_losses=newloss.tolist(),realization_standard_deviation=float(newloss.std()),
        seed_fresh_mean_loss=float(old.mean()),fresh_mean_standard_error=se,robust_improvement=robust,
        recorded_audio=median['audio'],recorded_render_loss=median['loss'],original_reference_assessment=median['assessment'],
        profile_source_vs_incumbent_validated=True,not_accepted_source_profile_trial=not robust)
    (ROOT/'full-validated-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'paired-source-comparison.json').write_text(json.dumps(captures,indent=2)+'\n')
    (ROOT/'completion.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        actual_Diva_source_profile_and_native_refit=True,old_source_mean=float(old.mean()),new_source_mean=float(newloss.mean()),
        robust_improvement=robust,standard_error_of_mean_difference=se,only_three_held_notes=True,match_reached=False),indent=2)+'\n')
    print('ACTUAL_DIVA_CUTOFF_PROFILE_COMPLETE',float(newloss.mean()),float(old.mean()),robust,flush=True)
