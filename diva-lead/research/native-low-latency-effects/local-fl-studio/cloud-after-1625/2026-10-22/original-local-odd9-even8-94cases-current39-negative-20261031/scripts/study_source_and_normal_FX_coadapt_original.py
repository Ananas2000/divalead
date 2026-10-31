"""Co-adapt actual Diva source and actual normal EQ/dynamics to the original.

Testing a changed source with frozen FX can miss an improvement; each actual
source here gets its own real primary-ZL87 refit, two heldouts and later fresh
native6/cold2. No old Finish, sampled reference in synthesis or fast MIDI notes.
"""
from pathlib import Path
import ast,concurrent.futures,datetime,gzip,hashlib,json,queue,struct,tarfile,threading,traceback,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
import original_Diva_coadapt_library as q
R=q.ROOT;N=q.N;STATE=N/'ORIGINAL_SOURCE_FX_COADAPT_STUDY.json';main=Path('/workspace/divalead-work/pc-stereo-20261024/continue_stereo_ZL_matching.py').read_text();tree=ast.parse(main);ns=dict(Path=Path,struct=struct,ET=ET,np=np,params=q.params if hasattr(q,'params')else{})
# Reuse the exact physical parameter bounds/proposal semantics of the current
# real-plugin primary matcher, without executing or changing that main job.
import csv
from win_vst3 import D,WinVST3
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')};ns['params']=params
for name in ['specs_from_component','configure']:
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);exec(compile(ast.get_source_segment(main,node),'<unchanged-main-'+name+'>','exec'),ns)
specs,dynamic=ns['specs_from_component'](R/'PRIMARY.bin');ns.update(specs=specs,dynamic=dynamic);initial=[p['value']for p in specs];configure=ns['configure']
clients=[];pool=queue.Queue();rows=[];mutex=threading.Lock();active_folder=None
def record(phase,**kw):
 s=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=q.os.getpid(),phase=phase,root=str(R),cases=len(rows),actual_ZL_hosts=[c.child.pid for p,z in clients for c in [p,z]],original_is_the_only_target=True,v83_Finish_not_used=True,source_and_normal_FX_coadapted=True,only_three_held_notes=True,ARP_ADSR_unchanged=True,not_adopted=True,reference_match_reached=False,**kw);p=STATE.with_suffix('.partial');p.write_text(json.dumps(s,indent=2)+'\n');p.replace(STATE)
def evaluate(case,phase=0,keep=True):
 label,x=case;p,z=pool.get()
 try:
  configure(p,x);z.load(R/'POST.bin');mid,_=p.render(input_file=active_folder/f'native-{phase}.f32');out,_=z.render(mid);row=dict(label=label,x=list(x),**q.assess(out));assert p.latency()+z.latency()==0
  if keep:
   with mutex:rows.append(row)
  return row
 finally:pool.put((p,z))
