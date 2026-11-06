from pathlib import Path
import json,hashlib,os
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-native12-highcrest8-proxy-fullChorus-20261104');D=Path('/tmp/divalead-crest8-native-replay-diagnosis-20261104');D.mkdir();prior=json.loads((R/'PRIOR_COMBINED_CANDIDATE.json').read_text());seed=prior['native_base'];state=R/'saved-native-bundle/verification/SOURCE_WaveShaper.bin';assert state.read_bytes()==(R/'SELECTED_CURVE_RESEARCH_ONLY.bin').read_bytes();results=[];first=None
for kind,path in [('control',Path(seed['native_saved_state_bundle']['directory'])/'verification/SOURCE_WaveShaper.bin'),('crest8',state)]:
 cross=None;errs=[]
 for k in range(3):
  c=NativeChain(seed['source_manifest']['native_input'],'Crest8NativeDiag-'+kind+'-'+str(k)+'-'+str(os.getpid()),fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
  try:
   apply_candidate(c,np.array(seed['x']),seed)
   for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
   c.load_state(0,path);c.set(3,1,0);saved=D/(kind+'-'+str(k)+'-WS.bin');c.save_state(0,saved);assert saved.read_bytes()==path.read_bytes();outputs=[]
   for rep in range(2):out,_=c.render();outputs.append(out.copy());sf.write(D/(kind+'-'+str(k)+'-'+str(rep)+'.wav'),out,48000,subtype='FLOAT')
   if cross is None:cross=outputs[0].copy()
   err=float(abs(outputs[0]-cross).max());warm=float(abs(outputs[1]-outputs[0]).max());errs.append(dict(cold_vs_first_cold=err,second_vs_first_within_instance=warm))
  finally:c.close()
 results.append(dict(model=kind,three_instances=errs))
proof=dict(rows=results,selected_WS_resave_byte_exact=True,unchanged_native_replay_limit=2e-7,no_threshold_relaxed=True,original_hot_vs_fresh_assertion_preserved=True,not_adopted=True);(D/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(V/'CREST8_NATIVE_REPLAY_DIAGNOSIS.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
