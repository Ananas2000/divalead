"""Chain verified full-model refinements until the existing controls stall.

Every accepted result has a fresh Diva/Windows render and a matching independent
source proof. No automatic Git publication, target lookup, or finished-match claim.
"""
from pathlib import Path
import os, sys, json, subprocess, datetime, time, shutil, hashlib, traceback, fcntl, math

W = Path(os.environ.get('DIVALEAD_VALIDATION_WORK', '/workspace/divalead-work/all-repository-selection'))
P = Path(__file__).resolve().parent
REPO = P.parents[2]
ROOT = Path('/workspace/divalead-work/warm-source-continuation')
STATE = W / 'warm-source-continuation-state.json'
PY = '/workspace/.venvs/divalead/bin/python'
MODES = ['hf', 'power', 'core', 'joint', 'balance', 'strength', 'stereo', 'fine_phase']
INITIAL = Path('/workspace/divalead-work/warm-source-continuation/initial')
MANIFEST = json.loads((INITIAL / 'source_manifest.json').read_text())
SOURCE_DIRECTORY = Path('/workspace/divalead-work/all-repository-selection/validated-snapshots/warm-source-balance-coupled-0003')
assert (SOURCE_DIRECTORY / 'validation.json').is_file()
ORIGINAL = json.loads((P / 'ranking.json').read_text())['results'][0]['metrics']
GLOBAL_LIMITS = dict(H24=1., upper_harm=1.01, upper_off=1.01,
    low_harm=1.01, ERB=1.01, relative_phase=1.005, whole=1.01,
    envelope=1.01, body=1.03, stereo_phase=1.03, stereo_balance=1.03)

def write(phase, **fields):
    row = dict(time_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        controller_PID=os.getpid(), phase=phase, match_reached=False,
        automatic_publication=False, **fields)
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(row, indent=2))
    temp.replace(STATE)

def atomic_json(path, row):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(row, indent=2))
    temp.replace(path)

def checked(path):
    report = json.loads(path.read_text())
    assert report['old247_NOT_used_for_changed_source']
    assert report['source_updates'] == MANIFEST['source_updates']
    assert report['source_render_history'] == MANIFEST['source_render_history']
    assert hashlib.sha256(Path(report['new_source_raw']).read_bytes()).hexdigest() == MANIFEST['source_WAV_SHA256']
    assert report['all281_source_verified']
    assert report['fresh_raw_samples_and_dump_equal_selected_source']
    assert report['MIDI_preSTFT_processing_unchanged53']
    assert report['Windows_native_max_error'] < 2e-7
    assert report['full_NEW_SOURCE_independent_max_error'] < 3e-7
    assert report['spectral_fixture_max_error'] < 2e-7
    assert Path(report['core_model']).is_file()
    assert (path.parent / 'REFERENCE_EDIT_WIP.wav').is_file()
    feasible = all(report['metrics'][key] <= ORIGINAL[key] * limit
                   for key, limit in GLOBAL_LIMITS.items())
    return report, feasible

def execute(command, log_path, env, timeout=None):
    with log_path.open('w') as log:
        subprocess.run(command, env=env, stdin=subprocess.DEVNULL,
            stdout=log, stderr=log, check=True, timeout=timeout)

def inspect_sources():
    for key in ['source_preset', 'source_WAV', 'before_spectral_WAV']:
        assert hashlib.sha256((REPO / MANIFEST[key]).read_bytes()).hexdigest() == MANIFEST[key + '_SHA256']

