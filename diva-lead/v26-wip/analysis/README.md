# v26 WIP verification

The supplied actual Diva is the source. This directory contains the complete Windows finish source and fixed filter coefficients, not a recording or a MIDI schedule. The proprietary Diva binary is not redistributed.

Build with the configured MinGW compiler:

```sh
x86_64-w64-mingw32-gcc-posix -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v26_WIP_x64.dll analysis/lead_finish.c -lm
x86_64-w64-mingw32-gcc-posix -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe analysis/fx_render_host.c -lm
```

The host accepts `plugin.dll input_float32.wav output.wav [block] [amount] [output_db] [preroll]`, checks the VST chunk roundtrip, and prints the reported PDC. Use Amount 1 and Output +1.8525063970852007 dB.

```sh
python -B analysis/compare.py
python -B analysis/roughness_compare.py
python -B analysis/fir_design.py
python -B analysis/dynamic_design.py
python -B analysis/exciter_design.py
python -B analysis/chorus_design.py
python -B analysis/harmonic_color_design.py
python -B analysis/return_damp_design.py
python -B analysis/verify_spectral.py --fixtures
```

The FIR, dynamic EQ, excitation, chorus and ten tracked peaks are unchanged v25 components. `spectral_ms.h` adds a causal, input-pitch-driven spectral M/S matrix after those components. `spectral_ms_settings.h` has seven rows of four fixed coefficients on frequency anchors 200/500/1400/3500/6000/8000 Hz, with zero correction at the endpoints. The Gaussian distance mask has sigma 0.23 of the live fundamental. The estimator accepts 45–220 Hz and holds its last estimate outside that range.

`verify_spectral.py` builds its temporary component library outside the checkout, verifies the fixed constants, and independently checks all twelve arbitrary signals and causal prefixes. `--fixtures` also compares the new stage against the actual Diva/Windows fixtures and requires the repository's adjacent v25 folder. Without that flag the component checks work from the standalone ZIP.

The window is `8*round(sampleRate*(4096/48000)/8)`, hop window/8, FFT the next power of two. Hann analysis and synthesis use overlap normalization. The complete window is added to the previously reported base PDC; at 48 kHz total PDC is 12416 frames. No future input is accessed. State resets with transport or sample rate. `independent_spectral_ms.py` uses separate SciPy filters and STFT/ISTFT; `spectral_independent_checks.json` records twelve arbitrary-input cases, causal-prefix tests and the independent complete-pipeline comparison.

Align the full continuous render using `with_pdc[12416-819:]` before the fixed reference cuts. Preserve pre-ringing. The first slice is 64041 frames; the second source slice 128007:192049 is copied to 112022:176064. Neither the cuts nor level normalization are part of the synthesizer or effect. The root `reference_edit.json` records this explicitly.

Audio and measurements are an intermediate backup. No listening or FL Studio validation is claimed. Slight harmonic/balance/coherence regressions are retained, and the perceptual target remains open.
