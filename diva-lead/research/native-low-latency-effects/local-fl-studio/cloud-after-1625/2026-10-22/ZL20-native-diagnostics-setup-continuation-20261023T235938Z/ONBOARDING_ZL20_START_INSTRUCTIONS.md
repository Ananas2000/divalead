# Diva lead — authoritative ZL20 / actual OscMix6.5 continuation

Continue the user's actual sound-matching task; do not stop after announcing a WIP. Work until a convincing reference match or actual resource/service limits. Service quota percentage is not exposed; do not pretend to detect the requested5%remaining. Back up useful completed stages/full FL20 kits progressively to Ananas2000/divalead main. User authorizes Git pushes, internet FL20-compatible plugins and removing only unnecessary old intermediates/local duplicates. Do not ask for per-trial listening feedback or ordinary confirmations. Do not present a partial match as final.

Read available cloud-environment-runtime and cloud-environment-onboarding:setup skills, inspect environment_status and configured network/credentials. Desired network is restricted/package-manager hosts; observed policy state may remain unknown. GitHub via platform HTTPS proxy works; no secrets/runtime credentials were configured. Do not bypass network policy. This is Linux/Wine cloud, with no attached local Windows FL GUI control; do not claim a new PC FL export, subjective listening, whole-DAW or ASIO latency.

Repository /workspace/divalead, main workflow. The saved repository SHA at this checkpoint isea3492b712ca3965d12bdc56cd9bfcb58058ac82. Four extra Git checkouts under divalead-setup/codec, codec-research and divalead-tools are audio codec dependency build caches, not project repositories. Full /workspace traversal found no unknown checkouts/errors; leave those caches unchanged.

FIRST read the repository's current diva-lead/research/native-low-latency-effects/start_skill_current.md, then the most recent ZLnn_CONTINUATION_RU.md and corresponding FL_STUDIO_RU.md. Newer successfully published current headers override older historical snapshots. At this checkpoint the latest complete kit is ZL20.

PUBLIC=diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22
Full user kit PUBLIC/ZL-WIP20/Diva_ZL_20_WIP_complete_WIP.zip contains actual FLP/WAV/Diva H2P/MIDI/17FST/standard VSTpreset/proofs/FL Studio20 guide. A/B PUBLIC/ZL-WIP20/AB_REFERENCE_ZL20_WIP.mp3: original0s -> candidate4.168s. Full export6 mean1.3308421080422417; independently extracted ZIP/new6 actual renders mean1.3309341134842132. These are the fixed original-reference objective, not similarity percentages or proof of exact perceptual match.

Only THREE incoming held notes41->37->36 per phrase, repeated twice. Six note-ons and six note-offs, velocities96/96/101 per phrase. Note-ons frames0/24000/48000/128000/152000/176000; note-offs24000/48000/64000/152000/176000/192000 at48kHz. Upward movement is Diva's internal ARP up+down2 / two octaves /1/8 /180BPM, not16 external short notes. No MistaTowa samples; original used for analysis/A-B only, never mixed into synthesis.

Latest accepted SOURCE change: Diva OSC OscMix6.3->6.5. All other280 parameters, ARP, ADSR and12MIDI events unchanged against ZL16 source. Both original H2P execution and real effSetChunk replay gave all281/12MIDI/rawfloat32/effGetChunk byte-exact matches. Fresh actual Diva has also been run from ZL17 H2P and the chunk extracted from the actual new FLP; full actual native+ZL rendered from that newly generated source, objective1.3440752855228726.
Source6.5 directory N/source-bases/FL05_OscMix_6p5. Relative to v83, source changes remain OscMix5.71->6.5, PWModDepth0->+1 KeyFollow2, VCA ModDepth-68->-58. Noise0, Drift24.8, Pan-39.33 and existing Plate/ARP/ADSR unchanged. Use actual all281 dumps/manifests, not assumptions.

