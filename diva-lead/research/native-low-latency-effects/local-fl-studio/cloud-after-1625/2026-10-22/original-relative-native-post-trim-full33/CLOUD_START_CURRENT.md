# Diva original reference: current native13 / two-ZL cloud startup

Continue Ananas2000/divalead main in the existing /workspace/divalead checkout.
No additional worktree. User wants actual renders and matching on three held
incoming notes per phrase, ordinary FL20 effects, sustained work until a real
resource/service limit or convincing match. No MistaTowa, no v83/Finish target,
no per-trial questions or ending the turn claiming background work. Quota% is
not exposed: do not invent15%; save completed useful work promptly. User has
authorized normal Git pushes, complete WIP/FL20 guides, internet-compatible
plugins, and reclaiming recoverable local duplicate files.

Paths:
P=/workspace/divalead
N=/workspace/divalead-work/native-low-latency-effects
A=/workspace/divalead-work/pc-stereo-20261024
H=/workspace/divalead-work/stereo-refinement-20261026
OLD=/workspace/divalead-work/stereo-refinement-20261025
R=/workspace/divalead-work/three-held-continuation
B=/tmp/divalead-local-1625
D=/tmp/divalead-local-1625/internet-plugins-20261023
W=/tmp/divalead-native-effects
S=/workspace/divalead-setup
PY=/workspace/.venvs/divalead/bin/python
PUBLIC=P/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22

Inspect actual Git HEAD/status, PUBLIC/README_RU.md and BEST before using a
snapshot below. Preserve existing work; no force push/reset. Latest complete
kit33: PUBLIC/ZL-WIP33/Diva_ZL33_STEREO_WIP_complete.zip SHA256
ee7d5d7dd189deddeb20a5b6b785879738969c84365caef7c66c91daed03a324.
Read ZL33_CONTINUATION_RU.md and FL_STUDIO_RU.md. Not a full sound match.

REQUIRED topology: Diva -> original native12/base10/WS52 -> PRIMARY ZL2 ->
POST ZL2 -> NEW native Fruity Stereo Shaper POST TRIM. Exactly TWO official
ZL Equalizer2v1.4.1 minimum-phase/lookahead0/AutoGainOFF. Total13native effects;
last native trim is AFTER the secondZL, not in the original native12 prefix.
Original native12/Diva281/MIDI/ARP/ADSR/routes unchanged. Input notes41,37,36
twice, sixnote-ons/12events. InternalARP creates upper jumps. No old Finish.

Original target P/diva-lead/v83-wip/Diva_original_lead_reference.wav SHA256
7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f.
Directory v83 is only a storage location, not an instruction to match v83.
Source N/source-bases/FL05_OscMix_6p5; h2p SHA256
 da2471b5684fcf2614fa309020db606bfcaac0fb4ff843e80512b941c8e51f1c.
Never mix reference samples into synthesis or replace three held notes.

PRIMARY now keeps RelativeON in existing Side dynamicband21 plus the saved
joint refit; actual610dump/component bytes are authoritative. POST same32,
SHA256460cc43537b391236b3e8821910eede427bb6334bcce64e6e4f7be03a84e985d:
SideAP10207.6/Q2.198,2149.8/Q4.702,930/Q11.336; StereoAP782.9/Q20.561;
LeftPeak994/Q5.871/-1.70dB. NativePOSTtrim raw[0,12769,12800,0,0,0], Left
requested-.035dB/Rightunchanged, stateSHA256
31944f3ceca30f54f1b66643f738eb37583e690d9d0846556ef330e2d7e40f66.
StereoShaper paramorder R->L,L->L,R->R,L->R,delayL,delayR; do not guess
[Left,0,0,Right]. Actual isolated DLL calibration, unity5.96e-8, six gains
<=2e-7, impulse no crossfeed/added delay0, cold save/resave0 were executed.
The renderer uses actual original DLL; other isolated host nodes bypassed.
No custom DSP replacement or plugin is needed in FL Studio.

Native10 schema B/fl20_curve.py must support high4 on top of48coordinates;
ordinary WaveShaper FST contains129points. Install verified published runtime
if missing/stale, preserving different current work until reviewed. Assert
native_dsp_settings_SHA256(seed.x,seed)==saved_bundle.settings_SHA256 BEFORE
rendering. Bundle N/validated-bases/FL20_NATIVE_ZL_REBASED_10. Do not feed a
wrong older helper to native10; main already asserts the fingerprint.

Environment: use /workspace/.venvs/divalead/bin/python, not system Python,
for numpy/soundfile/scipy. PYTHONPATH=H:OLD:A:D:W:B (expand paths);
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1.
Wine S/sysroot/usr/lib/wine/wine64; native prefixW/wine, VST prefixS/wine2,
WINEDLLPATH S/sysroot/usr/lib/x86_64-linux-gnu/wine, DISPLAY=:90. Classes set
these selectors. X server processes do not survive snapshots. Start/check:
python3 H/start_native_headless_display.py
Actual separate:91 startup/socket probe passed and probe stopped; :90 kept.
Then run expanded paths:
env PYTHONPATH=H:OLD:A:D:W:B OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PY -B H/check_current_original_chain_readiness.py
It checks originalSHA/nativefingerprint, all12 actual native state resaves,
actual native-prefix render, two fresh trueZL plus nativePOSTtrim chains,
state resaves/PDC0 and original score, while preserving BEST/public files.
Supports trim33; read current H/CURRENT_CHAIN_READINESS.json, not an old
mean as a universal deterministic value. Free-running original Chorus varies.
No Windows FLStudio GUI/ASIO capability is attached; newFLP GUI test pending.

