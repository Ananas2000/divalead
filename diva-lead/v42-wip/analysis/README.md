# Analysis of v42 WIP

Actual supplied Diva source and MIDI are identical to v41; all281 parameters verified. Current352 constants are147core+12phase+100upper+93gain. New gain orders11/13/15/17/21 add15values. Existing78gain, upper42core, phase12 and upper100 values are unchanged41. Existing85lowercore values recalibrated on an identical paired objective;90+82evaluations, ftol criterion. Allpre-spectral processing remains31/41, so the independently calculated31prebase remains valid.

`compare.py` reproduces scalar spectral, dynamics and stereo measurements. `measure_stationary_powers.py` and `measure_stationary_low_powers.py` reproduce16single-note carrier-fitted M/S power masks. `verify_spectral.py --fixtures` checks all352header constants and12arbitrary inputs including new11/13/15/21orders, four sample rates, causality, recipes andactualDiva fixture. Controls andselected actualWindows/native/independent reports are inresearch_selection.json. Inherited design inputs namedv10…v36 describe unchanged pre-spectral recipes andhistorical research; spectral_model.json is the current spectral configuration.

Model auditory input is unsupported; no audition orFL Studio GUI claim. Measured distances are notperceptual percentages orisolated hiss. Source binary is excluded. Match remains open.
