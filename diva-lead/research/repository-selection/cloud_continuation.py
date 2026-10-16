"""Chain verified full-model refinements until the existing controls stall.

Every accepted result has a fresh Diva/Windows render and a matching independent
source proof. No automatic Git publication, target lookup, or finished-match claim.
"""
from pathlib import Path
import os, sys, json, subprocess, datetime, time, shutil, hashlib, traceback, fcntl

W = Path(os.environ.get('DIVALEAD_VALIDATION_WORK', '/workspace/divalead-work/all-repository-selection'))
P = Path(__file__).resolve().parent
REPO = P.parents[2]
ROOT = Path('/workspace/divalead-work/continuous-refinement')
STATE = W / 'continuous-refinement-state.json'
PY = '/workspace/.venvs/divalead/bin/python'
MODES = ['hf', 'power', 'core', 'joint', 'balance']
INITIAL = Path('/workspace/divalead-work/full-model-round3/frozen-power-actual')
MANIFEST = json.loads((INITIAL / 'source_manifest.json').read_text())
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
    assert report['source_updates'] == {'OSC:Tune2': 24.02}
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
    write('waiting_for_round3_actual_results')
    while True:
        states = [json.loads((W / ('round3-' + mode + '-state.json')).read_text())
                  for mode in ['core', 'joint']]
        if all(state['phase'] in ['completed_actual_matched_source_validation', 'failed']
               for state in states):
            break
        time.sleep(3)
    candidates = [seed_path]
    candidates += [Path(state['validation']) for state in states
                   if state['phase'] == 'completed_actual_matched_source_validation']
    blend = W / 'validated-snapshots/round3-blend-53-control-source-combination/validation.json'
    if blend.exists():
        candidates.append(blend)
    balance_probe = W / 'validated-snapshots/balance-direction-53-control-source-combination/validation.json'
    if balance_probe.exists():
        candidates.append(balance_probe)
    saved_best = ROOT / 'BEST_ACTUAL.json'
    if saved_best.exists():
        candidates.append(Path(json.loads(saved_best.read_text())['validation']))
    valid = [(checked(path)[0]['score'], path) for path in candidates if checked(path)[1]]
    _, best_path = min(valid, key=lambda item: item[0])
    best, _ = checked(best_path)
    atomic_json(saved_best, dict(validation=str(best_path), score=best['score'], match_reached=False))
    index = max([0] + [int(path.name.split('-')[1]) for path in ROOT.glob('round-*')])
    empty_cycles = 0
    while empty_cycles < 2:
        cycle_start_score = best['score']
        for mode in MODES:
            index += 1
            run = ROOT / ('round-' + format(index, '04d') + '-' + mode)
            base = run / 'frozen-base'
            (base / 'analysis').mkdir(parents=True, exist_ok=False)
            shutil.copy2(best['core_model'], base / 'analysis/spectral_model.json')
            shutil.copy2(best_path.parent / 'REFERENCE_EDIT_WIP.wav', base / 'REFERENCE_EDIT_WIP.wav')
            shutil.copy2(best_path, base / 'validation.json')
            atomic_json(base / 'source_manifest.json', MANIFEST)
            inspect_sources()
            env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                DIVALEAD_MODEL_BASE=str(base), DIVALEAD_SELECTION_WORK=str(run / 'numeric'),
                DIVALEAD_NUMERIC_WORKERS='4', DIVALEAD_CPU_SET='0,1,2,3')
            script = P / ('refine_complete_' + mode + '.py')
            with (run / 'fit.log').open('w') as log:
                process = subprocess.Popen([PY, '-B', str(script)], env=env,
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True)
                write('numeric_fit_running', round=index, mode=mode, fit_PID=process.pid,
                    fit_directory=str(run / 'numeric' / ('complete-' + mode + '-frozen-base')),
                    best_validation=str(best_path), best_actual_score=best['score'],
                    fit_script_SHA256=hashlib.sha256(script.read_bytes()).hexdigest(),
                    numeric_workers=4, CPU_set='0,1,2,3', empty_cycles=empty_cycles)
                code = process.wait()
            if code:
                raise RuntimeError('Numeric ' + mode + ' exited ' + str(code))
            fit_dir = run / 'numeric' / ('complete-' + mode + '-frozen-base')
            assert (fit_dir / 'best.json').is_file()
            env['DIVALEAD_SELECTED_FIT'] = str(fit_dir)
            name = 'continuous-' + format(index, '04d') + '-' + mode + '-53-control'
            write('actual_validation_running', round=index, mode=mode,
                  best_validation=str(best_path), best_actual_score=best['score'])
            execute([PY, '-B', str(W / 'validate_joint_snapshot.py'), name], run / 'control.log', env, 300)
            execute([PY, '-B', str(W / 'combine_core_source.py'), name], run / 'matched-source.log', env, 300)
            control = W / 'validated-snapshots' / name
            execute([PY, '-B', str(control / 'analysis/verify_spectral.py')], run / 'arbitrary-input.json', env, 300)
            candidate = W / 'validated-snapshots' / (name + '-source-combination') / 'validation.json'
            report, feasible = checked(candidate)
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
