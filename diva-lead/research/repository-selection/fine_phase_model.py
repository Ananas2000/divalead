"""Isolated experimental fine-phase C/SciPy implementation; no main-file mutation."""
from pathlib import Path
import shutil,json
import numpy as np

def create(source_analysis,destination,model):
 source_analysis=Path(source_analysis);destination=Path(destination);shutil.copytree(source_analysis,destination)
 spec=model['fine_phase_harmonic_parameters'];coeff=np.asarray(spec['chebyshev_coefficients']);assert coeff.shape==(5,11) and np.isfinite(coeff).all();assert spec['harmonic_orders']==list(range(1,13))+[20,40]
 width=float(spec.get('order_plateau_width',.23));strength=float(spec.get('order_plateau_strength',0.));assert np.isfinite([width,strength]).all() and 0<=width<=.45 and 0<=strength<=1
 array=lambda x:'{'+','.join(array(v) if isinstance(v,(list,tuple,np.ndarray)) else format(float(v),'.17g') for v in x)+'}'
 h='#ifndef SMS_FINE_PHASE_SETTINGS\n#define SMS_FINE_PHASE_SETTINGS\nstatic const double SMS_FINE_PHASE_ORDERS[14]='+array(spec['harmonic_orders'])+';\nstatic const double SMS_FINE_PHASE_TARGET[5][11]='+array(coeff)+';\n'
 h+='static const double SMS_FINE_PHASE_KEY_LOW_HZ='+format(spec['key_lower_Hz'],'.17g')+',SMS_FINE_PHASE_KEY_HIGH_HZ='+format(spec['key_upper_Hz'],'.17g')+',SMS_FINE_PHASE_LIMIT='+format(spec['phase_limit_radians'],'.17g')+';\n'
 h+='static const double SMS_FINE_PHASE_PLATEAU_WIDTH='+format(width,'.17g')+',SMS_FINE_PHASE_PLATEAU_STRENGTH='+format(strength,'.17g')+';\n#endif\n';(destination/'fine_phase_settings.h').write_text(h)
 p=destination/'spectral_ms.h';s=p.read_text();s='#include "fine_phase_settings.h"\n'+s
 fn='''static double sms_fine_wave_phase(double order,double key){
 if(order<=SMS_FINE_PHASE_ORDERS[0]||order>=SMS_FINE_PHASE_ORDERS[13])return 0;
 if(SMS_FINE_PHASE_PLATEAU_STRENGTH>0){
  double q=floor(order+.5),d=order-q,u=fmax(0.,fmin(1.,(fabs(d)-SMS_FINE_PHASE_PLATEAU_WIDTH)/(.5-SMS_FINE_PHASE_PLATEAU_WIDTH)));
  double warped=q+(d<0?-1.:1.)*.5*u*u*(3-2*u);
  order=(1-SMS_FINE_PHASE_PLATEAU_STRENGTH)*order+SMS_FINE_PHASE_PLATEAU_STRENGTH*warped;
 }
 double lo=log(SMS_FINE_PHASE_KEY_LOW_HZ/100)/log(2.),hi=log(SMS_FINE_PHASE_KEY_HIGH_HZ/100)/log(2.);
 double x=fmax(-1.,fmin(1.,2*(key-lo)/(hi-lo)-1)),t[5]={1,x,0,0,0};
 for(int d=2;d<5;d++)t[d]=2*x*t[d-1]-t[d-2];
 for(int j=0;j<13;j++)if(order<SMS_FINE_PHASE_ORDERS[j+1]){
  double a=0,b=0;
  for(int d=0;d<5;d++){if(j>=1&&j<=11)a+=t[d]*SMS_FINE_PHASE_TARGET[d][j-1];if(j<11)b+=t[d]*SMS_FINE_PHASE_TARGET[d][j];}
  double u=log(order/SMS_FINE_PHASE_ORDERS[j])/log(SMS_FINE_PHASE_ORDERS[j+1]/SMS_FINE_PHASE_ORDERS[j]);
  return fmax(-SMS_FINE_PHASE_LIMIT,fmin(SMS_FINE_PHASE_LIMIT,a+(b-a)*u));
 }
 return 0;
}
'''
 needle='static double sms_wave_phase(';assert s.count(needle)==1;s=s.replace(needle,fn+needle);needle='double theta=sms_wave_phase(f/f0,key),';assert s.count(needle)==1;s=s.replace(needle,'double theta=sms_wave_phase(f/f0,key)+sms_fine_wave_phase(f/f0,key),');p.write_text(s)
 p=destination/'independent_spectral_ms.py';s=p.read_text();needle='final_stereo_balance=None):';assert s.count(needle)==1;s=s.replace(needle,'final_stereo_balance=None,fine_phase=None):')
 block=''' if fine_phase is not None:
  fp=fine_phase;coeff=np.asarray(fp['chebyshev_coefficients']);assert coeff.shape==(5,11)
  lo,hi=np.log2(np.array([fp['key_lower_Hz'],fp['key_upper_Hz']])/100)
  key=np.clip(2*(np.log2(f0/100)-lo)/(hi-lo)-1,-1,1);vv=np.polynomial.chebyshev.chebvander(key,4).T
  rr=np.maximum(f[:,None]/f0,1);ps=float(fp.get('order_plateau_strength',0.));pw=float(fp.get('order_plateau_width',.23));assert 0<=ps<=1 and 0<=pw<=.45
  if ps>0:
   qq=np.floor(rr+.5);dd=rr-qq;uu=np.clip((abs(dd)-pw)/(.5-pw),0,1);warped=qq+np.sign(dd)*.5*uu*uu*(3-2*uu);rr=(1-ps)*rr+ps*warped
  ratio=np.log(np.maximum(rr,1));knots=np.log(fp['harmonic_orders']);phi=np.zeros_like(ratio)
  for degree in range(5):phi+=np.interp(ratio,knots,np.r_[0,coeff[degree],0,0])*vv[degree]
  phi=np.clip(phi,-fp['phase_limit_radians'],fp['phase_limit_radians']);out*=np.exp(1j*phi)[None]
'''
 needle=' if hf_parameters is not None:';assert s.count(needle)==1;s=s.replace(needle,block+needle);compile(s,str(p),'exec');p.write_text(s)
 p=destination/'verify_spectral.py';s=p.read_text();needle="final_stereo_balance=cfg['final_stereo_balance'])";assert s.count(needle)==2;s=s.replace(needle,"final_stereo_balance=cfg['final_stereo_balance'],fine_phase=cfg['fine_phase_harmonic_parameters'])")
 needle="if args.fixtures:";assert s.count(needle)==1;block="""fine=cfg['fine_phase_harmonic_parameters'];fh=(A/'fine_phase_settings.h').read_text();fixed=[float(x) for x in re.findall(number,fh.split('SMS_FINE_PHASE_TARGET[5][11]={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(fixed,np.asarray(fine['chebyshev_coefficients']).ravel());assert len(fixed)==55
fo=[float(x) for x in re.findall(number,fh.split('SMS_FINE_PHASE_ORDERS[14]={',1)[1].split('};',1)[0])];np.testing.assert_array_equal(fo,fine['harmonic_orders'])
for field,name in [('key_lower_Hz','SMS_FINE_PHASE_KEY_LOW_HZ'),('key_upper_Hz','SMS_FINE_PHASE_KEY_HIGH_HZ'),('phase_limit_radians','SMS_FINE_PHASE_LIMIT')]:np.testing.assert_array_equal(float(re.search(name+r'=([^,;]+)',fh)[1]),fine[field])
for field,name,default in [('order_plateau_width','SMS_FINE_PHASE_PLATEAU_WIDTH',.23),('order_plateau_strength','SMS_FINE_PHASE_PLATEAU_STRENGTH',0.)]:np.testing.assert_array_equal(float(re.search(name+r'=([^,;]+)',fh)[1]),fine.get(field,default))
report.update(fine_phase_coefficients_checked=55,total_spectral_coefficients=693,fine_phase_new_states=0,fine_phase_extra_latency_frames=0)
report.update(fine_phase_order_plateau_width=fine.get('order_plateau_width',.23),fine_phase_order_plateau_strength=fine.get('order_plateau_strength',0.))
""";s=s.replace(needle,block+needle);compile(s,str(p),'exec');p.write_text(s)
 (destination/'spectral_model.json').write_text(json.dumps(model,indent=2)+'\n')


