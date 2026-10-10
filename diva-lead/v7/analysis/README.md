# Rendering and measurements

The final WAV was rendered by the user's actual Diva revision 16519 under Wine, followed by the actual compiled Windows x64 VST2 `Diva_Lead_Finish_v7_x64.dll` under Wine. No original Diva binary is redistributed. FL Studio and subjective listening were not performed; the original preset and effects remain unknown.

V7 changes the saved Diva core and note velocities. Its own finishing DSP applies compensated tanh, 11 differential EQ filters (opposite gains in each channel), three stationary allpasses per channel, five common EQ filters, and a high-passed three-tap fractional chorus send. `Finish_settings.json` and `tuned_settings.h` contain all constants. The old V6 low-frequency phase LFO is removed. There is no buffer latency. Amount and Output persist in the state chunk; V7 has a distinct VST ID.

Build with an x64 MinGW C compiler:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v7_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
```

The effect test host accepts stereo IEEE float32 WAV, with optional block size, Amount 0…1, Output dB and stopped-host preroll block count:

```sh
ffmpeg -i ../Diva_v7_DIVA_DRY.wav -c:a pcm_f32le input_float.wav
fx_render_host.exe Diva_Lead_Finish_v7_x64.dll input_float.wav output.wav
```

Under Linux use Wine for both commands that execute Windows binaries. Each host run checks the state chunk. Starting playback or seeking backward resets filters, buffers and LFO phase. Blocks 512/93 and 300 stopped blocks before Play produce bit-identical outputs.

`diva_vst2_host.c` is the separate synth host source. It accepts `pattern`, `timing`, `lastgate` and `stepvel`. The actual uploaded Diva exposes VSTPluginMain despite its .vst3 suffix. The final synth was loaded twice from the saved H2P and produced identical float output. Diva rounds parameters on save; fitting calculations used a fresh load of that rounded preset. The earlier optimizer's waveform differs, and that difference is recorded in validation rather than hidden.

Independent measurements need no plugins or Wine:

```sh
python -m pip install -r requirements.txt
python compare.py
```

Spectral distances use the previous published fixed windows and normalized power distributions. Dynamics uses 12/24 ms RMS envelopes, with a single reference-span RMS normalization, fixed body windows 45–120 ms after each of 16 nominal note starts, and a 1.337–1.450 s tail window. Candidate audio is kept at full length for envelope filtering to preserve boundary conditions.

`harmonic_stereo.py` compares fixed 55–145 ms note windows, harmonics 1–12, FFT8192 at 48 kHz. Complex L/R cross power is summed within ±max(7 Hz, harmonic×0.45 Hz). Wrapped phase differences and L/R power balance differences are weighted by reference harmonic power^0.65 and normalized across all 16×12 observations. This avoids confusing common oscillator phase with interchannel phase.

V7 is closer by harmonic phase/balance, whole-fragment spectrum, weighted spectrum and note body level measurements. V6 is closer by aggregate/band stereo correlation and steady-window spectral distance. Scores are candidate-selection criteria, not perceptual similarity percentages. The short reference does not establish the original preset or effect chain. The WAV A/B includes both versions at matched whole-fragment RMS.
