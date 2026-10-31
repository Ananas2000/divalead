"""Native WaveShaper metadata shared by fitting, export, replay and restoration."""
import hashlib,json,struct
from pathlib import Path
import numpy as np
from apply_native_candidate import apply,curve_bytes

FORMAT='native_monotone_bump_v1'
LOCAL_FORMAT='smooth_local_bumps4_v1'
DETAIL_FORMAT='smooth_detail_bumps8_v1'
FINE_FORMAT='smooth_fine_bumps32_v1'
HIGH_FORMAT='smooth_high_peak_bumps4_v1'
HIGH_CENTERS=np.array([.65,.67,.69,.71])
HIGH_WIDTHS=np.full(4,.0125)
FINE_CENTERS=np.linspace(.02,.64,32)
FINE_WIDTHS=np.full(32,.0125)
DETAIL_CENTERS=np.array([.08,.16,.24,.32,.40,.48,.56,.64])
DETAIL_WIDTHS=np.full(8,.055)
LOCAL_CENTERS=np.array([.12,.28,.50,.75])
LOCAL_WIDTHS=np.array([.10,.16,.20,.20])

def waveshaper_controls(candidate):
    values=candidate.get('waveshaper_native_controls')
    if values is None:return None
    assert isinstance(values,list)and len(values)==3,'Expected native Preamp/Mix/Post raw controls'
    assert all(isinstance(v,int)and not isinstance(v,bool)for v in values)
    assert 64<=values[0]<=192 and 0<=values[1]<=128 and 0<=values[2]<=128,'Outside measured UI MIDI mapping'
    return values

def validate_curve_candidate(candidate):
    assert not candidate.get('not_compatible_with_standard_x95_exporter',False),'Research proposal requires explicit supported metadata migration'
    waveshaper_controls(candidate)
    bipolar=candidate.get('waveshaper_bipolar_even_adjustment')
    if bipolar is not None:
        assert candidate.get('waveshaper_bipolar_format')==BIPOLAR_FORMAT,'Unsupported bipolar curve format'
        assert candidate.get('waveshaper_curve_adjustment')is not None,'Pinned supported odd parent geometry is required'
        assert isinstance(bipolar,list)and len(bipolar)==8 and np.isfinite(np.asarray(bipolar,float)).all()
        assert isinstance(candidate.get('waveshaper_bipolar_base_state'),str)
        for key in ['waveshaper_bipolar_base_SHA256','waveshaper_bipolar_parent_geometry_SHA256']:
            assert isinstance(candidate.get(key),str)and len(candidate[key])==64
    adjustment=candidate.get('waveshaper_curve_adjustment')
    local=candidate.get('waveshaper_local_bump_adjustment')
    detail=candidate.get('waveshaper_detail_bump_adjustment')
    fine=candidate.get('waveshaper_fine_bump_adjustment')
    high=candidate.get('waveshaper_high_bump_adjustment')
    if adjustment is None:
        assert local is None and detail is None and fine is None and high is None,'Local/detail/fine/high bumps require the supported parent curve'
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

    if detail is not None:
        assert candidate.get('waveshaper_detail_bump_format')==DETAIL_FORMAT,'Missing or unsupported detail curve format'
        assert isinstance(detail,list)and len(detail)==8 and np.isfinite(np.asarray(detail,dtype=float)).all()
        for key,canonical in [('waveshaper_detail_bump_centers',DETAIL_CENTERS),('waveshaper_detail_bump_widths',DETAIL_WIDTHS)]:
            if key in candidate:assert np.array_equal(np.array(candidate[key]),canonical),'Detail curve basis does not match supported format'

    if fine is not None:
        assert candidate.get('waveshaper_fine_bump_format')==FINE_FORMAT
        assert isinstance(fine,list)and len(fine)==32 and np.isfinite(np.asarray(fine,dtype=float)).all()
        for key,canonical in [('waveshaper_fine_bump_centers',FINE_CENTERS),('waveshaper_fine_bump_widths',FINE_WIDTHS)]:
            if key in candidate:assert np.array_equal(np.array(candidate[key]),canonical),'Fine curve basis does not match supported format'

    if high is not None:
        assert candidate.get('waveshaper_high_bump_format')==HIGH_FORMAT
        assert isinstance(high,list)and len(high)==4 and np.isfinite(np.asarray(high,dtype=float)).all()
        for key,canonical in [('waveshaper_high_bump_centers',HIGH_CENTERS),('waveshaper_high_bump_widths',HIGH_WIDTHS)]:
            if key in candidate:assert np.array_equal(np.array(candidate[key]),canonical),'High curve basis does not match supported format'