def source_case(label,values,allowed):
 folder=R/label;folder.mkdir();h2p=folder/'Diva.h2p';h2p.write_text(q.patched(values));raw,actual=q.actual_Diva(h2p,folder/'actual-Diva');changed={i for i in q.original if actual[i]['normalized']!=q.original[i]['normalized']};assert changed==allowed,(label,changed,allowed)
 if not allowed:np.testing.assert_array_equal(raw,q.baseline_raw)
 padded=folder/'source-with-tail.wav';sf.write(padded,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT');c=q.native(padded,'OriginalCoadapt-'+label)
 try:
  for phase in range(3):native,_=c.render();native.astype('<f4').tofile(folder/f'native-{phase}.f32');sf.write(folder/f'TRAINING_NATIVE_{phase}.wav',native,48000,subtype='FLOAT')
 finally:c.close()
 info=dict(label=label,folder=str(folder),source_preset=str(h2p),source_audio=str(folder/'actual-Diva/Diva_source.wav'),source_VST_chunk=str(folder/'actual-Diva/Diva_VST_chunk.bin'),native_input=str(padded),changed_parameters={actual[i]['name']:dict(before=q.original[i],after=actual[i])for i in changed},all281_and12_MIDI_events_exact=True,ARP_ADSR_unchanged=True)
 (folder/'ACTUAL_SOURCE_PROOF.json').write_text(json.dumps(info,indent=2)+'\n');return info
def eligible_min(checked,fallback):return min([fallback]+[r for r in checked if r['stereo_preservation_passed']],key=lambda r:r['loss'])
try:
 record('starting_source_and_normal_FX_coadaptation')
 for k in range(2):p=WinVST3('OriginalCoadapt-primary-'+str(k));z=WinVST3('OriginalCoadapt-post-'+str(k));clients.append((p,z));pool.put((p,z))
 control=source_case('unchanged-control',{},set());active_folder=Path(control['folder'])
 for p,z in clients:p.load(R/'PRIMARY.bin')
 control_rows=[evaluate(('original-source-control',initial),phase,False)for phase in range(3)];original_control_mean=float(np.mean([r['loss']for r in control_rows]));results=[]
 cases=[('quality-divine',{('OPT','Acc'):3},{18}),('quality-fast',{('OPT','Acc'):1},{18}),('shape-ideal',{('OSC','triSp'):0},{120}),('shape-analog2',{('OSC','triSp'):2},{120}),('voices-2',{('VCC','Voices'):0},{4}),('voices-4',{('VCC','Voices'):2},{4})]
 rng=np.random.default_rng(2026102543)
 with concurrent.futures.ThreadPoolExecutor(2)as executor:
  for label,values,allowed in cases:
   source=source_case(label,values,allowed);active_folder=Path(source['folder']);rows=[]
   for p,z in clients:p.load(R/'PRIMARY.bin')
   current=evaluate(('initial-'+label,initial));baseline=current;groups={}
   for j,p in enumerate(specs):
    key=''.join(c for c in p['title']if c.isdigit())
    if key:groups.setdefault(key,[]).append(j)
   groups=list(groups.values());coupled=[]
   for k in range(32):
    x=list(current['x'])
    for index in rng.choice(len(groups),size=1+k%3,replace=False):
     for j in groups[int(index)]:
      p=specs[j];delta=rng.normal()*p['step']*float(rng.choice([.7,1.4,2.8]));x[j]=float(np.clip(x[j]*2**delta if p['log']else x[j]+delta,p['lo'],p['hi']))
    coupled.append((f'coupled-{label}-{k}',x))
   current=eligible_min(list(executor.map(evaluate,coupled)),current)
   for coord in rng.permutation(len(specs)):
    p=specs[coord];proposals=[]
    for factor in [-2,-1,1,2]:
     x=list(current['x']);x[coord]=float(np.clip(x[coord]*2**(factor*p['step'])if p['log']else x[coord]+factor*p['step'],p['lo'],p['hi']));proposals.append((f'coordinate-{label}-{coord}-{factor}',x))
    selected=eligible_min(list(executor.map(evaluate,proposals)),current)
    if selected['loss']<current['loss']:current=selected
    record('actual_source_with_87_normal_ZL_parameter_refit',source=label,original_source_control=original_control_mean,source_initial_loss=baseline['loss'],source_current_loss=current['loss'],coordinate=int(coord))
   held=[]
   for phase in [1,2]:held.append(evaluate(('source-heldout-'+str(phase),current['x']),phase,False))
   p,z=clients[0];configure(p,current['x']);p.save(active_folder/'CANDIDATE_PRIMARY_RESEARCH_ONLY.bin');mid,_=p.render(input_file=active_folder/'native-0.f32');z.load(R/'POST.bin');out,_=z.render(mid);sf.write(active_folder/'SELECTED_TRAINING_FULL_WIP.wav',out,48000,subtype='FLOAT')
   result=dict(source=source,training_initial=baseline,training_selected=current,heldout=held,heldout_mean=float(np.mean([r['loss']for r in held])),original_source_control_mean=original_control_mean,training_cases=len(rows),post_unchanged=True,not_adopted=True);results.append(result);(active_folder/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(active_folder/'SCREEN_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(R/'COMPLETED_SOURCE_REFITS.json').write_text(json.dumps(results,indent=2)+'\n');record('source_refit_completed',source=label,heldout_mean=result['heldout_mean'],original_control=original_control_mean)
 eligible=[r for r in results if all(h['stereo_preservation_passed']for h in r['heldout'])];winner=min(eligible,key=lambda r:r['heldout_mean'])if eligible else None;ready=bool(winner and original_control_mean-winner['heldout_mean']>.0003)
 summary=dict(source_cases=len(results),training_cases=sum(r['training_cases']for r in results),original_control_mean=original_control_mean,winner=winner,sufficient_screen=ready,robust_improvement=False,original_is_the_only_target=True,only_three_held_notes=True,ARP_ADSR_unchanged=True,not_adopted=True,requires_latest_main_context_revalidation=True,reference_match_reached=False)
 (R/'FROZEN_BEFORE_FRESH_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n')
 if ready:
  record('fresh6_cold2_source_and_normal_FX_candidate_validation',selected=winner['source']['label']);source=winner['source'];c0=q.native(q.source['native_input'],'OriginalCoadapt-control-validation');c1=q.native(source['native_input'],'OriginalCoadapt-candidate-validation');p0,z0=clients[0];p1,z1=clients[1];captures=[];members=[]
  try:
   with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz','w:gz',compresslevel=3)as tar:
    for rep in range(8):
     if rep in [6,7]:c0.close();c1.close();c0=q.native(q.source['native_input'],'OriginalCoadapt-cold-control-'+str(rep));c1=q.native(source['native_input'],'OriginalCoadapt-cold-candidate-'+str(rep))
     raw0,_=c0.render();p0.load(R/'PRIMARY.bin');z0.load(R/'POST.bin');mid,_=p0.render(raw0);old,_=z0.render(mid);d0=q.assess(old);raw1,_=c1.render();p1.load(Path(source['folder'])/'CANDIDATE_PRIMARY_RESEARCH_ONLY.bin');z1.load(R/'POST.bin');mid,_=p1.render(raw1);out,_=z1.render(mid);d1=q.assess(out);captures.append(dict(rep=rep,control=d0,candidate=d1,improvement=d0['loss']-d1['loss']))
     for name,y in [('native-control',raw0),('native-candidate',raw1),('control',old),('candidate',out)]:q.add(tar,f'{name}-{rep}.wav',y,members)
     if rep==0:
      for name,y in [('NATIVE_CONTROL',raw0),('NATIVE_CANDIDATE',raw1),('CONTROL',old),('CANDIDATE',out)]:sf.write(R/(name+'_00.wav'),y,48000,subtype='FLOAT')
  finally:c0.close();c1.close()
  cold,actual=q.actual_Diva(Path(source['source_VST_chunk']),R/'selected-source-cold-chunk-replay');source_raw,_=sf.read(source['source_audio'],dtype='float32',always_2d=True);np.testing.assert_array_equal(cold,source_raw);assert actual==q.parameters(Path(source['source_audio']).parent/'all281.tsv');assert(R/'selected-source-cold-chunk-replay/Diva_VST_chunk.bin').read_bytes()==Path(source['source_VST_chunk']).read_bytes();delta=np.array([r['improvement']for r in captures]);sem=float(np.std(delta[:6],ddof=1)/np.sqrt(6));robust=bool(np.mean(delta[:6])>max(.0005,3*sem)and min(delta[6:])>0 and all(r['candidate']['stereo_preservation_passed']for r in captures))
  with tarfile.open(R/'EIGHT_FRESH_NATIVE_PROCESSED_CONTROL_CANDIDATE_WAVs.tar.gz')as tar:
   for item in members:assert hashlib.sha256(tar.extractfile(item['name']).read()).hexdigest()==item['SHA256']
  summary.update(captures=captures,archive_members=members,first6_mean_improvement=float(np.mean(delta[:6])),first6_SEM=sem,required_improvement=max(.0005,3*sem),cold2_improvements=delta[6:].tolist(),robust_improvement=robust,actual_source_cold_chunk281_events_audio_bytes_exact=True)
 (R/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');record('finite_source_FX_coadaptation_complete_not_adopted',robust_improvement=summary['robust_improvement'],sufficient_screen=ready);print(json.dumps({k:v for k,v in summary.items()if k not in ['winner','captures','archive_members']}),flush=True)
except BaseException:record('failed_preserve_main_and_all_accepted_kits',error=traceback.format_exc());raise
finally:
 for p,z in clients:p.close();z.close()
