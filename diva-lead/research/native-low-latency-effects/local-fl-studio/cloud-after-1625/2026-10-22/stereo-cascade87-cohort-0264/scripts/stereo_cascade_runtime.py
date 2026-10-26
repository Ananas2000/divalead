"""Two actual official ZL instances; primary search plus immutable Side-phase repair."""
from pathlib import Path
import hashlib,json
from win_vst3 import WinVST3
# Freeze the currently adopted saved POST for this entire process. Never
# silently revert a new phase repair to an older hard-coded full-kit state.
BEST_PATH=Path('/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json')
ADOPTED=json.loads(BEST_PATH.read_text())
assert ADOPTED['requires_two_ZL_instances']
POST=Path(ADOPTED['post_ZL_component_state'])
assert POST.is_file()
EXPECTED_POST=hashlib.sha256(POST.read_bytes()).hexdigest()
class CascadedZL:
 def __init__(self,tag):
  self.primary=WinVST3('ST24-'+tag+'-primary')
  try:self.post=WinVST3('ST24-'+tag+'-post');self.post.load(POST)
  except BaseException:self.primary.close();raise
  self.child=self.primary.child
 def load(self,path):
  assert hashlib.sha256(POST.read_bytes()).hexdigest()==EXPECTED_POST
  result=self.primary.load(path);self.post.load(POST);return result
 def text(self,id,value):return self.primary.text(id,value)
 def set(self,id,value):return self.primary.set(id,value)
 def dump(self,path):return self.primary.dump(path)
 def save(self,path):
  result=self.primary.save(path);dest=Path(path).parent/'fixed-post-component.bin';self.post.save(dest)
  assert dest.read_bytes()==POST.read_bytes();return result
 def block(self,n):self.primary.block(n);self.post.block(n)
 def latency(self):return self.primary.latency()+self.post.latency()
 def render(self,y=None,input_file=None):
  first,status=self.primary.render(y,input_file=input_file);out,last=self.post.render(first)
  return out,status+' POST '+last
 def close(self):
  try:self.primary.close()
  finally:self.post.close()
