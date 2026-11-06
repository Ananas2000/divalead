"""Actual native Chorus wet/depth/cutoff screen; source and incoming MIDI fixed."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import native_Chorus11_620_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;J=Path(__file__).resolve().parent;rows=[];captures=[];members=[];c=p=z=t=None
cache=threading.local();old_power=q.a.powers
def powers(*args,**kwargs):
    result=old_power(*args,**kwargs);cache.power=result[0];return result
q.a.powers=powers
def assess(y):
    d=q.assess(y);err=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(err[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.asarray(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d
def record(phase,**kwargs):
    d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),source_Diva281_MIDI3held_ARP_ADSR_unchanged=True,only_native_Chorus_depth_cutoff_and_parallel_wet_changed=True,both_ZL_and_final_trim_fixed=True,frozen_current_cohort=620,not_adopted=True,reference_match_reached=False,**kwargs);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)
assert q.prior['source_accepted_cohort']==620
depth=int(round(q.seed['x'][87]*5000));cutoff=int(round(q.seed['x'][92]*5000));wet=q.seed['x'][93];assert depth==2041 and cutoff==4640
(R/'ANCHOR40_PRIMARY.bin').write_bytes(Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP40/verification/ZL40_PRIMARY_COMPONENT.bin').read_bytes())
def configure(delta):
    d0,d1,d2=delta;actual_wet=round((wet+d0*.025)*12800)/12800;actual_depth=round(depth+d1*120);actual_cutoff=round(cutoff+d2*120)
    assert 0<actual_wet<1 and 0<=actual_depth<=5000 and 0<=actual_cutoff<=5000
    c.load_state(3,R/'CHORUS_CONTROL.bin');c.set(3,1,actual_depth);c.set(3,10,actual_cutoff);c.gain(0,1-actual_wet);c.gain(1,actual_wet)
    return dict(wet=actual_wet,depth_raw=actual_depth,cutoff_raw=actual_cutoff)
def cascade(raw,anchor=False):
    p.load(R/('ANCHOR40_PRIMARY.bin'if anchor else'PRIMARY.bin'));z.load(R/'POST.bin');mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(out)
def evaluate(label,delta):
    folder=R/label;folder.mkdir();settings=configure(delta);c.save_state(3,folder/'CHORUS.bin');ds=[]
    for rep in range(3):
        configure(delta);raw,_=c.render();out=cascade(raw);ds.append(assess(out))
        if rep==0:
            sf.write(folder/'FIRST_ACTUAL_NATIVE.wav',raw,48000,subtype='FLOAT');sf.write(folder/'FIRST_ACTUAL_FULL_WIP.wav',out,48000,subtype='FLOAT')
    row=dict(label=label,delta=list(map(float,delta)),folder=str(folder),settings=settings,loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),captures=ds);rows.append(row);(R/'PARTIAL_CASES.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_native_Chorus_tone_model',label=label);return row
def fresh(row):
    ds=[]
    for k in range(6):configure(row['delta']);raw,_=c.render();out=cascade(raw);ds.append(assess(out))
    return dict(captures=ds,loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['Air']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds))
def add(tar,name,y):
    buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');blob=buf.getvalue();i=tarfile.TarInfo(name);i.size=len(blob);tar.addfile(i,io.BytesIO(blob));members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(axes=['wet_step.025','depth_raw_step120','cutoff_raw_step120'],baseline3_and_6_derivative_models_then_up_to4_joint_fractions=True,full_original_Chorus_random_phase_preserved=True,no_audio_or_control_averaging=True,fresh6_control_and_top3_candidates=True,training_gain_over0003_and_Air_nonincreasing=True,entirely_NEW12_if_qualified=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcoldpositive=True,Air_first10_AND_bothcold_nonincreasing_vs_current620_AND_full40=True,TONE_nonincreasing=True,all12_stereo_upper148_abs16_lowmid325_paired002=True,all_other_native11_Diva_all281_MIDI3_ARP_ADSR_both_ZL_finaltrim_fixed=True,requires_supported_native_bundle_rebuild_no_cache_replay_latest_BEST_full_FL20_export_before_adoption=True),indent=2)+'\n')
try:
    c=q.native(q.source['native_input'],'NativeChorus11-620-N-'+str(os.getpid()));p=q.WinVST3('NativeChorus11-620-P-'+str(os.getpid()));z=q.WinVST3('NativeChorus11-620-Z-'+str(os.getpid()));t=NativePostTrim(R/'buffers','NativeChorus11-620-T-'+str(os.getpid()),cleanup_on_close=True);t.load(q.prior['post_native_trim_state']);c.save_state(3,R/'CHORUS_CONTROL.bin')
    baseline=evaluate('baseline',[0,0,0])
    for j in range(3):
        for sign in[-1,1]:delta=np.zeros(3);delta[j]=sign;evaluate(f'derivative-{j}-{sign}',delta)
    direction=np.zeros(3)
    for j in range(3):
        best=min([r for r in rows if r['label'].startswith(f'derivative-{j}-')],key=lambda r:r['loss'])
        if best['loss']<baseline['loss']:direction[j]=best['delta'][j]
    if np.any(direction):
        for fraction in[.25,.5,1.,1.5]:evaluate('joint-'+str(fraction),direction*fraction)
    candidates=sorted([r for r in rows[1:]if r['all_stereo']and r['settings']!=baseline['settings']],key=lambda r:r['loss'])[:3];control=fresh(baseline);ranked=[dict(model=row,fresh=fresh(row))for row in candidates];eligible=[r for r in ranked if r['fresh']['all_stereo']and r['fresh']['Air']<=control['Air']];winner=min(eligible,key=lambda r:r['fresh']['loss'])if eligible else None;ready=bool(winner and control['loss']-winner['fresh']['loss']>.0003)
    result=dict(training_models=len(rows),actual_training_native_cascade_renders=len(rows)*3,fresh_control=control,fresh_ranked=ranked,winner=winner,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,frozen_current_cohort=620)
    (R/'FROZEN_BEFORE_NEW12.json').write_text(json.dumps(result,indent=2)+'\n')
    if ready:
        candidate=winner['model'];configure(candidate['delta']);c.save_state(3,R/'CANDIDATE_CHORUS.bin');arc=R/'ALL60_NEW_NATIVE_CONTROL_ANCHOR_CANDIDATE_WAVs.tar.gz'
        with tarfile.open(arc,'w:gz',compresslevel=3)as tar:
            for rep in range(12):
                if rep in[10,11]:c.close();c=q.native(q.source['native_input'],'NativeChorus11-620-Cold-'+str(rep)+'-'+str(os.getpid()))
                configure([0,0,0]);raw0,_=c.render();old=cascade(raw0);d0=assess(old);anchor=cascade(raw0,True);da=assess(anchor);configure(candidate['delta']);raw1,_=c.render();out=cascade(raw1);d1=assess(out);captures.append(dict(rep=rep,control=d0,anchor40=da,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['Air']-d0['Air'],Air_delta_vs40=d1['Air']-da['Air']))
                for name,y in [('native-control',raw0),('native-candidate',raw1),('control620',old),('anchor40',anchor),('candidate',out)]:add(tar,f'{name}-{rep}.wav',y)
                if rep==0:
                    for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL620',old),('ANCHOR40',anchor),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
                (R/'PARTIAL_NEW12_METRICS.json').write_text(json.dumps(captures,indent=2)+'\n');record('actual_NEW12_native_Chorus_screen',completed_pairs=rep+1)
        g=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);aa=np.array([r['Air_delta_vs40']for r in captures]);s6=float(g[:6].std(ddof=1)/np.sqrt(6));s10=float(g[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guard=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);passed=bool(g[:6].mean()>max(.0005,3*s6)and g[:10].mean()>max(.0005,3*s10)and min(g[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and aa[:10].mean()<=0 and max(aa[10:])<=0 and tone<=0 and guard)
        with tarfile.open(arc)as tar:
            for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
        result.update(captures=captures,archive_members=members,first6_gain=float(g[:6].mean()),first6_SEM=s6,first10_gain=float(g[:10].mean()),first10_SEM=s10,cold2_gains=g[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_Air_delta_vs40=float(aa[:10].mean()),cold2_Air_delta_vs40=aa[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guard,robust_improvement=passed)
    (R/'completion.json').write_text(json.dumps(result,indent=2)+'\n');record('finite_native_Chorus11_current620_complete',sufficient_screen=ready,robust_improvement=result['robust_improvement']);print(json.dumps({k:v for k,v in result.items()if k not in['winner','fresh_control','fresh_ranked','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_current620',error=traceback.format_exc());raise
finally:
    for host in[c,p,z,t]:
        if host is not None:host.close()
