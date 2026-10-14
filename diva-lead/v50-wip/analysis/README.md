# v50 WIP analysis

User prioritizes timbre over residual left bias.26actualDiva source variants measured, source49retained. Refit23existing harmonicstrengths and12existing commonphases; add6phase-key curvatures.638totalvalues,47gain states and FFT/PDC unchanged. Source/all281/raw/MIDI/pre-STFT and explicit stereo settings exact49. Independent197prebase remains valid. Read README/research_selection/wave_shape/MP3 reports for remaining mismatch and mixed regressions. No audition/optimality/match claim.

Run `python -B analysis/compare.py`, `analysis/wave_shape_diagnostics.py`, `analysis/verify_spectral.py --fixtures`, `analysis/test_adaptive_transitions.py`, and `analysis/test_group_activation.py` with NumPy/SciPy/soundfile and gcc. New independent spectral calls must pass phase_key_quadratic=cfg['common_phase_key_quadratic'] as well as final_stereo_balance and all earlier fields. Omitted phasecurvature preserves linear behavior. No note/time/reference lookup in runtime DSP.
