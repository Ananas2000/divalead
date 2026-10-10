# Reproduction and limits

This is an incomplete intermediate checkpoint. The main source is the supplied Diva binary, loaded through its exported VST2 entry point by the included Windows host. The Diva binary is not included. The saved H2P was loaded twice into fresh instances; both source WAVs were identical.

The effect is a general processor of the incoming stereo signal: the existing nonlinear/EQ/modulated-chorus/dynamics core followed by a fixed 2×2 stereo FIR. It contains neither a lead recording nor a note timeline. The former post-side IIR is incorporated into the FIR. Processing latency remains 8320 frames at 48 kHz; the FIR now has four paths and approximately doubles the convolution work compared with v11. Off-diagonal resampling retains a zero identity term; diagonal paths retain a delayed identity. Supported rates are8–192 kHz.

Install `requirements.txt`, then run from the checkpoint directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python analysis/compare.py
PYTHONDONTWRITEBYTECODE=1 python analysis/fir_design.py
```

`compare.py` independently reads the delivered WAVs. Both reference-edit comparisons use exactly 176064 frames; extra silence beyond the clip changes envelope boundary behavior and is excluded. `fir_design.py` reproduces all four coefficient arrays from saved filter settings, without reading audio. The recipe was verified bit-exact against the design snapshot. It uses the v10 and v11 base designs, the saved residual diagonal correction, the folded side EQ, and the final output phase/balance and side correction.

Build the Windows effect with a MinGW-w64 x64 compiler:

```sh
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v12_WIP_x64.dll analysis/lead_finish.c -lm
```

`fx_render_host.c` reads stereo float32 WAV, checks chunk save/restore, and exercises a selected block size. Arguments are DLL, input WAV, output WAV, block size, Amount, Output dB, optional stopped-preroll blocks. The supplied DLL and a native build agreed within 5.96e-8. Validation covers 47/127/128/511/512/2048frames, stopped-preroll,44.1/48/96/192kHz, silence, delayed dry at Amount0, and isolated channel impulses through the new matrix paths.

`VIDEO_DIVA_ONLY` is a genuine six-second input with an eight-beat repeat. Processed `VIDEO` removes the reported DLL latency. `VIDEO_REFERENCE_EDIT` applies the externally observed video cuts offline. Its zero tail follows from editing. The short `REFERENCE` MIDI and its `FINAL` WAVs retain the separate earlier reference-pattern convention. No omitted instrument was inserted.

`codec_diagnostic.json` records the HE-AACv2 investigation. The diagnostic used official FDK-AAC v2.0.3 (commit 716f4394641d53f0d79c9ddac3fa93b03a49f278), AOT 29, 32 kbps, stereo PCM16 / 44.1 kHz input, decoded at 48 kHz. Encoder delay 7106 frames at 44.1 kHz matched an independently measured 7734 frames at 48 kHz. Reencoding the calibrated v11 worsened its spectral and stereo errors. This codec is not part of the effect. Original encoder context/settings are unknown.

Spectral and transition differences remain. No subjective listening or FL Studio validation was performed. Measured errors are not perceptual match percentages.
