# Rendering and independent measurements

This is an intermediate v9 checkpoint, not an exact match. The original Diva binary is provided by the user and is not redistributed. Source and saved preset are included; no original lead sample is embedded in the effect.

Build Windows x64 binaries with MinGW from this directory:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o ../Diva_Lead_Finish_v9_WIP_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o diva_vst2_host.exe diva_vst2_host.c -lm
```

Run the synth host under Wine with the user's Diva plugin path and `../Diva_Lead_v9_WIP.h2p`. Use render_timing.json values for step velocities, offsets and gates, plus swing 0.008518760579291153 and pattern 8 / transpose 0 / repeat 6.9913662341136575. Fresh preset verification must not overwrite the loaded parameters with `set` commands.

The effect host consumes IEEE float32 stereo WAV. It checks the state chunk on every invocation. The effect reports 4224 latency frames at 48 kHz (4096 filter + 128 partition); remove exactly that delay for reference comparison, then add the documented 843-frame reference alignment. Live DAWs should use the plugin's reported latency rather than manually shifting audio.

fir_design.py and fir_target_curve.json reproduce the kernels; controls are saved in Finish_settings.json. Resampling the correction preserves its physical frequency response while retaining a delayed identity outside its band. fir_finish.h implements uniform partitioned convolution. Amount 0 returns delayed dry audio at the selected Output gain. Silence and stopped-host preroll are verified.

Independent measurements, from this directory:

```sh
python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python compare.py
```

The same fixed v8 windows, level normalization and harmonic stereo measurement are retained. No listening or FL Studio validation was performed. Read validation.json for passed checks and remaining discrepancies.
