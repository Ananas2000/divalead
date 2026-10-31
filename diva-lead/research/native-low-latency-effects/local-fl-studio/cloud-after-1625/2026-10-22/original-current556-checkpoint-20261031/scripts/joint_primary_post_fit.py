"""Fit both real ZLs on shared native inputs; the saved source and native FX stay fixed."""
from pathlib import Path
import csv,hashlib,json,struct,threading,xml.etree.ElementTree as ET
import numpy as np
from win_vst3 import D
from checked_mean_three_real_primary_fit import CheckedMeanThreePrimaryFit

class JointPrimaryPostFit(CheckedMeanThreePrimaryFit):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs)
  self.configure_primary=self.configure
  self.primary_count=len(self.specs)
  assert self.primary_count==94
  original_specs=self.specs
  blob=self.post.read_bytes();xml=ET.fromstring(blob[8:8+struct.unpack_from('<I',blob,4)[0]])
  values={p.attrib['id']:float(p.attrib['value'])for p in xml.find('Para')}
  self.post_specs=[]
  for band in [0,1,2,3,5,6]:
   assert values['filter_type'+str(band)]==9 and values['filter_status'+str(band)]==2
   for title,key,step,lo,hi in [('Freq','freq',.06,20.,18000.),('Q','q',.09,.15,25.)]:
    self.post_specs.append(dict(title='Post '+title+str(band),parameter_title=title+str(band),value=values[key+str(band)],step=step,lo=lo,hi=hi,log=True))
  assert values['filter_type4']==0 and values['lr_mode4']==1 and values['filter_status4']==2
  for title,key,step,lo,hi,log in [('Freq','freq',.06,200.,5000.,True),('Q','q',.09,.15,25.,True),('Gain','gain',.15,-6.,3.,False)]:
   self.post_specs.append(dict(title='Post '+title+'4',parameter_title=title+'4',value=values[key+'4'],step=step,lo=lo,hi=hi,log=log))
  self.ids={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')}
  self.specs=[dict(s,title='Primary '+s['title'])for s in original_specs]+self.post_specs
  self.initial=[s['value']for s in self.specs]
  assert len(self.specs)==109
  (self.root/'EXACT109_PARAMETER_SPECS.json').write_text(json.dumps(self.specs,indent=2)+'\n')

 def apply_to_hosts(self,p,z,x):
  assert len(x)==109
  p.load(self.primary);self.configure_primary(p,x[:self.primary_count]);z.load(self.post)
  for spec,value in zip(self.post_specs,x[self.primary_count:]):
   if float(value)!=spec['value']:z.text(self.ids[spec['parameter_title']],format(value,'.12g'))

 def check_neutral_identity(self):
  proofs=[]
  for worker,(p,z)in enumerate(self.clients):
   p.load(self.primary);z.load(self.post);mid,_=p.render(self.native_inputs[0]);pre,_=z.render(mid);direct=self.trims[p.child.pid].render(pre)
   self.apply_to_hosts(p,z,self.initial);mid,_=p.render(self.native_inputs[0]);pre,_=z.render(mid);configured=self.trims[p.child.pid].render(pre)
   np.testing.assert_allclose(configured,direct,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
   proofs.append(dict(worker=worker,neutral_both_ZLs_vs_direct_load_max_error=float(abs(configured-direct).max()),both_baselines_loaded_before_every_case=True))
  (self.root/'BOTH_WORKERS_BOTH_ZLS_NEUTRAL_IDENTITY.json').write_text(json.dumps(proofs,indent=2)+'\n')

 def evaluate(self,case,phase=0,keep=True):
  label,x=case;p,z=self.pool.get()
  try:
   captures=[]
   for k in(range(3)if keep else[phase]):
    self.apply_to_hosts(p,z,x);mid,_=p.render(self.native_inputs[k]);pre,_=z.render(mid);out=self.trims[p.child.pid].render(pre)
    assert p.latency()+z.latency()==0
    captures.append(self.assess(out))
   row=dict(captures[len(captures)//2]);row.update(label=label,x=list(map(float,x)),loss=float(np.mean([v['loss']for v in captures])),positive_excess_air_dB=float(np.mean([v['positive_excess_air_dB']for v in captures])),lowmid_error=float(np.mean([v['lowmid_error']for v in captures])),training_realization_assessments=captures,training_realization_losses=[v['loss']for v in captures],actual_DSP_render_count=len(captures),original_stereo_preservation_passed=all(v['original_stereo_preservation_passed']for v in captures))
   row['stereo_preservation_passed']=bool(row['original_stereo_preservation_passed']and(not keep or(row['positive_excess_air_dB']<=self.training_air_cap and row['lowmid_error']<=self.training_lowmid_cap)))
   if keep:
    with self.lock:self.rows.append(row)
   return row
  finally:self.pool.put((p,z))
