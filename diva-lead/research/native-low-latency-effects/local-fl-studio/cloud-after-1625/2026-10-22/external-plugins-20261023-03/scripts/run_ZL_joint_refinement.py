"""Finite real-Windows-VST3 study after the validated three-held-note native chain.

All-pass filters change relative harmonic phase without a magnitude-EQ target.
No reference audio enters either the native graph or the VST3. This is guarded
research until FL state/preset export and independent replay are integrated.
"""
from pathlib import Path
import concurrent.futures,csv,shutil,struct,datetime,hashlib,io,json,os,queue,subprocess,tarfile,threading,time,traceback
import numpy as np
import soundfile as sf
from win_vst3 import WinVST3,D,S,win

B=D.parent;W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=D/'ZL-joint-static-dynamic-original-reference-01';ROOT.mkdir(exist_ok=False)
STATE=N/'FL20_EXTERNAL_ZL_JOINT_STUDY.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='external-ZL-full-FL20-preset-integration'
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

PILOT=D/'ZL-allpass-original-reference-01'
PRIOR=D/'ZL-dynamic-original-reference-01'
previous=read(PRIOR/'candidate-research-only.json');ap=previous['ZL_allpass_bands'];dyn=previous['ZL_dynamic_bands'];BASEGAIN=previous['ZL_output_gain_dB']
initial=np.r_[previous['ZL_peaking_MidSide_x'],np.log2([b['frequency']for b in ap]),np.log2([b['Q']for b in ap]),
              np.log2([b['frequency']for b in dyn]),np.log2([b['Q']for b in dyn]),[b['target']for b in dyn],
              [b['threshold']for b in dyn],np.log2([b['attack']for b in dyn]),np.log2([b['release']for b in dyn])]
assert len(initial)==52
lower=np.r_[np.full(12,-8.),np.full(12,np.log2(20)),np.full(12,np.log2(.15)),np.full(2,np.log2(20)),np.full(2,np.log2(.15)),
    np.full(2,np.log2(200)),np.full(2,np.log2(.15)),np.full(2,-15.),np.full(2,-65.),np.full(2,np.log2(.1)),np.full(2,np.log2(5))]
upper=np.r_[np.full(12,8.),np.full(12,np.log2(20000)),np.full(12,np.log2(8)),np.full(2,np.log2(18000)),np.full(2,np.log2(8)),
    np.full(2,np.log2(16000)),np.full(2,np.log2(8)),np.full(2,10.),np.full(2,-1.),np.full(2,np.log2(400)),np.full(2,np.log2(2000))]
steps=np.r_[np.full(12,.25),np.full(12,.12),np.full(12,.18),[.1,.1,.18,.18,.1,.1,.18,.18,.6,.6,2.,2.,.3,.3,.3,.3]]

def configure(c,x,gain_db=BASEGAIN):
    for k in range(24):c.set(id('Filter Status'+str(k)),1 if k<16 else 0)
    for k in range(12):
        for field,value in [('Gain',x[k]),('Freq',2**x[12+k]),('Q',2**x[24+k])]:c.text(id(field+str(k)),format(value,'.12g'))
    for k in range(2):
        c.text(id('Freq'+str(12+k)),format(2**x[36+k],'.12g'));c.text(id('Q'+str(12+k)),format(2**x[38+k],'.12g'))
        for field,value in [('Freq',2**x[40+k]),('Q',2**x[42+k]),('Target Gain',x[44+k]),('Threshold (dB)',x[46+k]),
                            ('Attack',2**x[48+k]),('Release',2**x[50+k]),('Side Freq',2**x[40+k]),('Side Q',2**x[42+k])]:
            c.text(id(field+str(14+k)),format(value,'.12g'))
    c.text(id('Output Gain'),format(gain_db,'.12g'))

def evaluate(case,phase=0,save=True,fixed_gain=None):
    label,x=case;x=np.asarray(x);c=pool.get()
    try:
        configure(c,x);y,status=c.render(input_file=ROOT/f'frozen-native-{phase}.f32');loss=score(y)
        gain_db=BASEGAIN+float(20*np.log10(features.local.last['diagnostics']['global_RMS_gain_for_AB'])) if fixed_gain is None else fixed_gain
        gain_db=float(np.clip(gain_db,-3,3))
        if abs(gain_db)>1e-5:
            c.text(id('Output Gain'),format(gain_db,'.12g'));y,status=c.render(input_file=ROOT/f'frozen-native-{phase}.f32');loss=score(y)
        assert c.latency()==0
        row=dict(label=label,x=x.tolist(),gain_db=gain_db,loss=loss,assessment=features.local.last)
        if save:
            with mutex:
                rows.append(row)
                if loss<min([r['loss']for r in rows[:-1]],default=float('inf')):
                    (ROOT/'best-training.json').write_text(json.dumps(row,indent=2)+'\n')
                    sf.write(ROOT/'best-training-WIP.wav',y,48000,subtype='FLOAT')
                    print('ZL_JOINT_ACTUAL_BEST',len(rows),label,loss,flush=True)
        return row
    finally:pool.put(c)