def consider_incoming(best_path, best):
    """Adopt only complete real proofs, without interrupting a live numerical fit."""
    for entry in sorted((ROOT / 'INCOMING').glob('*.json')):
        try:
            record = json.loads(entry.read_text())
            path = Path(record['validation'])
            report, feasible = checked(path)
            arbitrary = json.loads(Path(record['arbitrary_input_verification']).read_text())
            cases = arbitrary['arbitrary_input_no_MIDI_cases']
            assert len(cases) == 12
            assert {row['sample_rate'] for row in cases} == {44100, 48000, 96000, 192000}
            assert all(row['causal_prefix_equal'] and row['independent_max_error'] < 2e-10 for row in cases)
            if feasible and report['score'] < best['score'] - 1e-7:
                best_path, best = path, report
                atomic_json(ROOT / 'BEST_ACTUAL.json', dict(validation=str(path),
                    score=report['score'], incoming_record=str(entry), match_reached=False))
        except Exception as error:
            rejected = ROOT / 'incoming-rejections'
            rejected.mkdir(exist_ok=True)
            atomic_json(rejected / entry.name, dict(record=str(entry), reason=str(error),
                accepted=False, match_reached=False))
    return best_path, best

def prepare_HF_seed(mode, base, run):
    """Reuse HF coordinates after a verified change to other parameter blocks."""
    pending = ROOT / 'HF_REBASE_SEED.json'
    if mode != 'hf' or not pending.exists():
        return
    record = json.loads(pending.read_text())
    model = json.loads((base / 'analysis/spectral_model.json').read_text())
    manifest = json.loads((base / 'source_manifest.json').read_text())
    for key in ['source_preset', 'source_WAV', 'before_spectral_WAV']:
        assert record[key + '_SHA256'] == manifest[key + '_SHA256']
    target = record['target_hf_parameters']
    assert len(target) == len(model['hf_matrix_parameters']) == 100
    offsets = [float(a) - float(b) for a, b in zip(target, model['hf_matrix_parameters'])]
    assert all(math.isfinite(value) and abs(value) <= .10 for value in offsets)
    fit_dir = run / 'numeric/complete-hf-frozen-base'
    fit_dir.mkdir(parents=True, exist_ok=False)
    atomic_json(fit_dir / 'best.json', dict(
        baseline_model_SHA256=hashlib.sha256(json.dumps(model, sort_keys=True).encode()).hexdigest(),
        HF_offsets=offsets, warm_start_from=record['checkpoint'],
        requires_same_source_and_new_guard_check=True, restores_SLSQP_Hessian=False,
        numerical_only_not_an_actual_render=True, match_reached=False))
    pending.rename(run / 'HF_REBASE_SEED.checked.json')

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    inspect_sources()
    seed_path = INITIAL / 'validation.json'
    seed, feasible = checked(seed_path)
    assert feasible
    if '--check-only' in sys.argv:
        print(json.dumps(dict(source_hashes_checked=True,
            initial_actual_score=seed['score'], global_guard_ratios=GLOBAL_LIMITS,
            global_guard_basis='original selected53, fixed across all rounds',
            full_independent_tolerance=3e-7, fixture_tolerance=2e-7,
            stop_only_after_two_complete_cycles_without_accepted_improvement=True,
            actual_improvement_floor=1e-7, match_reached=False), indent=2))
        return
    lock = (ROOT / 'controller.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    candidates = [seed_path]
    saved_best = ROOT / 'BEST_ACTUAL.json'
    if saved_best.exists():
        candidates.append(Path(json.loads(saved_best.read_text())['validation']))
    valid = [(checked(path)[0]['score'], path) for path in candidates if checked(path)[1]]
    _, best_path = min(valid, key=lambda item: item[0])
    best, _ = checked(best_path)
    best_path, best = consider_incoming(best_path, best)
    atomic_json(saved_best, dict(validation=str(best_path), score=best['score'], match_reached=False))
    index = max([0] + [int(path.name.split('-')[1]) for path in ROOT.glob('round-*')])
    empty_cycles = 0
    while empty_cycles < 2:
        best_path, best = consider_incoming(best_path, best)
        cycle_start_score = best['score']
        for mode in MODES:
            if shutil.disk_usage(ROOT).free < 1024**3:
                write('paused_low_workspace_space', reason='Less than1GiB free; preserve all proved WAVs and stop before creating another round.', best_validation=str(best_path), best_actual_score=best['score'])
                return
            best_path, best = consider_incoming(best_path, best)
            index += 1
            run = ROOT / ('round-' + format(index, '04d') + '-' + mode)
            base = run / 'frozen-base'
            (base / 'analysis').mkdir(parents=True, exist_ok=False)
            shutil.copy2(best['core_model'], base / 'analysis/spectral_model.json')
            shutil.copy2(best_path.parent / 'REFERENCE_EDIT_WIP.wav', base / 'REFERENCE_EDIT_WIP.wav')
            shutil.copy2(best_path, base / 'validation.json')
            atomic_json(base / 'source_manifest.json', MANIFEST)
            inspect_sources()
            prepare_HF_seed(mode, base, run)
            env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                DIVALEAD_MODEL_BASE=str(base), DIVALEAD_SELECTION_WORK=str(run / 'numeric'),
                DIVALEAD_NUMERIC_WORKERS='2', DIVALEAD_CPU_SET='0,1,2,3', DIVALEAD_MAXITER='24')
            script = P / ('refine_complete_' + mode + '.py')
            with (run / 'fit.log').open('w') as log:
                process = subprocess.Popen([PY, '-B', str(script)], env=env,
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True)
                write('numeric_fit_running', round=index, mode=mode, fit_PID=process.pid,
                    fit_directory=str(run / 'numeric' / ('complete-' + mode + '-frozen-base')),
                    best_validation=str(best_path), best_actual_score=best['score'],
                    fit_script_SHA256=hashlib.sha256(script.read_bytes()).hexdigest(),
                    numeric_workers=2, CPU_set='0,1,2,3', empty_cycles=empty_cycles)
                code = process.wait()
            if code:
                raise RuntimeError('Numeric ' + mode + ' exited ' + str(code))
            fit_dir = run / 'numeric' / ('complete-' + mode + '-frozen-base')
            assert (fit_dir / 'best.json').is_file()
            env['DIVALEAD_SELECTED_FIT'] = str(fit_dir)
            name = 'warm-source-' + format(index, '04d') + '-' + mode + '-53-control'
            write('actual_validation_running', round=index, mode=mode,
                  best_validation=str(best_path), best_actual_score=best['score'])
            execute([PY, '-B', str(W / 'validate_joint_snapshot.py'), name], run / 'control.log', env, 300)
            execute([PY, '-B', str(W / 'combine_history_source.py'), name, str(SOURCE_DIRECTORY), name + '-source-combination'], run / 'matched-source.log', env, 300)
            control = W / 'validated-snapshots' / name
            execute([PY, '-B', str(control / 'analysis/verify_spectral.py')], run / 'arbitrary-input.json', env, 300)
            candidate = W / 'validated-snapshots' / (name + '-source-combination') / 'validation.json'
            report, feasible = checked(candidate)
            best_path, best = consider_incoming(best_path, best)
            accepted = feasible and report['score'] < best['score'] - 1e-7
            atomic_json(run / 'decision.json', dict(validation=str(candidate),
                score=report['score'], previous_best_score=best['score'],
                global_guards_passed=feasible, accepted=accepted,
                global_guard_ratios=GLOBAL_LIMITS, match_reached=False))
            if accepted:
                best_path, best = candidate, report
                atomic_json(saved_best, dict(validation=str(best_path), score=best['score'], match_reached=False))
            write('round_completed', round=index, mode=mode, accepted=accepted,
                best_validation=str(best_path), best_actual_score=best['score'])
        empty_cycles = 0 if best['score'] < cycle_start_score - 1e-7 else empty_cycles + 1
    write('stalled_existing_controls', reason='Two complete cycles with no accepted actual improvement; requires a new search hypothesis, not an exact-match claim.',
          best_validation=str(best_path), best_actual_score=best['score'], empty_cycles=empty_cycles)

try:
    main()
except BlockingIOError:
    print('Continuous refinement is already running; existing state preserved.')
except Exception as error:
    write('failed', error=str(error))
    traceback.print_exc()
    raise
