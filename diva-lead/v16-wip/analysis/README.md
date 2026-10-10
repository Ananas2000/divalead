# Reproduction and remaining differences

This incomplete WIP retains the saved Diva source, MIDI, eight FIR paths and latency of v15. Three linked causal peaking EQ bands follow the existing FIR/energy stage. Each band's fixed bandpass detector measures stereo energy relative to the total incoming stereo energy. The peaking gain moves toward MaximumGainDB when the relative band energy falls below QuietBandThresholdDB, with a clamped linear transition in dB. Detector and gain smoothing use independent exponential time constants. Both channels share gain decisions. A small five-band Side EQ follows. All runtime processing uses incoming Diva; no recording, note index or MIDI timeline is embedded. Constants are documented in dynamic_eq_settings.json.

The Windows x64 DLL was tested with two fresh identical loads of the supplied real Diva, a native build and an independent post-processing preview. Full checks cover block sizes, stopped preroll, 44.1/48/96/192 kHz, silence, Amount0, VST state chunks and isolated left/right probes. validation.json records actual output errors and all regressions. Native timing is a measurement of this host, not a FL Studio performance claim. FL Studio and subjective listening were not performed. The proprietary Diva binary is excluded.

```sh
PYTHONDONTWRITEBYTECODE=1 python analysis/compare.py
PYTHONDONTWRITEBYTECODE=1 python analysis/fir_design.py
PYTHONDONTWRITEBYTECODE=1 python analysis/dynamic_design.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v16_WIP_x64.dll analysis/lead_finish.c -lm
```

FIRs are unchanged from v15: the recursive JSON recipe reproduces all 131072 coefficients without audio. The separate dynamic recipe verifies 19 dynamic parameters and five additional Side gains. Independent WAV comparison reproduces every scalar and array in the four current/previous short/continuous cases. Comparisons preserve the FIR prefix by aligning WITH_PDC before removing latency. Each comparison is 176064 frames. External cuts and zero tails are editing results. The second reference prefix includes already sounding preceding source-video audio; no sample or assumed instrument is inserted. MistaTowa is excluded. Harmonics and transitions remain different; measured gains are not perceptual percentages.
