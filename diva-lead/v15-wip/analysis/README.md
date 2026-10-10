# Reproduction and limits

This incomplete WIP continues v14 using the same saved Diva source and linked-energy core. Additional 40-band smooth common EQ is fit to both all active STFT frames and fixed note windows. A simultaneous side correction restores the five-band width measure. All processing is folded into the two audible FIR outputs; the two detector outputs still process the incoming signal with the v12 matrix. No reference recording, MIDI timeline or note-specific processing is embedded. Eight paths, 16384 taps and8320-frame latency at48 kHz are unchanged.

Two fresh loads of the supplied genuine Diva H2P produced identical six-second source WAVs, matching v14 input. The proprietary Diva binary is excluded. The compiled Windows DLL is checked against a native build and the independent convolution preview; validation.json records errors, blocks, preroll, rates, silence, delayed dry at Amount 0, VST chunks and isolated L/R probes. FL Studio and subjective listening were not performed.

Install requirements.txt and run:

```sh
PYTHONDONTWRITEBYTECODE=1 python analysis/compare.py
PYTHONDONTWRITEBYTECODE=1 python analysis/fir_design.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v15_WIP_x64.dll analysis/lead_finish.c -lm
```

The recipe reconstructs the v10-v14 base and additional v15 filters from JSON, reproducing all 131072 coefficients bit-exact without audio. Independent WAV measurements cover both continuous/cut and short-pattern versions, each 176064 frames. Proper alignment preserves the FIR prefix by aligning WITH_PDC before any latency crop. VIDEO_DIVA_ONLY is six seconds of genuine Diva with repeat 8 beats; VIDEO is latency-compensated; VIDEO_REFERENCE_EDIT applies external cuts. Zero tail is an editing result. FINAL naming follows prior packages and does not mean a finished match. The second reference extract starts while preceding audio is still sounding; that source-video prefix is not inserted as an invented instrument or sample. The intervening instrument is unestablished; MistaTowa remains excluded. Full reference metrics retain that prefix, without silently masking it.

All gains and regressions relative to v14 are recorded in validation.json. The fit balances stationary spectrum, whole-fragment spectrum and stereo width. All metrics and the separate short-pattern comparison are retained; they are not perceptual percentages. Harmonic and transition differences remain.
