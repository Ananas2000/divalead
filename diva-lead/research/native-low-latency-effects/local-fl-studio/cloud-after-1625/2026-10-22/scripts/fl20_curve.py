"""Explicit native WaveShaper curve metadata shared by fit, export and replay."""
import struct
import numpy as np
from apply_native_candidate import apply,curve_bytes

FORMAT='native_monotone_bump_v1'

def validate_curve_candidate(candidate):
    adjustment=candidate.get('waveshaper_curve_adjustment')
    if adjustment is None:return
    assert candidate.get('waveshaper_curve_format')==FORMAT,'Missing or unsupported native curve format'
    assert isinstance(adjustment,list)and len(adjustment)==2
    assert np.isfinite(np.asarray(adjustment,dtype=float)).all()
    assert not candidate.get('not_compatible_with_standard_x95_exporter',False),'Research candidate needs explicit migration before export'

def curve_metadata(candidate):
    validate_curve_candidate(candidate)
    if candidate.get('waveshaper_curve_adjustment')is None:return {}
    return dict(waveshaper_curve_format=FORMAT,
                waveshaper_curve_adjustment=list(map(float,candidate['waveshaper_curve_adjustment'])))

def extended_curve_bytes(x,adjustment):
    u=np.linspace(0,1,129);a,b=map(float,adjustment)
    y=np.clip(u+x[76]*u**3+x[77]*u**5+a*u**3*(1-u*u)**2+b*u**5*(1-u*u)**2,0,1)
    data=bytearray(curve_bytes(*x[76:78]))
    for i,value in enumerate(y):struct.pack_into('<d',data,34+24*i+8,float(value))
    return bytes(data)

def apply_candidate(c,x,candidate):
    metadata=curve_metadata(candidate);apply(c,x)
    if metadata:
        path=c.output.parent/(c.output.stem+'-extended-WS.bin')
        path.write_bytes(extended_curve_bytes(x,metadata['waveshaper_curve_adjustment']))
        c.load_state(0,path)
