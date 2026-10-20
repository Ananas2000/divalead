from pathlib import Path
"""Refit audible FIR color and existing Side gains after chorus cleanup.

Independent core/SciPy processing; tracker/constant color never uses reference.
"""
import ctypes,importlib.util,json,re
import numpy as np
import soundfile as sf
from scipy.fft import rfft,irfft
from scipy.optimize import least_squares
from scipy.signal import butter,sosfilt,lfilter
import v18firlib as k
from v22_currentlib import ROOT,C,REPO,SR,measure,harmonic_errors,edit_aligned,align_with_pdc
P=ROOT
V=REPO/'diva-lead/v24-wip';seed=json.loads((V/'analysis/selected_candidate.json').read_text());dry=np.ascontiguousarray(sf.read(Path('/workspace/divalead-work/three-held-continuation/source-post80plate68-basis/Diva_source.wav'),dtype='float32')[0]);k.DRY=dry
body=(V/'analysis/fir_kernels.h').read_text().split(' = {',1)[1];hbase=np.array([float(q) for q in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',body)]).reshape(4,2,k.N);H0=rfft(np.roll(hbase,-k.HALF,axis=2),axis=2)
fx=ctypes.CDLL(str(ROOT/'analysis/v25-return-independent-core/native_finish.so'));fx.native_render.argtypes=k.NATIVE.native_render.argtypes;fx.native_set.argtypes=[ctypes.c_void_p];fx.native_clean_set.argtypes=[ctypes.c_double,ctypes.c_double];fx.native_return_set.argtypes=[ctypes.c_double,ctypes.c_double]
exc=ctypes.CDLL(str(ROOT/'analysis/quadratic_exciter_stereo.so'));exc.exciter_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p];ep=np.ascontiguousarray(seed['exciter_parameters']+[2.,0.],dtype='float64')
color=ctypes.CDLL(str(ROOT/'analysis/extra_color_native.so'));color.extra_color_render.argtypes=[ctypes.c_void_p]*3+[ctypes.c_int]*4+[ctypes.c_void_p]*3;orders=np.ascontiguousarray(seed['harmonic_color_orders'],dtype='float64');gains_color=np.ascontiguousarray(seed['harmonic_color_gains_db'],dtype='float64');q=np.ascontiguousarray(seed['harmonic_color_q_factors'],dtype='float64');dry64=np.ascontiguousarray(dry,dtype='float64')
centers=np.geomspace(60,14000,24);width=.25
def basis(freq):return np.exp(-.5*(np.log2(np.maximum(freq,1)[:,None]/centers[None,:])/width)**2)
B=basis(k.GRID);B[0]=B[-1]=0
def kernels(db):
 shifted=np.roll(irfft(H0*10**((B@db)[None,None,:]/20),n=k.N,axis=2),k.HALF,axis=2);h=hbase.copy();h[:2]=hbase[:2]+(shifted[:2]-hbase[:2])*np.hanning(k.N)[None,None,:];return h
def colorize(x):
 x=np.ascontiguousarray(x);excited=np.zeros_like(x);assert exc.exciter_render(x.ctypes.data,excited.ctypes.data,len(x),SR,ep.ctypes.data);return excited

def process(h,gains):
 y=colorize(k.process_kernels(h,gains));return y,edit_aligned(align_with_pdc(y,C['settings']))
target_corr=np.array(seed['metrics']['band_correlations']);active=np.r_[np.arange(2400,62400),np.arange(114400,174000)];filters=[butter(3,b,btype='bandpass',fs=SR,output='sos') for b in [(40,300),(300,800),(800,2000),(2000,5000),(5000,10000)]]
def correlations(x):return np.array([np.corrcoef(sosfilt(f,x,axis=0)[active].T)[0,1] for f in filters])
ff=np.fft.rfftfreq(4096,1/SR);BF=basis(ff[(ff>=35)&(ff<=16000)]);BN=basis(k.m.FREQ[k.m.SELECT]);unit_masks=np.array([abs(k.m.FREQ[k.m.SELECT]-f0)<f0*.28 for _,_,f0 in k.m.WINDOWS]);records=[]
spec=importlib.util.spec_from_file_location('roughness',V/'analysis/roughness_compare.py');rough=importlib.util.module_from_spec(spec);spec.loader.exec_module(rough)

c=json.loads((Path('/workspace/divalead-work/three-held-continuation/source-post80plate68-basis/analysis/selected_candidate.json')).read_text());p=np.ascontiguousarray(c['effect_parameters'],dtype='float64');fx.native_set(p.ctypes.data);fx.native_clean_set(c['mid_chorus_scale'],c['side_chorus_scale']);fx.native_return_set(c['return_damp_cutoff_Hz'],c['return_damp_amount']);core=np.zeros_like(dry);assert fx.native_render(dry.ctypes.data,core.ctypes.data,len(dry),SR);k.CORE=core.astype('float64');k.X=rfft(k.CORE,k.NFFT,axis=0).T;x,_=process(kernels(np.array(c['v25_eq_db'])),np.array(c['final_post_side_gains_db']));dry=dry.astype('float64')
cfg=json.loads((ROOT/'v25-return-validation/analysis/harmonic_color_settings.json').read_text())
z=sosfilt(butter(2,35,btype='highpass',fs=SR,output='sos'),dry.mean(axis=1))
z=sosfilt(butter(4,200,fs=SR,output='sos'),z)
crossings=np.flatnonzero((z[:-1]<=0)&(z[1:]>0))+1
raw=np.full(len(z),100.);last=None;frequencies=[]
for frame in crossings:
    crossing=frame-1-z[frame-1]/(z[frame]-z[frame-1])
    if last is not None:
        f=SR/(crossing-last)
        if 45<f<220:
            frequencies.append(f);frequencies=frequencies[-3:]
            raw[frame:]=np.median(frequencies)
    last=crossing
a=np.exp(-1/(SR*.005));tracked=lfilter([1-a],[1,-a],raw,zi=[a*raw[0]])[0]
delay=8320-round(cfg['lookahead_ms_from_existing_fir']*SR/1000)
frequency=np.r_[np.full(delay,100.),tracked][:len(x)]
orders=np.array(cfg['harmonic_orders']);gain=np.array(cfg['gains_db']);Q=orders*np.array(cfg['q_per_harmonic_order_factors']);A=10**(gain/40)
y=np.zeros_like(x);zi=np.zeros((len(orders),2,2))
for begin in range(0,len(x),16):
    f=np.clip(frequency[begin],45,220);w=2*np.pi*np.minimum(f*orders,SR*.45)/SR
    cosine=np.cos(w);alpha=np.sin(w)/(2*Q);den=1+alpha/A
    sos=np.c_[(1+alpha*A)/den,-2*cosine/den,(1-alpha*A)/den,np.ones(len(orders)),-2*cosine/den,(1-alpha/A)/den]
    y[begin:begin+16],zi=sosfilt(sos,x[begin:begin+16],axis=0,zi=zi)

sf.write(Path('/workspace/divalead-work/three-held-continuation/source-post80plate68-basis/NEW-independent-base-pdc.wav'),y,SR,subtype='FLOAT');prototype=sf.read(Path('/workspace/divalead-work/three-held-continuation/source-post80plate68-basis/Diva_before_spectral.wav'))[0];error=float(np.max(abs(y-prototype)));np.testing.assert_allclose(y,prototype,rtol=0,atol=5e-7);(Path('/workspace/divalead-work/three-held-continuation/source-post80plate68-basis/NEW-independent-base.json')).write_text(json.dumps({'max_error_against_search_preview':error,'uses_new_plugin_source_code':False,'baseline_finish':'separate43parameter core with Mid return damping, SciPy convolution/energy/Side and separate generic dynamics/exciter','color_stage':'independent SciPy input detector and10varyingSOS'},indent=2));print('INDEPENDENT247_NEW_SOURCE_PREBASE_PASS',error,flush=True)
