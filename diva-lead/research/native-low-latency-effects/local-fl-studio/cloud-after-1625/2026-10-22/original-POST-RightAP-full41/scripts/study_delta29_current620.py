"""Test actual existing-filter parameter directions on current620; no audio blending.

Old fine109 point FAILED acceptance. Its parameter direction is research only.
All quality/air/stereo gates remain fixed, with a stricter training stereo margin.
"""
from pathlib import Path
import csv,datetime,hashlib,io,itertools,json,os,shutil,struct,tarfile,threading,traceback
import xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
import delta29_current620_support as q
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
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),models=len(rows),frozen_current_cohort=q.prior['source_accepted_cohort'],source_pre_ZL_native12_MIDI3_ARP_ADSR_unchanged=True,only_existing_two_ZL_and_final_native_linear_LR_gains_changed=True,not_adopted=True,reference_match_reached=False,**kw)
    tmp=state.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(state)
def values(path):
    b=path.read_bytes();return {e.attrib['id']:float(e.attrib['value'])for e in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')}
ids={r['title']:int(r['id'])for r in csv.DictReader((q.D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def title(key):
    import re
    match=re.fullmatch('(target_gain|gain|freq|q|attack)([0-9]+)',key);assert match,key
    return dict(target_gain='Target Gain',gain='Gain',freq='Freq',q='Q',attack='Attack')[match[1]]+match[2]
directions=[]
for name in ['PRIMARY','POST']:
    before=values(OLD/(name+'.bin'));after=values(OLD/('CANDIDATE_'+name+'.bin'));current=values(R/(name+'.bin'))
    directions.append({k:dict(current=current[k],old=before[k],fine=after[k],delta=after[k]-before[k],id=ids[title(k)])for k in before if before[k]!=after[k]})
assert q.prior['source_accepted_cohort']==620,'This protocol freezes620; create a new study for a newer BEST'
shutil.copyfile(q.prior['post_native_trim_state'],R/'TRIM.bin')
base_raw=struct.unpack_from('<6i',(R/'TRIM.bin').read_bytes(),4);assert base_raw==(0,12764,12800,0,0,0)
public=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22')
shutil.copyfile(public/'ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin',R/'ANCHOR40_PRIMARY.bin')
(R/'PARAMETER_DIRECTIONS.json').write_text(json.dumps(directions,indent=2)+'\n')
protocol=dict(old_fine109_NOT_adopted=True,frozen_current620=True,no_audio_blending=True,primary_direction_scales=[0,.5,1],POST_direction_scales=[0,.5,1,1.5,2],native_trim_LR_offsets=[[0,0],[-4,4],[0,8]],both_channel_raw_gain_offsets=[0,4],only_actual_loaded_ZL_and_native_outputs=True,three_common_training_native_draws_plus_two_unused=True,training_gain_over0003=True,training_Air_mean_below_min_current620_full40_by0004=True,training_abs_high_LR_max159=True,training_paired_lowmid_plus0005=True,heldout_gain_over0003=True,entirely_NEW12_required=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_positive=True,Air_first10_AND_bothcold_nonincreasing_vs_current_AND_full40=True,TONE_nonincreasing=True,all12_stereo_upper148_abs16_lowmid325_paired002=True,source_native12_three_held_ARP_ADSR_unchanged=True,latest_BEST_full_supported_export_and_coldZIP_required_before_adoption=True)
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
def configure(model):
    alpha,beta,dl,dr,g=model
    for host,name,direction,scale in zip([p,z],['PRIMARY','POST'],directions,[alpha,beta]):
        host.load(R/(name+'.bin'))
        for key,spec in direction.items():
            if scale:
                host.text(spec['id'],format(spec['current']+scale*spec['delta'],'.12g'))
    t.configure(12764+dl+g,12800+dr+g)
def render(raw,label,model=None):
    if label=='candidate':configure(model)
    else:
        p.load(R/('ANCHOR40_PRIMARY.bin'if label=='anchor40'else'PRIMARY.bin'));z.load(R/'POST.bin');t.load(R/'TRIM.bin')
    mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)
def save_wav(tar,name,y):
    buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');blob=buf.getvalue();info=tarfile.TarInfo(name);info.size=len(blob);tar.addfile(info,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
try:
    record('starting_actual_current620_existing_filter_direction_screen')
    n=q.native(q.source['native_input'],'Delta29-620-N-'+str(os.getpid()));p=q.WinVST3('Delta29-620-P-'+str(os.getpid()));z=q.WinVST3('Delta29-620-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','Delta29-620-T-'+str(os.getpid()),cleanup_on_close=True)
    for k in range(5):
        raw,_=n.render();inputs.append(raw);old=render(raw,'control');anchor=render(raw,'anchor40');controls.append(assess(old));anchors.append(assess(anchor))
        for name,y in [('NATIVE',raw),('CONTROL620',old),('ANCHOR40',anchor)]:sf.write(R/f'TRAIN_{name}_{k}.wav',y,48000,subtype='FLOAT')
    (R/'TRAIN_CONTROL_ANCHOR_METRICS.json').write_text(json.dumps(dict(controls=controls,anchors=anchors),indent=2)+'\n')
    aircap=min(np.mean([d['Air']for d in controls[:3]]),np.mean([d['Air']for d in anchors[:3]]))-.004
    seen={};duplicate_models=[]
    for k,(alpha,beta,offset,g)in enumerate(itertools.product([0,.5,1],[0,.5,1,1.5,2],[(0,0),(-4,4),(0,8)],[0,4])):
        model=[alpha,beta,*offset,g];folder=R/f'model-{k:03d}';folder.mkdir();configure(model)
        for host,name in [(p,'PRIMARY'),(z,'POST'),(t,'TRIM')]:host.save(folder/(name+'.bin'))
        fingerprint=hashlib.sha256(b''.join((folder/(name+'.bin')).read_bytes()for name in ['PRIMARY','POST','TRIM'])).hexdigest()
        if fingerprint in seen:
            duplicate_models.append(dict(model=model,fingerprint=fingerprint,identical_to=seen[fingerprint]));continue
        seen[fingerprint]=model;ds=[]
        for raw in inputs[:3]:out=render(raw,'candidate',model);ds.append(assess(out))
        feasible=bool(np.mean([d['Air']for d in ds])<=aircap and all(d['stereo_preservation_passed']and max(abs(np.array(d['LR_dB'])[1:]))<=1.59 and d['lowmid_error']<=controls[j]['lowmid_error']+.005 for j,d in enumerate(ds)))
        gain=float(np.mean([base['loss']-d['loss']for base,d in zip(controls[:3],ds)]))
        row=dict(index=k,model=model,folder=str(folder),fingerprint=fingerprint,loss=float(np.mean([d['loss']for d in ds])),gain=gain,Air=float(np.mean([d['Air']for d in ds])),feasible=feasible,captures=ds);rows.append(row);sf.write(folder/'LAST_ACTUAL_WIP.wav',out,48000,subtype='FLOAT')
        (R/'PARTIAL_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_existing_filter_parameter_transplant_screen',completed_models=k+1,training_Air_cap=aircap)
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
            pp=q.WinVST3('Delta29-620-ColdP-'+str(k));zz=q.WinVST3('Delta29-620-ColdZ-'+str(k));tt=NativePostTrim(R/'cold-buffers','Delta29-620-ColdT-'+str(k),cleanup_on_close=True)
            try:
                for host,name in [(pp,'PRIMARY'),(zz,'POST'),(tt,'TRIM')]:
                    path=R/('CANDIDATE_'+name+'.bin');host.load(path);saved=R/f'COLD{k}_{name}.bin';host.save(saved);assert saved.read_bytes()==path.read_bytes()
                mid,_=pp.render(inputs[0]);pre,_=zz.render(mid);out=tt.render(pre);assert pp.latency()+zz.latency()==0
                if expected is None:expected=out.copy();sf.write(R/'CANONICAL_COLD_CANDIDATE.wav',out,48000,subtype='FLOAT')
                np.testing.assert_allclose(out,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-expected).max()))
            finally:pp.close();zz.close();tt.close()
        (R/'ACTUAL_COLD_COMPONENT_TRIM_PROOF.json').write_text(json.dumps(dict(two_cold_actual_errors=errors,all_component_trim_resaves_byte_exact=True,combined_ZL_PDC=0),indent=2)+'\n')
        n.close();n=q.native(q.source['native_input'],'Delta29-620-New12-'+str(os.getpid()));arc=R/'ALL48_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz'
        with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
            for rep in range(12):
                if rep in[10,11]:n.close();n=q.native(q.source['native_input'],'Delta29-620-ColdNative-'+str(rep)+'-'+str(os.getpid()))
                raw,_=n.render();old=render(raw,'control');d0=assess(old);anchor=render(raw,'anchor40');da=assess(anchor);candidate=render(raw,'candidate',winner['model']);d1=assess(candidate);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
                for name,y in [('native',raw),('control620',old),('anchor40',anchor),('candidate',candidate)]:save_wav(tar,f'{name}-{rep}.wav',y)
                if rep==0:
                    for name,y in [('NATIVE',raw),('CONTROL620',old),('ANCHOR40',anchor),('CANDIDATE',candidate)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
                (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(captures,indent=2)+'\n');record('actual_frozen_NEW12_comparison',completed_pairs=rep+1)
        gain=np.array([d['gain']for d in captures]);air=np.array([d['Air_delta']for d in captures]);aa=np.array([d['Air_delta_vs40']for d in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([d['candidate']['assessment']['tone_score']-d['control']['assessment']['tone_score']for d in captures[:10]]));guards=all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 for d in captures);passed=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guards)
        with tarfile.open(arc)as tar:
            for member in members:assert hashlib.sha256(tar.extractfile(member['name']).read()).hexdigest()==member['SHA256']
        result.update(captures=captures,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guards,robust_improvement=passed)
    (R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('finite_delta29_current620_complete',robust_improvement=result['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in result.items()if k not in['winner','heldout','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current_BEST',error=traceback.format_exc());raise
finally:
    for host in[n,p,z,t]:
        if host is not None:host.close()
