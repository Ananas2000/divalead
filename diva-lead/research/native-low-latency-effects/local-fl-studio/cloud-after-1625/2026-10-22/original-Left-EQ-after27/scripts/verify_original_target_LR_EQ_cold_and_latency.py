"""Actual new cold ZL instances, strict state replay and measured impulse latency."""
from pathlib import Path
import hashlib,json,struct,xml.etree.ElementTree as ET
import numpy as np,soundfile as sf
from win_vst3 import WinVST3
R=Path('/tmp/divalead-original-target-LR-balance-EQ-20261025-01');s=json.loads((R/'completion.json').read_text());assert s['robust_improvement']
def values(path):
 b=path.read_bytes();return{p.attrib['id']:float(p.attrib['value'])for p in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')}
old=values(R/'CONTROL_POST.bin');new=values(R/'CANDIDATE_POST.bin');changed={k:[v,new[k]]for k,v in old.items()if new[k]!=v};assert set(changed)=={'filter_status4','freq4','gain4','lr_mode4','q4'};assert new['lr_mode4']==1 and new['filter_type4']==0 and new['filter_status4']==2;assert all(new[k]==old[k] for k in old if not k.endswith('4'))
raw,sr=sf.read(R/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);want,_=sf.read(R/'CANDIDATE_00.wav',dtype='float32',always_2d=True);errors=[];delays=[]
for k in range(2):
 p=WinVST3('OriginalLeftEQ-cold-primary-'+str(k));z=WinVST3('OriginalLeftEQ-cold-post-'+str(k))
 try:
  for c,path in [(p,R/'PRIMARY.bin'),(z,R/'CANDIDATE_POST.bin')]:
   c.load(path);saved=R/(path.stem+'-cold-resaved-'+str(k)+'.bin');c.save(saved);assert saved.read_bytes()==path.read_bytes()
  mid,_=p.render(raw);out,_=z.render(mid);np.testing.assert_allclose(out,want,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-want).max()));assert p.latency()==z.latency()==0
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];mid,_=p.render(impulse);out,_=z.render(mid);assert not np.any(out[:4096]);delays.append(int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096);assert delays[-1]==0
 finally:p.close();z.close()
proof=dict(two_fresh_cold_actual_two_ZL_instances_replay_max_abs_errors=errors,all_component_roundtrips_exact=True,only_new_Left_Peaking_slot4_XML_changed=changed,new_actual_saved_Left_Peaking=dict(frequency=new['freq4'],Q=new['q4'],gain_dB=new['gain4'],mode='Left',slot=4),combined_declared_PDC_frames=0,impulse_added_delay_frames=delays,existing_three_Side_and_one_Stereo_AllPasses_unchanged=True,original_is_the_only_target=True,v83_Finish_not_used=True,no_GUI_or_ASIO_or_whole_DAW_latency_claim=True,reference_match_reached=False)
(R/'ACTUAL_COLD_REPLAY_AND_LATENCY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
