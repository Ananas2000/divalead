"""Reusable real two-ZL primary refit using the current original matcher bounds."""
from pathlib import Path
import ast,concurrent.futures,csv,queue,struct,threading,xml.etree.ElementTree as ET
import numpy as np
from win_vst3 import D,WinVST3
class RealPrimaryFit:
 def __init__(self,root,primary,post,assess,record):
  self.root=Path(root);self.primary=Path(primary);self.post=Path(post);self.assess=assess;self.record=record;self.rows=[];self.pool=queue.Queue();self.lock=threading.Lock();self.clients=[]
  text=Path('/workspace/divalead-work/pc-stereo-20261024/continue_stereo_ZL_matching.py').read_text();tree=ast.parse(text);ns=dict(Path=Path,ET=ET,struct=struct,np=np,params={r['title']:int(r['id'])for r in csv.DictReader((D/'ZL-default-parameters.tsv').open(),delimiter='\t')})
  for name in ['specs_from_component','configure']:
   node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);exec(compile(ast.get_source_segment(text,node),'<main-'+name+'>','exec'),ns)
  self.specs,self.dynamic=ns['specs_from_component'](primary);ns.update(specs=self.specs,dynamic=self.dynamic);self.configure=ns['configure'];self.initial=[p['value']for p in self.specs]
  for k in range(2):p=WinVST3('WS48JointFit-primary-'+str(k));z=WinVST3('WS48JointFit-post-'+str(k));p.load(primary);z.load(post);self.clients.append((p,z));self.pool.put((p,z))
 def evaluate(self,case,phase=0,keep=True):
  label,x=case;p,z=self.pool.get()
  try:
   self.configure(p,x);z.load(self.post);mid,_=p.render(input_file=self.root/f'frozen-native-{phase}.f32');out,_=z.render(mid);row=dict(label=label,x=list(x),**self.assess(out));assert p.latency()+z.latency()==0
   if keep:
    with self.lock:self.rows.append(row)
   return row
  finally:self.pool.put((p,z))
 def fit(self,sweeps=3):
  current=self.evaluate(('initial-WS48-fixed-primary',self.initial));baseline=current;rng=np.random.default_rng(2026102545);groups={}
  for j,p in enumerate(self.specs):
   band=''.join(c for c in p['title']if c.isdigit())
   if band:groups.setdefault(band,[]).append(j)
  groups=list(groups.values())
  def choose(rows,current):return min([current]+[r for r in rows if r['stereo_preservation_passed']],key=lambda r:r['loss'])
  with concurrent.futures.ThreadPoolExecutor(2)as executor:
   for sweep in range(sweeps):
    cases=[]
    for k in range(48):
     v=list(current['x'])
     for index in rng.choice(len(groups),size=1+k%3,replace=False):
      for j in groups[int(index)]:p=self.specs[j];d=rng.normal()*p['step']*float(rng.choice([.7,1.4,2.8]))*(.8**sweep);v[j]=float(np.clip(v[j]*2**d if p['log']else v[j]+d,p['lo'],p['hi']))
     cases.append((f'joint-{sweep}-{k}',v))
    current=choose(list(executor.map(self.evaluate,cases)),current)
    for j in rng.permutation(len(self.specs)):
     p=self.specs[j];cases=[]
     for factor in [-2,-1,1,2]:v=list(current['x']);d=factor*p['step']*(.65**sweep);v[j]=float(np.clip(v[j]*2**d if p['log']else v[j]+d,p['lo'],p['hi']));cases.append((f'coordinate-{sweep}-{j}-{factor}',v))
     current=choose(list(executor.map(self.evaluate,cases)),current);self.record('actual_WS48_plus_normal_primary87_joint_fit',sweep=sweep,coordinate=int(j),cases=len(self.rows),initial_loss=baseline['loss'],best_loss=current['loss'])
  return baseline,current
 def close(self):
  for p,z in self.clients:p.close();z.close()
