# Listener-directed v19 WIP

The listener described v17 as very close but the original as slightly wider, less compressed and less noisy. Core saturation is reduced by20%, chorus wet by10%; the final five existing Side EQ gains compensate chorus narrowing and modestly widen mid/high bands. Real Diva source parameters, v18 MIDI, eight FIR paths, five dynamic bands and quadratic exciter are unchanged. No new PDC:8320frames48k. No reference recording, MIDI schedule, note table or pitch tracker in runtime. MistaTowa excluded.

Fresh actual-Diva loads, Windows/native/independent preview, block/preroll/rates/silence/bypass/chunks/LR probes pass. This does not establish a perceptual match; no FL Studio or audition was performed here. Primary envelope and note-level metrics regress slightly, and width error rises because the trial deliberately widens the result. All metrics are preserved. Auxiliary inter-harmonic energy measurements address modulation roughness; they are not perceptual noise scores. Both source-video and short protocols remain available.

```sh
python analysis/compare.py
python analysis/fir_design.py
python analysis/dynamic_design.py
python analysis/exciter_design.py
python analysis/roughness_compare.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v19_WIP_x64.dll analysis/lead_finish.c -lm
```

The recipes reproduce131072FIR,69dynamic/Side and6exciter constants without audio. Independent delivered-WAV comparison reproduces52scalar measurements and arrays. Align WITH_PDC before removing latency, then apply reference cuts. Comparison has176064frames and preserves FIR prefix. The original second prefix contains preceding video context; no additional bass is synthesized. Continue after backups.
