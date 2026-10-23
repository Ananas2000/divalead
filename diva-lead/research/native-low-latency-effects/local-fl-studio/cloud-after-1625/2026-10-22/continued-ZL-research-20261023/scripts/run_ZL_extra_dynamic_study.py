"""Finite real-Windows-VST3 study after the validated three-held-note native chain.

All-pass filters change relative harmonic phase without a magnitude-EQ target.
No reference audio enters either the native graph or the VST3. This is guarded
research until FL state/preset export and independent replay are integrated.
"""
from pathlib import Path
import concurrent.futures,csv,itertools,datetime,hashlib,io,json,os,queue,subprocess,tarfile,threading,time,traceback
import numpy as np
import soundfile as sf
from win_vst3 import WinVST3,D,S,win

B=D.parent;W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=D/'ZL-extra-dynamic-original-reference-01';ROOT.mkdir(exist_ok=False)
STATE=N/'FL20_EXTERNAL_ZL_EXTRA_DYNAMIC_STUDY.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='external-ZL-extra-dynamic-finite-study'
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

EQ12=D/'ZL-joint-static-dynamic-original-reference-01'
PILOT=D/'ZL-allpass-original-reference-01'
def configure(c,bands):
    for k in range(16,18):
        band=bands[k-16]if k-16<len(bands)else None;c.set(id('Filter Status'+str(k)),1 if band else 0)
        if band is None:continue
        c.set(id('Filter Type'+str(k)),0);c.set(id('Order'+str(k)),1/6);c.set(id('LRMode'+str(k)),band['mode']/4)
        c.set(id('Dynamic ON'+str(k)),1);c.set(id('Dynamic Learn'+str(k)),0);c.set(id('Dynamic Relative'+str(k)),0)
        for field,value in [('Gain',0),('Freq',band['frequency']),('Q',band['Q']),('Target Gain',band['target']),
                            ('Threshold (dB)',band['threshold']),('Attack',band['attack']),('Release',band['release']),
                            ('Side Freq',band['frequency']),('Side Q',band['Q'])]:c.text(id(field+str(k)),format(value,'.12g'))
    c.set(id('Lookahead'),0);c.set(id('Filter Structure'),0)

