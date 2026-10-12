# v29 WIP verification

The supplied actual Diva source and MIDI remain unchanged28. The proprietary binary is not redistributed. This is a WIP with remaining timbre differences.

```sh
x86_64-w64-mingw32-gcc-posix -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v29_WIP_x64.dll analysis/lead_finish.c -lm
x86_64-w64-mingw32-gcc-posix -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe analysis/fx_render_host.c -lm
python -B analysis/compare.py
python -B analysis/measure_crest.py
python -B analysis/roughness_compare.py
python -B analysis/measure_mid_side.py
python -B analysis/verify_spectral.py --fixtures
```

The host accepts `plugin.dll input_float32.wav output.wav [block] [amount] [output_db] [preroll]`, verifies VST chunk state and reports PDC. Use Amount1 and Output+1.8525063970852007dB.

The previous56 base/key-slope coefficients and six common phase angles remain. An additional32 coefficients form eight upper-band matrix rows on anchors3500/4500/6500/9000/11000/14000Hz, with zero correction at endpoints. Rows: offMid gain, offSide gain, real/imaginary Side->Mid, real/imaginary Mid->Side, harmonicMid gain, harmonicSide gain. They act after the base matrix/common phase within the same FFT, using the same live-input Gaussian distance mask sigma.23. Frequency curves are cached per sample rate, while the harmonic mask follows live input. No original, MIDI schedule or note table is read at runtime.

Window remains4096/hop512@48k; scaled window is8*round(sampleRate*(4096/48000)/8), hop window/8, FFT next power of two. Total causal PDC remains12416@48k,11414@44.1k,24704@96k,49280@192k. State resets with transport/sample rate. Earlier FIR/dynamics/excitation/chorus/ten tracked peaks retain v25 settings.

The portable verifier checks all94 spectral coefficients, anchors, key law and mask width, builds outside the checkout, and independently compares12 arbitrary input/rate cases and causal prefixes. --fixtures also checks actual Windows audio using adjacent v25 before-spectral fixtures. Without that flag the verifier works from the standalone ZIP. spectral_independent_checks.json records a separate entire SciPy pipeline as well.

Preserve pre-ringing: align full-PDC[12416-819:], then apply the cuts in reference_edit.json. A/B RMS matching uses whole segments. Editing and normalization are outside DSP.

The upper nominal-mask Mid/Side statistics improve substantially, while weighted window error slightly regresses. Those statistics include modulation/drift/transition/codec context and do not isolate hiss or prove perceptual quality. No audition or FL Studio claim.

research_selection.json records narrow24/wide32 fits, the187 actual-Diva source pass, seven native-chorus replacements with the synthesized chorus disabled, and AAC diagnostics. These alternatives were retained privately because their tone/phase/dynamic gains were mixed or worse; source28 remains. Work continues.
