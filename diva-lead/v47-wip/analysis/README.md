# v47 WIP analysis

Actual supplied Diva and actual Windows x64 VST2 finish. One Diva parameter changes from46: index87 Tune2=24.02. MIDI unchanged. 575/587 spectral values exact46, existing12 phase values updated; existing power targets115 and stereo targets120 unchanged. Twenty-three independent harmonic amounts replace grouped indexing; no new states, FFT, filters or PDC. Total gain states47. All23 amounts checked, including independent late-only activation probes.

Full independent validation uses newly calculated197base after source/Side changes. Source parameter/raw comparisons, all block/rate/PDC checks and float WAV evidence are in validation.json. Tiny regressions are documented alongside improvements. No audition or completed match claim.

Run with Python/NumPy/SciPy/soundfile and gcc:

```
python -B analysis/verify_spectral.py --fixtures
python -B analysis/test_adaptive_transitions.py
python -B analysis/test_group_activation.py
python -B analysis/compare.py
```

Independent spectral fixtures validate the final spectral step separately from the full independent pipeline. The original/audio/MIDI/note schedule is never embedded in the effect. Offline measurement windows are not runtime lookup tables. Noise masks include leakage/modulation/codec and do not isolate hiss.