def evaluate(case,phase=0,save=True):
    label,bands=case;c=pool.get()
    try:
        configure(c,bands);y,status=c.render(input_file=ROOT/f'frozen-native-{phase}.f32');loss=score(y)
        assert c.latency()==0
        row=dict(label=label,bands=bands,loss=loss,assessment=features.local.last)
        if save:
            with mutex:
                rows.append(row)
                if loss<min([r['loss']for r in rows[:-1]],default=float('inf')):
                    (ROOT/'best-training.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(ROOT/'best-training-WIP.wav',y,48000,subtype='FLOAT')
                    print('ZL_DYNAMIC_REAL_BEST',len(rows),label,loss,flush=True)
        return row
    finally:pool.put(c)

try:
    assert read(PAUSE)['owner']==OWNER
    main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');assert main['phase']=='paused_by_control_or_actual_disk_reserve'
    seed=read(EQ12/'validated-native-base.json');validate_curve_candidate(seed)
    (ROOT/'validated-native-base.json').write_text(json.dumps(seed,indent=2)+'\n')
    for phase in range(3):os.link(PILOT/f'frozen-native-{phase}.f32',ROOT/f'frozen-native-{phase}.f32')
    for k in range(4):
        c=WinVST3('ZL-extra-dynamic-worker-'+str(k));c.load(EQ12/'ZL_joint_component.bin');clients.append(c);pool.put(c)
    baseline=evaluate(('static-EQ12-control',[]));cases=[]
    for frequency,mode,target,threshold in itertools.product([700,1800,4000,8500,13000],[0,3,4],[-6,-3,3,6],[-45,-30,-20,-10]):
        band=dict(frequency=frequency,mode=mode,target=target,threshold=threshold,Q=.8,attack=10.,release=100.)
        cases.append((f'single-{frequency}-{mode}-{target}-{threshold}',[band]))
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for k,result in enumerate(executor.map(evaluate,cases)):
            if k%8==0:record('actual_ZL_zero_lookahead_dynamic_EQ_grid',cases=len(rows),best_training_loss=min(r['loss']for r in rows),actual_VST3_hosts=[identity(c.child.pid)for c in clients])
        best=min(rows,key=lambda r:r['loss']);rng=np.random.default_rng(2026102303)
        if best['bands']:
            cases=[]
            for k in range(72):
                b=dict(frequency=float(2**rng.uniform(np.log2(500),np.log2(16000))),mode=int(rng.choice([0,3,4])),target=float(rng.uniform(-5,5)),
                    threshold=float(rng.uniform(-45,-8)),Q=float(2**rng.uniform(-1.5,1)),attack=float(2**rng.uniform(0,5)),release=float(2**rng.uniform(4,9)))
                cases.append((f'two-dynamic-{k}',best['bands'][:1]+[b]))
            list(executor.map(evaluate,cases));best=min(rows,key=lambda r:r['loss'])
        for sweep in range(3):
            for index in range(len(best['bands'])):
                for key,step,lo,hi,log in [('frequency',.14,100,18000,True),('Q',.2,.2,5,True),('target',.5,-8,8,False),
                                        ('threshold',2.5,-60,-3,False),('attack',.5,.1,500,True),('release',.5,10,1500,True)]:
                    cases=[]
                    for factor in [-2,-1,1,2]:
                        bands=[dict(b)for b in best['bands']];old=bands[index][key]
                        new=old*2**(factor*step/(sweep+1))if log else old+factor*step/(sweep+1)
                        bands[index][key]=float(np.clip(new,lo,hi));cases.append((f'coordinate-{sweep}-{index}-{key}-{factor}',bands))
                    checked=list(executor.map(evaluate,cases));selected=min(checked,key=lambda r:r['loss'])
                    if selected['loss']<best['loss']:best=selected
                    record('actual_ZL_dynamic_EQ_coordinate_fit',cases=len(rows),best_training_loss=best['loss'],actual_VST3_hosts=[identity(c.child.pid)for c in clients])
    held=[]
    for row in sorted(rows,key=lambda r:r['loss'])[:4]:
        checks=[evaluate(('heldout-'+row['label'],row['bands']),phase,False)for phase in [1,2]]
        held.append(dict(candidate=row,heldout=checks,mean=float(np.mean([row['loss'],*[r['loss']for r in checks]]))))
    selected=min(held,key=lambda r:r['mean'])['candidate'];c=clients[0];configure(c,selected['bands'])
    c.save(ROOT/'ZL_dynamic_component.bin');c.dump(ROOT/'ZL_dynamic_parameters.tsv')
    expected,_=c.render(input_file=ROOT/'frozen-native-0.f32');fresh=WinVST3('ZL-extra-dynamic-independent-state-replay')
    try:
        fresh.load(ROOT/'ZL_dynamic_component.bin');got,_=fresh.render(input_file=ROOT/'frozen-native-0.f32');replay_error=float(abs(expected-got).max());assert replay_error<=1e-12,replay_error
        fresh.save(ROOT/'ZL_dynamic_component_resaved.bin');assert (ROOT/'ZL_dynamic_component_resaved.bin').read_bytes()==(ROOT/'ZL_dynamic_component.bin').read_bytes()
    finally:fresh.close()
    control=clients[1];control.load(EQ12/'ZL_joint_component.bin');a=native();captures=[]
    record('actual_dynamic_EQ_independent12_fresh_paired_validation',selected_bands=selected['bands'])
    try:
        with tarfile.open(ROOT/'independent12-static-and-dynamic-captures.tar.gz','w:gz',compresslevel=3)as z:
            for rep in range(12):
                y,status=a.render();base,_=control.render(y);base_loss=score(base);out,_=c.render(y);loss=score(out)
                row=dict(rep=rep,base_loss=base_loss,loss=loss,assessment=features.local.last,note_residue=measure_native_raw(out),members=[])
                for label,audio in [('static',base),('dynamic',out)]:
                    blob=io.BytesIO();sf.write(blob,audio,48000,format='WAV',subtype='FLOAT');data=blob.getvalue();name=f'{label}-{rep}.wav'
                    info=tarfile.TarInfo(name);info.size=len(data);z.addfile(info,io.BytesIO(data));row['members'].append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))
                captures.append(row)
    finally:a.close()
    median=sorted(captures,key=lambda r:r['loss'])[6]
    with tarfile.open(ROOT/'independent12-static-and-dynamic-captures.tar.gz')as z:
        for row in captures:
            for member in row['members']:
                data=z.extractfile(member['name']).read();assert len(data)==member['bytes']and hashlib.sha256(data).hexdigest()==member['SHA256']
                if row is median and member['name'].startswith('dynamic'):(ROOT/'SELECTED_DYNAMIC_WIP.wav').write_bytes(data)
    delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(len(delta)))
    robust=bool(np.mean(delta)>max(.0005,3*sem));summary=dict(candidate_mean=float(np.mean([r['loss']for r in captures])),
        prior_joint_control_mean=float(np.mean([r['base_loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,cases=len(rows),seconds=time.monotonic()-start,reference_match_reached=False)
    result=dict(read(EQ12/'candidate-research-only.json'),ZL_dynamic_bands=read(EQ12/'candidate-research-only.json')['ZL_dynamic_bands']+selected['bands'],native_ZL_component_state=str(ROOT/'ZL_dynamic_component.bin'),
        recorded_audio=str(ROOT/'SELECTED_DYNAMIC_WIP.wav'),loss=summary['candidate_mean'],robust_improvement=robust,actual_component_audio_replay_bit_exact=bool(replay_error==0),component_audio_replay_max_abs_error=replay_error)
    for name,data in [('results.json',rows),('heldout.json',held),('independent-captures.json',captures),('candidate-research-only.json',result),('completion.json',summary)]:
        (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
    record('external_ZL_dynamic_EQ_study_complete_not_automatically_adopted',completion=summary)
    print('ZL_DYNAMIC_STUDY_COMPLETE',json.dumps(summary),flush=True)
except BaseException:
    record('external_ZL_dynamic_EQ_failed_preserve_complete_ZL01',error=traceback.format_exc());raise
finally:
    for c in clients:c.close()
    # This owner also covers full-kit/Git integration; the coordinator releases
    # it only after this finite study and its next-work decision are recorded.

    if PAUSE.exists()and read(PAUSE).get("owner")==OWNER:PAUSE.unlink()
