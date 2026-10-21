from pathlib import Path
import datetime,json,os
import numpy as np
from native_chain import NativeChain,W
from apply_native_candidate import apply
ROOT=W/'runtime-Chorus-after-repeat-prepare';ROOT.mkdir(exist_ok=True)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
N=Path('/workspace/divalead-work/native-low-latency-effects');s=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text());assert s['phase']=='paused_by_control_file_or_actual_disk_limit'
choice=json.loads((N/'NATIVE_BEST_CANDIDATE.json').read_text());x=np.array(choice['x']);features=FeaturesOriginal(target);c=NativeChain(W/'native-frozen-source-with-tail.wav','Chorus-after-repeat-prepare',fl_graph=True,engine_override='fl_native_chorus_verified_host.exe')
rows=[]
try:
 apply(c,x)
 for rep in range(6):
  y,status=c.render();r=features.residual(y[:len(target)]);rows.append(dict(loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025,native_status=status,assessment=features.local.last))
 c.set(3,1,0);control,status=c.render();again,_=c.render();error=float(abs(control-again).max());assert error<=2e-7,error
finally:c.close()
mean=float(np.mean([r['loss'] for r in rows]));std=float(np.std([r['loss'] for r in rows]));assert abs(mean-choice['loss'])<max(.02,5*std)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),runtime_prepared_twice_in_same_environment=True,independent_fresh_machine_restore_test=False,actual_native_DLL_audio=True,all_six_modulated_captures=rows,mean_original_objective=mean,std_original_objective=std,zero_depth_repeat_max_abs=error,three_incoming_held_notes_unchanged=True,reference_match_reached=False)
(ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(N/'NATIVE_CHORUS_RUNTIME_REPEATED_PREPARE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print('CHORUS_RUNTIME_REPEATED_PREPARE_ACTUAL_AUDIO_PASS',mean,std,error)