Source6.5 was selected in23 actual-Diva tone cases; initial12pairs positive but revalidation12 against current main inconclusive. A fixed independent48-pair plan was saved before running, without pooling the prior12 or tuning during confirmation. Actual48: control mean1.3474299268315668 -> candidate1.3448848901692187, pairedSEM0.00040449305688165864, passed unchanged max(.0005,3SEM) gate. Retain the inconclusive and successful evidence; do not describe the rejected12 as accepted. New source adopted only AFTER new base03 export, full17 actual ZIP replay and successful normal Git push.
All96 control/candidate WAVs retained losslessly in3 parts under PUBLIC/actual-Diva-OscMix6p5-fixed-independent48-confirmation/. Manifest FORTYEIGHT_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz.SPLIT_ARCHIVE_MANIFEST.json has part/full SHA256 and ordered reassembly. GitHub rejects ordinary blobs>100MiB; copy_or_split_evidence_file uses64MiB parts for evidence>80MiB. First overlarge unpublished commit f3ed5c50 was preserved before local amendment; its complete objects are now protected by local Git ref refs/archive/unpublished-pre-split-f3ed5c50. The redundant /tmp bundle was evicted only after complete reachability verification; no remote history rewrite/forcepush. Successful split backup774bcdcc9677c95c4707b13637ce603215f26e4f, full17 commit95477a7eaf7f92a3cf94f8cc79a2d36d8bd8c7cf.

CURRENT NATIVE BASE MUST BE /tmp/divalead-local-1625/FL20_NATIVE_ZL_REBASED_04, not Native17/base01/base02. Its full archive is PUBLIC/rebased-native-bases/FL20_NATIVE_ZL_REBASED_04-verified-base.zip, SHA256f6afff76bec8ffe3e4022b90bed9d2cf33a85c48148b8ade679e4d6a81cd904b.
Setup script restores/verifies it and source via PUBLIC/actual-Diva-OscMix6p5-fixed-independent48-confirmation/scripts/restore_verified_native_base_and_source.py. Independently tested restore:55files checked,48 newly extracted, existing source files preserved and exact; derived padded WAV samples checked bit-exact because WAV headers/PEAK timestamps may differ. Different existing files are never overwritten. This is a delta data/runtime validation, not a claim that a completely fresh machine was tested.

Native topology:12 actual stock effects plus one official free ZL Equalizer2 v1.4.1 on SUM. Source WS/Chorus/source-phase, Mid/Side EQ and routing preserved. WS all supported2parent+4local+8detail curve metadata MUST survive fitting/export/replay. Old spectral Finish with12416frames PDC is retired. Free official MSI is downloaded separately; no vendor binaries in Git. ZL PE SHA2563269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d.
ZL MinimumPhase/lookahead0; actual declaredPDC0 and impulse firstresponse0 verified, native whole graph firstresponse2samples. Native block-size variants have a measured small NONZERO residual; do not claim sample invariance. Whole native+ZL saved-state replay at zero Chorus depth in ZL17 was bit-exact0. Ordinary wet Chorus varies between captures. No ASIO/wholeDAW0 claim.

Paths:
P=/workspace/divalead
N=/workspace/divalead-work/native-low-latency-effects
R=/workspace/divalead-work/three-held-continuation
B=/tmp/divalead-local-1625
D=B/internet-plugins-20261023
W=/tmp/divalead-native-effects
S=/workspace/divalead-setup
PY=/workspace/.venvs/divalead/bin/python -B
PYTHONPATH=D:W:B; OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1.
Wine S/sysroot/usr/lib/wine/wine64, WINEPREFIX=S/wine2 for Diva/ZL or W/wine for native, WINEDLLPATH=S/sysroot/usr/lib/x86_64-linux-gnu/wine, WINEDEBUG=-all, DISPLAY=:90. Actual supplied Diva binary /workspace/attachments/6a76beaa-924d-4f2e-8491-512d9b487af2/Diva(x64).vst3 is a VST2 binary; use actual history host /workspace/divalead-work/current-source-history-probe/diva_performance_history.exe.

