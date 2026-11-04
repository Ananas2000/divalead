"""Informed joint source proposals from ACTUAL harmonic finite differences.

Seven ordinary Diva tone controls, exact three incoming held notes/ARP/ADSR.
Linear proposals are hypotheses only; every candidate is rendered by actual
Diva and current real native+two-ZL, accepted by unchanged original criterion.
"""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,json,shutil,tarfile,traceback
import numpy as np,soundfile as sf
from scipy.optimize import lsq_linear
from scipy.stats import qmc
import original_Diva_joint7_library as q
R=q.ROOT
names=[('OSC','OscMix'),('OSC','PW'),('OSC','PWMDpt'),('VCF1','Freq'),('VCF1','Res'),('OSC','Tune1'),('OSC','Tune2')];ids=[96,90,108,148,149,86,87]
start=np.array([6.5,51.91,1.,144.16,12.13,-.06,24.02]);step=np.array([.25,.05,.25,.4,.75,.02,.02]);low=start-2*step;high=start+2*step
def quant(v):return np.round(np.clip(v,low,high),2)
def run_case(label,v,reps=4):
 v=quant(v);values={names[j]:float(v[j])for j in range(7)if v[j]!=start[j]};allowed={ids[j]for j in range(7)if v[j]!=start[j]};row=q.evaluate((label,values,allowed),reps);row['source_parameter_vector']=v.tolist();return row
try:
 q.record('starting_actual_joint_Diva_harmonic_derivative_proposals')
 for k in range(2):
  c=q.native(q.source['native_input'],'OriginalJoint7-native-'+str(k));p=q.WinVST3('OriginalJoint7-primary-'+str(k));z=q.WinVST3('OriginalJoint7-post-'+str(k));q.clients.append((c,p,z));q.pool.put((c,p,z))
 control=run_case('unchanged-control',start,12);cases=[]
 for j in range(7):
  for sign in [-1,1]:v=start.copy();v[j]+=sign*step[j];cases.append((f'derivative-{j}-{sign}',v))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  derivatives=list(executor.map(lambda case:run_case(*case),cases))
 by_label={r['label']:r for r in derivatives};J=np.column_stack([(np.array(by_label[f'derivative-{j}-1']['harmonic_residual_vector'])-np.array(by_label[f'derivative-{j}--1']['harmonic_residual_vector']))/2 for j in range(7)]);residual=np.array(control['harmonic_residual_vector']);u=lsq_linear(J,-residual,bounds=(-1.8,1.8),tol=1e-10).x
 # A second proposal focuses on the harmonic orders diagnosed as mismatched.
 selected=np.tile(np.isin(np.arange(1,25),[6,11,13]),16);u_focus=lsq_linear(J[selected],-residual[selected],bounds=(-1.8,1.8),tol=1e-10).x
 (R/'ACTUAL_FINITE_DIFFERENCE_PROPOSALS.json').write_text(json.dumps(dict(source_control_names=[m+':'+n for m,n in names],start=start.tolist(),step=step.tolist(),all_harmonic_direction=u.tolist(),selected_harmonics_direction=u_focus.tolist(),actual_DSP_used_for_every_derivative=True,proposals_not_accepted_by_prediction=True,original_is_the_only_target=True),indent=2)+'\n')
 candidates=[];seen={tuple(start)}|{tuple(r['source_parameter_vector'])for r in derivatives}
 for mode,direction in [('all',u),('focused',u_focus)]:
  for fraction in [.25,.5,.75,1.]:
   v=quant(start+step*direction*fraction)
   if tuple(v)not in seen:candidates.append((f'joint-{mode}-{fraction}',v));seen.add(tuple(v))
 center=quant(start+step*u*.75)
 for k,unit in enumerate(qmc.LatinHypercube(7,seed=2026102542).random(12)):
  v=quant(center+(unit*2-1)*step*.65)
  if tuple(v)not in seen:candidates.append((f'joint-local-{k}',v));seen.add(tuple(v))
 q.record('actual_Diva_joint_proposals_rendering',proposed=len(candidates))
 with concurrent.futures.ThreadPoolExecutor(2)as executor:list(executor.map(lambda case:run_case(*case),candidates))
 (R/'ALL_TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(q.rows).encode(),mtime=0));eligible=sorted([r for r in q.rows if r['all_stereo_preservation_passed']],key=lambda r:r['loss'])[:4];finalists=[]
 for row in eligible:
  fresh=q.evaluate(('fresh-finalist-'+row['label'],{},set()),12,existing=row);fresh['source_parameter_vector']=row['source_parameter_vector'];finalists.append(fresh)
 winner=min(finalists,key=lambda r:r['loss']);ready=bool(winner['source_parameter_vector']!=start.tolist()and control['loss']-winner['loss']>.0003 and winner['all_stereo_preservation_passed'])
 (R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(dict(winner=winner,control_mean=control['loss'],sufficient_screen=ready,original_is_the_only_target=True),indent=2)+'\n');summary=dict(training_cases=len(q.rows),control_mean=control['loss'],winner=winner,sufficient_screen=ready,robust_improvement=False,all_Diva281_and12MIDI_events_audited=True,only_seven_tone_controls_varied=True,ARP_ADSR_unchanged=True,original_is_the_only_target=True,v83_Finish_not_used=True,only_three_held_notes=True,requires_latest_main_revalidation=True,not_adopted=True,reference_match_reached=False)
 if ready:
  q.record('fresh_six_plus_two_cold_joint_Diva_source_pairs',winner=winner['source_parameter_vector']);candidate_raw,_=sf.read(winner['source_audio'],dtype='float32',always_2d=True);candidate_input=R/'selected-source-with-tail.wav';sf.write(candidate_input,np.pad(candidate_raw,((0,32768),(0,0))),48000,subtype='FLOAT');c0,p0,z0=q.clients[0];c1,p1,z1=q.clients[1];c0.load_input(q.source['native_input']);c1.load_input(candidate_input);captures=[];members=[]
  with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
   for rep in range(8):
    if rep in [6,7]:
     c0.close();c1.close();c0=q.native(q.source['native_input'],'OriginalJoint7-cold-control-'+str(rep));c1=q.native(candidate_input,'OriginalJoint7-cold-candidate-'+str(rep));q.clients[0]=(c0,p0,z0);q.clients[1]=(c1,p1,z1)
    raw0,_=c0.render();old=q.cascade(raw0,p0,z0);d0=q.assess(old);raw1,_=c1.render();out=q.cascade(raw1,p1,z1);d1=q.assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
    for label,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:q.add(tar,f'{label}-{rep}.wav',y,members)
    if rep==0:
     for label,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(label+'_00.wav'),y,48000,subtype='FLOAT')
  cold,actual=q.actual_Diva(Path(winner['source_VST_chunk']),R/'selected-source-cold-chunk-replay');np.testing.assert_array_equal(cold,candidate_raw);assert actual==q.parameters(Path(winner['source_audio']).parent/'all281.tsv');assert(R/'selected-source-cold-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(winner['source_VST_chunk']).read_bytes();delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in members:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,actual_source_cold_chunk281_MIDI_audio_and_chunk_bytes_exact=True);(R/'SELECTED_SOURCE_RESEARCH_ONLY.json').write_text(json.dumps(winner,indent=2)+'\n')
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');q.record('finite_joint_Diva_screen_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','captures','archive_members']}),flush=True)
except BaseException:q.record('failed_preserve_current_main_and_all_accepted_kits',error=traceback.format_exc());raise
finally:
 for c,p,z in q.clients:c.close();p.close();z.close()
