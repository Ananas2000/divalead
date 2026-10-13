# Reproducing v41 WIP

Source/MIDI/tuning/base43/core147/phase12 unchanged40. CommonGain78 includesold54unchanged,3fixedzeros atorder40 and21newvalues beyond40;100upper coefficients recalibrated withmatchedoldgaincontrol. Total337. GenericC SMS_GAIN_POINTS26 controlsallgainloops/arrays. No original/MIDI/runtime event orcarrier table. Fullselected,regressionsreported.

Build lead_finish.c with MinGW gcc -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -lm; build fx_render_host.c separately. Process actual Diva-only WAV with Amount1/Output1.8525063970852007dB; PDC12416at48k. Run python -B verify_spectral.py --fixtures with gcc/NumPy/SciPy/soundfile. It checks all337constants,12arbitrary high-harmonic inputs including41/63/97/139/193 wherebelowNyquist at4rates,causal future-prefix and actual spectral fixture. Full independent pipeline proof is separate. Lower five core nodes unchanged38; changed upper own MidHarm/MidOff/SideHarm polynomial minima are recorded, signed SideOff transfer has no positivity assertion.

For the reference edit, full48kPDC WAV[11597:] retains preringing and alignment before external cuts; do not remove allPDC then prepend819zeros. Whole-fragment A/B RMS matching is outside DSP. Nominal mask powers are not isolated hiss or a perceived-match score. No audition or FLStudio GUI claim. Continue render/compare/correct after this backup.
