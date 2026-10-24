"""Fit original primary AllPass parameters with the measured stereo repair fixed."""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,json,os,queue,struct,threading,xml.etree.ElementTree as E
import numpy as np,soundfile as sf
from win_vst3 import D,WinVST3
A=Path(__file__).resolve().parent;ROOT=A/'primary-phase-stereo-fit01';ROOT.mkdir(exist_ok=False)
C=A/'local-fl-matching/sessions/2026-10-24';BASE=C/'ZL23_CONFIRMED_INPUT.bin';POST=A/'post-stereo-study01/CANDIDATE_COMPONENT.bin'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal();params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def values(path):
 b=Path(path).read_bytes();r=E.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]])
 return {x.attrib['id']:float(x.attrib['value'])for x in r.find('Para')}
v=values(BASE);specs=[]
for k in [12,13,18,19]:
 for title,key,step,lo,hi in [('Freq','freq',.09,40,18000),('Q','q',.15,.15,25)]:specs.append(dict(title=title+str(k),value=v[key+str(k)],step=step,lo=lo,hi=hi))
initial=[s['value']for s in specs]
for i in [0,1]:
 y,sr=sf.read(C/f'FL26_PRE_ZL_0{i}.wav',dtype='float32',always_2d=True);assert sr==48000;y.astype('<f4').tofile(ROOT/f'input-{i}.f32')
ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);freq=np.fft.rfftfreq(len(ref),1/48000);masks=[(freq>=lo)&(freq<hi)for lo,hi in [(2000,5000),(5000,10000),(10000,14000)]]
def lr(y):
 p=abs(np.fft.rfft(y,axis=0))**2
 return np.array([10*np.log10(p[m,0].sum()/p[m,1].sum())for m in masks])
target=lr(ref);pool=queue.Queue();clients=[];rows=[];lock=threading.Lock()
def state(phase,**extra):
 (ROOT/'STATE.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_hosts=[dict(primary=p.child.pid,post=z.child.pid)for p,z in clients],only_three_held_notes=True,source_native_unchanged=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra),indent=2)+'\n')
def configure(p,z,x):
 p.load(BASE);z.load(POST)
 for spec,value in zip(specs,x):p.text(params[spec['title']],str(value))
def evaluate(case,i=0,keep=True):
 label,x=case;p,z=pool.get()
 try:
  configure(p,z,x);raw,status=p.render(input_file=ROOT/f'input-{i}.f32');out,zstatus=z.render(raw);r=features.residual(out);edit=a.h.edit_aligned(a.h.align_with_pdc(out,dict(alignment_frames=819),latency=0));bands=lr(edit);err=float(np.sqrt(np.mean((bands-target)**2)))
  row=dict(label=label,x=x,loss=float(r@r),assessment=features.local.last,stereo_high_band_error=err,high_LR_dB=bands.tolist(),primary_status=status,post_status=zstatus)
  assert p.latency()==z.latency()==0
  if keep:
   with lock:rows.append(row)
  return row
 finally:pool.put((p,z))
def rank(row):return(row['stereo_high_band_error']>1.5,row['loss'])
try:
 for k in range(4):p=WinVST3(f'PC-primary-refit-{k}');z=WinVST3(f'PC-primary-refit-post-{k}');clients.append((p,z));pool.put((p,z))
 baseline=evaluate(('unchanged-primary-with-fixed-stereo-repair',initial));current=baseline;rng=np.random.default_rng(2026102462)
 state('actual_primary_phase_refit',baseline_loss=baseline['loss'])
 with concurrent.futures.ThreadPoolExecutor(4)as executor:
  for sweep in range(4):
   cases=[]
   for trial in range(24):
    x=list(current['x'])
    for j in rng.choice(len(specs),size=int(rng.choice([2,4,6])),replace=False):
     spec=specs[j];x[j]=float(np.clip(x[j]*2**(rng.normal()*spec['step']*(.7**sweep)),spec['lo'],spec['hi']))
    cases.append((f'coupled-{sweep}-{trial}',x))
   selected=min(executor.map(evaluate,cases),key=rank)
   if rank(selected)<rank(current):current=selected
   for j in rng.permutation(len(specs)):
    cases=[];spec=specs[j]
    for factor in [-2,-1,1,2]:
     x=list(current['x']);x[j]=float(np.clip(x[j]*2**(factor*spec['step']*(.65**sweep)),spec['lo'],spec['hi']));cases.append((f'axis-{sweep}-{j}-{factor}',x))
    selected=min(executor.map(evaluate,cases),key=rank)
    if rank(selected)<rank(current):current=selected
    state('actual_primary_phase_coordinate_sweep',sweep=sweep,best_loss=current['loss'],stereo_high_band_error=current['stereo_high_band_error'])
 held=evaluate(('existing-GUI-prefix01-frozen-candidate',current['x']),1,False)
 p,z=clients[0];configure(p,z,current['x']);p.save(ROOT/'PRIMARY_CANDIDATE_COMPONENT.bin');z.save(ROOT/'POST_CANDIDATE_COMPONENT.bin');assert (ROOT/'POST_CANDIDATE_COMPONENT.bin').read_bytes()==POST.read_bytes()
 raw,_=p.render(input_file=ROOT/'input-0.f32');out,_=z.render(raw);sf.write(ROOT/'CANDIDATE_GUI_PREFIX00.wav',out,48000,subtype='FLOAT')
 changed={k:[v[k],value]for k,value in values(ROOT/'PRIMARY_CANDIDATE_COMPONENT.bin').items()if v[k]!=value}
 assert all(k in [f'{key}{i}'for i in [12,13,18,19]for key in ['freq','q']]for k in changed),changed
 summary=dict(training_cases=len(rows),original_confirmed_loss=1.324779989389374,fixed_stereo_repair_loss=baseline['loss'],training_candidate=current,existing_GUI_prefix01_candidate=held,primary_changed_XML=changed,post_component_SHA256=hashlib.sha256(POST.read_bytes()).hexdigest(),new_candidate_frozen_before_archival_cohort_evaluation=True,source_native_281_MIDI_unchanged=True,only_three_held_notes=True,not_adopted=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');state('primary_phase_fit_completed_not_adopted',training_loss=current['loss'],stereo_high_band_error=current['stereo_high_band_error']);print(json.dumps(dict(training_cases=len(rows),training_loss=current['loss'],heldout_loss=held['loss'],stereo_error=current['stereo_high_band_error'],changed=changed)),flush=True)
finally:
 for p,z in clients:p.close();z.close()
