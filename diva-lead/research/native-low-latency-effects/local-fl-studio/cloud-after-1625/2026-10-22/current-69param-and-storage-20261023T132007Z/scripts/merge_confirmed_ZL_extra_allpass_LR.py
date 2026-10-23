"""Revalidate the phase addition against the latest incumbent, then resume."""
from pathlib import Path
import csv,datetime,hashlib,io,json,os,struct,subprocess,tarfile,traceback,xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from win_vst3 import D,WinVST3
from native_chain import NativeChain
from fl20_curve import apply_candidate
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-confirmed-extra-allpass-LR-merge-01';ROOT.mkdir(exist_ok=False)
OWNER='ZL-extra-allpass-LR-confirmed-handoff-20261023';PAUSE=N/'fl20-corrected-search.pause';STOP=N/'zl-continuation.stop';MAIN=D/'ZL-continuous65'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();clients=[];native=None
params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def read(p):return json.loads(Path(p).read_text())
def live(pid):
 p=Path('/proc')/str(pid)
 try:return (p/'stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
prior=read(MAIN/'BEST_CANDIDATE.json');seed=prior['native_base'];main_status=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')
assert main_status['phase']=='stopped_by_explicit_stop_file_after_completed_cohort'and not live(main_status['owner']['PID'])
assert read(STOP)['owner']==OWNER
with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,purpose='independent real-plugin revalidation of extra allpass against latest incumbent and restart'),f)
def score(y):
 a=features.residual(y[:288000]);return float(a@a)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025
