"""Continue actual low-latency VST3 matching until stop or observed reserves.

Four real-plugin workers, actual fresh native inputs, two held-out realizations,
fresh paired confirmation, real state replay and lossless validation WAVs.
No FL GUI or complete reference-match claim. Uses only the original three
incoming held notes per phrase; the frozen actual Diva source is unchanged.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,shutil,struct,tarfile,threading,time,traceback
import xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from win_vst3 import WinVST3,D
from native_chain import NativeChain
from fl20_curve import apply_candidate
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-continuous65';ROOT.mkdir(exist_ok=True)
STATE=N/'FL20_ZL_CONTINUOUS_CONTROLLER.json';PAUSE=N/'fl20-corrected-search.pause';STOP=N/'zl-continuation.stop'
OWNER='external-ZL-continuous65-refinement'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal()
def read(p):return json.loads(Path(p).read_text())
def identity(pid):
    p=Path('/proc')/str(pid)
    try:
        s=(p/'stat').read_text().split()
        if s[2]=='Z':return None
        return dict(PID=pid,starttime=s[21],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
clients=[]
def record(phase,**extra):
    obj=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,
        configured_real_VST3_workers=4,actual_VST3_hosts=[identity(c.child.pid)for c in clients],only_three_held_notes=True,
        source_and_native_12_effects_unchanged=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(obj,indent=2)+'\n');p.replace(STATE)
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
best=read(ROOT/'BEST_CANDIDATE.json')if(ROOT/'BEST_CANDIDATE.json').exists()else read(D/'ZL-extra-dynamic-original-reference-01/candidate-research-only.json');seed=best['native_base'];best_component=Path(best['native_ZL_component_state'])
pool=queue.Queue();mutex=threading.Lock();rows=[];current=None;work=None
def score(y):
    a=features.residual(y[:288000]);return float(a@a)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
def native(tag):
    c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
    apply_candidate(c,np.array(seed['x']),seed)
    for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
    return c
def specs_from_component(path):
    b=Path(path).read_bytes();xml=ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]])
    v={p.attrib['id']:float(p.attrib['value'])for p in xml.find('Para')};specs=[]
    def add(title,key,step,lo,hi,log=False):specs.append(dict(title=title,value=v[key],step=step,lo=lo,hi=hi,log=log))
    for k in range(12):
        for title,key,step,lo,hi,log in [('Gain','gain',.2,-10,10,False),('Freq','freq',.09,20,20000,True),('Q','q',.12,.15,8,True)]:add(title+str(k),key+str(k),step,lo,hi,log)
    for k in [12,13]:
        add('Freq'+str(k),'freq'+str(k),.09,20,18000,True);add('Q'+str(k),'q'+str(k),.12,.15,8,True)
    dynamic=[k for k in range(24)if v['filter_status'+str(k)]==2 and v['dynamic_on'+str(k)]==1]
    for k in dynamic:
        for title,key,step,lo,hi,log in [('Freq','freq',.09,200,18000,True),('Q','q',.12,.15,8,True),('Target Gain','target_gain',.4,-20,15,False),
            ('Threshold (dB)','threshold',1.5,-65,-1,False),('Attack','attack',.25,.1,500,True),('Release','release',.25,5,2000,True)]:add(title+str(k),key+str(k),step,lo,hi,log)
    add('Output Gain','total_output_gain',.05,-3,3)
    return specs,dynamic
def configure(c,x):
    for p,value in zip(specs,x):c.text(params[p['title']],format(value,'.12g'))
    # Keep detector bands tied to each corresponding main filter frequency/Q.
    d=dict(zip([p['title']for p in specs],x))
    for k in dynamic:
        c.text(params['Side Freq'+str(k)],format(d['Freq'+str(k)],'.12g'));c.text(params['Side Q'+str(k)],format(d['Q'+str(k)],'.12g'))
def evaluate(case,phase=0,save=True):
    label,x=case;c=pool.get()
    try:
        configure(c,x);y,status=c.render(input_file=ROOT/f'frozen-{phase}.f32');loss=score(y);assert c.latency()==0
        row=dict(label=label,x=list(x),loss=loss,assessment=features.local.last)
        if save:
            with mutex:rows.append(row)
        return row
    finally:pool.put(c)
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,purpose='genuine persistent actual VST3 matching with fresh paired confirmations and disk guards'),f)
try:
    assert not STOP.exists();rng=np.random.default_rng(2026102304)
    for k in range(4):
        c=WinVST3('ZL-continuous-worker-'+str(k));clients.append(c);pool.put(c)
    cohort=max([int(p.name.split('-')[1])for p in ROOT.glob('cohort-[0-9][0-9][0-9][0-9]')],default=0)
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        while not STOP.exists():
            reserves=dict(root_free_MiB=shutil.disk_usage('/workspace').free/2**20,tmp_free_MiB=shutil.disk_usage('/tmp').free/2**20)
            if reserves['root_free_MiB']<64 or reserves['tmp_free_MiB']<144:
                record('stopped_at_observed_storage_reserve_after_completed_cohort',reserves=reserves,best_candidate=best,completed_cohorts=cohort);break
            cohort+=1;work=ROOT/f'cohort-{cohort:04}';work.mkdir();rows=[]
            specs,dynamic=specs_from_component(best_component);initial=[p['value']for p in specs]
            for c in clients:c.load(best_component)
            a=native('ZL-continuous-frozen-source')
            try:
                for phase in range(3):y,_=a.render();y.astype('<f4').tofile(ROOT/f'frozen-{phase}.f32')
            finally:a.close()
            current=evaluate(('current-confirmed-control',initial));control_loss=current['loss']
            for coord in rng.permutation(len(specs)):
                p=specs[coord];cases=[]
                for factor in [-2,-1,1,2]:
                    x=list(current['x']);step=p['step']*(.82**((cohort-1)%5))
                    x[coord]=float(np.clip(x[coord]*2**(factor*step)if p['log']else x[coord]+factor*step,p['lo'],p['hi']))
                    cases.append((f'{cohort}-{coord}-{factor}',x))
                checked=list(executor.map(evaluate,cases));candidate=min(checked,key=lambda r:r['loss'])
                if candidate['loss']<current['loss']:current=candidate
                record('actual_coordinate_sweep_running',cohort=cohort,cases=len(rows),parameters=len(specs),best_training_loss=current['loss'],baseline_training_loss=control_loss,best_confirmed_mean=best['loss'],root=str(ROOT))
            held=[]
            for phase in [1,2]:
                baseline=evaluate(('heldout-control',initial),phase,False);candidate=evaluate(('heldout-candidate',current['x']),phase,False)
                held.append(dict(phase=phase,control=baseline,candidate=candidate))
            (work/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
            (work/'heldout.json').write_text(json.dumps(held,indent=2)+'\n')
            if current['loss']>=control_loss-.0001 or np.mean([r['control']['loss']-r['candidate']['loss']for r in held])<=.0001:continue
            c=clients[0];configure(c,current['x']);state=work/'candidate-component.bin';c.save(state)
            got,_=c.render(input_file=ROOT/'frozen-0.f32');fresh=WinVST3('ZL-continuous-canonical-validation')
            control=WinVST3('ZL-continuous-prior-control');a=native('ZL-continuous-independent6-native');captures=[];audio_pairs=[]
            try:
                fresh.load(state);again,_=fresh.render(input_file=ROOT/'frozen-0.f32');replay_error=float(abs(got-again).max());assert replay_error<=5e-9,replay_error
                # A prior hot instance may differ at an isolated float32 ULP.
                # Check two genuinely new instances separately and retain the
                # measured error; never rename a nonzero residual bit-exact.
                cold=WinVST3('ZL-continuous-second-cold-replay')
                try:
                    cold.load(state);cold_audio,_=cold.render(input_file=ROOT/'frozen-0.f32');cold_error=float(abs(cold_audio-again).max());assert cold_error<=5e-9,cold_error
                finally:cold.close()
                fresh.save(work/'component-resaved.bin');assert state.read_bytes()==(work/'component-resaved.bin').read_bytes();control.load(best_component)
                record('actual_independent6_paired_validation',cohort=cohort,training_loss=current['loss'],component_replay_max_abs_error=replay_error)
                for rep in range(6):
                    raw,_=a.render();old,_=control.render(raw);base_loss=score(old);out,_=fresh.render(raw);loss=score(out)
                    captures.append(dict(rep=rep,base_loss=base_loss,loss=loss,assessment=features.local.last));audio_pairs.append((old,out))
            finally:a.close();fresh.close();control.close()
            delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(len(delta)))
            robust=bool(np.mean(delta)>max(.0005,3*sem));summary=dict(cohort=cohort,robust_improvement=robust,paired_difference_SEM=sem,
                current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),component_replay_max_abs_error=replay_error,captures=captures)
            summary.update(cold_instance_replay_max_abs_error=cold_error,cold_instance_replay_bit_exact=bool(cold_error==0),numerical_replay_tolerance=5e-9)
            if robust:
                items=[];archive=work/'independent6-control-candidate-WAVs.tar.gz'
                with tarfile.open(archive,'w:gz',compresslevel=3)as z:
                    for rep,pair in enumerate(audio_pairs):
                        for label,audio in zip(['control','candidate'],pair):
                            blob=io.BytesIO();sf.write(blob,audio,48000,format='WAV',subtype='FLOAT');b=blob.getvalue();name=f'{label}-{rep}.wav'
                            info=tarfile.TarInfo(name);info.size=len(b);z.addfile(info,io.BytesIO(b));items.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
                with tarfile.open(archive)as z:
                    for item in items:assert hashlib.sha256(z.extractfile(item['name']).read()).hexdigest()==item['SHA256']
                selected=sorted(range(6),key=lambda k:captures[k]['loss'])[3];sf.write(work/'SELECTED_CANDIDATE_WIP.wav',audio_pairs[selected][1],48000,subtype='FLOAT')
                best=dict(best,loss=summary['candidate_mean'],native_ZL_component_state=str(state),recorded_audio=str(work/'SELECTED_CANDIDATE_WIP.wav'),
                    actual_component_state_roundtrip_exact=True,component_replay_max_abs_error=replay_error,not_compatible_with_standard_x95_exporter=True,
                    not_automatically_adopted_into_public_FL_project=True,extended_parameter_values_are_authoritative_in_component_state=True)
                best_component=state;(ROOT/'BEST_CANDIDATE.json').write_text(json.dumps(best,indent=2)+'\n');summary['lossless_capture_archive']=str(archive);summary['archive_members']=items
            (work/'completion.json').write_text(json.dumps(summary,indent=2)+'\n')
            print('ZL_CONTINUOUS_COMPLETED_COHORT',cohort,json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
        else:record('stopped_by_explicit_stop_file_after_completed_cohort',best_candidate=best)
except BaseException:
    record('failed_preserve_confirmed_ZL03_and_prior_private_best',error=traceback.format_exc(),best_candidate=best);raise
finally:
    for c in clients:c.close()
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
