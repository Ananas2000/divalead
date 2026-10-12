# Reproducing the v35 WIP checkpoint

The supplied Diva is Windows x64 VST2 despite the uploaded `.vst3` suffix. Its proprietary binary is not distributed here. Source preset, MIDI and parameter dump are identical to v34. This checkpoint changes the lower core matrix to 84 coefficients and preserves upper100, phase12 and harmonic gain24. Current improvements and regressions are documented in `../Knobs_FL_Studio_RU.md`; a perceptual match has not been reached.

Build `lead_finish.c` with MinGW: `-O3 -shared -static-libgcc -Wl,--no-insert-timestamp -lm`. Build `fx_render_host.c` as Windows x64 executable and run through Wine on the Diva-only WAV with Amount1 and Output1.8525063970852007 dB. Reported latency is12416 frames at48000 Hz.

`compare.py`, `measure_crest.py`, `measure_mid_side.py` and `measure_energy_envelopes.py` measure actual delivered WAVs against the original. Their corresponding JSON files record results. Full checks are in `../validation.json` and `spectral_independent_checks.json`.

Run `python -B verify_spectral.py --fixtures` with NumPy, SciPy, soundfile and gcc. The verifier checks220 fixed constants including all84 lower-core constants, the eight frequency anchors, core/gain sigma0.23, upper sigma0.19, phase and rolloff. It compares the C component with separate SciPy processing on12 arbitrary inputs across44.1/48/96/192 kHz, exercises upper transfers with high harmonics and verifies identical output prefixes when only future input changes. `--fixtures` also checks included actual Diva and before-spectral WAVs. Full independent processing separately rebuilds preceding core/filter/dynamics/exciter stages. Numerical parity does not establish perceptual identity.

The effect uses live input frequency and history. It does not read original audio, MIDI, note tables or a schedule. External EDIT cuts and whole-segment A/B RMS matching are outside the effect. `research_selection.json` records paired controls, harmonic preservation, solver termination and rejected prototypes. No verified audition or FL Studio GUI test was performed. Continue the render/compare/correct cycle after this backup.
