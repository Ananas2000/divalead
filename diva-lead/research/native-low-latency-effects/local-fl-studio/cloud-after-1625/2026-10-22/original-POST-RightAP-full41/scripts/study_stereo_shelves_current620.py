"""Test actual existing-filter parameter directions on current620; no audio blending.

Old fine109 point FAILED acceptance. Its parameter direction is research only.
All quality/air/stereo gates remain fixed, with a stricter training stereo margin.
"""
from pathlib import Path
import csv,datetime,hashlib,io,itertools,json,os,shutil,struct,tarfile,threading,traceback
import xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
import stereo_shelves620_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;J=Path(__file__).resolve().parent;OLD=Path('/tmp/divalead-native12-common109-fine-margin-20261104')
state=q.STATE;n=p=z=t=None;rows=[];members=[];captures=[];inputs=[];controls=[];anchors=[]
cache=threading.local();original_powers=q.a.powers
def powers(*args,**kw):
    value=original_powers(*args,**kw);cache.power=value[0];return value
q.a.powers=powers
def assess(y):
    d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15))
    d['Air']=float(np.maximum(e[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d
def record(phase,**kw):
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),models=len(rows),frozen_current_cohort=q.prior['source_accepted_cohort'],source_pre_ZL_native12_MIDI3_ARP_ADSR_unchanged=True,only_POST_two_static_HighShelf_filters_added=True,all_other_DSP_unchanged=True,not_adopted=True,reference_match_reached=False,**kw)
    tmp=state.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(state)
def values(path):
    b=path.read_bytes();return {e.attrib['id']:float(e.attrib['value'])for e in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')}
ids={r['title']:int(r['id'])for r in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
assert q.prior['source_accepted_cohort']==620,'This protocol freezes620; create a new study for a newer BEST'
shutil.copyfile(q.prior['post_native_trim_state'],R/'TRIM.bin')
base_raw=struct.unpack_from('<6i',(R/'TRIM.bin').read_bytes(),4);assert base_raw==(0,12764,12800,0,0,0)
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22')
shutil.copyfile(public/'ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin',R/'ANCHOR40_PRIMARY.bin')

protocol=dict(two_new_actual_POST_HighShelf_slots7_Left_and8_Right=True,all_existing_POST_filters_and_PRIMARY_native12_and_final_trim_fixed=True,no_added_plugin=True,frequencies=[1000,1600,2400,3600,5400],differential_gain_half=[.1,.25,.5,.75,1,1.5],common_gain_ratio=[-.5,0,.5,1],Q=.707,ordinary_actual_ZL_minphase_lookahead0_AutoGainOff=True,only_original_is_target=True,three_common_training_native_draws_plus_two_unused=True,training_gain_over0003=True,training_Air_mean_below_min_current620_full40_by0004=True,training_abs_high_LR_max159=True,training_paired_lowmid_plus0005=True,heldout_gain_over0003=True,entirely_NEW12_required=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_positive=True,Air_first10_AND_bothcold_nonincreasing_vs_current_AND_full40=True,TONE_nonincreasing=True,all12_stereo_upper148_abs16_lowmid325_paired002=True,source_native12_three_held_ARP_ADSR_unchanged=True,latest_BEST_full_supported_export_and_coldZIP_required_before_adoption=True)
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
def configure(model):
    frequency,half_difference,common_ratio=model;p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');t.load(R/'TRIM.bin')
    if not half_difference:return
    common=common_ratio*half_difference
    for slot,mode,gain in [(7,'Left',common-half_difference),(8,'Right',common+half_difference)]:
        for title,value in [('Filter Status','On'),('Filter Type','High Shelf'),('LRMode',mode),('Order','12 dB/oct'),('Freq',frequency),('Gain',gain),('Q',.707)]:z.text(ids[title+str(slot)],str(value))
def render(raw,label,model=None):
    if label=='candidate':configure(model)
    else:
        p.load(R/('ANCHOR40_PRIMARY.bin'if label=='anchor40'else'PRIMARY.bin'));z.load(R/'POST.bin');t.load(R/'TRIM.bin')
    mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)
def save_wav(tar,name,y):
    buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');blob=buf.getvalue();info=tarfile.TarInfo(name);info.size=len(blob);tar.addfile(info,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
try:
    record('starting_actual_current620_differential_stereo_shelves')
    n=q.native(q.source['native_input'],'DifferentialShelf-620-N-'+str(os.getpid()));p=q.WinVST3('DifferentialShelf-620-P-'+str(os.getpid()));z=q.WinVST3('DifferentialShelf-620-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','DifferentialShelf-620-T-'+str(os.getpid()),cleanup_on_close=True)
    configure((2400,.1,0));z.save(R/'SHELF_ENUM_PROBE.bin');z.dump(R/'SHELF_ENUM_ALL610.tsv')
    probe=values(R/'SHELF_ENUM_PROBE.bin')
    assert probe['filter_status7']==probe['filter_status8']==2 and probe['filter_type7']==probe['filter_type8']==3 and probe['lr_mode7']==1 and probe['lr_mode8']==2,probe
    assert probe['total_filter_structure']==0 and probe['total_lookahead']==0 and probe['total_auto_gain']==0
    for k in range(5):
        raw,_=n.render();inputs.append(raw);old=render(raw,'control');anchor=render(raw,'anchor40');controls.append(assess(old));anchors.append(assess(anchor))
        for name,y in [('NATIVE',raw),('CONTROL620',old),('ANCHOR40',anchor)]:sf.write(R/f'TRAIN_{name}_{k}.wav',y,48000,subtype='FLOAT')
    (R/'TRAIN_CONTROL_ANCHOR_METRICS.json').write_text(json.dumps(dict(controls=controls,anchors=anchors),indent=2)+'\n')
    aircap=min(np.mean([d['Air']for d in controls[:3]]),np.mean([d['Air']for d in anchors[:3]]))-.004
    seen={};duplicate_models=[]
    models=[(2400,0,0)]+list(itertools.product([1000,1600,2400,3600,5400],[.1,.25,.5,.75,1,1.5],[-.5,0,.5,1]))
    for k,model in enumerate(models):
        folder=R/f'model-{k:03d}';folder.mkdir();configure(model)
        for host,name in [(p,'PRIMARY'),(z,'POST'),(t,'TRIM')]:host.save(folder/(name+'.bin'))
        fingerprint=hashlib.sha256(b''.join((folder/(name+'.bin')).read_bytes()for name in ['PRIMARY','POST','TRIM'])).hexdigest()
        if fingerprint in seen:
            duplicate_models.append(dict(model=model,fingerprint=fingerprint,identical_to=seen[fingerprint]));continue
        seen[fingerprint]=model;ds=[]
        for raw in inputs[:3]:out=render(raw,'candidate',model);ds.append(assess(out))
        feasible=bool(np.mean([d['Air']for d in ds])<=aircap and all(d['stereo_preservation_passed']and max(abs(np.array(d['LR_dB'])[1:]))<=1.59 and d['lowmid_error']<=controls[j]['lowmid_error']+.005 for j,d in enumerate(ds)))
        gain=float(np.mean([base['loss']-d['loss']for base,d in zip(controls[:3],ds)]))
        row=dict(index=k,model=model,folder=str(folder),fingerprint=fingerprint,loss=float(np.mean([d['loss']for d in ds])),gain=gain,Air=float(np.mean([d['Air']for d in ds])),feasible=feasible,captures=ds);rows.append(row);sf.write(folder/'LAST_ACTUAL_WIP.wav',out,48000,subtype='FLOAT')
        (R/'PARTIAL_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_differential_stereo_shelf_screen',completed_models=k+1,training_Air_cap=aircap)
    (R/'DUPLICATE_QUANTIZED_MODELS.json').write_text(json.dumps(duplicate_models,indent=2)+'\n')
    eligible=[d for d in rows if d['feasible']and d['gain']>.0003];winner=min(eligible,key=lambda d:d['loss'])if eligible else None;held=[];ready=False
    if winner:
        for k in [3,4]:
            out=render(inputs[k],'candidate',winner['model']);d=assess(out);held.append(dict(input=k,control=controls[k],anchor40=anchors[k],candidate=d,gain=controls[k]['loss']-d['loss']));sf.write(R/f'UNSEEN_CANDIDATE_{k}.wav',out,48000,subtype='FLOAT')
        ready=bool(np.mean([d['gain']for d in held])>.0003 and all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 and d['candidate']['Air']<=min(d['control']['Air'],d['anchor40']['Air'])+.02 for d in held))
    result=dict(training_models=len(rows),actual_training_cascade_renders=3*len(rows),duplicate_models=duplicate_models,winner=winner,heldout=held,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_current_cohort=620)
    (R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(result,indent=2)+'\n')
    if ready:
        configure(winner['model'])
        for host,name in [(p,'PRIMARY'),(z,'POST'),(t,'TRIM')]:host.save(R/('CANDIDATE_'+name+'.bin'))
        errors=[];expected=None
        for k in range(2):
            pp=q.WinVST3('DifferentialShelf-620-ColdP-'+str(k));zz=q.WinVST3('DifferentialShelf-620-ColdZ-'+str(k));tt=NativePostTrim(R/'cold-buffers','DifferentialShelf-620-ColdT-'+str(k),cleanup_on_close=True)
            try:
                for host,name in [(pp,'PRIMARY'),(zz,'POST'),(tt,'TRIM')]:
                    path=R/('CANDIDATE_'+name+'.bin');host.load(path);saved=R/f'COLD{k}_{name}.bin';host.save(saved);assert saved.read_bytes()==path.read_bytes()
                mid,_=pp.render(inputs[0]);pre,_=zz.render(mid);out=tt.render(pre);assert pp.latency()+zz.latency()==0
                if expected is None:expected=out.copy();sf.write(R/'CANONICAL_COLD_CANDIDATE.wav',out,48000,subtype='FLOAT')
                np.testing.assert_allclose(out,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-expected).max()))
            finally:pp.close();zz.close();tt.close()
        (R/'ACTUAL_COLD_COMPONENT_TRIM_PROOF.json').write_text(json.dumps(dict(two_cold_actual_errors=errors,all_component_trim_resaves_byte_exact=True,combined_ZL_PDC=0),indent=2)+'\n')
        n.close();n=q.native(q.source['native_input'],'DifferentialShelf-620-New12-'+str(os.getpid()));arc=R/'ALL48_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz'
        with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
            for rep in range(12):
                if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'DifferentialShelf-620-ColdNative-'+str(rep)+'-'+str(os.getpid()))
                raw,_=n.render();old=render(raw,'control');d0=assess(old);anchor=render(raw,'anchor40');da=assess(anchor);candidate=render(raw,'candidate',winner['model']);d1=assess(candidate);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
                for name,y in [('native',raw),('control620',old),('anchor40',anchor),('candidate',candidate)]:save_wav(tar,f'{name}-{rep}.wav',y)
                if rep==0:
                    for name,y in [('NATIVE',raw),('CONTROL620',old),('ANCHOR40',anchor),('CANDIDATE',candidate)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
                (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(captures,indent=2)+'\n');record('actual_frozen_NEW12_comparison',completed_pairs=rep+1)
        gain=np.array([d['gain']for d in captures]);air=np.array([d['Air_delta']for d in captures]);aa=np.array([d['Air_delta_vs40']for d in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([d['candidate']['assessment']['tone_score']-d['control']['assessment']['tone_score']for d in captures[:10]]));guards=all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 for d in captures);passed=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guards)
        with tarfile.open(arc)as tar:
            for member in members:assert hashlib.sha256(tar.extractfile(member['name']).read()).hexdigest()==member['SHA256']
        result.update(captures=captures,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guards,robust_improvement=passed)
    (R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('finite_differential_shelves620_complete',robust_improvement=result['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in result.items()if k not in['winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_BEST',error=traceback.format_exc());raise
finally:
    for host in[n,p,z,t]:
        if host is not None:host.close()
