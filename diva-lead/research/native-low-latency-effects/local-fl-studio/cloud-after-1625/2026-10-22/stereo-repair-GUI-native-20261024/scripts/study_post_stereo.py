"""Actual ZL study of frequency-dependent stereo imbalance on real GUI inputs.

Original reference is analysis only. Existing GUI captures are a screen, not
new GUI exports. Source/native/MIDI never change. No automatic adoption.
"""
from pathlib import Path
import concurrent.futures,csv,datetime,gzip,hashlib,json,os,queue,struct,threading,xml.etree.ElementTree as ET
import numpy as np
import soundfile as sf
from win_vst3 import WinVST3,D
A=Path(__file__).resolve().parent;ROOT=A/'post-stereo-study01';ROOT.mkdir(exist_ok=False)
C=A/'local-fl-matching/sessions/2026-10-24'
BASE=D/'ZL-default-component.bin'
PRIMARY=C/'ZL23_CONFIRMED_INPUT.bin'
assert hashlib.sha256(PRIMARY.read_bytes()).hexdigest()=='37130685093f401343d9599d86f7426d224187a4c9d0abf1dbae2a8aafad4dce'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
def values(path):
 b=Path(path).read_bytes();r=ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]])
 return {x.attrib['id']:float(x.attrib['value'])for x in r.find('Para')}
original=values(BASE);assert all(original['filter_status'+str(k)]==0 for k in range(24))
primary=WinVST3('PC-post-stereo-original-primary')
try:
 for i in [0,1]:
  primary.load(PRIMARY);y,sr=sf.read(C/f'FL26_PRE_ZL_0{i}.wav',dtype='float32',always_2d=True);assert sr==48000
  out,status=primary.render(y);out.astype('<f4').tofile(ROOT/f'input-{i}.f32');sf.write(ROOT/f'UNCHANGED_CONFIRMED_FULL_{i}.wav',out,48000,subtype='FLOAT')
finally:primary.close()
ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True)
from fl20_objective import a
frequencies=np.fft.rfftfreq(len(ref),1/48000)
band_masks=[(frequencies>=lo)&(frequencies<hi)for lo,hi in [(2000,5000),(5000,10000),(10000,14000)]]
def balance(y):
 edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));power=abs(np.fft.rfft(edit,axis=0))**2
 return np.array([10*np.log10(power[m,0].sum()/power[m,1].sum())for m in band_masks])
ref_power=abs(np.fft.rfft(ref,axis=0))**2
reference_balance=np.array([10*np.log10(ref_power[m,0].sum()/ref_power[m,1].sum())for m in band_masks])

pool=queue.Queue();clients=[];rows=[];lock=threading.Lock()
def state(phase,**extra):
 r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,cases=len(rows),actual_VST3_hosts=[c.child.pid for c in clients],source_and_native_unchanged=True,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra)
 (ROOT/'STATE.json').write_text(json.dumps(r,indent=2)+'\n')
def configure(c,bands):
 c.load(BASE)
 for k,b in zip([0,1],bands):
  c.set(params['Filter Status'+str(k)],1);c.set(params['Filter Type'+str(k)],b['type']/10)
  c.set(params['LRMode'+str(k)],b['mode']/4);c.set(params['Order'+str(k)],1/6);c.set(params['Dynamic ON'+str(k)],0)
  for title,key in [('Freq','frequency'),('Q','Q'),('Gain','gain')]:c.text(params[title+str(k)],str(b[key]))
def evaluate(case,input_number=0,save=True):
 label,bands=case;c=pool.get()
 try:
  configure(c,bands);out,status=c.render(input_file=ROOT/f'input-{input_number}.f32');r=features.residual(out);loss=float(r@r)
  assert c.latency()==0
  balance_db=balance(out);row=dict(label=label,bands=bands,loss=loss,assessment=features.local.last,VST3_status=status,high_LR_dB=balance_db.tolist(),stereo_high_band_error=float(np.sqrt(np.mean((balance_db-reference_balance)**2))))
  if save:
   with lock:rows.append(row)
  return row
 finally:pool.put(c)
