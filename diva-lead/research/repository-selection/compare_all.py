"""One reference, declared criteria, all committed WAV variants; no listening claims."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import sys,json,re,hashlib,importlib.util,time
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.optimize import minimize_scalar
from concurrent.futures import ProcessPoolExecutor
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2];WORK=Path(os.environ.get('DIVALEAD_SELECTION_WORK',str(Path.home()/'.cache/divalead-repository-selection')));WORK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(REPO/'diva-lead/research/after-v56'))
import audio_match_helpers as h
def load_module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
wave=load_module('shape',REPO/'diva-lead/v55-wip/analysis/wave_shape_diagnostics.py')
REF=h.REFERENCE;N=len(REF);SR=48000
WINDOWS=wave.WINDOWS;F=np.fft.rfftfreq(65536,1/SR)
BANDS=[(120,300),(300,800),(400,1600),(1600,2500),(3500,4500),(4500,6500),(6500,10000),(10000,14000)]
def powers(x):
 rows=[];carriers=[];bound=[]
 for a,b,nom in WINDOWS:
  z=x[int(a*SR):int(b*SR)];t=np.arange(len(z))/SR;w=np.hanning(len(z));orders=np.array([1,2,3])
  def energy(f):
   co=z.T@(w[:,None]*np.exp(-2j*np.pi*t[:,None]*f*orders[None,:]));return -float(np.sum(abs(co)**2/orders[None,:]**2))
  fit=minimize_scalar(energy,bounds=(nom*.992,nom*1.008),method='bounded',options={'xatol':1e-9});f=float(fit.x);carriers.append(f);bound.append(not nom*.992+1e-4<f<nom*1.008-1e-4)
  ms=np.c_[z.mean(axis=1),(z[:,0]-z[:,1])/2];p=abs(np.fft.rfft(ms*w[:,None],65536,axis=0))**2;mask=abs(F-np.rint(F/f)*f)<.23*f;unit=max(float(p[abs(F-f)<.23*f].sum()),1e-30)
  rows.append([[float(p[(F>=lo)&(F<hi)&m,c].sum()/unit) for m in [mask,~mask] for c in [0,1]] for lo,hi in BANDS])
 return np.asarray(rows),carriers,bound
EF=np.fft.rfftfreq(16384,1/SR);erb=lambda f:21.4*np.log10(1+.00437*np.asarray(f));centers=np.linspace(erb(40),erb(16000),40);bank=np.exp(-.5*((erb(EF)[None]-centers[:,None])/.5)**2);active=(EF>=40)&(EF<=16000);bank[:,~active]=0
def erbpower(x):
 rows=[]
 for a,_,_ in WINDOWS:
  z=x[int(a*SR):int((a+.085)*SR)];p=np.sum(abs(np.fft.rfft(z*np.hanning(len(z))[:,None],16384,axis=0))**2,axis=1);rows.append(bank@p/max(float(p[active].sum()),1e-30))
 return np.asarray(rows)
TP,_,_=powers(REF);TE=erbpower(REF);EW=np.maximum(TE,1e-6)**.2;EW/=EW.sum();TS,TW,TC,_=wave.features(REF);TW=np.maximum(TW,1e-8)**.65;TW[:,0]=0;TW/=TW.sum()
def shift(x,n):
 return np.pad(x,((max(n,0),0),(0,0)))[max(-n,0):]
def canonical(a):
 p=a['path'];name=Path(p).name;v=re.search(r'Diva_v(\d+)',name);v=int(v.group(1)) if v else (53 if 'after-v53' in p else 56)
 x,sr=sf.read(REPO/p,always_2d=True);assert sr==SR and x.shape[1]==2
 if len(x)==N:return x,{'kind':'saved reference edit or corrected alignment','version':v,'shift':0}
 align=992 if v<=5 else 935 if v<=7 else 843 if v<=12 else 819
 if 'ALIGNED' in name:mode='saved aligned reference performance';n=0
 elif 'BEFORE_SPECTRAL' in name:mode='before spectral intermediate';n=align-8320
 elif 'WITH_PDC' in name:mode='complete chain with declared PDC';n=align-(12416 if v>=26 else 8320 if v>=11 else 4224)
 else:mode='raw or PDC-removed render';n=align
 x=shift(x,n)
 if a['frames']>240000:x=h.edit_aligned(x);mode+='; fixed video-to-reference edit'
 x=np.pad(x,((0,max(0,N-len(x))),(0,0)))[:N]
 return x,{'kind':mode,'version':v,'shift':n}
def prepare():
 inv=json.loads((HERE/'all_audio_inventory.json').read_text());groups={};excluded=[];coverage=[]
 for a in inv:
  name=Path(a['path']).name
  if name.lower().startswith('ab') or name=='Diva_original_lead_reference.wav':excluded.append(dict(a,reason='A/B containing original or original reference'));continue
  x,meta=canonical(a);assert np.isfinite(x).all()
  digest=hashlib.sha256(x.astype('<f8').tobytes()).hexdigest();entry=groups.get(digest)
  if entry is None:
   cid=f'c{len(groups):03d}';out=WORK/'canonical'/f'{cid}.wav';out.parent.mkdir(exist_ok=True);sf.write(out,x,SR,subtype='DOUBLE');entry=dict(id=cid,canonical_path=str(out),sample_sha256=digest,aliases=[]);groups[digest]=entry
  entry['aliases'].append(dict(a,**meta));coverage.append(dict(path=a['path'],candidate=entry['id'],**meta))
 # v1 has no committed synthesized WAV; render its committed preset on the modern common performance.
 x=sf.read(HERE/'V1_FRESH_CONTROLLED_REFERENCE_EDIT.wav')[0];cid=f'c{len(groups):03d}';out=WORK/'canonical'/f'{cid}.wav';sf.write(out,x,SR,subtype='DOUBLE');groups['v1']=dict(id=cid,canonical_path=str(out),sample_sha256=hashlib.sha256(x.astype('<f8').tobytes()).hexdigest(),aliases=[dict(path='Diva_lead_reference_v1.zip::Diva_lead_reference_v1/Diva_Lead_Reference_v1.h2p',version=1,kind='included fresh supplied-Diva render on common modern MIDI',shift=819)])
 result=dict(candidates=list(groups.values()),excluded=excluded,coverage=coverage,all_tracked_WAVs=len(inv));(WORK/'candidate_inventory.json').write_text(json.dumps(result,indent=2));return result
def score(entry):
 x=sf.read(entry['canonical_path'])[0];p,car,bound=powers(x);errors=10*np.log10(np.maximum(p,1e-15)/np.maximum(TP,1e-15));er=10*np.log10(np.maximum(erbpower(x),1e-12)/np.maximum(TE,1e-12));shape,_,crest,_=wave.features(x);branches=[TS,TS*np.exp(1j*np.pi*(1-wave.ORDERS))[None]];phase=[float(np.sqrt(np.sum(abs(shape-b)**2*TW))) for b in branches];met=h.measure(x);harm=h.harmonic_errors(x)
 metrics=dict(H24=harm['weighted_harmonic_error_db'],upper_harm=float(np.sqrt(np.mean(errors[:,4:,:2]**2))),upper_off=float(np.sqrt(np.mean(errors[:,4:,2:]**2))),low_harm=float(np.sqrt(np.mean(errors[:,:4,:2]**2))),ERB=float(np.sqrt(np.sum(er**2*EW))),relative_phase=min(phase),whole=met['whole_distance'],envelope=met['envelope12_error'],body=met['body_level_error_db'],stereo_phase=met['phase_rms_degrees'],stereo_balance=met['balance_rms_db'])
 result=dict(entry,metrics=metrics,diagnostics=dict(common_metrics=met,upper_band_RMS_db=np.sqrt(np.mean(errors[:,4:]**2,axis=0)).tolist(),low_band_RMS_db=np.sqrt(np.mean(errors[:,:4]**2,axis=0)).tolist(),carriers_Hz=car,carrier_at_bounds_windows=[i for i,b in enumerate(bound) if b],relative_phase_polarity_branch=int(np.argmin(phase)),crest_RMS_db=float(np.sqrt(np.mean((crest-TC)**2))),global_RMS_gain_for_AB=float(np.sqrt(np.mean(REF**2)/np.mean(x**2)))))
 (WORK/'scores'/f"{entry['id']}.json").write_text(json.dumps(result,indent=2));return result
WEIGHTS=dict(H24=.25,upper_harm=.20,ERB=.15,low_harm=.10,relative_phase=.07,upper_off=.05,whole=.05,envelope=.05,body=.03,stereo_phase=.025,stereo_balance=.025)
def rank(results):
 base=next(r for r in results if any(a['path']=='diva-lead/v55-wip/Diva_v55_VIDEO_REFERENCE_EDIT.wav' for a in r['aliases']))
 scales=base['metrics'];weights=WEIGHTS;v=np.array([[r['metrics'][k]/scales[k] for k in weights] for r in results]);w=np.array(list(weights.values()));scores=v@w
 rng=np.random.default_rng(5601);sens=rng.dirichlet(w*100,size=10000);wins=np.argmin(v@sens.T,axis=0);counts=np.bincount(wins,minlength=len(results))
 for i,r in enumerate(results):r.update(weighted_score=float(scores[i]),weight_sensitivity_wins=int(counts[i]),pareto_dominated=bool(np.any(np.all(v<=v[i]+1e-12,axis=1)&np.any(v<v[i]-1e-12,axis=1))))
 results.sort(key=lambda r:r['weighted_score']);report=dict(definition='Declared weighted mean of physical error ratios versus v55. Lower is better on these criteria; not perceived similarity or proof of exact match. No reference-derived audio in candidates. Ranking cannot establish a unique perceptual best.',weights=weights,normalizing_errors=scales,sensitivity='10000 deterministic Dirichlet(weight*100) draws; no subjective audition',reference_sha256=hashlib.sha256(REF.astype('<f8').tobytes()).hexdigest(),results=results,match_reached=False)
 (WORK/'ranking.json').write_text(json.dumps(report,indent=2));print('TOP_CANDIDATES',flush=True)
 for r in results[:20]:print(r['id'],round(r['weighted_score'],7),r['weight_sensitivity_wins'],[a['path'] for a in r['aliases']][:2],r['metrics'],flush=True)
 return report
if __name__=='__main__':
 if '--rank-only' in sys.argv:rank([json.loads(p.read_text()) for p in sorted((WORK/'scores').glob('*.json'))]);sys.exit()
 data=prepare();(WORK/'scores').mkdir(exist_ok=True);print('COVERAGE',len(data['candidates']),len(data['coverage']),len(data['excluded']),flush=True)
 pending=[e for e in data['candidates'] if not (WORK/'scores'/f"{e['id']}.json").exists() or json.loads((WORK/'scores'/f"{e['id']}.json").read_text()).get('sample_sha256')!=e['sample_sha256']]
 with ProcessPoolExecutor(max_workers=3) as pool:
  for n,result in enumerate(pool.map(score,pending)):
   if n%10==0:print('SCORED',n+1,len(pending),result['id'],flush=True)
 rank([json.loads(p.read_text()) for p in sorted((WORK/'scores').glob('*.json'))])
