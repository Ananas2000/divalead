# Analysis of v43 WIP

Actual supplied Diva source/MIDI/all281parameters are identical42. Existing352spectral coefficients are unchanged; adaptive69target coefficients define23smoothrelativepower curves acrossliveinputfundamental45–220Hz. Strength.25, logEMA20ms, desired6dBclampBEFOREstrength(actual1.5dB), relativefundamental-normalizedquadratic andstablepositive root. Silence/zero fundamental doesnotgenerate audio. No source audio, MIDI grid ortime lookup inprocessor. C dynamic_log_gain[23] state is serializedwiththe existingstatechunk; no extraPDC.

Existinglast5Side-filter gains changed afteradaptivecontrol; no newbank. New148independentprebase (separate43core/SciPyFIR/energy/Side/dynamics/exciter/tracker10SOS) verifiedbeforeactualWindows; old31fixture isinvalid forthis preSideconfiguration. PublicDiva_v43_BEFORE_SPECTRAL.wav isactualWindows withupdatedSidebank. independent_spectral_ms.py computes the static andadaptive stageusingNumPy/SciPySTFT, vectorizedpower reductions andlfilterEMA.

verify_spectral.py --fixtures checksall421constants, controls, recipes,12arbitraryinputcases atfour rates, changingfutureinput prefix independence andactualDiva fixture. Fullindependentpipeline error is recordedin spectral_independent_checks.json. Scale invariance fixdiagnostic is recordedin research_selection.json: oldabsoluteunit gate caused8.256e-7scale error; normalizedrelativeunits fixed it to4.44e-16. No tolerance was increased.

Allmixed regressions are documented. Measured distances are not perceivedsimilarity percentages, exactpitch orisolated hiss. Model auditory input unsupported; no audition/FL StudioGUI claim. ProvidedDiva binary excluded. Match remainsopen.
