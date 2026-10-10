# V10 intermediate reconstruction

This remains a WIP, not an exact match. The user-provided Diva plugin is not redistributed. The preset, performance, real WAV renders, Windows finish DLL and its source are included. No lead recording is embedded in the effect.

Build from this directory with MinGW:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o ../Diva_Lead_Finish_v10_WIP_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o diva_vst2_host.exe diva_vst2_host.c -lm
```

Use the synth host with the user's plugin and saved H2P. For fresh-load verification, do not override the loaded parameters. Set pattern 8, transpose 0, repeat 6.9913662341136575, swing 0.008518760579291153 and the velocities, offsets and gates in render_timing.json. The host sample rate is 48000; float32 stereo output is used by the effect host.

The effect reports 4224 frames of latency at 48 kHz (4096 FIR + 128 partition). Remove that latency and add the separate 843-frame reference alignment for measurement. Live DAWs should use reported plugin delay compensation. Amount 0 preserves delayed dry audio at Output gain. The DLL has its own VST ID and checks state chunks against it.

fir_design.make_v10_kernels(fir_target_curve, Finish_settings['fir']) reproduces the fixed coefficients. General common phase and amplitude corrections are applied to the v9 FIR. No note-index, timeline or reference sample is used at runtime. FIR resampling preserves the correction's physical frequency range and the delayed identity above it.

Independent measurements:

```sh
python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python compare.py
```

All fixed windows and normalization are unchanged from v8/v9. validation.json records real Windows renders, reproducibility and the small spectral/phase tradeoffs against v9. FL Studio and subjective listening were not performed. The original preset and effect chain remain unknown.
