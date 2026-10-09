# Rendering and measurements

The final WAV was rendered by the user's Diva revision 16519 under Wine, then processed by the actual compiled Windows x64 VST2 `Diva_Lead_Finish_v6_x64.dll` under Wine. The original Diva binary is not included. This effect is our implementation; the original effect chain remains unknown. FL Studio execution and subjective listening were not performed.

V6 changes Diva's ADS envelope and MIDI gates, and refines the finishing EQ. The effect now also applies a mild compensated tanh saturation before the low-frequency phase modulation, five broad EQ filters and high-passed fractional chorus taps. `Finish_settings.json` records the exact constants; `tuned_settings.h` supplies them to the binary. Amount and Output are saved in a state chunk. V6 has a different VST ID from V5, so both versions can coexist.

Build with an x64 MinGW C compiler:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v6_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
```

The test host accepts stereo **IEEE float32 WAV**. Convert the delivered dry PCM24 WAV without additional processing:

```sh
ffmpeg -i ../Diva_v6_DIVA_DRY.wav -c:a pcm_f32le input_float.wav
fx_render_host.exe Diva_Lead_Finish_v6_x64.dll input_float.wav output.wav
```

On Linux, run through a Windows x64 Wine installation. Optional host arguments after output: block size, Amount (0…1), Output dB, simulated stopped-host preroll blocks. Each run checks a state-chunk round trip. Starting playback and seeking backward reset modulation/filter state. A stopped preroll followed by Play was verified to reproduce the fresh-start output bit for bit.

`diva_vst2_host.c` is the source of the separate host used to execute the user's Diva. It accepts `pattern`, `timing`, `lastgate` and `stepvel` commands. It expects the actual Windows VST2 Diva binary supplied by the user, despite that uploaded binary's `.vst3` suffix. No synth binary or compiled host executable is redistributed.

Independent audio measurements need no plugin or Wine:

```sh
python -m pip install -r requirements.txt
python compare.py
```

The envelope errors use fixed 12/24 ms RMS windows and are normalized by the reference RMS. Body levels use the same 45…120 ms windows after each nominal note start for both versions; the errors are in dB. The tail metric is RMS from 1.337…1.450 s divided by reference RMS. Spectral power distances and channel correlations describe other aspects of the comparison. These measures are not perceptual percentages. V6 improves envelope/body/tail measurements; V5 retains a slight advantage in whole-fragment spectral distance. Both comparisons are included, rather than declaring an exact match.
