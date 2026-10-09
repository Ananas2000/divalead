# Rendering and measurements

The delivered final WAV was rendered by the user's Diva revision 16519 under Wine, then processed by the actual compiled Windows x64 VST2 `Diva_Lead_Finish_v5_x64.dll` under Wine. The original Diva binary is not included. The effect is our implementation, not a claim that this processor appeared in the source video.

`lead_finish.c` contains five broad peak EQ filters, low-band phase modulation, and three high-passed fractional chorus delay taps per channel. `tuned_settings.h` supplies the fitted constants; `Finish_settings.json` in the parent folder records their values. The effect exposes Amount and Output. Its state chunk stores these controls; processing coefficients are part of this version of the effect.

Build with an x64 MinGW C compiler:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v5_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
```

The test host accepts stereo **IEEE float32 WAV**. Convert the delivered dry PCM24 WAV to float32 without other processing:

```sh
ffmpeg -i ../Diva_v5_DIVA_DRY.wav -c:a pcm_f32le input_float.wav
fx_render_host.exe Diva_Lead_Finish_v5_x64.dll input_float.wav output.wav
```

On Linux, run the executable through a Windows x64 Wine installation. Host arguments after output are optional block size, Amount (0…1), Output dB, and the number of simulated stopped-host preroll blocks. Each run checks a state-chunk save/load round trip before rendering. The effect resets its modulation and filter state when the transport starts playing or jumps backward. A stopped preroll followed by Play was verified to reproduce the fresh-start output bit for bit.

Independent audio measurements need no plugin or Wine:

```sh
python -m pip install -r requirements.txt
python compare.py
```

Measurements compare power-spectrum distributions, note-level variation and L/R correlations. They are not perceptual percentages. The combined optimization score in `validation.json` is a selection criterion, not an absolute measure of sound quality. Whole-spectrum change is modest; the major measured improvement is the stereo spectrum. Some dynamics and attack differences remain. FL Studio execution and subjective listening were not available here.
