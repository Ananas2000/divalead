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
anchors=[float(x) for x in re.findall(number,re.search(r'SMS_ANCHORS\[9\]=\{([^}]+)\}',header)[1])]
fixed=[float(x) for x in re.findall(number,header.split('SMS_PARAMETERS[7][7]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(anchors,cfg['anchors_Hz']);np.testing.assert_array_equal(fixed,params);assert float(re.search(r'#define SMS_SIGMA ([^\n]+)',header)[1])==cfg['mask_sigma']
slopes=[float(x) for x in re.findall(number,header.split('SMS_KEY_SLOPES[7][7]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(slopes,cfg['key_slopes']);assert cfg['key_reference_Hz']==100
curvatures=[float(x) for x in re.findall(number,header.split('SMS_KEY_QUADRATIC[7][7]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(curvatures,cfg['key_quadratic'])
assert 'double key=log(f0/100)/log(2.);' in (A/'spectral_ms.h').read_text()
phase=[float(x) for x in re.findall(number,header.split('SMS_PHASE_PARAMETERS[6]={',1)[1].split('};',1)[0])]
po=[float(x) for x in re.findall(number,header.split('SMS_PHASE_ORDERS[8]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(phase,cfg['common_phase_radians']);np.testing.assert_array_equal(po,cfg['common_phase_orders'])
phase_slopes=[float(x) for x in re.findall(number,header.split('SMS_PHASE_KEY_SLOPES[6]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(phase_slopes,cfg['common_phase_key_slopes'])
phase_quadratic=[float(x) for x in re.findall(number,header.split('SMS_PHASE_KEY_QUADRATIC[6]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(phase_quadratic,cfg['common_phase_key_quadratic']);assert 'key*key*SMS_PHASE_KEY_QUADRATIC' in (A/'spectral_ms.h').read_text()
ha=[float(x) for x in re.findall(number,header.split('SMS_HF_ANCHORS[12]={',1)[1].split('};',1)[0])]
hp=[float(x) for x in re.findall(number,header.split('SMS_HF_PARAMETERS[10][10]={',1)[1].split('};',1)[0])]
assert float(re.search(r'#define SMS_HF_SIGMA ([^\n]+)',header)[1])==cfg['hf_mask_sigma'];np.testing.assert_array_equal(ha,cfg['hf_matrix_anchors_Hz']);np.testing.assert_array_equal(hp,cfg['hf_matrix_parameters'])
assert cfg['upper_rolloff_Hz']==[16000,16400] and cfg['upper_rolloff_law']=='raised cosine amplitude squared'
assert 'SMS_UPPER_START_HZ=16000,SMS_UPPER_STOP_HZ=16400' in header
go=[float(x) for x in re.findall(number,header.split('SMS_GAIN_ORDERS[33]={',1)[1].split('};',1)[0])]
gp=[float(x) for x in re.findall(number,header.split('SMS_GAIN_PARAMETERS[3][31]={',1)[1].split('};',1)[0])]
np.testing.assert_array_equal(go,cfg['harmonic_gain_orders']);np.testing.assert_array_equal(gp,cfg['harmonic_gain_parameters']);assert cfg['harmonic_gain_key_reference_Hz']==100
rows=[]
dh=(A/'spectral_dynamic_settings.h').read_text();dv=[float(v) for v in re.findall(number,dh.split('SMS_DYNAMIC_TARGET[5][23]={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(dv,np.array(cfg['dynamic_harmonic_parameters']['target_logpower_db_polynomial']).ravel());assert len(dv)==115
for key,name in [('strength','SMS_DYNAMIC_STRENGTH'),('tau_seconds','SMS_DYNAMIC_TAU'),('limit_db','SMS_DYNAMIC_LIMIT_DB')]:np.testing.assert_array_equal(float(re.search(name+r'=([^,;]+)',dh)[1]),cfg['dynamic_harmonic_parameters'][key])
group=[float(v) for v in re.findall(number,dh.split('SMS_DYNAMIC_GROUP_STRENGTH[23]={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(group,cfg['dynamic_harmonic_parameters']['group_strengths']);assert cfg['dynamic_harmonic_parameters']['harmonic_groups']==[[i,i] for i in range(2,25)]
assert 'SMS_DYNAMIC_GROUP_STRENGTH[j]' in (A/'spectral_ms.h').read_text()
group=[float(v) for v in re.findall(number,dh.split('SMS_DYNAMIC_GROUP_STRENGTH[23]={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(group,cfg['dynamic_harmonic_parameters']['group_strengths']);assert cfg['dynamic_harmonic_parameters']['harmonic_groups']==[[i,i] for i in range(2,25)]
assert 'SMS_DYNAMIC_GROUP_STRENGTH[j]' in (A/'spectral_ms.h').read_text()
assert int(re.search(r'SMS_DYNAMIC_TARGET_DEGREES=([0-9]+)',dh)[1])==5
assert cfg['dynamic_harmonic_parameters']['target_logpower_bounds_db']==[-120,20]
assert 'fmax(-120.,fmin(20.,target_db))' in (A/'spectral_ms.h').read_text()
ss=cfg['stereo_harmonic_parameters'];sh=(A/'spectral_stereo_settings.h').read_text();st=[float(v) for v in re.findall(number,sh.split('SMS_STEREO_TARGET[5][24]={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(st,np.array(ss['target_stereo_logodds_db_polynomial']).ravel());assert len(st)==120
for field,name in [('strength','SMS_STEREO_STRENGTH'),('tau_seconds','SMS_STEREO_TAU'),('limit_db','SMS_STEREO_LIMIT_DB')]:np.testing.assert_array_equal(float(re.search(name+r'=([^,;]+)',sh)[1]),ss[field])
assert ss['orders']==list(range(1,25)) and ss['target_logodds_bounds_db']==[-60,20]
balance=cfg['final_stereo_balance'];bh=(A/'spectral_balance_settings.h').read_text()
for key,name,count in [('anchors_Hz','SMS_BALANCE_ANCHORS',17),('log_side_scale','SMS_BALANCE_LOG_SCALE',15),('mid_to_side_real','SMS_BALANCE_MID_MIX',15),('mid_to_side_imag','SMS_BALANCE_MID_IMAG',15)]:
 values=[float(v) for v in re.findall(number,bh.split(name+'['+str(count)+']={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(values,balance[key])
assert balance['anchors_Hz'][0]==35 and balance['anchors_Hz'][-1]==16400
assert balance['anchors_Hz'][8]==1600
assert all(balance[k][7]==0 for k in ['log_side_scale','mid_to_side_real','mid_to_side_imag'])
from independent_spectral_ms import final_balance_gain
rng=np.random.default_rng(4848);frequencies=np.linspace(0,24000,2049);probe=rng.normal(size=(2,len(frequencies),17))+1j*rng.normal(size=(2,len(frequencies),17));changed=final_balance_gain(probe,frequencies,balance)
np.testing.assert_allclose(np.sum(abs(changed)**2,axis=0),np.sum(abs(probe)**2,axis=0),rtol=2e-15,atol=2e-15);np.testing.assert_array_equal(changed[:,frequencies<=35],probe[:,frequencies<=35]);np.testing.assert_array_equal(changed[:,frequencies>=16400],probe[:,frequencies>=16400]);np.testing.assert_array_equal(final_balance_gain(np.zeros_like(probe),frequencies,balance),np.zeros_like(probe))
with tempfile.TemporaryDirectory(prefix='divalead-spectral-') as tmp:
 library=Path(tmp)/'spectral.so';subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(library),str(A/'spectral_component.c'),'-lm'],check=True)
 lib=ctypes.CDLL(str(library));lib.spectral_component_render.argtypes=[ctypes.c_void_p]*3+[ctypes.c_int]*3
 for rate in [44100,48000,96000,192000]:
  for frequency in [60,110,195]:
   n=rate*2;tt=np.arange(n)/rate;phase=2*np.pi*(frequency*tt+.07*np.sin(2*np.pi*2.6*tt));rng=np.random.default_rng(6051)
   raw=.28*np.sin(phase)+.024*np.sin(2*phase+.2)+.11*np.sin(3*phase-.7)+.065*np.sin(7*phase)+.035*np.sin(17*phase-.3)+.026*np.sin(23*phase+.4)+.019*np.sin(37*phase-.2)+.015*np.sin(57*phase)+rng.normal(0,.001,n)

   for order,amount in [(11,.020),(13,.018),(15,.016),(21,.014),(41,.011),(63,.010),(97,.009),(139,.008),(193,.007)]:
    if order*frequency<rate*.45:raw+=amount*np.sin(order*phase+order*.021)
   dry=np.ascontiguousarray(np.stack([raw,raw*.97],axis=1));pd=round(8192*rate/48000)+128
   tone=np.pad(dry,((pd,0),(0,0)))[:n];side=.02*np.sin(phase*5+.15*np.sin(2*np.pi*3*tt));side=np.pad(side,(pd,0))[:n]
   processed=np.ascontiguousarray(tone+np.stack([side,-side],axis=1));y=np.zeros_like(processed)
   assert lib.spectral_component_render(processed.ctypes.data,dry.ctypes.data,y.ctypes.data,n,rate,pd)
   preview,extra=spectral_ms(processed,dry,rate,pd,params,sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);error=float(np.max(abs(y[extra:]-preview[:-extra])))
   np.testing.assert_allclose(y[extra:],preview[:-extra],rtol=0,atol=2e-10)
   changed=processed.copy();changed_dry=dry.copy();cut=int(.8*rate);changed[cut:]*=-.47;changed_dry[cut:]*=.22
   other=np.zeros_like(y);assert lib.spectral_component_render(changed.ctypes.data,changed_dry.ctypes.data,other.ctypes.data,n,rate,pd)
   np.testing.assert_array_equal(y[:cut],other[:cut]);rows.append({'sample_rate':rate,'fundamental_Hz':frequency,'extra_latency_frames':extra,'independent_max_error':error,'causal_prefix_equal':True})
report={'fixed_constants_match':True,'hf_mask_sigma_checked':cfg['hf_mask_sigma'],'common_phase_key_law_checked':'base+slope*k+curvature*k^2; k=log2(live_f0/100Hz)','key_tracking_law':'base+slope*k+curvature*k^2; k=log2(live_f0/100Hz)','fixed_matrix_coefficients_checked':147,'fixed_common_phase_coefficients_checked':18,'fixed_HF_matrix_coefficients_checked':100,'fixed_harmonic_gain_coefficients_checked':93,'adaptive_target_coefficients_checked':115,'adaptive_group_strengths_checked':23,'total_spectral_coefficients':638,'final_stereo_coefficients_checked':45,'final_stereo_bin_power_low_identity_zero_checked':True,'stereo_target_coefficients_checked':120,'total_gain_states':47,'arbitrary_input_no_MIDI_cases':rows}
if args.fixtures:
 base=sf.read(V/'Diva_v55_BEFORE_SPECTRAL.wav')[0];dry=sf.read(V/'Diva_v55_VIDEO_DIVA_ONLY.wav')[0];actual=sf.read(V/'Diva_v55_VIDEO_WITH_PDC.wav')[0]
 preview,extra=spectral_ms(base,dry,48000,8320,params,sigma=cfg['mask_sigma'],key_quadratic=cfg['key_quadratic'],key_slopes=cfg['key_slopes'],phase_angles=cfg['common_phase_radians'],hf_parameters=cfg['hf_matrix_parameters'],hf_anchors=cfg['hf_matrix_anchors_Hz'],upper_rolloff=cfg['upper_rolloff_Hz'],harmonic_gain=cfg['harmonic_gain_parameters'],gain_orders=cfg['harmonic_gain_orders'],hf_sigma=cfg['hf_mask_sigma'],phase_key_slopes=cfg['common_phase_key_slopes'],phase_key_quadratic=cfg['common_phase_key_quadratic'],core_anchors=cfg['anchors_Hz'],adaptive_dynamic=cfg['dynamic_harmonic_parameters'],adaptive_stereo=cfg['stereo_harmonic_parameters'],final_stereo_balance=cfg['final_stereo_balance']);error=float(np.max(abs(actual[extra:]-preview[:-extra])))
 np.testing.assert_allclose(actual[extra:],preview[:-extra],rtol=0,atol=2e-7);report['independent_new_stage_actual_Diva_fixture_max_error']=error
print(json.dumps(report,indent=2))
