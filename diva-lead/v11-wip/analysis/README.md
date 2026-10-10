# V11 intermediate reconstruction

This is a WIP, not an exact match. The preset, genuine Diva renders, Windows finish DLL and source are included. The user-provided Diva binary is not redistributed. No lead recording or performance timeline is embedded in the finish effect.

Build with MinGW from this directory:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o ../Diva_Lead_Finish_v11_WIP_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o diva_vst2_host.exe diva_vst2_host.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o diva_vst2_host_6s.exe diva_vst2_host_6s.c -lm
```

Load the saved H2P without overriding its parameters; use render_timing.json or render_timing_VIDEO.json. The former is the earlier reference-comparison sequence, the latter the uninterrupted eight-beat source phrase spacing. The six-second host is needed for VIDEO. The effect host takes DLL, input WAV, output WAV, block size, Amount, Output dB and preroll count.

The effect reports 8320 frames at 48000 Hz (8192 FIR +128 partition). Remove this latency for exported comparison files, then apply the separate 843-frame alignment only for the reference. DAWs should use plugin delay compensation. Supported sample rates: 8000 through192000 Hz; the partition and dry-delay capacities cover this range. Amount0 and bypass preserve delayed dry audio. This DLL has its own VST ID and rejects other versions' state chunks.

The kernel is the v10 general FIR followed by a power-preserving L/R phase/balance correction and a common EQ. Five broad post-FIR side biquads restore bandwidth correlations. fir_design.make_v11_kernels with base_v10_curve.json, base_v10_settings.json['fir'] and selected_candidate.json reproduces fir_kernels.h exactly, without source audio. The runtime has no note-index correction or sample playback.

```sh
python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python compare.py
PYTHONDONTWRITEBYTECODE=1 python fir_design.py
```

Fixed measurement windows and normalization remain identical to v8-v10. validation.json uses final WAVs from fresh preset loads and the real Windows DLL; analysis/measurements.json is independently recomputed from delivered audio. H2P parameter rounding is explicitly recorded. Reference-edit metrics are separate: an edited zero tail must not be attributed to the synth. Subjective listening and FL Studio testing were not performed.
