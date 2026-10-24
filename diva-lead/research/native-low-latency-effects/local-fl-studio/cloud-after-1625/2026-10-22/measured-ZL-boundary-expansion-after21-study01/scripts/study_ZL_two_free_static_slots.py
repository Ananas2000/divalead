"""Actual spare-slot filter topology screen; incumbent is never overwritten."""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,itertools,json,math,os,queue,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
from win_vst3 import D,WinVST3
ROOT=D/'ZL-two-free-static-slots-current20-01';ROOT.mkdir(exist_ok=False)
N=Path('/workspace/divalead-work/native-low-latency-effects');STATE=N/'ZL_TWO_FREE_STATIC_SLOTS_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();prior=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];base=ROOT/'INITIAL_COMPONENT.bin';base.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'INITIAL_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def read(p):return json.loads(Path(p).read_text())
def xml_values(path):
    b=Path(path).read_bytes();xml=ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]);return {r.attrib['id']:float(r.attrib['value'])for r in xml.find('Para')}
assert all(xml_values(base)['filter_status'+str(k)]==0 for k in [22,23])
def record(phase,**kw):
    o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_VST3_hosts=[c.child.pid for c in clients],only_three_held_notes=True,source_and_all_native_settings_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(o,indent=2)+'\n');p.replace(STATE)
def native(tag):
    c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
    for k,v in seed['chorus_overrides'].items():c.set(3,int(k),int(v))
    return c
def score(y):
    r=features.residual(y[:288000]);return float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
def configure(c,bands):
    for index in [22,23]:
        b=bands[index-22]if index-22<len(bands)else None;c.set(params['Filter Status'+str(index)],1 if b else 0)
        if b is None:continue
        c.set(params['Filter Type'+str(index)],b['type']/10);c.set(params['LRMode'+str(index)],b['mode']/4);c.set(params['Order'+str(index)],1/6);c.set(params['Dynamic ON'+str(index)],0)
        for title,key in [('Gain','gain'),('Freq','frequency'),('Q','Q')]:c.text(params[title+str(index)],str(b[key]))
def evaluate(case,phase=0,save=True):
    label,bands=case;c=pool.get()
    try:
        configure(c,bands);out,status=c.render(input_file=ROOT/f'frozen-{phase}.f32');assert c.latency()==0;row=dict(label=label,bands=bands,loss=score(out),assessment=features.local.last)
        if save:
            with mutex:rows.append(row)
        return row
    finally:pool.put(c)
