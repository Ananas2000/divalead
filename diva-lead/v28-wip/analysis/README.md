# v28 WIP waveform-phase verification

The supplied actual Diva source and MIDI remain unchanged from v27. This checkpoint is experimental: crest/body metrics improve, with small whole-spectrum and envelope regressions. No listening or completed-match claim is made. The proprietary Diva binary is not redistributed.

```sh
x86_64-w64-mingw32-gcc-posix -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v28_WIP_x64.dll analysis/lead_finish.c -lm
x86_64-w64-mingw32-gcc-posix -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe analysis/fx_render_host.c -lm
python -B analysis/compare.py
python -B analysis/measure_crest.py
python -B analysis/roughness_compare.py
python -B analysis/measure_mid_side.py
python -B analysis/verify_spectral.py --fixtures
```

The Windows host accepts `plugin.dll input_float32.wav output.wav [block] [amount] [output_db] [preroll]`. It checks VST state and reports PDC. Use Amount1 and Output+1.8525063970852007dB.

The same seven-row spectral matrix retains28base coefficients and28slopes, with coefficient=base+slope*log2(live_f0/100Hz). The input crossing tracker accepts45–220Hz and uses median3/5ms smoothing. No original recording, note table or MIDI schedule is read at runtime. Six common phase angles interpolate linearly in log harmonic order between1/2/3/4/6/10/20/40, with zero phase at/outside endpoints. Both complex M/S channels receive the same unit-magnitude rotation before Hermitian reconstruction and inverse FFT. DC/Nyquist remain real.

The stage is fused into the existing Hann STFT, window4096/hop512@48k, sigma .23 harmonic mask. Window is8*round(sampleRate*(4096/48000)/8), hop window/8, FFT the next power of two. The complete causal window and total PDC are unchanged:12416@48k,11414@44.1k,24704@96k,49280@192k. No future input is read; state resets with transport or sample rate. Base FIR/dynamics/excitation/chorus/ten tracked peaks retain v25 settings.

The portable verifier checks all56 matrix coefficients, six phase angles, anchors, key law and mask width. It builds outside the checkout and independently compares12 arbitrary signals/rates and causal prefixes. With --fixtures it also compares delivered actual Windows audio using the repository's adjacent v25 before-spectral fixture. Without that flag it works from the standalone ZIP. The separate complete SciPy pipeline is recorded in spectral_independent_checks.json.

Reference alignment is full-PDC[12416-819:], preserving pre-ringing, followed by explicit external cuts. See reference_edit.json. A/B normalization uses whole segments. The crest diagnostic measures16 stationary windows and is not a perceptual compression or quality score.

research_selection.json records the unconstrained phase fit (360-call budget reached), constrained fit (373calls, numerical termination), final matrix refit and selected candidate. Numerical termination is not a completed perceptual match. v27 remains available because some metrics regress. The user requests continued independent matching without repeated listening questions.
