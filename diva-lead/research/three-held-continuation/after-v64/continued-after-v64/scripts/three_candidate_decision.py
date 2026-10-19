"""Recognize measured quality rejection; never reinterpret infrastructure failure."""
from pathlib import Path
import json

def quality_rejection(log_path,target):
 log=Path(log_path).read_text();target=Path(target)
 if (target/'validation.json').exists():return None
 allowed=["assert tone<json.loads((fit/'history.json').read_text())[0]['weighted_score']","assert all(measured['metrics'][k]<=base['metrics'][k]*limit", "crest=measured['diagnostics']['crest_RMS_db'];assert crest<=choice['fixed_crest_cap_dB'];assert standard<=base['score']*1.0001"]
 allowed += ["assert tone<source_basis_report.get('acceptance_tone_cap',json.loads((fit/'history.json').read_text())[0]['weighted_score'])-1e-6", "assert np.max(np.abs(actual))<.99"]
 if not log.rstrip().endswith('AssertionError') or not any(line in log for line in allowed):return None
 score=target/'scores/actual-three.json'
 if not score.exists():return None
 actual=json.loads(score.read_text())
 return dict(accepted=False,reason='Fresh actual reference metrics failed the unchanged quality requirement',actual_metrics=actual['metrics'],actual_crest_RMS_dB=actual['diagnostics']['crest_RMS_db'],full_proof_completed=False,arbitrary_cases_NOT_claimed=True,no_guard_or_tolerance_changed=True,match_reached=False)
