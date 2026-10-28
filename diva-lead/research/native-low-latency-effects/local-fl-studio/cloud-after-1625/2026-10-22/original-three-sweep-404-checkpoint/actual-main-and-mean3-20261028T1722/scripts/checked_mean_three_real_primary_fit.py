"""Mean of three real DSP assessments; never averages audio or changes the criterion."""
from pathlib import Path
import hashlib,json
import numpy as np
from win_vst3 import D
from normal_staged_primary_fit import RealPrimaryFit
from native_post_trim import NativePostTrim
class CheckedMeanThreePrimaryFit(RealPrimaryFit):
 def __init__(self,root,primary,post,assess,record,native_inputs,trim_state,training_air_cap,training_lowmid_cap):
  self.native_inputs=native_inputs;self.training_air_cap=training_air_cap;self.training_lowmid_cap=training_lowmid_cap;self.trims={};super().__init__(root,primary,post,assess,record)
  for k,(p,z)in enumerate(self.clients):
   c=NativePostTrim(self.root/'trim-buffers',self.host_tag+'-trim-'+str(k),cleanup_on_close=True);c.load(trim_state);self.trims[p.child.pid]=c
 def check_neutral_identity(self):
  proofs=[]
  for k,(p,z)in enumerate(self.clients):
   p.load(self.primary);z.load(self.post);mid,_=p.render(self.native_inputs[0]);pre,_=z.render(mid);direct=self.trims[p.child.pid].render(pre)
   p.load(self.primary);self.configure(p,self.initial);z.load(self.post);mid,_=p.render(self.native_inputs[0]);pre,_=z.render(mid);configured=self.trims[p.child.pid].render(pre)
   np.testing.assert_allclose(configured,direct,rtol=8*np.finfo(np.float32).eps,atol=1e-12);proofs.append(dict(worker=k,neutral_render_max_abs_error=float(abs(configured-direct).max()),baseline_loaded_before_every_evaluation=True))
  (self.root/'BOTH_HOSTS_NEUTRAL_IDENTITY.json').write_text(json.dumps(proofs,indent=2)+'\n')
 def evaluate(self,case,phase=0,keep=True):
  label,x=case;p,z=self.pool.get()
  try:
   captures=[]
   for k in(range(3)if keep else[phase]):
    p.load(self.primary);self.configure(p,x);z.load(self.post);middle,_=p.render(self.native_inputs[k]);before,_=z.render(middle);out=self.trims[p.child.pid].render(before);assert p.latency()+z.latency()==0;captures.append(self.assess(out))
   row=dict(captures[len(captures)//2]);row.update(label=label,x=list(map(float,x)),loss=float(np.mean([d['loss']for d in captures])),positive_excess_air_dB=float(np.mean([d['positive_excess_air_dB']for d in captures])),lowmid_error=float(np.mean([d['lowmid_error']for d in captures])),training_realization_losses=[d['loss']for d in captures],training_realization_assessments=captures,actual_DSP_render_count=len(captures),representative_assessment_index=len(captures)//2,original_stereo_preservation_passed=all(d['original_stereo_preservation_passed']for d in captures));row['stereo_preservation_passed']=bool(row['original_stereo_preservation_passed']and(not keep or(row['positive_excess_air_dB']<=self.training_air_cap and row['lowmid_error']<=self.training_lowmid_cap)))
   if keep:
    with self.lock:self.rows.append(row)
   return row
  finally:self.pool.put((p,z))
 def close(self):
  super().close()
  for c in self.trims.values():c.close()
  # These exact owned default buffers are overwritten by every render. All
  # original native training WAVs, component states and selected full WAV stay.
  removed=[]
  for p in D.glob(self.host_tag+'-*.f32'):
   if p.is_file()and(p.name.endswith('-input.f32')or p.name.endswith('-output.f32')):
    removed.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),closed_owned_default_render_buffer=True));p.unlink()
  (self.root/'CLOSED_OWN_RENDER_BUFFERS_RELEASE.json').write_text(json.dumps(dict(removed=removed,retained_training_WAV_and_selected_audio_and_exact_states=True),indent=2)+'\n')
