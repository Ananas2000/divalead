# v44 WIP analysis

Actual supplied Diva source, all 281 parameters and MIDI are identical to v43. Static 352 spectral values and 69 target coefficients are exact v43. Four fixed strengths cover harmonic ranges 2–6, 7–12, 13–18, 19–24; a shared log-gain EMA and the final five existing Side filters were refined. States remain 23, with no extra PDC or filter bank.

The reference is used offline to estimate fixed generic frequency-response values. The runtime uses only the live input and its tracked fundamental; it contains no waveform, MIDI, note or time schedule. Existing preset, source WAV and intrinsic note modulation remain unchanged relative to v43.

New prebase159 uses a separate 43parameter core and SciPy FIR/energy/Side, separate dynamics/exciter and independent tracker/10SOS. Independent spectral processing uses NumPy/SciPy STFT, vectorized power reductions, positive normalized quadratic roots and log-gain lfilter. The comparison does not silently reuse v43 prebase148 after Side changes.

verify_spectral.py --fixtures checks all 421 values, group mapping/strengths, shared time, 12 arbitrary inputs at four sample rates, causal prefixes and the delivered fixture. test_adaptive_transitions.py checks four changing-frequency/level cases and volume invariance. Recorded full Windows validation also covers block sizes, preroll, chunks, rates, silence, Amount=0 and L/R.

The selected search candidate excludes finite-difference probes outside the stated bounds. Research includes rejected paired target-curve controls, genuine source parameter controls and shared response-time controls. All metric regressions are documented. Measurements are not auditory similarity percentages, exact-pitch claims or isolated hiss. Audio input is unavailable to this model; no audition or FL Studio GUI claim is made. The provided Diva binary is excluded. Match remains open.
