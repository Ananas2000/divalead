"""Guarded new-host integration: unchanged controls and fresh real-DLL captures."""
from pathlib import Path
import hashlib,json,os,sys,time
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625');ROOT=BASE/'fl20-host-verification-01';ROOT.mkdir(exist_ok=False)
KIT=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')
LOCAL=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22')
OUT=ROOT/'assessment';OUT.mkdir();(OUT/'scores').mkdir();os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(BASE/'runtime/analysis-runtime/diva-lead/research/repository-selection'));import compare_all as a;a.WORK=OUT
scales=json.loads((BASE/'runtime/analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());TONE=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
sys.path.insert(0,'/tmp/divalead-native-effects');from native_chain import NativeChain
from native_features import Features
fl,sr=sf.read(LOCAL/'renders/FL_NATIVE_04_CALIBRATED.wav',dtype='float32');fl=np.pad(fl,((0,288000-len(fl)),(0,0)));features=Features(fl)
NAMES={0:'SOURCE_WaveShaper',3:'SOURCE_Chorus',4:'MID_EQ_A',5:'MID_EQ_B',6:'SIDE_EQ_A',7:'SIDE_EQ_B',8:'SUM_Stereo',10:'MID_Encode',11:'SIDE_Encode',12:'SIDE_Decode',13:'SOURCE_Phase_R',14:'SOURCE_Phase_L'}
def checkpoint(c):
 for node,name in NAMES.items():c.load_state(node,KIT/'verification'/(name+'.bin'))
 for node in [1,2,9]:c.bypass(node,True)
 for k,v in enumerate([1-4923/12800,4923/12800,1,1,1]):c.gain(k,v)
def render(engine,label,mode):
 c=NativeChain(KIT/'Diva_SOURCE_FROZEN_48k.wav',label,fl_graph=True,phase_pair=True,engine_override=engine)
 try:
  checkpoint(c)
  if mode=='bypass':c.gain(0,1);c.gain(1,0);c.bypass(3,True)
  elif mode=='zero-depth':c.set(3,1,0)
  y,status=c.render();return y,status
 finally:c.close()
controls=[]
for mode in ['bypass','zero-depth']:
 old,old_status=render('fl_native_common_phase_host.exe','fl20-control-old-'+mode,mode)
 new,new_status=render('fl_native_fl20_host.exe','fl20-control-new-'+mode,mode)
 delta=float(abs(old-new).max());assert delta<=2e-7,(mode,delta)
 controls.append(dict(mode=mode,max_abs_error=delta,decoded_float32_bit_exact=bool(np.array_equal(old,new)),old_status=old_status,new_status=new_status))
captures=[];states=[]
for instance in range(2):
 c=NativeChain(KIT/'Diva_SOURCE_FROZEN_48k.wav',f'fl20-fresh-instance-{instance}',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
 try:
  checkpoint(c)
  for node,name in NAMES.items():
   p=ROOT/(name+f'-instance{instance}.bin');c.save_state(node,p);assert p.read_bytes()==(KIT/'verification'/(name+'.bin')).read_bytes();states.append(dict(instance=instance,node=node,SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
  for rep in range(6):
   y,status=c.render();label=f'FL20_INSTANCE{instance}_REP{rep}';p=ROOT/(label+'.wav');sf.write(p,y,48000,subtype='FLOAT');edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype(float),dict(alignment_frames=819),latency=0));q=OUT/(label+'.wav');sf.write(q,edit,48000,subtype='FLOAT');score=a.score(dict(id=label,canonical_path=str(q),aliases=[]));m=score['metrics'];f=features.residual(y)
   row=dict(instance=instance,rep=rep,audio=str(p),score=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS),tone_score=sum(TONE[k]*m[k]/scales[k] for k in TONE),actual_FL_feature_distance=float(f@f),native_status=status)
   captures.append(row);print('FRESH_FL20_CONTEXT',row['instance'],row['rep'],row['score'],row['tone_score'],row['actual_FL_feature_distance'],flush=True)
 finally:c.close()
proof=dict(actual_native_DLL_renders=True,controls=controls,all12_state_bytes_exact_on_two_fresh_instances=states,captures=captures,
 old_host_original_source_unchanged=True,new_host_only_change='Bypass only Chorus during 128 silent warmup blocks, restore its existing bypass flag before source input',
 source_MIDI_mixer_and_native_states_unchanged=True,actual_FL_audio_is_published_FL04_not_a_new_GUI_export=True,full_waveform_match_claimed=False,not_a_new_timbre_candidate=True,reference_match_reached=False)
(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print('NATIVE_FL20_CONTEXT_INTEGRATION_PASSED',flush=True)
