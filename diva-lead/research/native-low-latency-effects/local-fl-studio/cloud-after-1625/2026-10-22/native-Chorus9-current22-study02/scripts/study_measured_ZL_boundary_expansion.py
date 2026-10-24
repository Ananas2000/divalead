"""Test measured real-plugin ranges beyond previously binding search limits."""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from scipy.stats import qmc
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import D,WinVST3
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-measured-boundary-expansion-after21-01';ROOT.mkdir(exist_ok=False)
STATE=N/'ZL_MEASURED_BOUNDARY_EXPANSION_STUDY_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();prior=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=prior['native_base'];component=ROOT/'INITIAL_COMPONENT.bin';component.write_bytes(Path(prior['native_ZL_component_state']).read_bytes());(ROOT/'PRIOR_COMBINED_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n')
def xml_values(path):
    b=Path(path).read_bytes();xml=ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]);return {row.attrib['id']:float(row.attrib['value'])for row in xml.find('Para')}
v=xml_values(component)
# Actual disabled-band tests established Q<=25 and Gain/TargetGain in[-30,30].
specs=[dict(title='Q'+str(k),key='q'+str(k),lo=.15,hi=25,step=.16,log=True)for k in [6,7,18,19]]+[dict(title='Target Gain'+str(k),key='target_gain'+str(k),lo=-30,hi=30,step=1.,log=False)for k in [14,16,17]]+[dict(title='Gain20',key='gain20',lo=-30,hi=15,step=1.,log=False)]
origin=np.array([v[p['key']]for p in specs]);params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')};clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock()
def read(p):return json.loads(Path(p).read_text())
def record(phase,**kw):
    o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_VST3_hosts=[c.child.pid for c in clients],only_three_held_notes=True,source_and_all_native_settings_unchanged=True,original_objective_and_all_validation_gates_unchanged=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(o,indent=2)+'\n');p.replace(STATE)
def native(tag):
    c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),seed)
    for k,value in seed['chorus_overrides'].items():c.set(3,int(k),int(value))
    return c
def score(y):
    r=features.residual(y[:288000]);return float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
def configure(c,x):
    for p,value in zip(specs,x):c.text(params[p['title']],str(value))
def evaluate(case,phase=0,save=True):
    label,x=case;c=pool.get()
    try:
        configure(c,x);out,status=c.render(input_file=ROOT/f'frozen-{phase}.f32');assert c.latency()==0;row=dict(label=label,x=list(x),loss=score(out),assessment=features.local.last)
        if save:
            with mutex:rows.append(row)
        return row
    finally:pool.put(c)
