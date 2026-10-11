# v24 WIP refine upper harmonic color

Listener:23 is closer but still audibly different.24 remains unconfirmed. Refine H13 and add constant-gain H14/H16/H20/H23/H24 peaks; ten peaks total. Source/MIDI, FIR, chorus, saturation, dynamic EQ and excitation remain21–23. Input-derived frequency only, no reference recording, MIDI schedule or note table. Monophonic low lead45–220Hz; median3 crossing estimates plus5ms smoothing, coefficient updates16samples,50ms lookahead within unchanged FIR PDC. No added latency. Not validated for arbitrary polyphony. MistaTowa excluded.

Fresh real-Diva saved-H2P loads, actual Windows/native/independent SciPy and delivered-WAV measurements pass. Harmonic and spectral errors improve modestly; some envelope/stereo metrics regress slightly. No audition, FL Studio validation or completed-match claim.

Recipes retain131072FIR,69dynamic/Side,6exciter and2chorus constants. harmonic_color_design.py verifies31 color/order/Q/lookahead constants and detector settings; harmonic_color_test.py validates the full10-peak cascade on arbitrary60/110/195Hz at44.1/48/96/192k without MIDI. compare.py and harmonic_compare.py read delivered WAVs;24relative harmonics in16identical windows. Offline metrics are not listening quality percentages. roughness_compare.py is an auxiliary mask, not a hiss detector.

Align WITH_PDC before cuts (PDC[7501:] at48k), preserving FIR prefix. VIDEO continuous; VIDEO_REFERENCE_EDIT fixed cuts. A/B normalizes full-segment RMS. Zero gaps/tails are edits. Backup does not end the task.