Current main D/continue_ZL_matching.py; authoritative N/FL20_ZL_CONTINUOUS_CONTROLLER.json AND actual /proc/PID/stat starttime/cmdline/real hosts. D/ZL-continuous65/BEST_CANDIDATE.json carries current accepted actual component and pinned native/source. Historical directory name continuous65 now represents87 physical parameters:12staticPeak(36)+4AllPass(8)+6dynamicPeak(42; each Gain/Freq/Q/Target/Threshold/Attack/Release)+OutputGain1.
Each cohort actual fresh native input/48coupled proposals/coordinate87/2heldouts/fresh paired6, unchanged original objective, robust mean gain>max(.0005,3SEM), component roundtrip bytes and2NEWcold instances float32 rtol8eps/atol1e-12. Hot-vs-cold residue diagnostic only. All12 validation WAVs losslessly archived+SHA. Real component XML/610physical readbacks authoritative over stale inherited arrays.
Main reserves root64MiB/tmp112MiB. N/zl-continuation.stop is finite owned handoff; N/fl20-corrected-search.pause owner external-ZL-continuous65-refinement while active. D/watch_ZL_useful_complete_backups.py --watch makes useful full kits only after actual render/parse/ZIP replay, root192/tmp180MiB reserve. Verify its exact cmdline, not PID alone: scoped export helpers temporarily write the same watcher status. Startup waits for a newly spawned actual main if prior stopped controller is stale. Fixed later resume code checks expected script in /proc cmdline, not just alive PID. A post-adoption logging exception did not undo successful17 publication/source adoption; its trace and verified status repair are retained.
Legacy stock matcher/watcher/Finish Git publisher are RETIRED; keep N/fl20-corrected-search.stop and do not revive them.

Before launching anything, inspect actual live processes/owned controls. If already running, continue monitoring/research without duplicate hosts/controllers. If restoration lacks a current BEST, read PUBLIC/ZL20-validated-continuation/canonical-export-input/candidate-research-only.json and completion.json, restore the actual component/state and source/nativebase04 paths, use complete20 WAV as saved example, then perform fresh confirmations. Do not seed from old stock-only loss or oldsource6.3. Copy/rebuild actual87 scripts from committed latest research scripts only when no live users of those paths; preserve any newer local work. Setup need not auto-start unlimited jobs.

OBJECTIVE B/fl20_objective.py FeaturesOriginal local_full_original_criteria_FL20_context_v1: .65tone+.35standard+.05abs(logRMSgain)+clip penalty+tiny nativeEQ regularizer. Full original P/diva-lead/v83-wip/Diva_original_lead_reference.wav SHA2567617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f. Align819, fixed video-to-reference edit, no changes to criterion/tolerances for fake improvement. Native-only score can worsen while the combined native+ZL improves; select using full combined heldout/fresh pairs. Chorus9 context study205 cases failed paired12 gate and was NOT adopted. Signed residual diagnostics show excess between-harmonic energy3.5–6.5kHz and deficit above6.5kHz; this is modulation/tails/leakage too, not a pure noise measure.

Git writes: R/auto-backup-Git.lock flock plus owned R/auto-backup.pause, cleanup owner authorized-local-backed-copy-cleanup-20261023 recognized by scoped publishers. Preserve all prior numbered/release/full-kit tree OIDs and user changes. Normal scoped push HEAD:main; no force. Bounded retries only for transient network503/etc; terminal large-file errors need splitting, not retries. aggregate SHA generation includes omitted skip-worktree blobs via Git, excludes intentionally staged deletions.
Many old version audio/ZIP/proof duplicate worktree files were evicted only after exact origin/HTTP proof. Restore individual file via git restore --ignore-skip-worktree-bits -- exact/path, or recorded git show commit:path; never blindly restore all large data. All remote versions/history preserved. Git objects compressed only in small verified packs, no unique objects removed. Old rejected auxiliary WAV pruning kept EVERY main/training/recorded example, all source/presets/metadata and accepted variants; later58 archived rejected trials also retained their protected main WAV members bit-exact. Receipts/decision SHA manifests in N and published research. Never remove originals/current native/source/runtime.

