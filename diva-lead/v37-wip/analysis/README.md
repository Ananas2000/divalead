# Reproducing v37 WIP

The supplied proprietary Diva binary is not redistributed. Preset/MIDI/all281 actual parameter values match36; only Author changes. The new general input-frequency core adds quadratic live-key terms:147 core +12 phase +100 upper M/S +24 common harmonic gain =283 stored coefficients. Only15 curvature variables are fitted; other curvature entries are zero. No original audio, MIDI or note/time lookup at runtime. Improvements and regressions are documented in ../Knobs_FL_Studio_RU.md; auditory match remains unconfirmed.

Build lead_finish.c using MinGW -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -lm; build fx_render_host.c separately. Run on the Diva-only WAV with Amount1 and Output1.8525063970852007dB. Reported PDC is12416 at48kHz. All included Windows WAVs come from this effect. Full independent reconstruction is recorded separately from the isolated spectral fixture comparison.

Run python -B verify_spectral.py --fixtures with gcc/NumPy/SciPy/soundfile. It checks all283 coefficient values, anchors, sigma, rolloff,12 arbitrary-input cases at4 sample rates, future-input prefix causality and the actual Diva fixture. core_polynomial_positive_bound.json evaluates exact polynomial extrema of newly fitted lower nodes. Inherited higher-node signed Side gains remain unchanged; do not claim positivity of the whole core.

External reference edits and whole-fragment A/B RMS matching occur outside the effect. Full PDC WAV[11597:] preserves alignment/pre-ringing before the documented reference cuts; do not remove allPDC then prepend zeros. Source preset/DLL, actual281 parameter dump, coefficient recipe, measurements and SHA/ZIP are included. No listening or FL Studio GUI test was performed. Continue render/compare/correct after backup.
