"""Native WaveShaper metadata shared by fitting, export, replay and restoration."""
import struct
import numpy as np
from apply_native_candidate import apply,curve_bytes

FORMAT='native_monotone_bump_v1'
LOCAL_FORMAT='smooth_local_bumps4_v1'
LOCAL_CENTERS=np.array([.12,.28,.50,.75])
LOCAL_WIDTHS=np.array([.10,.16,.20,.20])

def validate_curve_candidate(candidate):
    assert not candidate.get('not_compatible_with_standard_x95_exporter',False),'Research proposal requires explicit supported metadata migration'
    adjustment=candidate.get('waveshaper_curve_adjustment')
    local=candidate.get('waveshaper_local_bump_adjustment')
    if adjustment is None:
        assert local is None,'Local bumps require the supported parent curve'
        return
    assert candidate.get('waveshaper_curve_format')==FORMAT,'Missing or unsupported native curve format'
    assert isinstance(adjustment,list)and len(adjustment)==2
    assert np.isfinite(np.asarray(adjustment,dtype=float)).all()
    if local is not None:
        assert candidate.get('waveshaper_local_bump_format')==LOCAL_FORMAT,'Missing or unsupported local curve format'
        assert isinstance(local,list)and len(local)==4
        assert np.isfinite(np.asarray(local,dtype=float)).all()
        for key,canonical in [('waveshaper_local_bump_centers',LOCAL_CENTERS),('waveshaper_local_bump_widths',LOCAL_WIDTHS)]:
            if key in candidate:assert np.array_equal(np.array(candidate[key]),canonical),'Local curve basis does not match the supported format'

def curve_metadata(candidate):
    validate_curve_candidate(candidate)
    if candidate.get('waveshaper_curve_adjustment')is None:return {}
    result=dict(waveshaper_curve_format=FORMAT,
                waveshaper_curve_adjustment=list(map(float,candidate['waveshaper_curve_adjustment'])))
    if candidate.get('waveshaper_local_bump_adjustment')is not None:
        result.update(waveshaper_local_bump_format=LOCAL_FORMAT,
                      waveshaper_local_bump_adjustment=list(map(float,candidate['waveshaper_local_bump_adjustment'])))
    return result

def extended_curve_bytes(x,adjustment,local_adjustment=None):
    u=np.linspace(0,1,129);a,b=map(float,adjustment)
    y=np.clip(u+x[76]*u**3+x[77]*u**5+a*u**3*(1-u*u)**2+b*u**5*(1-u*u)**2,0,1)
    if local_adjustment is not None:
        basis=(u[:,None]*(1-u[:,None])/(LOCAL_CENTERS*(1-LOCAL_CENTERS)))**2*np.exp(-.5*((u[:,None]-LOCAL_CENTERS)/LOCAL_WIDTHS)**2)
        basis/=np.max(basis,axis=0)
        y=np.clip(y+basis@np.asarray(local_adjustment,dtype=float),0,1)
    data=bytearray(curve_bytes(*x[76:78]))
    for i,value in enumerate(y):struct.pack_into('<d',data,34+24*i+8,float(value))
    return bytes(data)

def apply_candidate(c,x,candidate):
    metadata=curve_metadata(candidate);apply(c,x)
    if metadata:
        path=c.output.parent/(c.output.stem+'-extended-WS.bin')
        path.write_bytes(extended_curve_bytes(x,metadata['waveshaper_curve_adjustment'],metadata.get('waveshaper_local_bump_adjustment')))
        c.load_state(0,path)