try:
    record('three_actual_current_native_training_and_heldout_realizations')
    c=native('ZL-boundary-expansion-native-inputs')
    try:
        for phase in range(3):raw,_=c.render();raw.astype('<f4').tofile(ROOT/f'frozen-{phase}.f32');sf.write(ROOT/f'prefix-{phase}.wav',raw,48000,subtype='FLOAT')
    finally:c.close()
    for k in range(4):c=WinVST3('ZL-measured-boundary-worker-'+str(k));c.load(component);clients.append(c);pool.put(c)
    baseline=evaluate(('unchanged-control',origin));cases=[]
    for j,p in enumerate(specs):
        values=[9,10.5,12,16,20,25]if p['title'].startswith('Q')else([-20,-22,-24,-27,-30]if j in [4,7]else[16,18,21,24,27,30])
        for value in values:
            x=origin.copy();x[j]=value;cases.append((f'measured-range-{j}-{value}',x))
    for k,u in enumerate(qmc.LatinHypercube(8,seed=2026102461).random(128)):
        x=origin.copy();x[:4]=8*np.power(25/8,u[:4]);x[4]=-18-12*u[4];x[5:7]=15+15*u[5:7];x[7]=-15-15*u[7];cases.append((f'coupled-physical-range-{k}',x))
    with concurrent.futures.ThreadPoolExecutor(4)as executor:
        for k,row in enumerate(executor.map(evaluate,cases)):
            if k%16==0:record('actual_measured_range_joint_screen',best_training_mean=min(r['loss']for r in rows),control_mean=baseline['loss'])
        current=min(rows,key=lambda r:r['loss'])
        for sweep in range(3):
            for j,p in enumerate(specs):
                cases=[]
                for factor in [-2,-1,1,2]:
                    x=np.array(current['x']);delta=factor*p['step']/(sweep+1);x[j]=float(np.clip(x[j]*2**delta if p['log']else x[j]+delta,p['lo'],p['hi']));cases.append((f'fine-{sweep}-{j}-{factor}',x))
                selected=min(executor.map(evaluate,cases),key=lambda r:r['loss'])
                if selected['loss']<current['loss']:current=selected
                record('actual_measured_range_refinement',best_training_mean=current['loss'],control_mean=baseline['loss'])
    held=[]
    for row in [baseline,*sorted(rows,key=lambda r:r['loss'])[:4]]:
        checks=[evaluate(('heldout-'+row['label'],row['x']),phase,False)for phase in [1,2]];held.append(dict(candidate=row,heldout=checks,mean=float(np.mean([row['loss'],*[r['loss']for r in checks]]))))
    selected=min(held,key=lambda r:r['mean'])['candidate'];(ROOT/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'heldout.json').write_text(json.dumps(held,indent=2)+'\n');(ROOT/'PARAMETER_SPECIFICATION.json').write_text(json.dumps(specs,indent=2)+'\n')
    latest=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert Path(latest['native_ZL_component_state']).read_bytes()==component.read_bytes(),'Finite handoff incumbent changed'
    control,candidate=clients[:2]
    for c in [control,candidate]:c.load(component)
    configure(control,origin);configure(candidate,selected['x']);saved=ROOT/'CANDIDATE_COMPONENT.bin';candidate.save(saved);candidate.dump(ROOT/'ACTUAL_610_PARAMETERS.tsv')
    actual=xml_values(saved)
    for p,value in zip(specs,selected['x']):assert abs(actual[p['key']]-value)<.006,(p,actual[p['key']],value)
    cold1=WinVST3('ZL-boundary-cold1');cold2=WinVST3('ZL-boundary-cold2')
    try:
        for c in [cold1,cold2]:c.load(saved)
        a,_=cold1.render(input_file=ROOT/'frozen-0.f32');b,_=cold2.render(input_file=ROOT/'frozen-0.f32');cold_error=float(abs(a-b).max());np.testing.assert_allclose(a,b,rtol=8*np.finfo(np.float32).eps,atol=1e-12);cold1.save(ROOT/'COMPONENT_RESAVED.bin');assert saved.read_bytes()==(ROOT/'COMPONENT_RESAVED.bin').read_bytes()
    finally:cold1.close();cold2.close()
    c=native('ZL-boundary-independent12-native');captures=[];audio=[];record('twelve_fresh_actual_same_input_pairs')
    try:
        for repeat in range(12):
            raw,_=c.render();old,_=control.render(raw);loss0=score(old);out,_=candidate.render(raw);loss1=score(out);captures.append(dict(rep=repeat,base_loss=loss0,loss=loss1,assessment=features.local.last));audio.append((old,out))
    finally:c.close()
    delta=np.array([r['base_loss']-r['loss']for r in captures]);sem=float(np.std(delta,ddof=1)/np.sqrt(12));robust=bool(np.mean(delta)>max(.0005,3*sem));impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];response,_=candidate.render(impulse);first=int(np.flatnonzero(np.max(abs(response),axis=1)>1e-9)[0])-4096;assert first==0 and candidate.latency()==0
    archive=ROOT/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';members=[]
    with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
        for repeat,pair in enumerate(audio):
            for label,y in zip(['control','candidate'],pair):
                buffer=io.BytesIO();sf.write(buffer,y,48000,format='WAV',subtype='FLOAT');blob=buffer.getvalue();name=f'{label}-{repeat}.wav';info=tarfile.TarInfo(name);info.size=len(blob);tar.addfile(info,io.BytesIO(blob));members.append(dict(name=name,SHA256=hashlib.sha256(blob).hexdigest()))
    with tarfile.open(archive)as tar:
        for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
    median=sorted(range(12),key=lambda k:captures[k]['loss'])[6];sf.write(ROOT/'SELECTED_COMBINED_WIP.wav',audio[median][1],48000,subtype='FLOAT')
    summary=dict(cohort='measured-ZL-boundary-expansion-after21',training_cases=len(rows),current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),paired_difference_SEM=sem,robust_improvement=robust,selected_physical_values=[dict(parameter=p['title'],value=actual[p['key']])for p in specs],cold_instance_replay_max_abs_error=cold_error,component_state_roundtrip_exact=True,declared_PDC_frames=0,impulse_first_response_frames=first,only_three_held_notes=True,source_and_all_native_settings_unchanged=True,captures=captures,archive_members=members,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
    choice=dict(prior,loss=summary['candidate_mean'],native_ZL_component_state=str(saved),recorded_audio=str(ROOT/'SELECTED_COMBINED_WIP.wav'),measured_parameter_range_study=True,not_automatically_adopted_into_main_or_public_FL_project=True)
    (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');(ROOT/'CANDIDATE_RESEARCH_ONLY.json').write_text(json.dumps(choice,indent=2)+'\n');record('measured_boundary_study_complete_not_adopted',summary={k:v for k,v in summary.items()if k not in ['captures','archive_members']});print('ACTUAL_MEASURED_BOUNDARY_STUDY_COMPLETE',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
    record('failed_preserve_confirmed_main_and_all_complete_kits',error=traceback.format_exc());raise
finally:
    for c in clients:c.close()
