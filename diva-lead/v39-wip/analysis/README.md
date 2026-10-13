# Reproducing v39 WIP

Source/MIDI/base43/commonPhase12/commonGain54 unchanged38. Existing147 core coefficients include newly fitted upper3500/6000Hz base/key/key² values, followed by100 recalibrated upper coefficients. Total313; no new DSP algorithm or additional18upper-key stage.

Build lead_finish.c with MinGW gcc -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -lm; build fx_render_host.c separately. Process actual Diva-only WAV with Amount1/Output1.8525063970852007dB; PDC12416at48k. Run python -B verify_spectral.py --fixtures with gcc/NumPy/SciPy/soundfile. It checks all313constants,12arbitrary high-harmonic inputs at4rates,causal future-prefix and actual spectral fixture. Full independent pipeline proof is separate. Lower five core nodes unchanged38; changed upper own MidHarm/MidOff/SideHarm polynomial minima are recorded, signed SideOff transfer has no positivity assertion.

For the reference edit, full48kPDC WAV[11597:] retains preringing and alignment before external cuts; do not remove allPDC then prepend819zeros. Whole-fragment A/B RMS matching is outside DSP. Nominal mask powers are not isolated hiss or a perceived-match score. No audition or FLStudio GUI claim. Continue render/compare/correct after this backup.