try:
    record('capture_three_actual_current_native_training_and_heldout_inputs')
    c=native('ZL-two-free-static-slots-native-inputs')
    try:
        for phase in range(3):
            raw,_=c.render();raw.astype('<f4').tofile(ROOT/f'frozen-{phase}.f32');sf.write(ROOT/f'prefix-{phase}.wav',raw,48000,subtype='FLOAT')
    finally:c.close()
    for j in range(4):
        c=WinVST3('ZL-two-free-static-slots-worker-'+str(j));c.load(base);clients.append(c);pool.put(c)
    baseline=evaluate(('unchanged-control',[]));cases=[]
    # All types were read back from actual VST3 enum: Peak0,LS1,HS3,Tilt7,FlatTilt8.
    for typ,mode,freq,Q,gain in itertools.product([0,1,3,7,8],[0,3,4],[500,1500,3500,6500,10000],[.4,.7,1.4],[-2,-1,1,2]):
        cases.append((f'one-{typ}-{mode}-{freq}-{Q}-{gain}',[dict(type=typ,mode=mode,frequency=freq,Q=Q,gain=gain)]))
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for j,row in enumerate(executor.map(evaluate,cases)):
            if j%24==0:record('actual_spare_slot_filter_type_frequency_gain_grid',best_training=min(r['loss']for r in rows),control_loss=baseline['loss'])
        current=min(rows,key=lambda r:r['loss']);rng=np.random.default_rng(2026102349);cases=[]
        for j in range(192):
            b=dict(type=int(rng.choice([0,1,3,7,8])),mode=int(rng.choice([0,3,4])),frequency=float(2**rng.uniform(math.log2(80),math.log2(18000))),Q=float(2**rng.uniform(-2,2)),gain=float(rng.uniform(-3,3)))
            cases.append((f'two-{j}',current['bands'][:1]+[b]))
        for j,row in enumerate(executor.map(evaluate,cases)):
            if j%16==0:record('actual_two_spare_static_filters_joint_grid',best_training=min(r['loss']for r in rows))
        current=min(rows,key=lambda r:r['loss'])
        for sweep in range(3):
            for band in range(len(current['bands'])):
                for key,step,lo,hi,log in [('frequency',.12,20,20000,True),('Q',.15,.15,8,True),('gain',.2,-6,6,False)]:
                    cases=[]
                    for factor in [-2,-1,1,2]:
                        bands=[dict(b)for b in current['bands']];old=bands[band][key];bands[band][key]=float(np.clip(old*2**(factor*step/(sweep+1))if log else old+factor*step/(sweep+1),lo,hi));cases.append((f'fine-{sweep}-{band}-{key}-{factor}',bands))
                    selected=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
                    if selected['loss']<current['loss']:current=selected
                    record('actual_spare_filters_coordinate_refinement',best_training=current['loss'])
    held=[]
    for row in [baseline,*sorted(rows,key=lambda r:r['loss'])[:5]]:
        checks=[evaluate(('heldout-'+row['label'],row['bands']),phase,False)for phase in [1,2]];held.append(dict(candidate=row,heldout=checks,mean=float(np.mean([row['loss'],*[r['loss']for r in checks]]))))
    selected=min(held,key=lambda r:r['mean'])['candidate'];(ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'heldout.json').write_text(json.dumps(held,indent=2)+'\n')
    latest=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert latest['native_base']['source_manifest']['source_preset_SHA256']==seed['source_manifest']['source_preset_SHA256'];assert native_dsp_settings_SHA256(latest['native_base']['x'],latest['native_base'])==native_dsp_settings_SHA256(seed['x'],seed)
    control_state=ROOT/'LATEST_CONTROL_COMPONENT.bin';control_state.write_bytes(Path(latest['native_ZL_component_state']).read_bytes());assert all(xml_values(control_state)['filter_status'+str(k)]==0 for k in [22,23])
    control,candidate=clients[:2]
    for c in [control,candidate]:c.load(control_state)
    configure(control,[]);configure(candidate,selected['bands']);component=ROOT/'CANDIDATE_COMPONENT.bin';candidate.save(component);candidate.dump(ROOT/'ACTUAL_610_PARAMETERS.tsv')
    for i,b in enumerate(selected['bands'],22):assert xml_values(component)['filter_type'+str(i)]==b['type']
    cold1=WinVST3('ZL-two-free-static-slots-cold1');cold2=WinVST3('ZL-two-free-static-slots-cold2')
    try:
        for c in [cold1,cold2]:c.load(component)
        y1,_=cold1.render(input_file=ROOT/'frozen-0.f32');y2,_=cold2.render(input_file=ROOT/'frozen-0.f32');cold_error=float(abs(y1-y2).max());np.testing.assert_allclose(y1,y2,rtol=8*np.finfo(np.float32).eps,atol=1e-12);cold1.save(ROOT/'COMPONENT_RESAVED.bin');assert component.read_bytes()==(ROOT/'COMPONENT_RESAVED.bin').read_bytes()
    finally:cold1.close();cold2.close()
    native_host=native('ZL-two-free-static-slots-paired12');captures=[];audio=[];record('twelve_fresh_same_input_pairs_against_latest_main',selected_bands=selected['bands'])
    try:
        for repeat in range(12):
            raw,_=native_host.render();a,_=control.render(raw);loss0=score(a);b,_=candidate.render(raw);loss1=score(b);captures.append(dict(rep=repeat,base_loss=loss0,loss=loss1,assessment=features.local.last));audio.append((a,b))
    finally:native_host.close()
    delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(12));robust=bool(np.mean(delta)>max(.0005,3*sem))
    impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];response,_=candidate.render(impulse);first=int(np.flatnonzero(np.max(abs(response),axis=1)>1e-9)[0])-4096;assert first==0 and candidate.latency()==0
    archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';members=[]
    with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
        for repeat,pair in enumerate(audio):
            for label,y in zip(['control','candidate'],pair):
                buffer=io.BytesIO();sf.write(buffer,y,48000,format='WAV',subtype='FLOAT');blob=buffer.getvalue();name=f'{label}-{repeat}.wav';info=tarfile.TarInfo(name);info.size=len(blob);tar.addfile(info,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
    with tarfile.open(archive)as tar:
        for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
    median=sorted(range(12),key=lambda k:captures[k]['loss'])[6];sf.write(ROOT/'SELECTED_COMBINED_WIP.wav',audio[median][1],48000,subtype='FLOAT')
    summary=dict(training_cases=len(rows),current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,selected_extra_static_bands=selected['bands'],cold_instance_replay_max_abs_error=cold_error,cold_instance_replay_bit_exact=bool(cold_error==0),component_state_roundtrip_exact=True,declared_PDC_frames=0,impulse_first_response_frames=first,only_three_held_notes=True,source_and_native_unchanged=True,captures=captures,archive_members=members,reference_match_reached=False,actual_FL_GUI_validation_pending=True,not_adopted=True,requires_supported_static_filter_topology_metadata_and_main_migration=True)
    proposed=dict(latest,loss=summary['candidate_mean'],native_ZL_component_state=str(component),recorded_audio=str(ROOT/'SELECTED_COMBINED_WIP.wav'),additional_static_filter_indices=list(range(22,22+len(selected['bands']))),additional_static_filter_settings=selected['bands'],not_automatically_adopted_into_main_or_public_FL_project=True,not_compatible_with_standard_x95_exporter=True,extended_parameter_values_are_authoritative_in_component_state=True)
    (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');(ROOT/'CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(proposed,indent=2)+'\n');record('finite_extra_static_filters_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print('ACTUAL_TWO_FREE_STATIC_FILTERS_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
    record('failed_keep_confirmed_main_and_all_full_kits',error=traceback.format_exc());raise
finally:
    for c in clients:c.close()
