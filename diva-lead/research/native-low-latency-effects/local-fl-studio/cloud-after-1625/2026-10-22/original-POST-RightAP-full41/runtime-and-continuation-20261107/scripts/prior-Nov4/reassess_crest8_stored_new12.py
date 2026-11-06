"""Recover quality metrics from the original preserved WAVs, never rerender/cherry-pick."""
from pathlib import Path
import hashlib,io,json,tarfile,threading
import numpy as np,soundfile as sf
import crest8_reassessment_support as q
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-native12-highcrest8-proxy-fullChorus-20261104');frozen=json.loads((R/'PRIOR_COMBINED_CANDIDATE.json').read_text());assert q.seed['x']==frozen['native_base']['x'];assert q.seed['source_manifest']['source_audio_SHA256']==frozen['native_base']['source_manifest']['source_audio_SHA256'];cache=threading.local();power=q.a.powers

def powers(*args,**kw):v=power(*args,**kw);cache.power=v[0];return v
q.a.powers=powers

def assess(y):
 d=q.assess(y);e=10*np.log10(np.maximum(cache.power,1e-15)/np.maximum(q.a.TP,1e-15));d['Air']=float(np.maximum(e[:,4:6,2:],0).mean());d['stereo_preservation_passed']=bool(d['upper_LR_error']<=1.48 and max(abs(np.array(d['LR_dB'])[1:]))<=1.6 and d['lowmid_error']<=3.25);return d

arc=R/'ALL48_NEW_NATIVE_CONTROL_CANDIDATE_WAVs.tar.gz';rows=[];members=[]
with tarfile.open(arc)as tar:
 assert len(tar.getmembers())==48
 for rep in range(12):
  audio={}
  for label in ['native-control','native-candidate','control','candidate']:
   name=f'{label}-{rep}.wav';blob=tar.extractfile(name).read();y,rate=sf.read(io.BytesIO(blob),dtype='float32',always_2d=True);assert rate==48000;audio[label]=y;members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
  a=assess(audio['control']);b=assess(audio['candidate']);rows.append(dict(rep=rep,control=a,candidate=b,gain=a['loss']-b['loss'],Air_delta=b['Air']-a['Air']))
gain=np.array([d['gain']for d in rows]);air=np.array([d['Air_delta']for d in rows]);s6=float(gain[:6].std(ddof=1)/np.sqrt(6));s10=float(gain[:10].std(ddof=1)/np.sqrt(10));tone=float(np.mean([d['candidate']['assessment']['tone_score']-d['control']['assessment']['tone_score']for d in rows[:10]]));guards=all(d['candidate']['stereo_preservation_passed']and d['candidate']['lowmid_error']<=d['control']['lowmid_error']+.02 for d in rows);passed=bool(gain[:6].mean()>max(.0005,3*s6)and gain[:10].mean()>max(.0005,3*s10)and min(gain[10:])>0 and air[:10].mean()<=0 and max(air[10:])<=0 and tone<=0 and guards)
proof=dict(original_all48_WAVs_reassessed_no_new_quality_audio=True,frozen_comparator=frozen['source_accepted_cohort'],rows=rows,archive_members=members,first6_gain=float(gain[:6].mean()),first6_SEM=s6,first10_gain=float(gain[:10].mean()),first10_SEM=s10,cold2_gains=gain[10:].tolist(),first10_Air_delta=float(air[:10].mean()),cold2_Air_delta=air[10:].tolist(),first10_TONE_delta=tone,all12_stereo_pairedlowmid=guards,quality_criteria_passed=passed,original_hot_to_cold_native_assertion_failed=True,not_adopted=True,reference_match_reached=False)
(R/'REASSESSED_STORED_NEW12_METRICS.json').write_text(json.dumps(proof,indent=2)+'\n');(V/'CREST8_STORED_NEW12_REASSESSMENT.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in ['rows','archive_members']}),flush=True)