def curve_metadata(candidate):
    validate_curve_candidate(candidate)
    result={}
    controls=waveshaper_controls(candidate)
    # Absent or explicit factory controls preserve existing DSP fingerprints.
    if controls is not None and controls!=[128,128,128]:
        result['waveshaper_native_controls']=list(controls)
    if candidate.get('waveshaper_curve_adjustment')is None:return result
    result.update(waveshaper_curve_format=FORMAT,
                  waveshaper_curve_adjustment=list(map(float,candidate['waveshaper_curve_adjustment'])))
    if candidate.get('waveshaper_local_bump_adjustment')is not None:
        result.update(waveshaper_local_bump_format=LOCAL_FORMAT,
                      waveshaper_local_bump_adjustment=list(map(float,candidate['waveshaper_local_bump_adjustment'])))
    if candidate.get('waveshaper_detail_bump_adjustment')is not None:
        result.update(waveshaper_detail_bump_format=DETAIL_FORMAT,
                      waveshaper_detail_bump_adjustment=list(map(float,candidate['waveshaper_detail_bump_adjustment'])))
    fine=candidate.get('waveshaper_fine_bump_adjustment')
    if fine is not None and np.any(np.asarray(fine,dtype=float)!=0):
        result.update(waveshaper_fine_bump_format=FINE_FORMAT,waveshaper_fine_bump_adjustment=list(map(float,fine)))
    high=candidate.get('waveshaper_high_bump_adjustment')
    if high is not None and np.any(np.asarray(high,dtype=float)!=0):
        result.update(waveshaper_high_bump_format=HIGH_FORMAT,waveshaper_high_bump_adjustment=list(map(float,high)))
    if candidate.get('waveshaper_bipolar_even_adjustment')is not None:
        result.update(waveshaper_bipolar_format=BIPOLAR_FORMAT,
                      waveshaper_bipolar_even_adjustment=list(map(float,candidate['waveshaper_bipolar_even_adjustment'])),
                      waveshaper_bipolar_base_SHA256=candidate['waveshaper_bipolar_base_SHA256'],
                      waveshaper_bipolar_parent_geometry_SHA256=candidate['waveshaper_bipolar_parent_geometry_SHA256'])
    return result

def extended_curve_bytes(x,adjustment,local_adjustment=None,detail_adjustment=None,fine_adjustment=None,high_adjustment=None):
    u=np.linspace(0,1,129);a,b=map(float,adjustment)
    y=np.clip(u+x[76]*u**3+x[77]*u**5+a*u**3*(1-u*u)**2+b*u**5*(1-u*u)**2,0,1)
    if local_adjustment is not None:
        basis=(u[:,None]*(1-u[:,None])/(LOCAL_CENTERS*(1-LOCAL_CENTERS)))**2*np.exp(-.5*((u[:,None]-LOCAL_CENTERS)/LOCAL_WIDTHS)**2)
        basis/=np.max(basis,axis=0)
        y=np.clip(y+basis@np.asarray(local_adjustment,dtype=float),0,1)
    if detail_adjustment is not None:
        basis=(u[:,None]*(1-u[:,None])/(DETAIL_CENTERS*(1-DETAIL_CENTERS)))**2*np.exp(-.5*((u[:,None]-DETAIL_CENTERS)/DETAIL_WIDTHS)**2)
        basis/=np.max(basis,axis=0)
        y=np.clip(y+basis@np.asarray(detail_adjustment,dtype=float),0,1)
    if fine_adjustment is not None:
        basis=(u[:,None]*(1-u[:,None])/(FINE_CENTERS*(1-FINE_CENTERS)))**2*np.exp(-.5*((u[:,None]-FINE_CENTERS)/FINE_WIDTHS)**2)
        basis/=np.max(basis,axis=0)
        y=np.clip(y+basis@np.asarray(fine_adjustment,dtype=float),0,1)
    if high_adjustment is not None:
        basis=(u[:,None]*(1-u[:,None])/(HIGH_CENTERS*(1-HIGH_CENTERS)))**2*np.exp(-.5*((u[:,None]-HIGH_CENTERS)/HIGH_WIDTHS)**2)
        basis/=np.max(basis,axis=0)
        y=np.clip(y+basis@np.asarray(high_adjustment,dtype=float),0,1)
    data=bytearray(curve_bytes(*x[76:78]))
    for i,value in enumerate(y):struct.pack_into('<d',data,34+24*i+8,float(value))
    return bytes(data)

