# v27 WIP verification

The supplied actual Diva is the source. Its proprietary binary is not redistributed. The complete Windows finish source and fixed coefficients are included; this is an intermediate checkpoint with a remaining timbre difference.

```sh
x86_64-w64-mingw32-gcc-posix -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v27_WIP_x64.dll analysis/lead_finish.c -lm
x86_64-w64-mingw32-gcc-posix -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe analysis/fx_render_host.c -lm
python -B analysis/compare.py
python -B analysis/roughness_compare.py
python -B analysis/measure_mid_side.py
python -B analysis/verify_spectral.py --fixtures
```

The Windows host accepts `plugin.dll input_float32.wav output.wav [block] [amount] [output_db] [preroll]`, checks chunk state, and prints actual PDC. Use Amount1 and Output+1.8525063970852007 dB. Two actual Diva loads gave identical source WAVs, unchanged from v26; v27 modifies only the input-driven spectral matrix.

Each of its seven rows has four base coefficients and four slopes at500/1400/3500/6000Hz, zero correction at200/8000Hz endpoints. Log-frequency interpolation uses `base+slope*log2(live_f0/100Hz)`. Its live-input crossing estimator accepts45–220Hz, median3 and5ms smoothing; the50ms lookahead fits inside the existing base latency. No original recording, note table or MIDI schedule is accessed at runtime.

The harmonic distance mask has sigma .23 of the live fundamental. Hann analysis and synthesis use overlap normalization. Window size is `8*round(sampleRate*(4096/48000)/8)`, hop window/8, FFT the next power of two. This is fused into the same causal spectral stage as v26, with the same total PDC12416@48k,11414@44.1k,24704@96k,49280@192k. Future input is not accessed; state resets with transport or sample rate. The other FIR, dynamics, excitation, chorus and ten tracked peaks retain v25 settings.

`verify_spectral.py` checks all56 matrix coefficients, anchors, mask width and key law. It compiles a temporary component library outside the checkout and compares12 arbitrary input/rate cases and causal prefixes with a separate SciPy implementation. `--fixtures` also compares the actual Windows output using the repository's adjacent v25 before-spectral WAV; without that flag the checks work from the standalone ZIP. `spectral_independent_checks.json` additionally records the independent entire base-plus-spectral calculation.

Align the full continuous render using `with_pdc[12416-819:]`, preserving pre-ringing. Then copy first64041frames and source128007:192049 into destination112022:176064. See `reference_edit.json`. Those external cuts and A/B whole-fragment normalization are not synth/effect processing.

The delivery retains slight envelope regressions and remaining harmonic/M/S differences. Metrics are not listening scores; no listening or FL Studio validation is claimed. `research_selection.json` records the key-only trial, four mask-width refits and the final joint coefficient model. Earlier metadata and sources for unchanged base components remain for reproducibility.
