"""Finite real-Windows-VST3 study after the validated three-held-note native chain.

All-pass filters change relative harmonic phase without a magnitude-EQ target.
No reference audio enters either the native graph or the VST3. This is guarded
research until FL state/preset export and independent replay are integrated.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,hashlib,io,json,os,queue,subprocess,tarfile,threading,time,traceback
import numpy as np
import soundfile as sf
from win_vst3 import WinVST3,D,S,win

B=D.parent;W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=D/'ZL-allpass-original-reference-01';ROOT.mkdir(exist_ok=False)
STATE=N/'FL20_EXTERNAL_ZL_VST3_STUDY.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='external-ZL-EQ-real-VST3-study-after-Native16'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
from native_chain import NativeChain
from fl20_curve import apply_candidate,validate_curve_candidate
from native_note_residue import measure_native_raw

def read(p):return json.loads(Path(p).read_text())
def identity(pid):
    p=Path('/proc')/str(pid)
    try:
        stat=(p/'stat').read_text().split()
        if stat[2]=='Z':return None
        return dict(PID=pid,starttime=stat[21],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def record(phase,**extra):
    obj=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,
        root=str(ROOT),only_three_held_notes=True,actual_official_Windows_VST3=True,production_source_and_graph_not_replaced=True,
        actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra)
    temp=STATE.with_suffix('.partial');temp.write_text(json.dumps(obj,indent=2)+'\n');temp.replace(STATE)

features=FeaturesOriginal();seed=None;clients=[];pool=queue.Queue();mutex=threading.Lock();rows=[];start=time.monotonic()
params={r['title']:r for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def id(title):return int(params[title]['id'])
def score(y):
    r=features.residual(y[:288000]);return float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
def native():
    c=NativeChain(seed['source_manifest']['native_input'],ROOT.name+'-fresh-native',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    apply_candidate(c,np.array(seed['x']),seed)
    for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
    return c
def configure(c,bands):
    for i in range(2):
        c.set(id('Filter Status'+str(i)),1 if i<len(bands)else 0)
        if i<len(bands):
            band=bands[i];c.set(id('Filter Type'+str(i)),.9)
            c.set(id('LRMode'+str(i)),band['mode']/4)
            c.set(id('Order'+str(i)),band['order']/6)
            c.text(id('Freq'+str(i)),format(band['frequency'],'.12g'))
            c.text(id('Q'+str(i)),format(band['Q'],'.12g'))
            c.text(id('Gain'+str(i)),'0')

def evaluate(case,phase=0,save=True):
    label,bands=case;c=pool.get()
    try:
        configure(c,bands);y,status=c.render(input_file=ROOT/f'frozen-native-{phase}.f32');loss=score(y)
        assert c.latency()==0,'Reject plugin settings that introduce declared latency'
        row=dict(label=label,bands=bands,loss=loss,assessment=features.local.last,native_status=status)
        if save:
            with mutex:
                rows.append(row)
                if loss<min([r['loss']for r in rows[:-1]],default=float('inf')):
                    (ROOT/'best-training.json').write_text(json.dumps(row,indent=2)+'\n')
                    sf.write(ROOT/'best-training-WIP.wav',y,48000,subtype='FLOAT');print('ZL_ACTUAL_BEST',len(rows),label,loss,flush=True)
        return row
    finally:pool.put(c)

try:
    assert read(PAUSE)['owner']==OWNER
    deadline=time.monotonic()+1800
    while True:
        main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');now=identity(main['controller']['PID'])
        assert now and now['starttime']==main['controller']['starttime']
        if main['phase']=='paused_by_control_or_actual_disk_reserve':break
        assert time.monotonic()<deadline;record('waiting_for_current_native_cohort_and_all_fresh_checks',main_progress=main.get('progress'));time.sleep(3)
    seed=read(N/'FL20-corrected/BEST_CANDIDATE.json');validate_curve_candidate(seed)
    (ROOT/'validated-native-base.json').write_text(json.dumps(seed,indent=2)+'\n')
    # Launch the actual supplied Diva again, without changing a single parameter.
    record('fresh_actual_Diva_source_281_MIDI_and_raw_audio_check')
    fresh=ROOT/'fresh-Diva-three-held-source';fresh.mkdir();manifest=seed['source_manifest']
    env=dict(os.environ,WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
    commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(fresh/'all281.tsv'),
        'save '+win(fresh/'Diva_VST_chunk.bin'),'render '+win(fresh/'Diva_source.wav'),'quit']
    with(fresh/'Diva.log').open('w')as log:
        subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',
            r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(manifest['source_preset'])],
            input='\n'.join(commands)+'\n',text=True,stdout=log,stderr=log,env=env,check=True,timeout=120)
    assert(fresh/'all281.tsv').read_bytes()==(Path(manifest['source_preset']).parent/'all281.tsv').read_bytes()
    source,rate=sf.read(manifest['source_audio'],dtype='float32');again,rate2=sf.read(fresh/'Diva_source.wav',dtype='float32')
    assert rate==rate2==48000;np.testing.assert_array_equal(source,again)
    assert(fresh/'Diva_VST_chunk.bin').read_bytes()==Path(manifest['source_VST_chunk']).read_bytes()
    events=[line for line in(fresh/'Diva.log').read_text().splitlines()if line.startswith('NOTE ')]
    expected=[line for line in(Path(manifest['source_preset']).parent/'Diva.log').read_text().splitlines()if line.startswith('NOTE ')]
    assert events==expected and len(events)==12
    (fresh/'PROOF.json').write_text(json.dumps(dict(actual_fresh_Diva_execution=True,all281_exact=True,all12_MIDI_events_exact=True,
        raw_audio_bit_exact=True,real_effGetChunk_exact=True,three_held_notes_per_phrase=True,source_unmodified=True),indent=2)+'\n')
    record('rendering_three_actual_native_Chorus_realizations_for_training_and_two_holdouts')
    c=native();base_losses=[]
    try:
        for phase in range(3):
            y,status=c.render();y.astype('<f4').tofile(ROOT/f'frozen-native-{phase}.f32');base_losses.append(score(y))
    finally:c.close()
    c=WinVST3('ZL-real-audit');clients.append(c);flat=[]
    try:
        original=np.fromfile(ROOT/'frozen-native-0.f32',dtype='<f4').reshape(-1,2)
        for block in [128,512,1024]:
            c.block(block);y,status=c.render(original);error=float(abs(y-original).max());assert error==0,(block,error);flat.append(dict(block=block,flat_native_audio_bit_exact=True,declared_PDC=c.latency()))
        c.block(512);tone=np.sin(2*np.pi*1000*np.arange(48000)/48000)*.1;tone=np.c_[tone,tone].astype('float32')
        c.text(id('Filter Status0'),'On');c.text(id('Gain0'),'6');c.text(id('Freq0'),'1000');c.text(id('Q0'),'.707')
        plus,status=c.render(tone);gain=float(20*np.log10(np.sqrt(np.mean(plus[12000:]**2)/np.mean(tone[12000:]**2))))
        assert abs(gain-6)<.002,gain;c.save(ROOT/'gain-control-plus6.bin')
        c.text(id('Gain0'),'-6');minus,_=c.render(tone);assert float(np.sqrt(np.mean(minus[12000:]**2)))<float(np.sqrt(np.mean(tone[12000:]**2)))
        c.load(ROOT/'gain-control-plus6.bin');replay,_=c.render(tone);np.testing.assert_array_equal(replay,plus);c.save(ROOT/'gain-control-plus6-resaved.bin')
        assert(ROOT/'gain-control-plus6.bin').read_bytes()==(ROOT/'gain-control-plus6-resaved.bin').read_bytes()
        configure(c,[dict(frequency=1000.,Q=.707,mode=0,order=1)])
        impulse=np.zeros((32768,2),np.float32);impulse[4096]=.1;y,status=c.render(impulse);active=np.flatnonzero(np.max(abs(y),axis=1)>1e-9)
        first=int(active[0])-4096;peak=int(np.argmax(np.max(abs(y),axis=1)))-4096
        assert first==0 and not np.any(y[:4096])and c.latency()==0,(first,peak)
        audit=dict(actual_official_ZL_Windows_VST3=True,version='1.4.1',flat_controls=flat,active_plus6dB_measured_gain_dB=gain,
            changed_parameters_reach_actual_DSP=True,component_state_roundtrip_byte_exact=True,active_audio_replay_bit_exact=True,
            allpass_first_response_frames=first,allpass_peak_delay_frames=peak,declared_PDC_frames=0,pre_impulse_output_zero=True,
            actual_FL_GUI_validation_pending=True,reference_match_reached=False)
        (ROOT/'REAL_VST3_HOST_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print('ZL_REAL_PLUGIN_HOST_AUDIT_PASS',json.dumps(audit),flush=True)
    finally:c.close();clients.remove(c)
    for k in range(4):
        c=WinVST3('ZL-allpass-worker-'+str(k));clients.append(c);pool.put(c)
    cases=[('flat-control',[])]
    frequencies=[35,50,70,100,140,200,280,400,560,800,1100,1600,2300,3300,4700,6800,10000,14000]
    for mode in [0,3,4]:
        for frequency in frequencies:
            for q in [.35,.707,1.4,3.]:cases.append((f'single-{mode}-{frequency}-{q}',[dict(frequency=frequency,Q=q,mode=mode,order=1)]))
            cases.append((f'first-order-{mode}-{frequency}',[dict(frequency=frequency,Q=.707,mode=mode,order=0)]))
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for k,result in enumerate(executor.map(evaluate,cases)):
            if k%8==0:record('actual_ZL_allpass_phase_grid_running',cases=len(rows),best_training_loss=min(r['loss']for r in rows),actual_VST3_hosts=[identity(c.child.pid)for c in clients])
    best=min(rows,key=lambda r:r['loss']);rng=np.random.default_rng(20261023)
    extra=[]
    for k in range(96):
        band=dict(frequency=float(2**rng.uniform(np.log2(35),np.log2(14000))),Q=float(2**rng.uniform(np.log2(.3),np.log2(4))),mode=int(rng.choice([0,3,4])),order=int(rng.choice([0,1])))
        extra.append((f'two-allpass-{k}',best['bands'][:1]+[band]))
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for k,result in enumerate(executor.map(evaluate,extra)):
            if k%8==0:record('actual_ZL_two_allpass_grid_running',cases=len(rows),best_training_loss=min(r['loss']for r in rows),actual_VST3_hosts=[identity(c.child.pid)for c in clients])
    best=min(rows,key=lambda r:r['loss'])
    for sweep in range(3):
        for band_index in range(len(best['bands'])):
            for key in ['frequency','Q']:
                cases=[]
                for factor in [-2,-1,1,2]:
                    bands=[dict(b)for b in best['bands']];bands[band_index][key]*=2**(factor*.18/(sweep+1))
                    bands[band_index][key]=float(np.clip(bands[band_index][key],20 if key=='frequency'else .15,18000 if key=='frequency'else 8))
                    cases.append((f'coordinate-{sweep}-{band_index}-{key}-{factor}',bands))
                with concurrent.futures.ThreadPoolExecutor(4)as executor:checked=list(executor.map(evaluate,cases))
                current=min(checked,key=lambda r:r['loss'])
                if current['loss']<best['loss']:best=current
        record('actual_ZL_allpass_coordinate_refinement',cases=len(rows),best_training_loss=best['loss'],actual_VST3_hosts=[identity(c.child.pid)for c in clients])
    finalists=sorted(rows,key=lambda r:r['loss'])[:4];held=[]
    for row in finalists:
        hold=[evaluate(('held-out-'+row['label'],row['bands']),phase,False)for phase in [1,2]]
        held.append(dict(candidate=row,heldout=hold,mean=float(np.mean([row['loss'],*[r['loss']for r in hold]]))))
    selected=min(held,key=lambda r:r['mean'])['candidate'];c=clients[0];configure(c,selected['bands']);c.save(ROOT/'ZL_allpass_candidate_component.bin');c.dump(ROOT/'ZL_allpass_candidate_parameters.tsv')
    expected,_=c.render(input_file=ROOT/'frozen-native-0.f32')
    fresh_host=WinVST3('ZL-allpass-independent-state-replay')
    try:
        fresh_host.load(ROOT/'ZL_allpass_candidate_component.bin');got,_=fresh_host.render(input_file=ROOT/'frozen-native-0.f32');np.testing.assert_array_equal(expected,got)
        fresh_host.save(ROOT/'ZL_allpass_candidate_component_resaved.bin');assert(ROOT/'ZL_allpass_candidate_component.bin').read_bytes()==(ROOT/'ZL_allpass_candidate_component_resaved.bin').read_bytes()
    finally:fresh_host.close()
    record('independent24_paired_whole_chain_native_plus_official_VST3_validation',selected_bands=selected['bands'],actual_VST3_hosts=[identity(c.child.pid)for c in clients])
    captures=[];a=native();archive=ROOT/'independent24-native-and-ZL-captures.tar.gz'
    try:
        with tarfile.open(archive,'w:gz',compresslevel=3)as z:
            for rep in range(24):
                y,status=a.render();y.astype('<f4').tofile(ROOT/'fresh-native-input.f32');base_loss=score(y);base_assessment=features.local.last
                out,out_status=c.render(input_file=ROOT/'fresh-native-input.f32');loss=score(out)
                row=dict(rep=rep,base_loss=base_loss,loss=loss,base_assessment=base_assessment,assessment=features.local.last,note_residue=measure_native_raw(out),native_status=status,VST3_status=out_status,members=[])
                for label,audio in [('native',y),('native-ZL',out)]:
                    blob=io.BytesIO();sf.write(blob,audio,48000,format='WAV',subtype='FLOAT');data=blob.getvalue();name=f'{label}-{rep}.wav';info=tarfile.TarInfo(name);info.size=len(data);z.addfile(info,io.BytesIO(data));row['members'].append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
                captures.append(row)
    finally:a.close()
    median=sorted(captures,key=lambda row:row['loss'])[12]
    with tarfile.open(archive,'r:gz')as z:
        for row in captures:
            for member in row['members']:
                data=z.extractfile(member['name']).read();assert len(data)==member['bytes']and hashlib.sha256(data).hexdigest()==member['SHA256']
                if row is median:
                    (ROOT/('SELECTED_NATIVE_PLUS_ZL_WIP.wav'if member['name'].startswith('native-ZL')else'PAIRED_NATIVE_CONTROL_WIP.wav')).write_bytes(data)
    base_values=np.array([r['base_loss']for r in captures]);values=np.array([r['loss']for r in captures]);delta=base_values-values
    sem=float(np.std(delta,ddof=1)/np.sqrt(len(delta)));robust=bool(np.mean(delta)>max(.0005,3*sem))
    result=dict(native_base=seed,ZL_bands=selected['bands'],loss=float(np.mean(values)),native_control_mean=float(np.mean(base_values)),
        standard_deviation=float(np.std(values)),paired_difference_SEM=sem,robust_improvement=robust,
        not_compatible_with_standard_x95_exporter=True,not_automatically_adopted=True,actual_Windows_VST3=True,
        native_ZL_component_state=str(ROOT/'ZL_allpass_candidate_component.bin'),recorded_audio=str(ROOT/'SELECTED_NATIVE_PLUS_ZL_WIP.wav'),
        original_reference_assessment=median['assessment'],independent_whole_native_graph_captures=24,all_validation_WAV_bytes_losslessly_retained_and_verified=True,
        declared_added_PDC_frames=0,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
    for name,data in [('results.json',rows),('heldout.json',held),('independent-captures.json',captures),('candidate-research-only.json',result),('completion.json',dict(robust_improvement=robust,
        native_control_mean=result['native_control_mean'],candidate_mean=result['loss'],paired_difference_SEM=sem,cases=len(rows),seconds=time.monotonic()-start,reference_match_reached=False))]:
        (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
    record('external_ZL_allpass_study_complete_not_yet_integrated_into_FL_project',completion=read(ROOT/'completion.json'),actual_VST3_state_and_audio_roundtrip_bit_exact=True,
        next_step='If robust, integrate the actual new VST3 into a complete FL20 workflow and independent replay before replacing the production chain')
    print('ZL_STUDY_COMPLETE',json.dumps(read(ROOT/'completion.json')),flush=True)
except BaseException:
    record('external_ZL_study_failed_preserve_validated_native_base_and_diagnose',error=traceback.format_exc());raise
finally:
    for c in clients:c.close()
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