def apply_candidate(c,x,candidate):
    metadata=curve_metadata(candidate);apply(c,x)
    if metadata.get('waveshaper_curve_adjustment')is not None:
        path=c.output.parent/(c.output.stem+'-extended-WS.bin')
        path.write_bytes(extended_curve_bytes(x,metadata['waveshaper_curve_adjustment'],metadata.get('waveshaper_local_bump_adjustment'),metadata.get('waveshaper_detail_bump_adjustment'),metadata.get('waveshaper_fine_bump_adjustment'),metadata.get('waveshaper_high_bump_adjustment')))
        c.load_state(0,path)
    if metadata.get('waveshaper_bipolar_even_adjustment')is not None:
        path=c.output.parent/(c.output.stem+'-bipolar-even8-WS.bin')
        path.write_bytes(bipolar_even_curve_bytes(x,candidate));c.load_state(0,path)
    if metadata.get('waveshaper_native_controls')is not None:
        for index,value in enumerate(metadata['waveshaper_native_controls']):c.set(0,index,value)
    bundle=candidate.get('native_saved_state_bundle')
    if bundle and bundle['settings_SHA256']==native_dsp_settings_SHA256(x,candidate):
        # Use the exact saved preset for unchanged settings. A trial changing
        # any curve/Chorus/EQ/routing parameter must not reload the old preset.
        for row in bundle['manifest']:
            path=Path(bundle['directory'])/row['state']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['state_SHA256']
            c.load_state(row['node'],path)

def native_dsp_settings_SHA256(x,candidate):
    payload=dict(x=np.asarray(x,dtype=float).tolist(),curve=curve_metadata(candidate),
                 chorus_overrides={str(k):int(v)for k,v in candidate.get('chorus_overrides',{}).items()})
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


BIPOLAR_FORMAT='native_bipolar_compact_even8_v1'

def unipolar_parent_geometry_SHA256(x,candidate):
    parent={key:value for key,value in candidate.items()if not key.startswith('waveshaper_bipolar_')}
    geometry=curve_metadata(parent);geometry.pop('waveshaper_native_controls',None)
    payload=dict(polynomial=np.asarray(x,dtype=float)[76:78].tolist(),curve=geometry)
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def bipolar_even_curve_bytes(x,candidate):
    assert unipolar_parent_geometry_SHA256(x,candidate)==candidate['waveshaper_bipolar_parent_geometry_SHA256'],'Changing odd WS geometry requires a new verified bipolar base; old base cannot be reused'
    data=bytearray(Path(candidate['waveshaper_bipolar_base_state']).read_bytes())
    assert hashlib.sha256(data).hexdigest()==candidate['waveshaper_bipolar_base_SHA256']
    assert struct.unpack_from('<I',data,16)[0]==1
    count=struct.unpack_from('<I',data,30)[0];assert 2<=count<=4096 and len(data)>=34+24*count
    u=np.cumsum([struct.unpack_from('<d',data,34+24*k)[0]for k in range(count)])
    assert np.all(np.diff(u)>0)and abs(u[0])<1e-12 and abs(u[-1]-1)<1e-9
    axis=2*u-1;window=np.maximum(0,1-(axis/.67)**2)**4
    basis=[axis*axis*window,axis**4*window]
    for center in[.1,.2,.3,.4,.5,.6]:basis.append(axis*axis*np.exp(-.5*((abs(axis)-center)/.055)**2)*window)
    basis=np.column_stack(basis);basis/=basis.max(axis=0)
    original=np.array([struct.unpack_from('<d',data,42+24*k)[0]for k in range(count)])
    values=original+basis@np.asarray(candidate['waveshaper_bipolar_even_adjustment'],float)
    assert values.min()>=0 and values.max()<=1 and np.diff(values).min()>=-1e-10,'Bipolar proposal must preserve the valid monotone transfer'
    for k,value in enumerate(values):struct.pack_into('<d',data,42+24*k,float(value))
    return bytes(data)
