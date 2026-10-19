"""Bounded existing-gain refinement of the fully proved physical PW source."""
from pathlib import Path
import json, os, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'pw5190-gain-research'
RUN.mkdir(exist_ok=False)
SOURCE = ROOT / 'source-pw5190-basis'
PREVIOUS = ROOT / 'pw5190-verified-balance-0001'
BASIS = RUN / 'basis'
(BASIS / 'analysis').mkdir(parents=True)
for source, target in [(PREVIOUS/'analysis/spectral_model.json', BASIS/'analysis/spectral_model.json'),
                       (PREVIOUS/'validation.json', BASIS/'validation.json'),
                       (PREVIOUS/'REFERENCE_EDIT_WIP.wav', BASIS/'REFERENCE_EDIT_WIP.wav'),
                       (SOURCE/'source_manifest.json', BASIS/'source_manifest.json')]:
    shutil.copyfile(source, target)
SCRATCH = Path('/tmp/divalead-pw5190-gains')
assert not SCRATCH.exists()
(RUN/'numeric-location.json').write_text(json.dumps(dict(numeric_scratch=str(SCRATCH),
    temporary=True, baseline=str(BASIS), only_three_held=True), indent=2)+'\n')
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
           DIVALEAD_MODEL_BASE=str(BASIS), DIVALEAD_SELECTION_WORK=str(SCRATCH),
           DIVALEAD_NUMERIC_WORKERS='1', DIVALEAD_MAXITER='24')
with (RUN/'fit.log').open('w') as log:
    subprocess.run([sys.executable,'-B',str(ROOT/'fit_three_gains.py')], env=env,
                   stdin=subprocess.DEVNULL, stdout=log, stderr=log, check=True, timeout=2400)
fit = SCRATCH/'complete-joint-basis'
best = json.loads((fit/'best.json').read_text())
old = json.loads((PREVIOUS/'validation.json').read_text())
if best['weighted_score'] >= old['tone_score']-1e-6:
    (RUN/'decision.json').write_text(json.dumps(dict(accepted=False,
        reason='No lower feasible tone error than fully proved PW source',
        numeric_tone=best['weighted_score'], match_reached=False),indent=2)+'\n')
    print('PW5190_GAIN_NO_NEW_FEASIBLE_TONE_IMPROVEMENT', flush=True)
    raise SystemExit(0)
env.update(DIVALEAD_THREE_SOURCE_BASIS=str(SOURCE),
           DIVALEAD_THREE_SOURCE_REPORT=str(SOURCE/'preliminary-metrics.json'))
target = ROOT/'pw5190-verified-gain-0001'
try:
    with (RUN/'validation.log').open('w') as log:
        subprocess.run([sys.executable,'-B',str(ROOT/'validate_three_source_model.py'),
                        str(fit),target.name],env=env,stdout=log,stderr=log,check=True,timeout=900)
except subprocess.CalledProcessError:
    from three_candidate_decision import quality_rejection
    rejection = quality_rejection(RUN/'validation.log',target)
    if rejection is None:
        raise
    (RUN/'decision.json').write_text(json.dumps(rejection,indent=2)+'\n')
    print('PW5190_GAIN_FRESH_QUALITY_REJECTED', rejection, flush=True)
else:
    actual = json.loads((target/'validation.json').read_text())
    (RUN/'decision.json').write_text(json.dumps(dict(accepted=True,
        tone_score=actual['tone_score'],score=actual['score'],full_proof_completed=True,
        validation=str(target/'validation.json'),match_reached=False),indent=2)+'\n')
    print('PW5190_GAIN_FULL_ACTUAL_PASS', actual['tone_score'], flush=True)
