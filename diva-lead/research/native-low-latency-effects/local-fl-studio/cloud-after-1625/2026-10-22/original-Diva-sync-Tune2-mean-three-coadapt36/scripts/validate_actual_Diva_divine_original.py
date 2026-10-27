"""Predeclared great→divine source-quality check; fixed CURRENT normal FX."""
from pathlib import Path
import hashlib,json,tarfile,traceback
import numpy as np,soundfile as sf
import original_Diva_divine_validation_library as q
R=q.ROOT;clients=[]
try:
 q.record('actual_fresh_great_and_divine_sources')
 control,base_params=q.actual_Diva(Path(q.source['source_preset']),R/'actual-control-Diva');np.testing.assert_array_equal(control,q.baseline_raw);assert base_params==q.original
 h2p=R/'Diva_divine.h2p';h2p.write_text(q.patched({('OPT','Acc'):3}));candidate,actual=q.actual_Diva(h2p,R/'actual-divine-Diva');changed={i for i in q.original if actual[i]['normalized']!=q.original[i]['normalized']};assert changed=={18};input_path=R/'divine-source-with-tail.wav';sf.write(input_path,np.pad(candidate,((0,32768),(0,0))),48000,subtype='FLOAT')
 c0=q.native(q.source['native_input'],'OriginalDivine-control');c1=q.native(input_path,'OriginalDivine-candidate');clients=[c0,c1];p0=q.WinVST3('OriginalDivine-primary-control');z0=q.WinVST3('OriginalDivine-post-control');p1=q.WinVST3('OriginalDivine-primary-candidate');z1=q.WinVST3('OriginalDivine-post-candidate');vsts=[p0,z0,p1,z1];captures=[];members=[]
 q.record('fresh_six_plus_two_cold_native_validation_quality_only')
 with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
  for rep in range(8):
   if rep in [6,7]:c0.close();c1.close();c0=q.native(q.source['native_input'],'OriginalDivine-cold-control-'+str(rep));c1=q.native(input_path,'OriginalDivine-cold-candidate-'+str(rep));clients=[c0,c1]
   raw0,_=c0.render();old=q.cascade(raw0,p0,z0);d0=q.assess(old);raw1,_=c1.render();out=q.cascade(raw1,p1,z1);d1=q.assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
   for label,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:q.add(tar,f'{label}-{rep}.wav',y,members)
   if rep==0:
    for label,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(label+'_00.wav'),y,48000,subtype='FLOAT')
 delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures));cold,again=q.actual_Diva(R/'actual-divine-Diva/Diva_VST_chunk.bin',R/'cold-divine-chunk-replay');np.testing.assert_array_equal(cold,candidate);assert again==actual;assert(R/'actual-divine-Diva/Diva_VST_chunk.bin').read_bytes()==(R/'cold-divine-chunk-replay/Diva_VST_chunk.bin').read_bytes()
 with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
  for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 s=dict(only_source_Accuracy_great_to_divine_changed=True,changed_parameters={q.original[i]['name']:dict(before=q.original[i],after=actual[i])for i in changed},all281_and_all12_events_audited=True,cold_Diva_chunk_all281_audio_and_chunk_bytes_exact=True,native_and_current_two_ZL_unchanged=True,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,captures=captures,archive_members=members,source_preset=str(h2p),source_audio=str(R/'actual-divine-Diva/Diva_source.wav'),source_VST_chunk=str(R/'actual-divine-Diva/Diva_VST_chunk.bin'),native_input=str(input_path),original_is_the_only_target=True,v83_Finish_not_used=True,only_three_held_notes=True,ARP_ADSR_unchanged=True,not_adopted=True,requires_latest_main_context_revalidation=True,reference_match_reached=False)
 (R/'completion.json').write_text(json.dumps(s,indent=2)+'\n');q.record('divine_quality_validation_complete_not_adopted',robust_improvement=robust,mean_gain=s['first6_mean_improvement'],cold2=s['cold2_improvements']);print(json.dumps({k:v for k,v in s.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:q.record('failed_preserve_current_source_and_accepted_kit',error=traceback.format_exc());raise
finally:
 for c in clients:c.close()
 for c in locals().get('vsts',[]):c.close()
