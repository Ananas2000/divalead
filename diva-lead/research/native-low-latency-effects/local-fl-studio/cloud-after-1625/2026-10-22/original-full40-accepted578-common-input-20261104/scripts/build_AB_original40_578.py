"""Same real native input, original -> full40 -> accepted578; no new acceptance claim."""
from pathlib import Path
import datetime,hashlib,json,os
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-AB-original40-578-20261104');R.mkdir();P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22';K=PUBLIC/'ZL-WIP40';A=V.parent/'pc-stereo-20261024';read=lambda p:json.loads(Path(p).read_text());best=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert best['source_accepted_cohort']==578;seed=best['native_base'];rawsource=seed['source_manifest']['native_input'];c=NativeChain(rawsource,'AB40-578-Native',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');p=z=t=None
try:
 apply_candidate(c,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 for row in seed['native_saved_state_bundle']['manifest']:
  dst=R/('native-'+str(row['node'])+'.bin');c.save_state(row['node'],dst);assert dst.read_bytes()==(Path(seed['native_saved_state_bundle']['directory'])/row['state']).read_bytes()
 raw,_=c.render();c.close();c=None;sf.write(R/'COMMON_ACTUAL_NATIVE_INPUT.wav',raw,48000,subtype='FLOAT');assert Path(best['post_ZL_component_state']).read_bytes()==(K/'verification/ZL40_POST_COMPONENT.bin').read_bytes();assert Path(best['post_native_trim_state']).read_bytes()==(K/'verification/POST_NATIVE_STEREO_TRIM.bin').read_bytes();outputs={};replays=[]
 for name,path in [('40',K/'verification/ZL40_PRIMARY_COMPONENT.bin'),('578',Path(best['native_ZL_component_state'])),('578-cold2',Path(best['native_ZL_component_state']))]:
  p=WinVST3('AB40-578-P-'+name);z=WinVST3('AB40-578-Z-'+name);t=NativePostTrim(R/'buffers','AB40-578-T-'+name,cleanup_on_close=True)
  for host,src,label in[(p,path,'PRIMARY'),(z,Path(best['post_ZL_component_state']),'POST'),(t,Path(best['post_native_trim_state']),'TRIM')]:host.load(src);dst=R/(name+'-'+label+'.bin');host.save(dst);assert dst.read_bytes()==src.read_bytes()
  mid,_=p.render(raw);out,_=z.render(mid);out=t.render(out);assert p.latency()+z.latency()==0;outputs[name]=out.copy();p.close();z.close();t.close();p=z=t=None
 np.testing.assert_allclose(outputs['578'],outputs['578-cold2'],rtol=8*np.finfo(np.float32).eps,atol=1e-12);error=float(abs(outputs['578']-outputs['578-cold2']).max())
 for name in ['40','578']:sf.write(R/('ACTUAL_'+name+'_FULL_UNNORMALIZED.wav'),outputs[name],48000,subtype='FLOAT')
 os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment');from fl20_objective import a,FeaturesOriginal
 f=FeaturesOriginal();scores={}
 for name in ['40','578']:res=f.residual(outputs[name][:288000]);scores[name]=float(res@res)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
 ref,rate=sf.read(K/'Diva_original_lead_reference.wav',always_2d=True);assert rate==48000;assert hashlib.sha256((K/'Diva_original_lead_reference.wav').read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF)
 edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));clips=[ref,edit(outputs['40']),edit(outputs['578'])];rms=lambda y:float(np.sqrt(np.mean(y*y)));gains=[rms(ref)/rms(y)for y in clips];gap=np.zeros((24000,2));ab=np.concatenate([clips[0]*gains[0],gap,clips[1]*gains[1],gap,clips[2]*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
 sf.write(R/'AB_ORIGINAL_ZL40_578_WIP.flac',ab,48000,subtype='PCM_24');sf.write(R/'AB_TEMP.wav',ab,48000,subtype='FLOAT');q=__import__('subprocess');q.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(R/'AB_TEMP.wav'),'-codec:a','libmp3lame','-b:a','320k',str(R/'AB_ORIGINAL_ZL40_578_WIP.mp3')],check=True);(R/'AB_TEMP.wav').unlink();proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_Diva_MIDI3_ARP_ADSR_native12_POST_trim_unchanged=True,only_PRIMARY40_to578_changed=True,all12_native_resaves_exact=True,common_actual_native_input=True,two_cold578_replay_error=error,all_ZL_components_and_nativeTrim_resaved_exact=True,combined_ZL_PDC=0,original_is_only_target=True,order=['original','40','578'],starts_seconds=[0,4.168,8.336],only_AB_global_stereo_RMS_gains=gains,common_peak_safety_gain=safety,no_independent_channel_normalization=True,working_WAV_unnormalized=True,single_draw_objectives_not_new_acceptance=scores,accepted578_uses_own_fresh6_plus2cold_proof=True,reference_match_reached=False);(R/'ACTUAL_AB_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(V/'AB40_578_BUILD_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
 for host in[c,p,z,t]:
  if host is not None:host.close()