Continue improving. No per-trial user questions, no exact-match claim, no pretend human audition or FL GUI. Share useful intermediate GitHub ZIP/A-B links while actual work continues.


NEW CURRENT NATIVE CORE: setup appends fl20_curve.py and export_fl20_checkpoint.py
from PUBLIC/actual-Diva-22-PWM-sync-native04-rejected-study01/scripts after old
embedded bootstrap. Do not substitute the old embedded native exporter.
Canonical export audio is rendered from the actual12serialized native presets.
SDK-versus-preset audio is diagnostic; all FST replay tolerances remain2e-7.
native_saved_state_bundle has full settingsSHA256 and perstateSHA256. Load it
only when x95,2+4+8curve,Chorus overrides and supported WaveShaper controls all
match. Changed trials must actually stay changed. Actual DLL tests verified
unchanged bundle vs explicit FST0, changed EQ and curve stay changed; Preamp,
Mix,Post raw controls each survive save/reload bit-exact and match direct
native commands with audioerror0. Legacy/default controls preserve hashes.
Support waveshaper_native_controls=[Preamp,Mix,Post] within measured UI ranges
[64..192,0..128,0..128]. Values are raw native controls, not dB percentages.
No nondefault controls adopted at this checkpoint; the finite WS19 study is
research, not a new accepted full kit. Original-reference gates unchanged.

Since ZL17, nativeEQ76 refit robust paired12:1.3441599237931587->1.3381004698371395,
SEM.0008076357532817598; base04 plus fullZL18 adopted only after actual fullZIP
replay/push. Cycle03WS16 failed robust gate, do not adopt that curve. Further
87parameter officialZL fitting yielded fullZL19. Latest actual controllers and
BEST may be newer than this checkpoint; inspect them and current Git headers.

22actualDiva PWM/oscillator mix/sync cases were completed after a preserved
ENOSPC partial study and sequential recovery. Selected OscMix6.6 paired12
control1.3371417804013177->candidate1.3366307656179404 SEM.0007374561653916166,
robustFalse: source6.6 NOT adopted; retain accepted6.5. Evidence is public at
actual-Diva-22-PWM-sync-native04-rejected-study01 including22actual281/MIDI
sourceaudits, H2P/chunks,selectedraw/coldreplay,all24freshpairWAVs. Main pauses
for finite studies via OWNED stops; verify N/WS19_SEQUENTIAL_STUDY_CONTROLLER.json
and N/ZL_NATIVE_WS19_CONTROLS_STUDY_STATE.json plus real /proc hosts before
restarting anything. Stop owner native-WS19-controls-finite-refit-20261023.

Storage: redundant original200MBsource48bundle removed after allGitobjects
verified and protected by archive ref. Source48 full audio archive still in
localGitblob41e9bf7d7adba68226614297644c9661181bff6d and remote3SHAverifiedparts.
Some clearly worse old ZL auxiliary repeated-validation archives were pruned
explicitly, while EVERY main selectedWAV/component/training/metadata was kept;
these deleted auxiliary repeats are not claimed remotely backed. Current,
recent20,publishedsourcecohorts and every10th were protected. Receipts in N.
Retired /workspace/divalead-work/wine-clean-check generatedWindows/standard
programfiles cache was removed after proving no active process/openFD; no
userplugin/preset/audio was there. Rebuild that old diagnostic prefix if needed;
CURRENT wine2 and nativeWine remain intact. The oldcache was hardlinked and
its deletion reclaimed very little physicalspace; do not claim770MBrecovered.


