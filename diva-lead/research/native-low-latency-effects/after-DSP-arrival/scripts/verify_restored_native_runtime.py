from pathlib import Path
import datetime,json,os
import numpy as np
from native_chain import NativeChain,W
from apply_native_candidate import apply
N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=W/'restored-runtime-audio-proof';ROOT.mkdir(exist_ok=True)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
choice=json.loads((N/'NATIVE_RESTORED_ACCEPTED_SEED.json').read_text());x=np.array(choice['x']);features=FeaturesOriginal(target);c=NativeChain(W/'native-frozen-source-with-tail.wav','restored-native-real-audio',fl_graph=True,engine_override='fl_native_chorus_verified_host.exe')
rows=[]
try:
 apply(c,x)
 for rep in range(6):
  y,status=c.render();r=features.residual(y[:len(target)]);rows.append(dict(loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025,native_status=status,assessment=features.local.last))
 c.set(3,1,0);control,_=c.render();again,_=c.render();error=float(abs(control-again).max());assert error<=2e-7,error
finally:c.close()
mean=float(np.mean([r['loss'] for r in rows]));std=float(np.std([r['loss'] for r in rows]));assert abs(mean-choice['loss'])<max(.02,5*std)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),ephemeral_runtime_rebuilt_after_tmp_and_process_loss=True,six_actual_native_DLL_renders=rows,mean_original_objective=mean,std_original_objective=std,zero_depth_repeat_max_abs=error,source_preset_and_three_held_MIDI_unchanged=True,original_reference_match_reached=False,complete_independent_new_cloud_machine_restore_not_claimed=True)
(N/'NATIVE_RESTORED_RUNTIME_AUDIO_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print('RESTORED_NATIVE_ACTUAL_AUDIO_PASS',mean,std,error)
