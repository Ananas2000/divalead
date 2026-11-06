"""Finer actual Diva PWM/mix/detune/filter probes; exact source chunk and distinct-audio gates."""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile,threading,traceback
import numpy as np,soundfile as sf
import Diva_precise17_support as q
from native_post_trim import NativePostTrim
R=q.ROOT;U=Path(__file__).resolve().parent;assert q.prior['full_public_kit_directory']=='ZL-WIP40';(U/'DIVA_PRECISE17_CURRENT576').symlink_to(R,target_is_directory=True)
rows=[];captures=[];members=[];c=p=z=t=None;cache=threading.local();origpower=q.a.powers
axes=[dict(section='OSC',key='OscMix',index=96,origin=6.5,step=.06),dict(section='OSC',key='PW',index=90,origin=51.91,step=.025),dict(section='OSC',key='Tune1',index=86,origin=-.06,step=.01),dict(section='VCF1',key='Freq',index=148,origin=144.16,step=.12),dict(section='VCF1',key='Res',index=149,origin=12.13,step=.15),dict(section='OSC',key='Tune2',index=87,origin=24.02,step=.01)]
def powers(*args,**kw):v=origpower(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);err=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['positive_excess_air_dB']=float(np.maximum(err[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

def record(phase,**kw):
 d=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,root=str(R),cases=len(rows),frozen_comparator_cohort=q.prior['source_accepted_cohort'],native_base='12',actual_native_host=None if c is None else c.proc.pid,actual_ZL_hosts=[]if p is None else[p.child.pid,z.child.pid],actual_native_trim_host=None if t is None else t.chain.proc.pid,original_is_only_target=True,only_three_held_notes=True,ARP_ADSR_MIDI_and_all_native_states_both_ZL_trim_unchanged=True,only_recorded_Diva_tone_parameters_changed=True,requires_latest_context_and_full_export=True,not_adopted=True,reference_match_reached=False,**kw);tmp=q.STATE.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(q.STATE)

def cascade(raw):
 p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');mid,_=p.render(raw);pre,_=z.render(mid);assert p.latency()+z.latency()==0;return t.render(pre)

def evaluate(label,delta):
 folder=R/label;folder.mkdir();values={(a['section'],a['key']):round(a['origin']+a['step']*v,2) for a,v in zip(axes,delta)if round(a['origin']+a['step']*v,2)!=a['origin']};h2p=folder/'Diva.h2p';h2p.write_text(q.patched(values));raw,actual=q.actual_Diva(h2p,folder/'actual-Diva');changed={i for i in q.original if actual[i]['normalized']!=q.original[i]['normalized']};expected={a['index']for a in axes if(a['section'],a['key'])in values};assert changed==expected,(label,changed,expected)
 if not expected:np.testing.assert_array_equal(raw,q.baseline_raw)
 cold,params_cold=q.actual_Diva(folder/'actual-Diva/Diva_VST_chunk.bin',folder/'canonical-source-chunk-replay');canonical_ok=bool(np.array_equal(cold,raw)and params_cold==actual);distinct=bool(not np.array_equal(raw,q.baseline_raw))
 padded=folder/'padded_source.f32';sf.write(padded,np.pad(raw,((0,32768),(0,0))),48000,format='WAV',subtype='FLOAT');c.load_input(padded);ds=[]
 for k in range(3):
  native,_=c.render();out=cascade(native);ds.append(assess(out))
  if k==0:sf.write(folder/'FIRST_ACTUAL_FULL_PROCESSED.wav',out,48000,subtype='FLOAT')
 audit=dict(all281_audited=True,changed_indices=sorted(changed),changed_parameters={actual[i]['name']:dict(before=q.original[i],after=actual[i])for i in changed},all12_MIDI_events_exact=True,ARP_ADSR_held3_unchanged=True,source_h2p_SHA256=hashlib.sha256(h2p.read_bytes()).hexdigest(),raw_source_SHA256=hashlib.sha256((folder/'actual-Diva/Diva_source.wav').read_bytes()).hexdigest(),padded_source_regenerable=np.pad.__name__+' raw(source.wav) by32768zeroFrames',padded_WAV_container_in_f32_scratch_not_archive=True)
 (folder/'ACTUAL_SOURCE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');row=dict(label=label,source_distinct_from_baseline=distinct,canonical_source_chunk_replay_exact=canonical_ok,delta=list(map(float,delta)),folder=str(folder),source_h2p=str(h2p),source_chunk=str(folder/'actual-Diva/Diva_VST_chunk.bin'),source_audio=str(folder/'actual-Diva/Diva_source.wav'),native_input=str(padded),changed_indices=sorted(changed),loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['positive_excess_air_dB']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),captures=ds);rows.append(row);(R/'PARTIAL_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');record('actual_Diva_tone_case_completed',label=label,mean_loss=row['loss'],Air=row['Air']);return row

def fresh(row,reps):
 c.load_input(row['native_input']);ds=[]
 for k in range(reps):raw,_=c.render();ds.append(assess(cascade(raw)))
 return dict(label=row['label'],loss=float(np.mean([d['loss']for d in ds])),Air=float(np.mean([d['positive_excess_air_dB']for d in ds])),all_stereo=all(d['stereo_preservation_passed']for d in ds),captures=ds)

def add(tar,name,y):
 b=io.BytesIO();sf.write(b,y,48000,format='WAV',subtype='FLOAT');data=b.getvalue();i=tarfile.TarInfo(name);i.size=len(data);tar.addfile(i,io.BytesIO(data));members.append(dict(name=name,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest()))

(R/'PREDECLARED_PROTOCOL.json').write_text(json.dumps(dict(axes=axes,new_material_context='supported bipolar OSstep1 local17 native12 plus actual latest primary',source_models='baseline +12 scalar derivatives +up to4 joint proposals; h2p values round2 decimals; every source chunk replayed; identical source audio rejected',all_actual_Diva281_and12MIDI_audited=True,every_actual_source_chunk_replayed_before_candidate_ranking=True,identical_Diva_audio_not_eligible=True,fresh6_top3_ranking_then_new12_pairs=True,first6_AND_first10_gain_over_max0005_3SEM=True,bothcold_positive=True,all_stereo148_abs16_lowmid325_pairedlowmid002=True,Air_first10_and_bothcold_nonincreasing=True,TONEfirst10_nonincreasing=True,latest_BEST_context_full_supported_export_and_source_chunk_replay_required=True,no_reference_audio_mixed_into_synthesis=True),indent=2)+'\n')
try:
 record('start_actual_Diva_baseline_source_replay');c=q.native(q.source['native_input'],'DivaPrecise17-576-native-'+str(os.getpid()));p=q.WinVST3('DivaPrecise17-576-primary-'+str(os.getpid()));z=q.WinVST3('DivaPrecise17-576-post-'+str(os.getpid()));t=NativePostTrim(R/'buffers','DivaPrecise17-576-trim-'+str(os.getpid()),cleanup_on_close=True);t.load(q.prior['post_native_trim_state']);baseline=evaluate('baseline',[0]*6)
 for j in range(6):
  for sign in[-1,1]:delta=np.zeros(6);delta[j]=sign;evaluate('derivative-'+str(j)+'-'+str(sign),delta)
 direction=np.zeros(6)
 for j in range(6):
  best=min([r for r in rows if r['label'].startswith('derivative-'+str(j)+'-')],key=lambda r:r['loss'])
  if best['loss']<baseline['loss']:direction[j]=best['delta'][j]
 if np.any(direction):
  for fraction in[.25,.5,1.,1.5]:evaluate('joint-'+str(fraction),direction*fraction)
 candidates=sorted([r for r in rows[1:]if r['all_stereo']and r['source_distinct_from_baseline']and r['canonical_source_chunk_replay_exact']],key=lambda r:r['loss'])[:3];control=fresh(baseline,6);ranked=[]
 for row in candidates:ranked.append(dict(model=row,fresh=fresh(row,6)))
 valid=[r for r in ranked if r['fresh']['all_stereo']and r['fresh']['Air']<=control['Air']];winner=min(valid,key=lambda r:r['fresh']['loss'])if valid else None;ready=bool(winner and control['loss']-winner['fresh']['loss']>.0003);summary=dict(training_source_cases=len(rows),actual_training_native_DSP_renders=3*len(rows),frozen_comparator=q.prior['source_accepted_cohort'],baseline=baseline,fresh_control=control,fresh_ranked=ranked,winner=winner,sufficient_screen=ready,robust_improvement=False,not_adopted=True,reference_match_reached=False,latest_context_full_export_required=True);(R/'FROZEN_BEFORE_NEW_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  row=winner['model'];cold,actual=q.actual_Diva(Path(row['source_chunk']),R/'cold-source-chunk-replay');want,_=sf.read(row['source_audio'],dtype='float32',always_2d=True);np.testing.assert_array_equal(cold,want);assert actual==q.parameters(Path(row['source_audio']).parent/'all281.tsv');assert(R/'cold-source-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(row['source_chunk']).read_bytes()
  archive=Path('/tmp/divalead-Diva-local15-new12-'+str(os.getpid())+'.tar.gz');(R/'ALL48_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz').symlink_to(archive)
  with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
   for rep in range(12):
    if rep in[10,11]:c.close();c=q.native(q.source['native_input'],'DivaPrecise17-576-cold-'+str(rep)+'-'+str(os.getpid()))
    c.load_input(q.source['native_input']);raw0,_=c.render();old=cascade(raw0);d0=assess(old);c.load_input(row['native_input']);raw1,_=c.render();out=cascade(raw1);d1=assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,gain=d0['loss']-d1['loss'],Air_delta=d1['positive_excess_air_dB']-d0['positive_excess_air_dB']))
    for name,y in[('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:add(tar,f'{name}-{rep}.wav',y)
    if rep==0:
     for name,y in[('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    record('actual_new12_source_tone_validation',completed_pairs=rep+1)
  gain=np.array([r['gain']for r in captures]);air=np.array([r['Air_delta']for r in captures]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([r['candidate']['assessment']['tone_score']-r['control']['assessment']['tone_score']for r in captures[:10]]));guards=all(r['candidate']['stereo_preservation_passed']and r['candidate']['lowmid_error']<=r['control']['lowmid_error']+.02 for r in captures);robust=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and tone<=0 and guards);summary.update(captures=captures,archive_members=members,first6_mean_gain=float(gain[:6].mean()),first6_SEM=s6,first10_mean_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),TONE_delta=tone,all12_stereo_pairedlowmid=guards,source_chunk_params_audio_replay_exact=True,robust_improvement=robust)
  with tarfile.open(archive)as tar:
   for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_actual_Diva_local15_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in['baseline','fresh_control','fresh_ranked','winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_latest_accepted40',error=traceback.format_exc());raise
finally:
 if c is not None:c.close()
 for host in[p,z,t]:
  if host is not None:host.close()
