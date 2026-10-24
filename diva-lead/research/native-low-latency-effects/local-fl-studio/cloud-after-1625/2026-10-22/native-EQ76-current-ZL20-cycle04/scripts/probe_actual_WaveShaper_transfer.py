"""Measure native WaveShaper transfer with all other real effects bypassed."""
from pathlib import Path
import datetime,json,os,subprocess
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import curve_bytes
from fl20_curve import apply_candidate
from win_vst3 import D,S,win
ROOT=D/'actual-native-WaveShaper-transfer-04';ROOT.mkdir(exist_ok=False);best=json.loads((D/'ZL-continuous65/BEST_CANDIDATE.json').read_text());seed=best['native_base'];levels=np.linspace(-.8,.8,65);block=2048;input=np.repeat(levels,block);stereo=np.column_stack([input,input]).astype('float32');path=ROOT/'synthetic-static-transfer-input.wav';sf.write(path,stereo,48000,subtype='FLOAT')
env=dict(os.environ,WINEPREFIX='/tmp/divalead-native-effects/wine',WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90')
plugin=Path('/tmp/divalead-native-effects/plugins/Fruity_WaveShaper_x64/Fruity WaveShaper_x64.dll')
c=NativeChain(path,'actual-WaveShaper-static-transfer',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
try:
 apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
 for node in range(1,15):c.bypass(node,True)
 for j,value in enumerate([1,0,1,1,0]):c.gain(j,value)
 current,_=c.render();sf.write(ROOT/'current-curve-output.wav',current,48000,subtype='FLOAT');identity=ROOT/'identity-state.bin';identity.write_bytes(curve_bytes(0,0));c.load_state(0,identity);flat,_=c.render();sf.write(ROOT/'identity-curve-output.wav',flat,48000,subtype='FLOAT');c.bypass(0,True);bypassed,_=c.render();np.testing.assert_array_equal(bypassed,stereo)
finally:c.close()
def plateaus(y):return np.asarray([y[(k+1)*block-512:(k+1)*block].mean(axis=0,dtype=np.float64)for k in range(len(levels))])
control=plateaus(flat);response=plateaus(current);identity_error=float(abs(control-levels[:,None]).max())
raw,sr=sf.read(seed['source_manifest']['source_audio'],dtype='float32');assert sr==48000
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_supplied_Fruity_WaveShaper_DLL=True,all_other_native_nodes_bypassed=True,bypassed_native_routing_float32_exact=True,identity_curve_unity_error_measured_not_assumed=identity_error,levels=levels.tolist(),actual_current_curve_steady_output=response.tolist(),current_curve_odd_symmetry_max_error=float(abs(response+response[::-1]).max()),source_raw_peak=float(abs(raw).max()),source_abs_quantiles=np.quantile(abs(raw),[.5,.9,.95,.99,1]).tolist(),notes_or_source_not_changed=True,no_reference_audio_in_plugin_input=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
(ROOT/'ACTUAL_WAVESHAPER_TRANSFER.json').write_text(json.dumps(report,indent=2)+'\n');print('REAL_WAVESHAPER_TRANSFER_MEASURED',json.dumps({k:v for k,v in report.items()if k not in ['levels','actual_current_curve_steady_output']}),flush=True)
