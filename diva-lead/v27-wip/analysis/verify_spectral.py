"""Independent input-driven spectral tests; temporary binaries stay outside repo."""
import sys
sys.dont_write_bytecode=True
import argparse,ctypes,json,re,subprocess,tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from independent_spectral_ms import spectral_ms
A=Path(__file__).resolve().parent;V=A.parent
parser=argparse.ArgumentParser();parser.add_argument('--fixtures',action='store_true');args=parser.parse_args()
cfg=json.loads((A/'spectral_model.json').read_text());params=cfg['parameters'];header=(A/'spectral_ms_settings.h').read_text()
number=r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
anchors=[float(x) for x in re.findall(number,re.search(r'SMS_ANCHORS\[6\]=\{([^}]+)\}',header)[1])]
fixed=[float(x) for x in re.findall(number,header.split('SMS_PARAMETERS[7][4]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(anchors,cfg['anchors_Hz']);np.testing.assert_array_equal(fixed,params);assert float(re.search(r'#define SMS_SIGMA ([^\n]+)',header)[1])==cfg['mask_sigma']
slopes=[float(x) for x in re.findall(number,header.split('SMS_KEY_SLOPES[7][4]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(slopes,cfg['key_slopes']);assert cfg['key_reference_Hz']==100
assert 'double key=log(f0/100)/log(2.);' in (A/'spectral_ms.h').read_text()
rows=[]
with tempfile.TemporaryDirectory(prefix='divalead-spectral-') as tmp:
 library=Path(tmp)/'spectral.so';subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(library),str(A/'spectral_component.c'),'-lm'],check=True)
 lib=ctypes.CDLL(str(library));lib.spectral_component_render.argtypes=[ctypes.c_void_p]*3+[ctypes.c_int]*3
 for rate in [44100,48000,96000,192000]:
  for frequency in [60,110,195]:
   n=rate*2;tt=np.arange(n)/rate;phase=2*np.pi*(frequency*tt+.07*np.sin(2*np.pi*2.6*tt));rng=np.random.default_rng(6051)
   raw=.28*np.sin(phase)+.024*np.sin(2*phase+.2)+.11*np.sin(3*phase-.7)+.065*np.sin(7*phase)+rng.normal(0,.001,n)
   dry=np.ascontiguousarray(np.stack([raw,raw*.97],axis=1));pd=round(8192*rate/48000)+128
   tone=np.pad(dry,((pd,0),(0,0)))[:n];side=.02*np.sin(phase*5+.15*np.sin(2*np.pi*3*tt));side=np.pad(side,(pd,0))[:n]
   processed=np.ascontiguousarray(tone+np.stack([side,-side],axis=1));y=np.zeros_like(processed)
   assert lib.spectral_component_render(processed.ctypes.data,dry.ctypes.data,y.ctypes.data,n,rate,pd)
   preview,extra=spectral_ms(processed,dry,rate,pd,params,sigma=cfg['mask_sigma'],key_slopes=cfg['key_slopes']);error=float(np.max(abs(y[extra:]-preview[:-extra])))
   np.testing.assert_allclose(y[extra:],preview[:-extra],rtol=0,atol=2e-10)
   changed=processed.copy();changed_dry=dry.copy();cut=int(.8*rate);changed[cut:]*=-.47;changed_dry[cut:]*=.22
   other=np.zeros_like(y);assert lib.spectral_component_render(changed.ctypes.data,changed_dry.ctypes.data,other.ctypes.data,n,rate,pd)
   np.testing.assert_array_equal(y[:cut],other[:cut]);rows.append({'sample_rate':rate,'fundamental_Hz':frequency,'extra_latency_frames':extra,'independent_max_error':error,'causal_prefix_equal':True})
report={'fixed_constants_match':True,'key_tracking_law':'base+slope*log2(live_f0/100Hz)','fixed_matrix_coefficients_checked':56,'arbitrary_input_no_MIDI_cases':rows}
if args.fixtures:
 base=sf.read(V.parent/'v25-wip/Diva_v25_VIDEO_WITH_PDC.wav')[0];dry=sf.read(V/'Diva_v27_VIDEO_DIVA_ONLY.wav')[0];actual=sf.read(V/'Diva_v27_VIDEO_WITH_PDC.wav')[0]
 preview,extra=spectral_ms(base,dry,48000,8320,params,sigma=cfg['mask_sigma'],key_slopes=cfg['key_slopes']);error=float(np.max(abs(actual[extra:]-preview[:-extra])))
 np.testing.assert_allclose(actual[extra:],preview[:-extra],rtol=0,atol=2e-7);report['independent_new_stage_actual_Diva_fixture_max_error']=error
print(json.dumps(report,indent=2))
