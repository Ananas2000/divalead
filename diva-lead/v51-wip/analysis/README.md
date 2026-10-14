# v51 WIP analysis

Sequential timbre fits after50: existing power targets, core Mid off response, all100HF values,23power amounts/sharedtau/limit,18common phase values. Same638spectral values,47gainstates and DSP algorithms/FFT/PDC. Source/all281/raw/MIDI/pre-STFT/explicit stereo controls exact50. Independent197prebase valid.220cache error rejected;222corrected and actual223validated. See research_selection and README for mixed metrics and remaining mismatch. No audition/optimality/match claim.

Run `python -B analysis/compare.py`, `analysis/wave_shape_diagnostics.py`, `analysis/verify_spectral.py --fixtures`, `analysis/test_adaptive_transitions.py` and `analysis/test_group_activation.py` with NumPy/SciPy/soundfile/gcc. Pass all spectral fields, including phase_key_quadratic and final_stereo_balance, to independent_spectral_ms. No runtime note/time/reference lookup.