try:
    assert read(PAUSE)['owner']==OWNER
    deadline=time.monotonic()+1800
    while True:
        main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');live=identity(main['controller']['PID'])
        assert live and live['starttime']==main['controller']['starttime']
        if main['phase']=='paused_by_control_or_actual_disk_reserve':break
        assert time.monotonic()<deadline
        record('waiting_for_current_cohort_to_finish_without_interruption',main_progress=main.get('progress'));time.sleep(3)
    seed=read(N/'FL20-corrected/BEST_CANDIDATE.json');validate_curve_candidate(seed)
    old=read(PILOT/'validated-native-base.json')
    for key in ['x','chorus_overrides','waveshaper_curve_adjustment','waveshaper_local_bump_adjustment','waveshaper_detail_bump_adjustment','source_manifest']:
        assert seed[key]==old[key],('Native base changed; must generate new frozen captures',key)
    (ROOT/'validated-native-base.json').write_text(json.dumps(seed,indent=2)+'\n')
    for phase in range(3):os.link(PILOT/f'frozen-native-{phase}.f32',ROOT/f'frozen-native-{phase}.f32')
    for k in range(4):
        c=WinVST3('ZL-joint-worker-'+str(k));c.load(PRIOR/'ZL_dynamic_component.bin');clients.append(c);pool.put(c)
    c=clients[0];c.load(PRIOR/'ZL_dynamic_component.bin')
    expected,_=c.render(input_file=ROOT/'frozen-native-0.f32')
    configure(c,initial);got,_=c.render(input_file=ROOT/'frozen-native-0.f32')
    error=float(abs(expected-got).max());assert error<2e-7,error
    (ROOT/'FLAT_PEAKING_BAND_TRANSPARENCY.json').write_text(json.dumps(dict(actual_VST3=True,new_zero_gain_peaking_bands=12,
        maximum_sample_error=error,bit_exact=bool(error==0),unmodified_prior_dynamic_control=True),indent=2)+'\n')
    best=evaluate(('zero-extra-EQ-control',initial));control=best
    rng=np.random.default_rng(2026102302)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for sweep in range(3):
            for coord in rng.permutation(52):
                step=steps[coord]*(.72**sweep)
                cases=[]
                for factor in [-2,-1,1,2]:
                    x=np.array(best['x']);x[coord]=np.clip(x[coord]+factor*step,lower[coord],upper[coord])
                    cases.append((f'coordinate-{sweep}-{coord}-{factor}',x))
                checked=list(executor.map(evaluate,cases));new=min(checked,key=lambda r:r['loss'])
                if new['loss']<best['loss']:best=new
                record('actual_official_ZL_MidSide_EQ12_coordinate_fit',cases=len(rows),sweep=sweep,coordinate=int(coord),
                    best_training_loss=best['loss'],actual_VST3_hosts=[identity(c.child.pid)for c in clients])
    finalists=sorted(rows,key=lambda r:r['loss'])[:4];held=[]
    for row in finalists:
        checks=[evaluate(('heldout-'+row['label'],row['x']),phase,False,row['gain_db'])for phase in [1,2]]
        held.append(dict(candidate=row,heldout=checks,mean=float(np.mean([row['loss'],*[r['loss']for r in checks]]))))
    selected=min(held,key=lambda r:r['mean'])['candidate'];c=clients[0]
    configure(c,selected['x'],selected['gain_db']);c.save(ROOT/'ZL_joint_component.bin');c.dump(ROOT/'ZL_joint_parameters.tsv')
    expected,_=c.render(input_file=ROOT/'frozen-native-0.f32')
    fresh=WinVST3('ZL-joint-independent-state-replay')
    try:
        fresh.load(ROOT/'ZL_joint_component.bin');got,_=fresh.render(input_file=ROOT/'frozen-native-0.f32');np.testing.assert_array_equal(expected,got)
        fresh.save(ROOT/'ZL_joint_component_resaved.bin')
        assert(ROOT/'ZL_joint_component.bin').read_bytes()==(ROOT/'ZL_joint_component_resaved.bin').read_bytes()
    finally:fresh.close()
    record('independent12_native_allpass_and_EQ12_triplet_validation',selected=selected)
    a=native();control_host=clients[1];control_host.load(PRIOR/'ZL_dynamic_component.bin');captures=[]
    archive=ROOT/'independent12-native-and-EQ12-captures.tar.gz'
    try:
        with tarfile.open(archive,'w:gz',compresslevel=3)as z:
            for rep in range(12):
                y,status=a.render();base_loss=score(y);base_assessment=features.local.last
                y.astype('<f4').tofile(ROOT/'fresh-native-input.f32')
                old_audio,_=control_host.render(input_file=ROOT/'fresh-native-input.f32');old_loss=score(old_audio);old_assessment=features.local.last
                out,out_status=c.render(input_file=ROOT/'fresh-native-input.f32');loss=score(out)
                row=dict(rep=rep,native_loss=base_loss,prior_dynamic_loss=old_loss,loss=loss,native_assessment=base_assessment,prior_dynamic_assessment=old_assessment,
                    assessment=features.local.last,note_residue=measure_native_raw(out),native_status=status,VST3_status=out_status,members=[])
                for label,audio in [('native',y),('native-ZL-joint',out)]:
                    blob=io.BytesIO();sf.write(blob,audio,48000,format='WAV',subtype='FLOAT');data=blob.getvalue();name=f'{label}-{rep}.wav'
                    info=tarfile.TarInfo(name);info.size=len(data);z.addfile(info,io.BytesIO(data))
                    row['members'].append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
                captures.append(row)
    finally:a.close()
    median=sorted(captures,key=lambda r:r['loss'])[6]
    with tarfile.open(archive,'r:gz')as z:
        for row in captures:
            for member in row['members']:
                data=z.extractfile(member['name']).read();assert len(data)==member['bytes']and hashlib.sha256(data).hexdigest()==member['SHA256']
                if row is median:(ROOT/('SELECTED_NATIVE_ZL_JOINT_WIP.wav'if member['name'].startswith('native-ZL')else'PAIRED_NATIVE_CONTROL_WIP.wav')).write_bytes(data)
    delta=np.array([r['prior_dynamic_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(len(delta)))
    robust=bool(np.mean(delta)>max(.0005,3*sem))
    v=np.array(selected['x']);updated_ap=[dict(b,frequency=float(2**v[36+k]),Q=float(2**v[38+k]))for k,b in enumerate(ap)];updated_dyn=[dict(b,frequency=float(2**v[40+k]),Q=float(2**v[42+k]),target=float(v[44+k]),threshold=float(v[46+k]),attack=float(2**v[48+k]),release=float(2**v[50+k]))for k,b in enumerate(dyn)]
    result=dict(native_base=seed,ZL_dynamic_bands=updated_dyn,ZL_allpass_bands=updated_ap,ZL_peaking_MidSide_x=selected['x'][:36],ZL_joint_x=selected['x'],ZL_output_gain_dB=selected['gain_db'],
        loss=float(np.mean([r['loss']for r in captures])),prior_dynamic_control_mean=float(np.mean([r['prior_dynamic_loss']for r in captures])),
        native_control_mean=float(np.mean([r['native_loss']for r in captures])),paired_difference_SEM=sem,robust_improvement_over_dynamic=robust,
        not_compatible_with_standard_x95_exporter=True,not_automatically_adopted=True,actual_Windows_VST3=True,declared_added_PDC_frames=c.latency(),
        native_ZL_component_state=str(ROOT/'ZL_joint_component.bin'),recorded_audio=str(ROOT/'SELECTED_NATIVE_ZL_JOINT_WIP.wav'),
        only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
    completion=dict(candidate_mean=result['loss'],prior_dynamic_control_mean=result['prior_dynamic_control_mean'],native_control_mean=result['native_control_mean'],
        robust_improvement_over_dynamic=robust,paired_difference_SEM=sem,cases=len(rows),seconds=time.monotonic()-start,reference_match_reached=False)
    for name,data in [('results.json',rows),('heldout.json',held),('independent-captures.json',captures),('candidate-research-only.json',result),('completion.json',completion)]:
        (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
    record('external_ZL_JOINT_complete_not_yet_integrated_into_FL_project',completion=completion,actual_VST3_state_audio_replay_bit_exact=True)
    print('ZL_JOINT_STUDY_COMPLETE',json.dumps(completion),flush=True)
except BaseException:
    record('external_ZL_JOINT_study_failed_preserve_supported_production_chain',error=traceback.format_exc());raise
finally:
    for c in clients:c.close()
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
