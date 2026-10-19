"""Re-evaluate real saved Diva source probes using the newer full-proved Finish."""
from pathlib import Path
import os, sys, json, ctypes, hashlib
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/tmp/divalead-source-current65')
SELECTED = ROOT / 'verified-balance-power-0011-balance42'
WORK = Path('/tmp/divalead-source-current65-b11')
WORK.mkdir(exist_ok=False)
(WORK / 'scores').mkdir()
RESEARCH = Path('/workspace/divalead/diva-lead/research/repository-selection')
sys.path.insert(0, str(RESEARCH))
import compare_all as comparison
comparison.WORK = WORK
anchor = json.loads((ROOT / 'baseline/validation.json').read_text())
selected = json.loads((SELECTED / 'validation.json').read_text())
scales = json.loads((RESEARCH / 'ranking.json').read_text())['normalizing_errors']
weights = dict(H24=.30, upper_harm=.25, ERB=.20, low_harm=.10, upper_off=.10, relative_phase=.05)
events = json.loads((ROOT / 'baseline/MIDI_events_48k.json').read_text())
lib = ctypes.CDLL(str(SELECTED / 'native_finish.so'))
lib.native_render.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
rows = []
for original in json.loads((SOURCE / 'history.json').read_text()):
    source = SOURCE / ('trial-' + format(original['index'], '03d'))
    logged = [list(map(int, line.split()[1:])) for line in (source / 'Diva.log').read_text().splitlines() if line.startswith('NOTE ')]
    assert logged == events
    dry, rate = sf.read(source / 'Diva_source.wav', dtype='float32')
    assert rate == 48000 and dry.shape == (288000, 2)
    assert hashlib.sha256(dry.tobytes()).hexdigest() == original['raw_SHA256']
    out = np.zeros_like(dry)
    assert lib.native_render(dry.ctypes.data, out.ctypes.data, len(dry), rate)
    edit = comparison.h.edit_aligned(comparison.h.align_with_pdc(out.astype('float64'), dict(alignment_frames=819), latency=12416))
    path = WORK / ('trial-' + format(original['index'], '03d') + '.wav')
    sf.write(path, edit, rate, subtype='FLOAT')
    measured = comparison.score(dict(id='source'+str(original['index']), canonical_path=str(path), aliases=[]))
    metrics = measured['metrics']
    tone = sum(weights[k] * metrics[k] / scales[k] for k in weights)
    standard = sum(comparison.WEIGHTS[k] * metrics[k] / scales[k] for k in comparison.WEIGHTS)
    excess = {k: metrics[k] / anchor['metrics'][k] - limit for k, limit in selected['guard_limits'].items() if metrics[k] > anchor['metrics'][k] * limit}
    crest = measured['diagnostics']['crest_RMS_db']
    feasible = not excess and crest <= selected['crest_cap_dB'] and standard <= anchor['score'] * 1.0001 and np.max(abs(out)) < .99
    row = dict(index=original['index'], fields=original['fields'], tone_score=tone, score=standard,
               metrics=metrics, guard_excesses=excess, crest_RMS_dB=crest, feasible=bool(feasible),
               source_probe=str(source), processed_edit=str(path), fixed_finish_basis=str(SELECTED),
               arbitrary_input_full_proof_completed=False, match_reached=False)
    if not original['fields']:
        np.testing.assert_allclose(out, sf.read(SELECTED / 'actual-Windows.wav', dtype='float32')[0], rtol=0, atol=2e-7)
        assert abs(tone - selected['tone_score']) < 1e-7
    rows.append(row)
    (WORK / 'scores-summary.json').write_text(json.dumps(rows, indent=2) + '\n')
    print('LATEST_FINISH_SOURCE', row['index'], row['fields'], tone, feasible, excess, flush=True)
report = dict(fixed_finish_basis=str(SELECTED), trials=rows, new_full_match=False,
              notes_per_phrase=3, total_note_on=6, original_reference_used=True)
(ROOT / 'source-current65-rescore.json').write_text(json.dumps(report, indent=2) + '\n')
print('LATEST_FINISH_ALL_REAL_SOURCE_PROBES_RESCORED', len(rows), flush=True)
