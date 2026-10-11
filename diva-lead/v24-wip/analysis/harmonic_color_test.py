"""Test tracking without MIDI at arbitrary frequencies, gain response and silence."""
from pathlib import Path
import ctypes,json,subprocess,tempfile
import numpy as np
from scipy.signal import sosfreqz
BASE=Path(__file__).resolve().parent
cfg=json.loads((BASE/'harmonic_color_settings.json').read_text())
orders=np.array(cfg['harmonic_orders']);gains=np.array(cfg['gains_db']);Q=orders*np.array(cfg['q_per_harmonic_order_factors']);A=10**(gains/40)
result=[]
with tempfile.TemporaryDirectory(prefix='diva-color-test-',dir='/tmp') as tmp:
    so=Path(tmp)/'color_probe.so'
    subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(so),str(BASE/'harmonic_color_probe.c'),'-lm'],check=True)
    lib=ctypes.CDLL(str(so));lib.color_probe.argtypes=[ctypes.c_void_p]*3+[ctypes.c_int]*3
    def render(raw,processed,rate,latency):
        raw=np.ascontiguousarray(raw,dtype='float64');processed=np.ascontiguousarray(processed,dtype='float64');out=np.zeros_like(raw)
        assert lib.color_probe(raw.ctypes.data,processed.ctypes.data,out.ctypes.data,len(raw),rate,latency)
        assert np.isfinite(out).all();return out
    for rate in [44100,48000,96000,192000]:
        latency=round(8192*rate/48000)+128
        for fundamental in [60.,110.,195.]:
            t=np.arange(round(rate*1.5))/rate
            mono=.2*np.sin(2*np.pi*fundamental*t)
            for k in orders:mono+=.02*np.sin(2*np.pi*k*fundamental*t+.2*k)
            raw=np.c_[mono,mono*.8];processed=np.pad(raw,((latency,0),(0,0)))[:len(raw)]
            out=render(raw,processed,rate,latency);start=round(rate*.75);x=processed[start:];y=out[start:];tt=np.arange(len(x))/rate;win=np.hanning(len(x))
            harmonic=np.r_[1,orders];projection=np.exp(-2j*np.pi*fundamental*tt[:,None]*harmonic)
            px=np.sum(x[:,0,None]*win[:,None]*projection,axis=0);py=np.sum(y[:,0,None]*win[:,None]*projection,axis=0)
            measured=20*np.log10(abs(py)/abs(px));w=2*np.pi*fundamental*orders/rate;c=np.cos(w);alpha=np.sin(w)/(2*Q);den=1+alpha/A
            sos=np.c_[(1+alpha*A)/den,-2*c/den,(1-alpha*A)/den,np.ones(len(orders)),-2*c/den,(1-alpha/A)/den]
            _,response=sosfreqz(sos,worN=2*np.pi*fundamental*harmonic/rate)
            expected=20*np.log10(abs(response));error=float(np.max(abs(measured-expected)))
            assert error<.12,(rate,fundamental,measured,expected)
            assert abs(measured[0])<.05;assert measured[3]<-3.8;assert measured[5]>4.5
            result.append({'sample_rate':rate,'fundamental_Hz':fundamental,'orders':harmonic.tolist(),'measured_gain_db':measured.tolist(),'expected_combined_response_db':expected.tolist(),'max_response_error_db':error})
    silence=np.zeros((48000,2));assert not np.any(render(silence,silence,48000,8320))
print(json.dumps({'arbitrary_frequency_cases':result,'silence_exact_zero':True,'no_midi_or_reference_or_note_grid':True},indent=2))
