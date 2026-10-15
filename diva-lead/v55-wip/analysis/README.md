# v55 WIP analysis

Source267/all281/raw/MIDI/preSTFT unchanged54. NEW268 remains valid;247/197 are invalid for this source. Existing core/gain/power/mask/HF/phase values refined; explicit stereo fields remain54. Array shapes unchanged:638main coefficients+23group weights=661tuned array values, separate scalars/anchors;47gain states. No audition/match claim.

Run verify_spectral.py --fixtures, test_adaptive_transitions.py and test_group_activation.py with python -B, NumPy/SciPy/soundfile/gcc. Full calls include phase_key_quadratic,final_stereo_balance and all other current fields. Historical design files retain versioned names; current measurements use reference/v54/v55. No runtime note/time/reference lookup.
