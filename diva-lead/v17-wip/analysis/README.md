# Reproduction and remaining differences

This is an incomplete WIP. Real supplied Diva is rendered from the saved H2P with FineTune +1.02 cents and explicit MIDI. Five linked input-driven quiet-band peaking EQs follow eight general stereo FIR paths and linked energy matching. A small fixed opposite phase response for L/R is embedded in the audible FIRs; the four detector paths are unchanged. Four sequential five-band static Side EQ stages follow. Latency remains 8320 frames at 48 kHz. Runtime contains no recording, note-index table or MIDI timeline. MistaTowa is excluded.

The Windows x64 DLL matches two fresh identical Diva loads, a native build and an independent processing preview. Block sizes, stopped preroll, 44.1/48/96/192 kHz, silence, Amount0, chunks and isolated L/R probes passed. These are host measurements; FL Studio and subjective listening were not performed. The proprietary Diva binary is excluded.

```sh
python analysis/compare.py
python analysis/fir_design.py
python analysis/dynamic_design.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v17_WIP_x64.dll analysis/lead_finish.c -lm
```

The recursive fixed JSON recipe reproduces all 131072 FIR coefficients without audio. v17_filter_settings.json contains the already scaled relative phase coefficients; do not multiply by a diagnostic amount again. dynamic_eq_settings.json reproduces 29 dynamic parameters and 20 Side gains/frequencies. Independent WAV comparison reproduces every scalar and array in the four short/continuous current/previous cases. Comparisons align WITH_PDC before removing latency, preserving the prefix, and contain 176064 frames. v16 comparison exports remain bit-identical.

The main continuous source-video edit improves all primary error measurements versus v16; its FFT-window level spread regresses slightly. The separate short seven-beat-repeat benchmark regresses in spectrum, envelopes, levels and width. See both complete comparisons in validation.json and Knobs_FL_Studio_RU.md. Zero tails follow from external editing. The second reference prefix includes preceding source-video audio, which is retained in the benchmark and excluded from the lead synthesis. Harmonics and transitions still differ. Metrics are not perceptual percentages.
