# Reproduction and limits

This is an incomplete intermediate backup. The genuine supplied Diva was loaded through its exported VST2 entry by the included Windows host; its proprietary binary is excluded. Two fresh H2P loads produced identical six-second source WAVs.

The general effect consists of the nonlinear/EQ/modulated chorus/linked transient core and an eight-path FIR. Two matrix outputs carry the audible corrected signal; two carry the unchanged v12 filtered signal used only as an energy detector. Their linked stereo RMS energies are smoothed by a2 ms EMA. The audible channels receive the same exp(clamp(0.5*log((E_detector+epsilon)/(E_audible+epsilon)), +/-0.45)) gain. The detector processes the same incoming Diva signal. There is no lead recording, MIDI timeline, reference-audio lookup or note-specific processor in the DLL. Gain matching adds no latency. FIR latency remains8320 frames/173.33 ms at48 kHz. Eight paths double convolution work relative to v12; validation.json records a local six-second native processing time, including setup. This is not a FL Studio performance test.

Install requirements.txt and run:

```sh
PYTHONDONTWRITEBYTECODE=1 python analysis/compare.py
PYTHONDONTWRITEBYTECODE=1 python analysis/fir_design.py
x86_64-w64-mingw32-gcc -O2 -shared -static -Wl,--no-insert-timestamp -o Diva_Lead_Finish_v13_WIP_x64.dll analysis/lead_finish.c -lm
```

The filter recipe reproduces all131072 coefficients bit-exact from general saved EQ/stereo filter parameters without reading audio. compare.py reads the delivered WAVs independently. Both continuous and short-pattern comparisons use176064 frames, preserving the FIR prefix by aligning the original WITH_PDC output before any latency crop. Previous-v12 comparison WAVs were reexported from unchanged v12 outputs with this corrected alignment. This export fix is separate from the DSP improvement; published v12 files are untouched.

fx_render_host.c reads stereo float32 WAV, checks VST chunk save/restore and supports DLL,input,output,block size,Amount,Output dB,optional stopped-preroll. Checks cover47/127/128/511/512/2048 blocks,stopped-preroll 3/17,44.1/48/96/192 kHz,silence,Amount 0 delayed-dry and isolated-channel probes. Native/Windows/preview differences are recorded in validation.json.

VIDEO_DIVA_ONLY is genuine continuous six-second Diva with repeat 8 beats. VIDEO removes the reported latency; VIDEO_REFERENCE_EDIT applies only externally observed video cuts. Its zero tail is an editing consequence. FINAL files retain the prior short reference-pattern naming convention and do not mean a finished reconstruction. MIDI files keep velocity and timing. The omitted intervening instrument is unknown and excluded; MistaTowa was never used. No subjective listening or FL Studio test was performed. Spectral, phase and transition differences remain; these errors are not perceptual percentages. codec_diagnostic.json is inherited evidence, not a codec installed in the effect.
