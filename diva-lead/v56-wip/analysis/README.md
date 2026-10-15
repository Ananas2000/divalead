# v56 WIP analysis

Only existing93 common harmonic gain coefficients changed55. Source267/all281/raw/MIDI/preSTFT unchanged55; NEW268 remains valid. Other spectral parameters and algorithms unchanged. 638 main coefficients +23 group weights =661 array values, anchors/scalars separate;47 gain states. No audition or match claim.

Run verify_spectral.py --fixtures, test_adaptive_transitions.py, test_group_activation.py and measure_erb_band_energy.py with python -B, NumPy/SciPy/soundfile/gcc. Independent calls include mask_sigma, phase_key_quadratic, final_stereo_balance and all other current fields. Current comparisons reference/v55/v56. Historical design files retain their historical version names. No runtime reference, note or time lookup.
