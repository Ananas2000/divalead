# Rendering and measurements

The WAV was rendered by the user's actual Diva rev16519 under Wine, then processed by the compiled Windows x64 VST2 `Diva_Lead_Finish_v8_x64.dll` under Wine. The original Diva binary is not redistributed. FL Studio and subjective listening were not performed. The original preset/effects are unknown.

V8 changes the saved ADS envelope, note velocities and articulation. Native Diva FX2 is Plate2 at Wet 1%. The custom finish applies compensated tanh, 11 differential EQ filters, three stationary allpasses per channel, five common EQ filters, a high-passed three-tap fractional chorus send and two bell filters on the Side signal. The linked transient stage was tested and rejected; its selected AttackAmount/ReleaseAmount constants are both zero, so that stage is an identity. No reference sample, note-specific audio equalization or prerecorded lead is embedded in the effect. Amount/Output persist in state chunks. V8 has a distinct VST ID and zero buffer latency.

Build with x64 MinGW:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v8_x64.dll lead_finish.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o fx_render_host.exe fx_render_host.c -lm
x86_64-w64-mingw32-gcc -O2 -static -Wl,--no-insert-timestamp -o diva_vst2_host.exe diva_vst2_host.c -lm
```

The effect test host accepts stereo IEEE float32 WAV and optional block size, Amount 0…1, Output dB and stopped-host preroll block count. Every invocation checks the state chunk:

```sh
ffmpeg -i ../Diva_v8_DIVA_ONLY.wav -c:a pcm_f32le input_float.wav
fx_render_host.exe Diva_Lead_Finish_v8_x64.dll input_float.wav output.wav
```

The published input WAV uses PCM24. Its rounding causes a small difference from the float32 input used for engine verification. The final DLL's default Output is 1.852506397 dB.

The separate synth host takes the Diva binary path and H2P path as its command-line arguments. It accepts stdin commands `pattern 8 0 REPEAT`, `timing SWING GATE`, `stepvel V1 ... V8`, `stepgrid O1 ... O8 G1 ... G8`, `render PATH` and `quit`. Offsets O are beats; gates G are fractions of a half-beat. Use values from `render_timing.json`. Source `stepgrid` is new in v8. The host checks ranges and finite values. MIDI PPQ 16000 represents each sample at 48 kHz/180 BPM before tempo's integer-microsecond rounding. A loaded preset is warmed before the first note. Two fresh loads of the final H2P produced identical audio. Under Linux execute Windows binaries through Wine.

Independent measurements need no plugins or Wine:

```sh
python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python compare.py
```

The same fixed spectrum, 12/24 ms RMS envelope, body-level and tail windows are used for both versions. A single RMS gain matches the full reference span. Full-length candidate WAVs are retained during envelope filtering to preserve boundary conditions. Harmonic stereo compares 16 fixed 55–145 ms windows, harmonics 1–12, FFT8192 and summed complex L/R cross power within ±max(7 Hz, harmonic×0.45 Hz), weighted by reference power^0.65. This measures interchannel phase rather than common oscillator phase.

V8 improves band/aggregate stereo width, harmonic balance, steady/whole spectrum and envelope/body-level errors against v7. V7 retains a small harmonic phase advantage. These measurements are not perceptual percentages; full identity is not established. The native ARP up+dn 2/two-octave/1x/1/8 combination reproduced the observed pitches from three held notes, but its tested dynamics/timbre were less accurate than the selected eight-event performance.
