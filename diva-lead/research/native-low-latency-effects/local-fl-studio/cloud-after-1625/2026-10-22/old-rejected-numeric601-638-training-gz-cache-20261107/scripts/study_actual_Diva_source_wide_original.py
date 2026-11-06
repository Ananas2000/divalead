"""Wider actual Diva PW/mix/cutoff/keyfollow/VCA-level/offset screen on base07."""
from pathlib import Path
import concurrent.futures,gzip,hashlib,json,tarfile,traceback
import numpy as np,soundfile as sf
import original_Diva_source_wide_library as q
R=q.ROOT
assert q.prior['accepted_full_public_kit']=='ZL28' and q.prior['full_public_kit_directory']=='ZL-WIP28'
assert q.prior['native_base_export_directory'].endswith('_07')
assert Path(q.prior['native_ZL_component_state']).read_bytes()==Path('/tmp/divalead-original-WS48-primary-joint-20261025-01/CANDIDATE_PRIMARY_RESEARCH_ONLY.bin').read_bytes()
cases=[('unchanged-control',{},set())]
for key,ident,start,deltas in [
 (('OSC','PW'),90,51.91,[-1.,-.6,-.3,-.15,.15,.3,.6,1.]),
 (('OSC','OscMix'),96,6.5,[-1.,-.5,.5,1.,2.]),
 (('VCF1','Freq'),148,144.16,[-2.,-1.,1.,2.]),
 (('VCF1','KeyScl'),154,8.38,[-5.,5.,10.]),
 (('VCA1','Vol'),168,49.,[-2.,-1.,1.,2.]),
 (('VCA1','Offset'),175,-.12,[-.02,.02,.12]),
 (('OSC','PWMDpt'),108,1.,[-1.,-.5,.5,1.])]:
 for delta in deltas:
  v=round(start+delta,2);cases.append((key[0]+'-'+key[1]+'-'+str(v),{key:v},{ident}))
try:
 q.record('actual_Diva_source_wide_screen_starting')
 for k in range(2):
  c=q.native(q.source['native_input'],'OriginalSourceWide-native-'+str(k));p=q.WinVST3('OriginalSourceWide-primary-'+str(k));z=q.WinVST3('OriginalSourceWide-post-'+str(k));q.clients.append((c,p,z));q.pool.put((c,p,z))
 control=q.evaluate(cases[0],12)
 with concurrent.futures.ThreadPoolExecutor(2)as ex:list(ex.map(lambda case:q.evaluate(case,4),cases[1:]))
 (R/'ALL_TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(q.rows).encode(),mtime=0));eligible=sorted([r for r in q.rows if r['label']!='unchanged-control'and r['all_stereo_preservation_passed']],key=lambda r:r['loss'])[:3];finalists=[]
 for row in eligible:finalists.append(q.evaluate(('fresh-'+row['label'],{},set()),12,existing=row))
 winner=min(finalists,key=lambda r:r['loss']);ready=bool(control['loss']-winner['loss']>.0003 and winner['all_stereo_preservation_passed'])
 summary=dict(training_cases=len(q.rows),control_mean=control['loss'],winner=winner,finalists=finalists,sufficient_screen=ready,robust_improvement=False,all_Diva281_and12MIDI_events_audited=True,only_seven_declared_tone_controls_varied=True,ARP_ADSR_MIDI_unchanged=True,nativebase07_and_both_ZLs_unchanged=True,original_is_the_only_target=True,not_adopted=True,reference_match_reached=False)
 (R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  raw,_=sf.read(winner['source_audio'],dtype='float32',always_2d=True);inp=R/'selected-source-with-tail.wav';sf.write(inp,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT');c0,p0,z0=q.clients[0];c1,p1,z1=q.clients[1];c0.load_input(q.source['native_input']);c1.load_input(inp);captures=[];members=[]
  with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(8):
    if rep in [6,7]:
     c0.close();c1.close();c0=q.native(q.source['native_input'],'OriginalSourceWide-cold-control-'+str(rep));c1=q.native(inp,'OriginalSourceWide-cold-candidate-'+str(rep));q.clients[0]=(c0,p0,z0);q.clients[1]=(c1,p1,z1)
    a0,_=c0.render();old=q.cascade(a0,p0,z0);d0=q.assess(old);a1,_=c1.render();new=q.cascade(a1,p1,z1);d1=q.assess(new);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
    for name,y in [('native-control',a0),('native-candidate',a1),('control',old),('candidate',new)]:q.add(tar,f'{name}-{rep}.wav',y,members)
    if rep==0:
     for name,y in [('NATIVE_CONTROL',a0),('NATIVE_CANDIDATE',a1),('CONTROL',old),('CANDIDATE',new)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
    q.record('source_wide_fresh_confirmation',completed_pairs=rep+1,latest_gain=captures[-1]['improvement'])
  cold,actual=q.actual_Diva(Path(winner['source_VST_chunk']),R/'selected-source-cold-chunk-replay');np.testing.assert_array_equal(cold,raw);assert actual==q.parameters(Path(winner['source_audio']).parent/'all281.tsv');assert(R/'selected-source-cold-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(winner['source_VST_chunk']).read_bytes();delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in members:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,actual_source_cold_chunk281_MIDI_audio_and_chunk_bytes_exact=True);(R/'SELECTED_SOURCE_RESEARCH_ONLY.json').write_text(json.dumps(winner,indent=2)+'\n')
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');q.record('finite_actual_source_wide_study_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','captures','archive_members','finalists']}),flush=True)
except BaseException:q.record('failed_preserve_supported_full27',error=traceback.format_exc());raise
finally:
 for c,p,z in q.clients:c.close();p.close();z.close()
