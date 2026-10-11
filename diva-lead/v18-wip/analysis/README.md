# Reproduction and remaining differences

This is an incomplete WIP. The real supplied Diva preset retains v17 parameters. Continuous VIDEO MIDI refines the two phrases separately; the short protocol retains v17 MIDI to isolate the DSP change. Six fixed constants describe a complex resonator and stereo quadratic harmonic exciter after the unchanged v17 finish. It generates harmonics only from incoming audio, with a 10 Hz DC-removal filter. Experimental energy recovery is disabled and omitted. No recording, MIDI timeline, note table or pitch tracker is present. MistaTowa is excluded. FIRs, five dynamic bands, twenty Side biquads and 8320-frame latency remain unchanged.

Windows matches two fresh Diva loads, the native build and an independent preview. Block sizes, stopped preroll, 44.1/48/96/192 kHz, silence, Amount0, chunks and isolated L/R probes passed. No FL Studio or listening validation was performed. The proprietary Diva binary is excluded.

```sh
python analysis/compare.py
python analysis/fir_design.py
python analysis/dynamic_design.py
python analysis/exciter_design.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v18_WIP_x64.dll analysis/lead_finish.c -lm
```

The unchanged recursive v17 FIR recipe reproduces 131072 coefficients without audio. Dynamic constants and six excitation constants also reproduce bit-exact. Independent WAV comparison reproduces all52scalar measurements and arrays. Align WITH_PDC before removing latency to preserve the prefix, then apply external reference cuts. Each comparison contains176064frames. Previous-v17 exports are bit-identical.

Most continuous errors improve modestly; note body levels improve from.076382 to.061200dB. FFT-window level spread and five-band width regress. The separate short benchmark is mixed. Both full comparisons are retained. These are not perceptual percentages and do not establish an exact match. The second reference prefix contains preceding source-video audio. Keep the full benchmark; no additional bass is synthesized. Continue harmonics and transitions after this backup.