Full33 accepted finite point:27actualtrimcases,3newtraininginputs/2heldouts,
frozen before12NEWpairs. First6gain.001654673101 SEM.000216774468;
first10gain.001582554358 SEM.000150564389, both >max(.0005,3SEM), bothcold
positive. All12 upperLRRMSerror<=1.48 and maxabsupperLR1.6; lowmid<=3.25
and perpair<=control+.02. Airfirst10-.006803254698dB, bothcold<=control+.02.
First10originalscore1.289322707703, not perceptual%. Mixed residualmetrics
are disclosed in PAIRED_FIRST10_METRICS.json. No auditory/perfectmatch claim.
ZIP independently restored, two fresh actual ZL-before-trim replays0/0 and
native13/twoZL full replays0/0 at unchanged strict tolerances. Native13 impulse
added delay0 and component/native savedstate exact. Existing native12 block
variation and source firstresponse2samples remain disclosed. Not wholeDAW0.

Actual continuation state A/stereo-continuous87/BEST_CANDIDATE.json and
N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json plus /proc PID/starttime/cmdline
are authoritative. Main A/continue_stereo_ZL_matching.py now supports extra
nativePOSTtrim through A/stereo_cascade_runtime.py and A/native_post_trim.py.
Runtime freezes current POST and native trim from BEST at process import;
start a fresh process after adopting changed fixed effects. Two workers means
4actual ZL hosts AND2actual isolated native trim hosts; controller records both.
Do not start duplicates. Legacy single-ZL65 loops remain retired; old stops
N/zl-continuation.stop and zl-useful-full-backup.stop must remain.

Full32 main stopped gracefully after309 under owner dynamic-detector-family-20261026.
Adopt33 only after its publication with H/adopt_and_check_full33_runtime.py,
which writes BEST then checks two cold actual CURRENT runtime chains against
saved33audio and all fixed states. Start once with
H/start_actual_full33_original_target_continuation.py, checking4ZL+2native
hosts and cohort310+. Before any later restart inspect real process/state,
remove only a stale own numeric pause after matching PID is dead, and preserve
intentional finite-study coordination stops. Do not blindly rerun old adopters
or launchers over a newer BEST. Newer accepted numerical point may supersede
33primary; preserve its current native trim and POST exactly.

Fixed objective B/fl20_objective.py local_full_original_criteria_FL20_context_v1,
alignment819, edit176064, uploaded original only. All old fullscore weights
and strict tolerances unchanged. For33 main additionally preserves highLRRMS
1.48/lowmid3.25 and pairedAir increase<=.02 (first6mean/bothcold), upperabsLR1.6.
Never relax nativeFST2e-7 or coldZL8float32eps/1e-12 to make a candidate pass.
Main accepted cohorts use actual native+twoZL+nativeTrim output, new6warm/2cold,
and automatically back all24native/control/candidateWAVs plus playable ZIP.
Backup helper must retain last StereoShaper afterZLs in FLP/FST and guide.
No userPython is needed to open the FL20 kit.

Research/evidence that must not be repeated as fresh successes: detector24
289cases failed;25unchanged-origin setter checks were exact0. Corrected
internalChorus3latefits and4tone/drivefits failed; old colliding fragments were
excluded. RealPrimaryFit hostnames now rootSHA+PID; fixed shared names caused
cross-study scratch interference and are forbidden. WS52ref04 and nativeEQ76ref06
failed fresh screens. Relative21alone improvedtone but failedAir+.071>.02;
newprimarycofit passedtone/air but one upperLRRMS1.503>1.5, not lowmid failure.
POSTretune/HighShelf attempts failed required heldouts. Full33is a DIFFERENT
point adding actual channeltrim; rejected data not pooled to force acceptance.
All finite files/WAVs archived in linked original-* study directories. One-shot
watchers perform backup only; never call a watcher alone continued matching.

Storage: root208MiB/tmp128MiB main reserve. Full native-trim archive backup once
hit root-full after staging all3parts; exact temporary outer archive moved to
/tmp, existing stage verified, normal push852d253197b41b35e0b0e82a2fd6c5f706b23706
completed without data loss; allselectedstates/WAV retained. Old PUBLIC24..31
ZIP worktreecopies were HTTP/Git-byte-verified and locally offloaded only,
index skip-worktree. They remain in remote history and can be fetched on demand;
never interpret absent checkout ZIP as a deleted Git version. Current33/current
sourcebases/native10/presets remain. Closed default buffers may be freed with
FD-aware cleanup; keep selected audio/states and avoid deleting unknown packs.
Private original source48 blob41e9bf7d7adba68226614297644c9661181bff6d/private
archive refs/PCGUItrees/alloldfullkit trees must remain. Public Git promisorcache
may intentionally lack large blobs; do not bulk fetch, git diff HEAD origin/main,
or ls-tree --long. Use single-tree OIDs and normal scoped fetch/push. Publishers
coordinate R/auto-backup.pause and auto-backup-Git.lock; never steal a live pause.
Generic finite publisher now waits its turn. Best artifacts go to Git promptly.

Read runtime/onboarding skills at resumed startup. Inspect real network policy/
status, retain proxy/CA/injected Git auth, no secret dumps. No new domains or
secrets needed. Startup instructions are a saved review draft, not an applied
or published environment snapshot. No fresh-machine install is claimed.
