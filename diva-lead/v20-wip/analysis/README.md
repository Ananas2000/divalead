# Listener-directed v20 WIP

The listener described v17 as very close but the original as slightly wider, less compressed and less noisy. V19 saturation/chorus settings are retained. The Mid contribution of the chorus is reduced by10%, Side unchanged; final five existing Side gains are refitted to preserve19 width. No additional filters or latency. Real Diva source parameters, v19 MIDI, eight FIR paths, five dynamic bands and quadratic exciter are unchanged. No new PDC:8320frames48k. No reference recording, MIDI schedule, note table or pitch tracker in runtime. MistaTowa excluded.

Fresh actual-Diva loads, Windows/native/independent preview, block/preroll/rates/silence/bypass/chunks/LR probes pass. This does not establish a perceptual match; no FL Studio or audition was performed here. Envelope, note levels, whole-spectrum distance and phase regress slightly; window-spectrum distances improve. The trial preserves19 wider target. Inter-harmonic fractions decrease another~11%; this is not a listening quality percentage. All metrics are preserved. Auxiliary inter-harmonic energy measurements address modulation roughness; they are not perceptual noise scores. Both source-video and short protocols remain available.

```sh
python analysis/compare.py
python analysis/fir_design.py
python analysis/dynamic_design.py
python analysis/exciter_design.py
python analysis/chorus_design.py
python analysis/roughness_compare.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v20_WIP_x64.dll analysis/lead_finish.c -lm
```

The recipes reproduce131072FIR,69dynamic/Side and6exciter constants without audio. Independent delivered-WAV comparison reproduces52scalar measurements and arrays. Align WITH_PDC before removing latency, then apply reference cuts. Comparison has176064frames and preserves FIR prefix. The original second prefix contains preceding video context; no additional bass is synthesized. Continue after backups.
