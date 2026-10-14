# v49 WIP analysis

Extend the same final fixed complex M→S balance below1600Hz, with per-note harmonic phase and level safeguards.587earlier coefficients+21upper coefficients exact48;21fitted low values+3fixed zero join values=632total.47gain states and FFT/PDC unchanged. Original/Diva/all281/raw/MIDI unchanged. Independent197prebase remains valid; any pre-STFT/source change needs a new independently calculated prebase.

Run `python -B analysis/stereo_profile.py`, `analysis/verify_spectral.py --fixtures`, `analysis/test_adaptive_transitions.py`, and `analysis/test_group_activation.py` with NumPy/SciPy/soundfile and gcc. Read README/validation/repetition/MP3 reports for mixed regressions.210fit ended on ftol,15nfev/436observed evaluations. Cached proposals separately verified actualWindows/fullindependent. No optimum/listening-match claim; no reference/note/time lookup in runtime DSP.