def spectral_implementation_path(research):
 path=Path(research)/'independent_spectral_plateau.py'
 return path if path.exists() else Path(research)/'independent_spectral_extended.py'

def spectral_source(research):
 return spectral_implementation_path(research).read_text()

def extend_prefix(prefix,research):
 old="(R/'analysis/independent_spectral_ms.py').read_text()";assert prefix.count(old)==1
 prefix=prefix.replace(old,'Path('+repr(str(spectral_implementation_path(research)))+').read_text()')
 old="core_anchors=cfg['anchors_Hz'])";assert prefix.count(old)==1
 return prefix.replace(old,"core_anchors=cfg['anchors_Hz'],fine_phase=cfg.get('fine_phase_harmonic_parameters'))")

def carry_fine_phase(row,cfg):
 if cfg.get('fine_phase_harmonic_parameters') is not None:row['fine_phase_harmonic_parameters']=cfg['fine_phase_harmonic_parameters']
 return row

def fine_phase_curve(f,f0,specification):
 if specification is None:return np.zeros((len(f),len(f0)))
 spec=specification;coeff=np.asarray(spec['chebyshev_coefficients']);assert coeff.shape==(5,11)
 lo,hi=np.log2(np.array([spec['key_lower_Hz'],spec['key_upper_Hz']])/100);key=np.clip(2*(np.log2(f0/100)-lo)/(hi-lo)-1,-1,1);vv=np.polynomial.chebyshev.chebvander(key,4).T
 rr=np.maximum(np.asarray(f)[:,None]/f0,1);ps=float(spec.get('order_plateau_strength',0.));pw=float(spec.get('order_plateau_width',.23));assert 0<=ps<=1 and 0<=pw<=.45
 if ps>0:
  qq=np.floor(rr+.5);dd=rr-qq;uu=np.clip((abs(dd)-pw)/(.5-pw),0,1);warped=qq+np.sign(dd)*.5*uu*uu*(3-2*uu);rr=(1-ps)*rr+ps*warped
 ratio=np.log(np.maximum(rr,1));knots=np.log(spec['harmonic_orders']);phase=np.zeros_like(ratio)
 for degree in range(5):phase+=np.interp(ratio,knots,np.r_[0,coeff[degree],0,0])*vv[degree]
 return np.clip(phase,-spec['phase_limit_radians'],spec['phase_limit_radians'])