try:
 for k in range(4):c=WinVST3(f'PC-post-stereo-{k}');clients.append(c);pool.put(c)
 baseline=evaluate(('confirmed-control',[]));state('actual_phase_stereo_screen',control_loss=baseline['loss'])
 cases=[]
 for lo in [3000,4500,6000,8000]:
  for ratio in [1.1,1.4,2]:
   for q in [.5,1.2,2.4]:
    for modes in [(3,4),(4,3)]:
     cases.append((f'phase-pair-{lo}-{ratio}-{q}-{modes}',[dict(type=9,mode=modes[0],frequency=lo,Q=q,gain=0),dict(type=9,mode=modes[1],frequency=min(20000,lo*ratio),Q=q,gain=0)]))
 with concurrent.futures.ThreadPoolExecutor(4)as executor:
  for n,row in enumerate(executor.map(evaluate,cases)):
   if n%16==0:state('actual_single_mid_side_allpass_screen',best_loss=min(r['loss']for r in rows),control_loss=baseline['loss'])
  best=min(rows,key=lambda r:r['loss']);rng=np.random.default_rng(2026102451)
  # Also test channel-specific equalization: previous static-slot experiments
  # used Stereo/Mid/Side, never the user's newly requested Left/Right repair.
  cases=[]
  for typ,frequency in [(0,450),(0,700),(3,3000),(3,5000),(3,7000)]:
   for mode,gains in [(1,[-1,-2,-4]),(2,[1,2,4])]:
    for gain in gains:cases.append((f'LR-EQ-{typ}-{mode}-{frequency}-{gain}',[dict(type=typ,mode=mode,frequency=frequency,Q=.7,gain=gain)]))
  list(executor.map(evaluate,cases));best=min(rows,key=lambda r:r['loss']);state('actual_two_filter_stereo_fit',best_loss=best['loss'],control_loss=baseline['loss'])
  cases=[]
  for frequency in [2500,5000,7500]:
   for delta in [.5,1,2,3,4,5]:
    cases.append((f'complementary-LR-shelf-{frequency}-{delta}',[dict(type=3,mode=1,frequency=frequency,Q=.707,gain=-delta/2),dict(type=3,mode=2,frequency=frequency,Q=.707,gain=delta/2)]))
  list(executor.map(evaluate,cases))
  def rank(row):
   # Requested stereo repair is reported separately from unchanged original
   # objective. A worse original score is never called an accepted improvement.
   return (row['loss']>baseline['loss']+.01,row['stereo_high_band_error'],row['loss'])
  current=min(rows,key=rank)
  for sweep in range(2):
   for index in range(len(current['bands'])):
    for key,step,log in [('frequency',.2,True),('Q',.25,True),('gain',.4,False)]:
     if key=='gain'and current['bands'][index]['type']==9:continue
     cases=[]
     for factor in [-2,-1,1,2]:
      bands=[dict(b)for b in current['bands']];v=bands[index][key];v=v*2**(factor*step/(sweep+1))if log else v+factor*step/(sweep+1)
      bounds={'frequency':(80,20000),'Q':(.15,12),'gain':(-8,8)};bands[index][key]=float(np.clip(v,*bounds[key]));cases.append((f'fine-{sweep}-{index}-{key}-{factor}',bands))
     selected=min(executor.map(evaluate,cases),key=rank)
     if rank(selected)<rank(current):current=selected
     state('actual_stereo_filter_coordinate_refinement',best_loss=current['loss'],control_loss=baseline['loss'],selected_bands=current['bands'])
 held_control=evaluate(('heldout-confirmed',[]),1,False);held_candidate=evaluate(('heldout-frozen-candidate',current['bands']),1,False)
 control,candidate=clients[:2];configure(control,[]);configure(candidate,current['bands'])
 audio0,_=control.render(input_file=ROOT/'input-0.f32');audio1,_=candidate.render(input_file=ROOT/'input-0.f32')
 sf.write(ROOT/'CONTROL_GUI_PREFIX_00.wav',audio0,48000,subtype='FLOAT');sf.write(ROOT/'CANDIDATE_GUI_PREFIX_00.wav',audio1,48000,subtype='FLOAT')
 candidate.save(ROOT/'CANDIDATE_COMPONENT.bin');candidate.dump(ROOT/'ACTUAL_610_PARAMETERS.tsv')
 check=values(ROOT/'CANDIDATE_COMPONENT.bin');changed={key:[value,check[key]]for key,value in original.items()if check[key]!=value}
 assert all(any(key.endswith(str(k))for k in [0,1])for key in changed),changed
 cold=WinVST3('PC-post-stereo-cold-replay')
 try:
  cold.load(ROOT/'CANDIDATE_COMPONENT.bin');again,_=cold.render(input_file=ROOT/'input-0.f32');cold.save(ROOT/'COMPONENT_RESAVED.bin')
  assert (ROOT/'CANDIDATE_COMPONENT.bin').read_bytes()==(ROOT/'COMPONENT_RESAVED.bin').read_bytes()
  np.testing.assert_allclose(audio1,again,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
 finally:cold.close()
 summary=dict(reference_high_LR_dB=reference_balance.tolist(),control_stereo_high_band_error=baseline['stereo_high_band_error'],candidate_stereo_high_band_error=current['stereo_high_band_error'],candidate_high_LR_dB=current['high_LR_dB'],original_objective_improvement_passed_training=bool(current['loss']<baseline['loss']-.0005),separate_centering_preview_only=True,primary_component_unchanged=True,training_cases=len(rows),training_control=baseline['loss'],training_candidate=current['loss'],training_gain=baseline['loss']-current['loss'],existing_GUI_input01_control=held_control['loss'],existing_GUI_input01_candidate=held_candidate['loss'],existing_GUI_input01_gain=held_control['loss']-held_candidate['loss'],selected_bands=current['bands'],changed_XML_fields=changed,component_state_roundtrip_byte_exact=True,cold_replay_max_abs_error=float(abs(audio1-again).max()),not_a_new_independent_GUI_cohort=True,not_adopted=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
 (ROOT/'TRAINING_RESULTS.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0));(ROOT/'completion.json').write_text(json.dumps(summary,indent=2)+'\n');state('stereo_prescreen_completed_not_adopted',summary=summary);print(json.dumps(summary),flush=True)
finally:
 for c in clients:c.close()
