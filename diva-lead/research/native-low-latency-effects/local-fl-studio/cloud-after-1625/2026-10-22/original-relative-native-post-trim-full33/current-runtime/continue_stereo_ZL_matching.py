"""Continue actual low-latency VST3 matching until stop or observed reserves.

Two real-plugin workers with two actual ZL instances each, actual fresh native inputs, two held-out realizations,
fresh paired confirmation, real state replay and lossless validation WAVs.
No FL GUI or complete reference-match claim. Uses only the original three
incoming held notes per phrase; the frozen actual Diva source is unchanged.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,io,json,os,queue,shutil,struct,tarfile,threading,time,traceback
import xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from win_vst3 import D
from stereo_cascade_runtime import CascadedZL as WinVST3, POST, EXPECTED_POST
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=Path('/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87');ROOT.mkdir(exist_ok=True)
STATE=N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json';PAUSE=N/'zl-stereo-numerical.pause';STOP=N/'zl-stereo-continuation.stop'
OWNER='two-ZL-stereo-continuation-20261024'
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
        fixed_post_component=str(POST),fixed_post_SHA256=EXPECTED_POST,full_base_kit=best.get('full_public_kit_directory','ZL-WIP24'),additional_lowmid_300_800_error_limit_dB=best.get('lowmid_error_limit_dB',3.35),upper_stereo_error_limit_dB=best.get('upper_stereo_error_limit_dB',1.5),requires_post_native_trim=bool(best.get('requires_post_native_trim')),actual_native_post_trim_hosts=[identity(c.trim.chain.proc.pid)for c in clients if c.trim],configured_real_VST3_workers=2,real_VST3_instances_per_worker=2,requires_two_ZL_instances=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,actual_VST3_hosts=[identity(host.child.pid)for c in clients for host in [c.primary,c.post]],only_three_held_notes=True,
        source_Diva_unchanged_within_current_ZL_refinement=True,source_Diva_preset_SHA256=seed['source_manifest']['source_preset_SHA256'],source_tone_changed_since_ZL16=bool(best.get('source_tone_changed_since_ZL16')),native_12_effects_pinned_to_current_validated_base=True,native_base_export_directory=best.get('native_base_export_directory','legacy-base17'),actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(obj,indent=2)+'\n');p.replace(STATE)
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
best=read(ROOT/'BEST_CANDIDATE.json')if(ROOT/'BEST_CANDIDATE.json').exists()else read(D/'ZL-extra-dynamic-original-reference-01/candidate-research-only.json');seed=best['native_base'];best_component=Path(best['native_ZL_component_state'])
assert not seed.get('native_saved_state_bundle') or seed['native_saved_state_bundle']['settings_SHA256']==native_dsp_settings_SHA256(seed['x'],seed),'Native replay schema mismatch: load published fl20_curve.py before running this saved base'
pool=queue.Queue();mutex=threading.Lock();rows=[];current=None;work=None
reference,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True)
assert hashlib.sha256(Path('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav').read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f'
from fl20_objective import a as original_analysis
frequency=np.fft.rfftfreq(len(reference),1/48000)
stereo_masks=[(frequency>=lo)&(frequency<hi)for lo,hi in [(2000,5000),(5000,10000),(10000,14000)]]
def lr_bands(y):
    power=abs(np.fft.rfft(y,axis=0))**2
    return np.array([10*np.log10(power[m,0].sum()/power[m,1].sum())for m in stereo_masks])
reference_LR=lr_bands(reference)
lowmid_mask=(frequency>=300)&(frequency<800)
def lowmid_lr(y):
    power=abs(np.fft.rfft(y,axis=0))**2
    return float(10*np.log10(power[lowmid_mask,0].sum()/power[lowmid_mask,1].sum()))
reference_lowmid_LR=lowmid_lr(reference)
def stereo_diag(y):
    edit=original_analysis.h.edit_aligned(original_analysis.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));lr=lr_bands(edit);error=float(np.sqrt(np.mean((lr-reference_LR)**2)))
    low=lowmid_lr(edit);low_error=abs(low-reference_lowmid_LR)
    # Additional preservation constraint; original fit/loss/acceptance gates
    # are unchanged. Keep the independently confirmed ZL25 low-mid repair.
    result=dict(stereo_high_band_error=error,high_LR_dB=lr.tolist(),lowmid_300_800_LR_dB=low,lowmid_300_800_error_dB=low_error,lowmid_preservation_passed=bool(low_error<=best.get('lowmid_error_limit_dB',3.35)),stereo_preservation_passed=bool(error<=best.get('upper_stereo_error_limit_dB',1.5)and np.max(np.abs(lr))<=1.6 and low_error<=best.get('lowmid_error_limit_dB',3.35)))
    if best.get('positive_excess_air_preservation_required'):
        power=original_analysis.powers(edit)[0];e=10*np.log10(np.maximum(power,1e-15)/np.maximum(original_analysis.TP,1e-15));result['positive_excess_air_3500_6500_dB']=float(np.maximum(e[:,4:6,2:],0).mean())
    return result
def eligible_min(checked,fallback):return min([fallback]+[r for r in checked if r['stereo_preservation_passed']],key=lambda r:r['loss'])
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
        for title,key,step,lo,hi,log in [('Gain','gain',.2,-10,10,False),('Freq','freq',.09,20,20000,True),('Q','q',.12,.15,25,True)]:add(title+str(k),key+str(k),step,lo,hi,log)
    allpass=[k for k in range(24)if v['filter_status'+str(k)]==2 and v['filter_type'+str(k)]==9]
    for k in allpass:
        add('Freq'+str(k),'freq'+str(k),.09,20,18000,True);add('Q'+str(k),'q'+str(k),.12,.15,25,True)
    dynamic=[k for k in range(24)if v['filter_status'+str(k)]==2 and v['dynamic_on'+str(k)]==1]
    for k in dynamic:
        for title,key,step,lo,hi,log in [('Gain','gain',.25,-30,30,False),('Freq','freq',.09,200,18000,True),('Q','q',.12,.15,25,True),('Target Gain','target_gain',.4,-30,30,False),
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
        row=dict(label=label,x=list(x),loss=loss,assessment=features.local.last);row.update(stereo_diag(y))
        if save:
            with mutex:rows.append(row)
        return row
    finally:pool.put(c)
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,purpose='genuine persistent actual VST3 matching with fresh paired confirmations and disk guards'),f)
try:
    assert not STOP.exists();rng=np.random.default_rng(2026102304)
    for k in range(2):
        c=WinVST3('ZL-continuous-worker-'+str(k));clients.append(c);pool.put(c)
    cohort=max([int(p.name.split('-')[1])for p in ROOT.glob('cohort-[0-9][0-9][0-9][0-9]')],default=0)
    with concurrent.futures.ThreadPoolExecutor(2)as executor:
        while not STOP.exists():
            reserves=dict(root_free_MiB=shutil.disk_usage('/workspace').free/2**20,tmp_free_MiB=shutil.disk_usage('/tmp').free/2**20)
            # Existing frozen/scores buffers are reused. Measured new space per
            # accepted cohort is <48MiB, including verified lossless WAV archive;
            # retain64MiB after that worst case instead of accumulating caches.
            if reserves['root_free_MiB']<208 or reserves['tmp_free_MiB']<128:
                record('stopped_at_observed_storage_reserve_after_completed_cohort',reserves=reserves,best_candidate=best,completed_cohorts=cohort);break
            cohort+=1;work=ROOT/f'cohort-{cohort:04}';work.mkdir();rows=[]
            specs,dynamic=specs_from_component(best_component);initial=[p['value']for p in specs]
            for c in clients:c.load(best_component)
            a=native('ZL-continuous-frozen-source')
            try:
                for phase in range(3):y,_=a.render();y.astype('<f4').tofile(ROOT/f'frozen-{phase}.f32')
            finally:a.close()
            current=evaluate(('current-confirmed-control',initial));control_loss=current['loss']
            # Joint band proposals can cross minima that independent scalar
            # coordinates cannot. Same frozen input and unchanged full original
            # criterion; all proposals still need heldouts and fresh paired6.
            by_band={}
            for j,p in enumerate(specs):
                key=''.join(ch for ch in p['title']if ch.isdigit())
                if key:by_band.setdefault(key,[]).append(j)
            groups=list(by_band.values());coupled=[]
            record('actual_coupled_band_proposals_running',cohort=cohort,cases=len(rows),parameters=len(specs),best_confirmed_mean=best['loss'])
            for proposal in range(48):
                x=list(current['x']);count=1+proposal%3;selected=rng.choice(len(groups),size=min(count,len(groups)),replace=False)
                strength=float(rng.choice([.7,1.4,2.8]))
                for index in selected:
                    for j in groups[int(index)]:
                        p=specs[j];delta=float(rng.normal())*p['step']*strength
                        x[j]=float(np.clip(x[j]*2**delta if p['log']else x[j]+delta,p['lo'],p['hi']))
                coupled.append((f'coupled-{cohort}-{proposal}',x))
            selected=eligible_min(list(executor.map(evaluate,coupled)),current)
            if selected['loss']<current['loss']:current=selected
            for coord in rng.permutation(len(specs)):
                p=specs[coord];cases=[]
                for factor in [-2,-1,1,2]:
                    x=list(current['x']);step=p['step']*(.82**((cohort-1)%5))
                    x[coord]=float(np.clip(x[coord]*2**(factor*step)if p['log']else x[coord]+factor*step,p['lo'],p['hi']))
                    cases.append((f'{cohort}-{coord}-{factor}',x))
                checked=list(executor.map(evaluate,cases));candidate=eligible_min(checked,current)
                if candidate['loss']<current['loss']:current=candidate
                record('actual_coordinate_sweep_running',cohort=cohort,cases=len(rows),parameters=len(specs),best_training_loss=current['loss'],baseline_training_loss=control_loss,best_confirmed_mean=best['loss'],root=str(ROOT))
            held=[]
            for phase in [1,2]:
                baseline=evaluate(('heldout-control',initial),phase,False);candidate=evaluate(('heldout-candidate',current['x']),phase,False)
                held.append(dict(phase=phase,control=baseline,candidate=candidate))
            (work/'training-results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
            (work/'heldout.json').write_text(json.dumps(held,indent=2)+'\n')
            if current['loss']>=control_loss-.0001 or np.mean([r['control']['loss']-r['candidate']['loss']for r in held])<=.0001 or not all(r['candidate']['stereo_preservation_passed']for r in held):continue
            c=clients[0];configure(c,current['x']);state=work/'candidate-component.bin';c.save(state)
            got,_=c.render(input_file=ROOT/'frozen-0.f32');fresh=WinVST3('ZL-continuous-canonical-validation')
            control=WinVST3('ZL-continuous-prior-control');a=native('ZL-continuous-independent6-native');captures=[];audio_pairs=[];validation_raws=[]
            try:
                fresh.load(state);again,_=fresh.render(input_file=ROOT/'frozen-0.f32');replay_error=float(abs(got-again).max())
                # Presets store parameters, not a running detector's history.
                # Hot/cold error is diagnostic. Reproducibility is established
                # with two new instances using the same saved component.
                cold=WinVST3('ZL-continuous-second-cold-replay')
                try:
                    cold.load(state);cold_audio,_=cold.render(input_file=ROOT/'frozen-0.f32');cold_error=float(abs(cold_audio-again).max())
                    np.testing.assert_allclose(cold_audio,again,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
                finally:cold.close()
                fresh.save(work/'component-resaved.bin');assert state.read_bytes()==(work/'component-resaved.bin').read_bytes();control.load(best_component)
                record('actual_independent6_paired_validation',cohort=cohort,training_loss=current['loss'],component_replay_max_abs_error=replay_error)
                for rep in range(8):
                    if rep in [6,7]:a.close();a=native('Stereo24-cold-native-'+str(rep))
                    raw,_=a.render();old,_=control.render(raw);base_loss=score(old);base_diag=stereo_diag(old);out,_=fresh.render(raw);loss=score(out)
                    captures.append(dict(rep=rep,base_loss=base_loss,loss=loss,assessment=features.local.last,control_stereo_diagnostics=base_diag));audio_pairs.append((old,out));validation_raws.append(raw.copy());captures[-1].update(stereo_diag(out))
            finally:a.close();fresh.close();control.close()
            all_delta=np.array([r['base_loss']-r['loss']for r in captures]);delta=all_delta[:6];sem=float(np.std(delta,ddof=1)/np.sqrt(6))
            robust=bool(np.mean(delta)>max(.0005,3*sem)and min(all_delta[6:8])>0 and all(r['stereo_preservation_passed']for r in captures));summary=dict(cohort=cohort,robust_improvement=robust,paired_difference_SEM=sem,
                current_control_mean=float(np.mean([r['base_loss']for r in captures])),candidate_mean=float(np.mean([r['loss']for r in captures])),component_replay_max_abs_error=replay_error,captures=captures)
            if best.get('positive_excess_air_preservation_required'):
                air=np.array([r['positive_excess_air_3500_6500_dB']-r['control_stereo_diagnostics']['positive_excess_air_3500_6500_dB']for r in captures]);cap=best.get('paired_air_increase_limit_dB',.02);air_ok=bool(np.mean(air[:6])<=cap and max(air[6:])<=cap);robust=bool(robust and air_ok);summary.update(robust_improvement=robust,first6_air_increase=float(np.mean(air[:6])),cold2_air_increases=air[6:].tolist(),air_preservation_passed=air_ok)
            summary.update(first6_mean_improvement=float(np.mean(delta)),required_improvement=max(.0005,3*sem),first6_control_mean=float(np.mean([r['base_loss']for r in captures[:6]])),first6_candidate_mean=float(np.mean([r['loss']for r in captures[:6]])),new_native6_and_two_cold_native=True,cold_input_improvements=all_delta[6:8].tolist(),requires_two_ZL_instances=True,only_three_held_notes=True,reference_match_reached=False,cold_instance_replay_max_abs_error=cold_error,cold_instance_replay_bit_exact=bool(cold_error==0),
                cold_numeric_rtol=float(8*np.finfo(np.float32).eps),cold_numeric_atol=1e-12,hot_vs_cold_error_is_diagnostic_only=True)
            if robust:
                items=[];archive=work/'independent8-native-control-candidate-WAVs.tar.gz'
                with tarfile.open(archive,'w:gz',compresslevel=3)as z:
                    for rep,pair in enumerate(audio_pairs):
                        for label,audio in zip(['native-input','control','candidate'],[validation_raws[rep],*pair]):
                            blob=io.BytesIO();sf.write(blob,audio,48000,format='WAV',subtype='FLOAT');b=blob.getvalue();name=f'{label}-{rep}.wav'
                            info=tarfile.TarInfo(name);info.size=len(b);z.addfile(info,io.BytesIO(b));items.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
                with tarfile.open(archive)as z:
                    for item in items:assert hashlib.sha256(z.extractfile(item['name']).read()).hexdigest()==item['SHA256']
                selected=sorted(range(6),key=lambda k:captures[k]['loss'])[3];sf.write(work/'SELECTED_CANDIDATE_WIP.wav',audio_pairs[selected][1],48000,subtype='FLOAT')
                best=dict(best,source_accepted_cohort=cohort,requires_two_ZL_instances=True,post_ZL_component_state=str(work/'fixed-post-component.bin'),loss=summary['candidate_mean'],native_ZL_component_state=str(state),primary_ZL_component_state=str(state),recorded_audio=str(work/'SELECTED_CANDIDATE_WIP.wav'),
                    actual_component_state_roundtrip_exact=True,component_replay_max_abs_error=replay_error,not_compatible_with_standard_x95_exporter=True,
                    not_automatically_adopted_into_public_FL_project=True,extended_parameter_values_are_authoritative_in_component_state=True)
                best_component=state;(ROOT/'BEST_CANDIDATE.json').write_text(json.dumps(best,indent=2)+'\n');summary['lossless_capture_archive']=str(archive);summary['archive_members']=items
            (work/'completion.json').write_text(json.dumps(summary,indent=2)+'\n')
            if robust:
                import subprocess
                subprocess.run(['/workspace/.venvs/divalead/bin/python','-B','/workspace/divalead-work/pc-stereo-20261024/backup_stereo_numeric_checkpoint.py','--cohort',str(work)],check=True)
            print('ZL_CONTINUOUS_COMPLETED_COHORT',cohort,json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
        else:record('stopped_by_explicit_stop_file_after_completed_cohort',best_candidate=best)
except BaseException:
    record('failed_preserve_confirmed_stereo24_and_prior_private_best',error=traceback.format_exc(),best_candidate=best);raise
finally:
    for c in clients:c.close()
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
