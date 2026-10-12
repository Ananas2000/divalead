# Reproducing the v33 WIP checkpoint

The supplied Diva is a Windows x64 VST2 plugin despite the uploaded `.vst3` suffix. Its proprietary binary is not distributed here. The source preset, MIDI and parameter dump are identical to v32. Current status and measured improvements/regressions are documented in `../Knobs_FL_Studio_RU.md`.

Build `lead_finish.c` with MinGW: `-O3 -shared -static-libgcc -Wl,--no-insert-timestamp -lm`. Build `fx_render_host.c` as a Windows x64 executable, then run it through Wine against the Diva-only WAV and the built effect, with Amount 1 and Output 1.8525063970852007 dB. The reported latency is 12416 frames at 48000 Hz.

`compare.py`, `measure_crest.py`, `measure_mid_side.py` and `measure_energy_envelopes.py` measure the actual delivered WAVs against the original. `measurements.json`, `crest_measurements.json`, `mid_side_measurements.json` and `energy_envelope_measurements.json` are their results. Full checks are in `../validation.json` and `spectral_independent_checks.json`.

Run `python -B verify_spectral.py --fixtures` with NumPy, SciPy, soundfile and gcc. The verifier checks 172 fixed coefficients, core/gain sigma 0.23, upper-matrix sigma 0.19, common phase base/slopes and rolloff. It compares the C spectral component with a separate SciPy implementation on 12 arbitrary inputs across four sample rates and checks unchanged output prefixes when only future input changes. With `--fixtures`, it also uses the included actual Diva and before-spectral WAVs. The independent full-pipeline comparison rebuilds the earlier core/filter/dynamics/exciter stages separately; its measured error is recorded, not a claim of perceptual identity.

The spectral model uses live input frequency and audio history. It does not read the original, MIDI, a note table or a schedule. A/B files use whole-segment RMS matching. External reference-edit cuts and A/B normalization are outside the effect.

`research_selection.json` retains private prototype measurements, numerical solver limits, phase-strength comparisons and rejected actual-Diva filter experiments. All prototypes remain WIP; only the delivered combination received Windows and independent validation. No verified audio audition or FL Studio GUI test was performed.