try:
 (ROOT/'PRIOR_BEST_CANDIDATE.json').write_text(json.dumps(prior,indent=2)+'\n');control_state=ROOT/'CONTROL_COMPONENT.bin';control_state.write_bytes(Path(prior['native_ZL_component_state']).read_bytes())
 study=read(D/'ZL-extra-allpass-LR-after-ZL06-01/completion.json');assert study['robust_improvement'];bands=study['selected_extra_allpass_bands']
 control=WinVST3('ZL-extra-allpass-LR-merge-control');candidate=WinVST3('ZL-extra-allpass-LR-merge-candidate');clients.extend([control,candidate])
 for c in clients:c.load(control_state)
 for k,b in enumerate(bands,19):
  candidate.set(params['Filter Status'+str(k)],1);candidate.set(params['Filter Type'+str(k)],.9);candidate.set(params['Order'+str(k)],1/6)
  candidate.set(params['LRMode'+str(k)],b['mode']/4);candidate.set(params['Dynamic ON'+str(k)],0)
  candidate.text(params['Freq'+str(k)],str(b['frequency']));candidate.text(params['Q'+str(k)],str(b['Q']))
 component=ROOT/'CANDIDATE_COMPONENT.bin';candidate.save(component);candidate.dump(ROOT/'ACTUAL_610_PARAMETERS.tsv')
 cold1=WinVST3('ZL-extra-allpass-LR-merge-cold1');cold2=WinVST3('ZL-extra-allpass-LR-merge-cold2');clients.extend([cold1,cold2])
 for c in [cold1,cold2]:c.load(component)
 input_file=D/'ZL-allpass-original-reference-01/frozen-native-0.f32';a,_=cold1.render(input_file=input_file);b,_=cold2.render(input_file=input_file);cold_error=float(abs(a-b).max());np.testing.assert_allclose(a,b,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
 cold1.save(ROOT/'COMPONENT_RESAVED.bin');assert component.read_bytes()==(ROOT/'COMPONENT_RESAVED.bin').read_bytes()
 cold1.close();cold2.close();clients.remove(cold1);clients.remove(cold2)
 native=NativeChain(seed['source_manifest']['native_input'],'ZL-extra-allpass-LR-confirmed-merge-native',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(native,np.array(seed['x']),seed)
 for k,v in seed['chorus_overrides'].items():native.set(3,int(k),int(v))
 rows=[];audio=[]
 for k in range(6):
  raw,_=native.render();old,_=control.render(raw);old_loss=score(old);out,_=candidate.render(raw);loss=score(out);rows.append(dict(rep=k,base_loss=old_loss,loss=loss,assessment=features.local.last));audio.append((old,out))
 native.close();native=None
 delta=np.array([r['base_loss']-r['loss']for r in rows]);sem=float(np.std(delta,ddof=1)/np.sqrt(6));robust=bool(np.mean(delta)>max(.0005,3*sem))
 impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];response,_=candidate.render(impulse);first=int(np.flatnonzero(np.max(abs(response),axis=1)>1e-9)[0])-4096;assert first==0 and candidate.latency()==0
 summary=dict(cohort='extra-allpass-merge-after-'+Path(prior['native_ZL_component_state']).parent.name,robust_improvement=robust,current_control_mean=float(np.mean([r['base_loss']for r in rows])),candidate_mean=float(np.mean([r['loss']for r in rows])),paired_difference_SEM=sem,captures=rows,cold_instance_replay_max_abs_error=cold_error,cold_instance_replay_bit_exact=bool(cold_error==0),actual_component_state_roundtrip_exact=True,extra_allpass_bands=bands,declared_PDC_frames=0,impulse_first_response_frames=first,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
 if robust:
  archive=ROOT/'PAIRED6_CONTROL_CANDIDATE_WAVs.tar.gz';members=[]
  with tarfile.open(archive,'w:gz',compresslevel=3)as z:
   for k,pair in enumerate(audio):
    for label,y in zip(['control','candidate'],pair):
     buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');b=buf.getvalue();name=f'{label}-{k}.wav';info=tarfile.TarInfo(name);info.size=len(b);z.addfile(info,io.BytesIO(b));members.append(dict(name=name,SHA256=hashlib.sha256(b).hexdigest()))
  with tarfile.open(archive)as z:
   for m in members:assert hashlib.sha256(z.extractfile(m['name']).read()).hexdigest()==m['SHA256']
  median=sorted(range(6),key=lambda k:rows[k]['loss'])[3];selected=ROOT/'SELECTED_CANDIDATE_WIP.wav';sf.write(selected,audio[median][1],48000,subtype='FLOAT')
  summary.update(lossless_capture_archive=str(archive),archive_members=members)
  choice=dict(prior,loss=summary['candidate_mean'],native_ZL_component_state=str(component),recorded_audio=str(selected),actual_component_state_roundtrip_exact=True,component_replay_max_abs_error=cold_error,additional_allpass_filter_indices=list(range(19,19+len(bands))),not_automatically_adopted_into_public_FL_project=True,not_compatible_with_standard_x95_exporter=True,extended_parameter_values_are_authoritative_in_component_state=True)
  (ROOT/'CANDIDATE_ACCEPTED_RESEARCH_ONLY.json').write_text(json.dumps(choice,indent=2)+'\n');tmp=MAIN/'BEST_CANDIDATE.partial';tmp.write_text(json.dumps(choice,indent=2)+'\n');tmp.replace(MAIN/'BEST_CANDIDATE.json')
 (ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('LATEST_INCUMBENT_EXTRA_ALLPASS_REVALIDATION',json.dumps({k:v for k,v in summary.items()if k not in ['captures','archive_members']}),flush=True)
except BaseException:
 (ROOT/'FAILURE_PRESERVE_CURRENT_BEST.json').write_text(json.dumps(dict(error=traceback.format_exc(),reference_match_reached=False),indent=2)+'\n');raise
finally:
 if native:native.close()
 for c in clients:c.close()
 if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
 # Resume from whichever best survived; remove only this handoff's stop.
 if STOP.exists()and read(STOP).get('owner')==OWNER:STOP.unlink()
 env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:/tmp/divalead-local-1625',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
 with(N/'ZL_CONTINUED_AFTER_EXTRA_ALLPASS_LR_MERGE.log').open('ab')as f:c=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(D/'continue_ZL_matching.py')],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 (N/'ZL_POST_EXTRA_ALLPASS_LR_MERGE_RESTART.json').write_text(json.dumps(dict(PID=c.pid,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=str(D/'continue_ZL_matching.py'),best_mean=read(MAIN/'BEST_CANDIDATE.json')['loss'],only_three_held_notes=True,reference_match_reached=False),indent=2)+'\n');print('ACTUAL_ZL_MATCHER_RESTARTED',c.pid,flush=True)