NEW ZL20 FULL KIT: commit ddd36ee037d567b2e396fc08002d42e8e4605846;
ZIP10719631bytes SHA2567a08d9c99caa1f99126db03fe2a2e182d94d3195eeb4c10434d42d8a500493cd.
The standalone full render and independent extractedZIP six renders improve on
ZL19; NOT an original sound match or perceptual percentage. Current nativebase04
and actualOscMix6.5 source remain accepted. Existing87physicalparams,12staticPeak,
4AllPass,6dynamicPeak,OutputGain. Actual610readbacks override inherited stale
metadata arrays (a private old array may still list only4dynamic bands).

Actual WaveShaper19-parameter controls/curve study310cases rejected paired12:
control1.3310779438308884->candidate1.3309296157641408,SEM.0006760317852846968.
Preamp/Mix/Post selected128/128/128; no new WS curve adopted. Public evidence
native-WS19-controls-current-ZL-study01. 25actualDivaDrift/Plate cases also failed:
control1.3300977410635577->candidate1.3303675641765675,SEM.0005837933214899449;
source stillDrift24.8/PlateWet1.12/Damp68. All281 and12MIDI audited; selected
chunk/raw cold exact. Public actual-Diva-Drift-Plate-native04-study01.

ZL20 originally refused the mixed warm/cold wholezero comparison, nativeerror
6.258487701416016e-7,whole1.4901161193847656e-6. Failure originalZIP/code/captures
are preserved, not silently discarded. Independent diagnostic3fresh chains
and8cold/repeated/wet-history captures all gave exact0; cause NOT established.
New validation protocol compares ORIGINAL and TWO extractedZIP native+ZL chains
in identical fresh conditions. Every12native state byte, native2e-7 absolute
and wholefloat32rtol8eps/atol1e-12 gates unchanged. All3fresh full outputs exact0.
The six-capture hot/cold result is diagnostic; no universal native bit-exact
claim. Full20verification/VALIDATION_PROTOCOL_AND_PRIOR_FAILURE.json records it.
Future finalizer template supports this3cold protocol. Do not just retry failed
checks until they pass or loosen a gate. NativewetChorus still legitimatelyvaries.

Comprehensive WaveShaper transfer/control tests, saved-native-bundle regression,
older SDK/FST audit, failed20andnewcold diagnostics are retained losslessly with
all file hashes in ACTUAL_NATIVE_STATE_CONTROL_AND_ZIP_DIAGNOSTICS.tar.xz.
This archive is127252241rawbytes->13079196compressedbytes, SHA256
9508c8663efab4ea02f2b8a8603cac288a2842d2e85c95b7435434d8f7a7c24d.
No machine hearing or exactoriginalmatching claim derives from these tests.

Additional current study uses unusedZLslots22/23, actualPeak/LowShelf/HighShelf/
Tilt/FlatTilt types. Read N/ZL_TWO_FREE_STATIC_SLOTS_STUDY_STATE.json and its
completion. This study NEVER adopts automatically. A positive result needs an
owned safe-main handoff, latest-control fresh confirmation, supported static
metadata migration, new fullFLP/ZIPactualreplay and push before adoption.
Proposed migration scripts in D/static-slot-supported-migration-proposal-01 are
NOT installed merely because they exist. All old accepted87main remains safe.
Actual enum: Peak0,LowShelf1,LowPass2,HighShelf3,HighPass4,Notch5,BandPass6,Tilt7,
FlatTilt8,AllPass9,FlatGain10, normalizedtypeindex/10.

Storage now retains full20ZIP locally; olderZL01..19ZIP worktree copies are
skip-worktree after exactorigin checks, allGitHubversions andobjects retained.
Completed private native03/source22/source25/WS19 paired archives were evicted
only as byte-exact copies of publicGit blobs; all their audio can be restored
using receipt commands. No private selectedWAV/preset/metadata was removed.
33obsolete private auxiliary A/B cache archives were pruned by111086386bytes:
only derived AB members; every retained actual/reference-edit mainWAV and
choice/validation was verified and kept. Every10th auxiliary comparison and
all publicversions remain. Explicitly deleted oldauxiliary A/B bytes are NOT
claimed remotely backed. Receipts plus SHA/retainedmember proofs are in N.
