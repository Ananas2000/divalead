"""Replay the selected Mid AP point in two fresh actual effect chains."""
from pathlib import Path
import hashlib,json
import numpy as np,soundfile as sf
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
H=Path(__file__).resolve().parent;Q=H/'JOINT109_AIR_MARGIN_REPAIR';R=Path('/tmp/divalead-full38-inputs');R.mkdir();s=json.loads((Q/'completion.json').read_text());assert s['robust_improvement'];prior=json.loads((Q/'PRIOR_COMBINED_CANDIDATE.json').read_text());primary=(Q/'CANDIDATE_PRIMARY.bin').read_bytes();post=(Q/'CANDIDATE_POST.bin').read_bytes();trim=Path(prior['post_native_trim_state']).read_bytes()
for name,b in [('PRIMARY.bin',primary),('POST.bin',post),('POST_NATIVE_TRIM.bin',trim)]:(R/name).write_bytes(b)
raw,sr=sf.read(Q/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);want,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);errors=[]
latest=json.loads(Path('/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json').read_text());assert latest['source_accepted_cohort']==prior['source_accepted_cohort']==413;assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
for k in range(2):
 p=WinVST3('WIP38-input-proof-P-'+str(k));z=WinVST3('WIP38-input-proof-Z-'+str(k));c=NativePostTrim(R/'buffers','WIP38-input-proof-trim-'+str(k),cleanup_on_close=True)
 try:
  p.load(R/'PRIMARY.bin');z.load(R/'POST.bin');c.load(R/'POST_NATIVE_TRIM.bin');mid,_=p.render(raw);before,_=z.render(mid);got=c.render(before);np.testing.assert_allclose(got,want,rtol=8*np.finfo(np.float32).eps,atol=1e-12);assert p.latency()+z.latency()==0;errors.append(float(abs(got-want).max()))
  if k==0:sf.write(R/'BEFORE_TRIM_00.wav',before,48000,subtype='FLOAT')
  for obj,name,b in [(p,'PRIMARY',primary),(z,'POST',post),(c,'NATIVE_TRIM',trim)]:
   path=R/('COLD_'+name+'_'+str(k)+'.bin');obj.save(path);assert path.read_bytes()==b
 finally:p.close();z.close();c.close()
result=dict(two_actual_cold_ZL_ZL_nativeTrim_replay_errors=errors,all_component_and_native_state_resaves_exact=True,combined_ZL_PDC_frames=0,existing_PRIMARY_and_POST_jointly_refitted_with_small_Air_margin_repair=True,source_Diva_native12_MIDI_ARP_ADSR_and_nativeTrim_unchanged=True,new_POST_SHA256=hashlib.sha256(post).hexdigest(),native_trim_SHA256=hashlib.sha256(trim).hexdigest(),before_trim=str(R/'BEFORE_TRIM_00.wav'),reference_match_reached=False);(H/'FULL38_INPUT_AND_COLD_PROOF.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
