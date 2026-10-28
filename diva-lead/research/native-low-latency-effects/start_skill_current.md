BEGIN_TWO_ZL_NUMERIC_cohort-0413
Latest complete base ZL-WIP37 with TWO ZL. New accepted numerical continuation stereo-cascade87-cohort-0413: originalpaired control1.2790974164620283, candidate1.278551797908969, SEM6.391698922381846e-05, separatecold2[0.000801089326433635, 0.0005222086176046581], stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/EQ76-WS16-contextual-refit01/3longincomingnotes/ARP/postFilters Side 10744.5Hz/Q1.895000100135803+2080.0Hz/Q5.117000102996826+966.1000366210938Hz/Q9.017999649047852; Stereo 775.1000366210938Hz/Q25.0+1680.0Hz/Q9.305999755859375; Left 994.0Hz/Q5.871000289916992/-1.700000762939453dB; Mid 662.2999877929688Hz/Q7.687000274658203 unchanged; additional lowmid300-800 errorlimit3.25dB. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_cohort-0413

AUTHORITATIVE CORRECTION / ACTUAL407+106 CHECKPOINT 2026-10-28

Earlier startup paragraphs inaccurately described per-pair lowmid+.02 as a
numeric-main gate. Until cohort406, numeric main enforced ABSOLUTE stereo
bounds only; the per-pair rule was only implemented in finite studies. Do not
repeat that inaccurate historical claim. Accepted403 had measured lowmid-error
increase~.023dB vs372, outside the described .02; no claim403passedthatgate.
404 improved that balance by~.0155dB vs403. A NEW independent DIRECT404_VS372
fresh12 audit then compared404 DIRECTLY to372, not through403: first6 gain
.0012576375/SEM.0000767886, first10 .0012819405/SEM.0000470989, bothcold
positive .0009699852/.0012425905. All12 absolute bounds AND per-pairlowmid+.02
passed (maxincrease.007630825). Air10+.00414993, bothcold+.00870227/+.00277863
within original+.02. Stateexact/PDC0, all36actualWAVs complete remoteverified:
2b9678924d15b3cfc3550f6274ac2f20560bc59d. This qualifies404 against the added
stricter rule directly; no rollback or false retrospective403qualification.
MAIN_PAIRED_LOWMID_GUARD_CORRECTION_20261028.json records old/new code SHAs.

Main code NOW adds the per-pairlowmid+.02 rule to heldouts and all8 fresh
numeric comparisons. All pre-existing weights/criteria/gates remain. Only
own paired-lowmid-audit-20261028 stop was released after full audit remote
proof; actual NEW MAIN PID691090/cohort407 loaded the patched code SHA
491e8c93e074032726998c1c97010eb96a1e123d16641f9ed0ab9d3d1f374277.
Read ACTUAL_MAIN_RESTART_WITH_PAIRED_LOWMID_GUARD_20261028.json and actual
controller/PID/starttime. 405 and406 ended NEGATIVE, never adopted. Temporary
SIGSTOP pauses of old687642 during storage/Git staging were fully resumed,
then oldmain finished406 and obeyed ownstop. It is now closed; don't signal
historical PIDs. A process snapshot is not future liveness evidence.

Finite PRIMARY94 mean-three/three-sweep study CLOSED NEGATIVE:1273 proposals,
3819actual training DSP renders; two unseen mean gain .0002194997 below.0003
screen, no12finaltest and noadoption. Fully backed fdd12ec4d312b63cf72158629aacb0460357b943.
Automatic actual continuation PID690286 now runs
H/study_PRIMARY106_detector_joint_three_sweeps404.py on the exact SAME five
native inputs, hardlinked before oldcache eviction. ROOT
H/PRIMARY106_DETECTOR_JOINT_THREE_SWEEPS404; controller
N/ORIGINAL_PRIMARY106_DETECTOR_JOINT_THREE_SWEEPS404_STUDY.json. 94existing
PRIMARY variables plus knee/RMSlength/RMSmix/smooth for ACTIVE20/21/22.
Both newprimary hosts neutralconfigure0/0, baseline loaded every trial.
Three common inputs/three sweeps, source281/ARP/3held/native12/POST/trimfixed.
All existing fullkit12gates kept, EXTRA final cleanliness: Airfirst10<=-.005
and bothcold<=0 againstcontrol. No neweffect/no PDC/no altered scoring.
Any positive finite point needs latestBEST revalidation/full export/coldZIP
replay/publication BEFORE adoption. Do not mistake it for alreadyaccepted.

Two closed old DERIVED A/B cache batches were fully losslessly uploaded,
all nestedWAV+archiveSHAchecked, then only oldprivateTARcopies released:
133b316bc928e3622b6d36d498ed345ae8ae1699 /67409124bytes,
b5725ea74a54dfafab4d34112076c864781034c8 /69709599bytes.
Recovery locations are recorded in original private .tar.gz.json metadata and
OLD_DERIVED_AB_REMOTE_VERIFIED_LOCAL_RELEASE_20261028*.json. Do not delete
candidate/source/main/referenceWAVs or any unknown gzip content stores.
Closed default VST3 buffers were separately regenerated-cache-cleaned using
FD/log/code/JSON reference checks, freeing~212MiB /tmp on28Oct; not recorded
candidate audio. Both disks have independent resource guards.

Everything below is older historical detail. This correction, current BEST,
actual controllers, observed PID/starttime and newer remote proofs win.

ACTUAL PROCESS SNAPSHOT 2026-10-28T17:22:08.698795+00:00 (check current state; not a promise):
Main687642/starttime60598535 really restarted atcohort405 after remote
verified release of64MiB of OLD DERIVED A/B archives, recoverycommit
133b316bc928e3622b6d36d498ed345ae8ae1699. Keep all actualcandidate/sourceWAVs.
Concurrent finite mean-three/three-sweep study PID687430/starttime60592318
is actually running, both loaded/configured primary hosts neutral identity0/0.
Read ACTUAL_DUAL_MAIN_AND_MEAN3_SNAPSHOT_20261028.json and realcontrollers.
No106-detector joint job has started at this snapshot. Its prepared
H/study_PRIMARY106_detector_joint_three_sweeps404.py can reuse SAME exact404
five nativeinputs only after the94-parameter study finishes and before its
WAVs are evicted. It jointly varies94 old parameters plus knee/RMS length/
RMS mix/smooth of ACTIVE20,21,22; no added effect. Final extra cleanliness
gate first10Air<=control-.005 and bothcold<=control, other strict gates kept.
Positive screens still require latest-context revalidation/full export/replay/
publication. Never automatically adopt a finite positive before those checks.

AUTHORITATIVE 2026-10-28 THREE-SWEEP / ACCEPTED404 CHECKPOINT

Continue actual three-held-note Diva matching against the uploaded ORIGINAL.
Only three held incoming notes per phrase; internal ARP creates upper jumps.
No MistaTowa, no v83/Finish as target or playback effect. The reference happens
to be stored in v83-wip; that folder name never changes the target. User has
authorized actual renders, normal FL20 effects, useful complete Git backups,
and safe release of recoverable local duplicate files. Do not ask per trial.
Do not claim exact match, hearing, Windows FL GUI/ASIO, quota percentage, or
imaginary ongoing work. Check real PID/starttime, not a historical snapshot.

Latest accepted at this checkpoint:403 then404 on full ZL-WIP37. Each has a
full playable FL20 ZIP, FST/FLP/h2p/MIDI/WAV, and all24 fresh6warm+2cold paired
native/control/candidate WAVs on ordinary Git. 403commit deb1e67dffb931bf986264faa68d2ae65ba3ff96;
404commit e4693110822f66df28f8812ced38c5582643190b. Read current
A/stereo-continuous87/BEST_CANDIDATE.json FIRST; do not overwrite a newer
accepted state with an old37 adopter. 404 is a search cohort number, not a
claim of a large audible improvement. Both gains are small and fullmatch=false.

Public LATEST_THREE_NOTE_RU.md links404 ZIP, FL20 guide and original->37->404
shared-input A/B. A/B starts0/4.168/8.336s; only common stereo RMS matching,
never individual L/R normalization. Same actual native input for37 and404.
Publication d4f97866c033a21d1949afd627ee00751e6be859. Old372 A/B stays372.
48000Hz and180BPM are canonical for comparison. Old kits/PC GUI tree remain.

Actual main A/continue_stereo_ZL_matching.py now performs THREE sequential
coordinate sweeps per frozen input, step factors1/.7/.49, before unchanged
fresh6+2cold confirmation. MAIN_THREE_SWEEP_REFINEMENT_20261028.json records
it. Initial real run PID680606 accepted403/404, then storage-stopped after404.
NEVER assert680606 is currently alive. Current controller is
N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json. Four real ZL hosts and two native
post-trim hosts are required. Runtime reads current BEST at import. Restart
H/restart_current372_three_sweep_20261028.py is generic despite its historical
name: it preserves latest BEST and asserts native fingerprint, no live main,
no owner stop, both retired single-stage stops and root208/tmp128MiB reserves.
Current actual process status must be checked before any restart.

Training Air was TIGHTENED to current-control+0. Main final scoring/weights,
alignment819/edit176064, numeric fresh6+2cold, >max(.0005,3SEM) and bothcold
positive, upperLRerror1.48/maxabs1.6/lowmid3.25/per-pairlowmid+.02, freshAir+.02,
and strict cold-state replay tolerances are unchanged. Local acceptable Air
increases may accumulate across checkpoints; cumulative Air37 preservation
is NOT claimed. Finite full-kit studies must pass BOTH first6 andfirst10 plus
bothcold, latest-context validation, full export and independent replay before
adoption. Do not equate a scalar-loss gain with an audible percent match.

New finite negative studies: Side22 detector(97 proposals/291DSP), four fine
Diva Plate settings, six-existing-AP retune, extra AP7, and primary23 quiet
relative dynamics all failed their stated screens. They have complete remote
archives and were not adopted. PRIMARY bands20/21 are MID,22 SIDE; physical
component metadata is authoritative. Existing detector24 study did not test22.

Important technical correction: first PRIMARY_REAL_JACOBIAN_CURRENT test is
INVALID: second parallel primary host had not loaded baseline, and the old
residual was scalar sqrt(loss), not a detailed residual vector. No point was
adopted, so accepted372/403/404 unaffected. Public invalid-study README and
TECHNICAL_INVALID_FIRST_ATTEMPT.json explicitly correct it; do not use its
negative gain as an acoustic conclusion. Corrected FIXED_BASE test loaded
baseline in BOTH hosts before every evaluation, neutral identity0/0, detailed
1188x94 actual-DSP Jacobian with residual norm exactly equal to original loss
on EVERY evaluation. Its16LM cases selectedbaseline and no improvement. A
subsequent constrained SLSQP/LM test reused the exact actual403 matrix and
five WAVs, checked42 actual joint proposals, two unseen gain .0000393 only;
not accepted. Both corrected studies complete and losslessly backed up:
fixed4341cd2fa0c5ccceeabbfad80a9314abdf534d99,
constrained7499d43b659dffc33c2c332a4768a5fb6425e68f.

Prepared next finite study H/study_PRIMARY_mean3_three_sweeps_current404.py:
three common actual inputs, three coordinate sweeps, normal bounds/step1,
trainingAircontrol+0, unchanged12newpaired gates, two-host neutral identity
before fitting and explicit baseline load before EVERY trial. Controller
N/ORIGINAL_PRIMARY_MEAN3_THREE_SWEEPS_CURRENT404_STUDY.json decides whether
it has started/completed; do not duplicate live work. It does not adopt points.
Positive result still needs latestcontext/full export/replay/Git before adoption.

Space: /workspace overlay and /tmp are distinct nearly-full filesystems. No
repository quota error has been observed. Never delete unknown packs, private
original48 blob41e9bf7d7adba68226614297644c9661181bff6d, original reference,
source-bases, latest full37/404 assets, current study states, or user PC tree.
Only exact current-remote-tree+HTTP-proved loose public blob caches may be
evicted by verified helpers while preserving refs/index/privateblob. Old
PUBLIC32..36/numeric363/367/369/371 WAV/ZIP copies may be skip-worktree and
missing locally; all stayremote, restore individual paths only. Old failed
study WAVs have complete archive receipts. Do not bulk restore or use
ls-tree--long / two-treegitdiff that rehydrates large missing objects.
H/backup_and_release_old_derived_AB_batch.py backs up a bounded CLOSED OLD
DERIVED A/B archive batch, checks all nested WAV hashes, uploads/verifies all
parts, THEN removes old private archive copies and records recovery locations.
This is storage recovery, not new sound research. Keep actual candidate WAVs.

No subagents: current instructions prohibit spawning unless explicitly requested.
Managed tools do not control the user's PC. Use actual Wine/DLL/VST3 DSP;
Windows GUI validation is separate and pending. Setup drafts are saved only,
not automatically applied/published; review does not block authorized audio work.

The paragraphs below are retained historical setup detail. Their old versions,
PIDs, 'latest' claims and stops cannot override the checkpoint above or real
BEST/controller/process evidence. Core environment paths and fingerprint checks
remain useful. Read runtime/onboarding skills on resumed startup.

--- HISTORICAL DETAILS FOLLOW ---

ACTUAL LATEST checkpoint2026-10-28 after the earlier snapshots below:
Both finite anchored-Air849 and alpha-merge6 studies CLOSED NEGATIVE and were
fully losslessly archived. They were not adopted and no full38 was declared.
Latest accepted372 remains on complete37; source281/threeheldnotes/ARP/ADSR/
native12/POST37/nativeTrim remain unchanged. Never re-adopt an old37 primary.
Own anchored-air-primary-fit-20261028 stop was removed only after negative
completion+remote archive proof. Actual main RESUMED PID670946 atcohort374,
4actualZL+2actualnativeTrim verified. Read realcontroller/PID/starttime and
ACTUAL_FULL37_AFTER_VERIFIED_CLEANUP_20261028_START.json, not an older status.
Training Air was TIGHTENED from currentcontrol+.01 to currentcontrol+0;
MAIN_ZERO_EXTRA_TRAINING_AIR_CHANGE_20261028.json records the reason/hash.
All original score weights, source/MIDI/native/POST/trim, heldout/fresh6/cold2
+.02Air tolerance and strict cold/native tolerances remain unchanged. This is
not proof of cumulativeAirpreservation vsfull37. Latest372/37 and all previous
remote versions/presets/projects remain. Only exact recoverable older public
WAV/ZIP cache copies may be absent locally; restoreindividualfiles viaGit.
All older paragraphs describing668376 alive or ownstop present are historical.
A process snapshot does not promise future/background work or a perfect match.

CURRENT 2026-10-28: complete37 plus accepted numeric372 are saved, not a
perfect match. Read current BEST/controller and public README first. Later
numeric headers are historical checkpoints, never instructions to overwrite
newer data. Actual full37 publication/adoption/readiness and372 artifacts are
verified; main is storage-stopped and current actual matching is the explicit
anchored-Air finite study. Do not describe a watcher as sound matching.

BEGIN_TWO_ZL_NUMERIC_cohort-0372
Latest complete base ZL-WIP37 with TWO ZL. New accepted numerical continuation stereo-cascade87-cohort-0372: originalpaired control1.2807144806309347, candidate1.2801991335911027, SEM6.832482417140852e-05, separatecold2[0.0003505628667221927, 0.0006493943280043712], stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/EQ76-WS16-contextual-refit01/3longincomingnotes/ARP/postFilters Side 10744.5Hz/Q1.895000100135803+2080.0Hz/Q5.117000102996826+966.1000366210938Hz/Q9.017999649047852; Stereo 775.1000366210938Hz/Q25.0+1680.0Hz/Q9.305999755859375; Left 994.0Hz/Q5.871000289916992/-1.700000762939453dB; Mid 662.2999877929688Hz/Q7.687000274658203 unchanged; additional lowmid300-800 errorlimit3.25dB. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_cohort-0372

BEGIN_TWO_ZL_NUMERIC_cohort-0371
Latest complete base ZL-WIP37 with TWO ZL. New accepted numerical continuation stereo-cascade87-cohort-0371: originalpaired control1.2812080657451752, candidate1.2805171062192733, SEM4.648939747628753e-05, separatecold2[0.0006723364788889796, 0.001004120201402836], stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/EQ76-WS16-contextual-refit01/3longincomingnotes/ARP/postFilters Side 10744.5Hz/Q1.895000100135803+2080.0Hz/Q5.117000102996826+966.1000366210938Hz/Q9.017999649047852; Stereo 775.1000366210938Hz/Q25.0+1680.0Hz/Q9.305999755859375; Left 994.0Hz/Q5.871000289916992/-1.700000762939453dB; Mid 662.2999877929688Hz/Q7.687000274658203 unchanged; additional lowmid300-800 errorlimit3.25dB. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_cohort-0371

BEGIN_TWO_ZL_NUMERIC_cohort-0369
Latest complete base ZL-WIP37 with TWO ZL. New accepted numerical continuation stereo-cascade87-cohort-0369: originalpaired control1.2830819610342907, candidate1.2822046161348069, SEM5.6208191549757367e-05, separatecold2[0.00047126633648408855, 0.0013520336383245901], stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/EQ76-WS16-contextual-refit01/3longincomingnotes/ARP/postFilters Side 10744.5Hz/Q1.895000100135803+2080.0Hz/Q5.117000102996826+966.1000366210938Hz/Q9.017999649047852; Stereo 775.1000366210938Hz/Q25.0+1680.0Hz/Q9.305999755859375; Left 994.0Hz/Q5.871000289916992/-1.700000762939453dB; Mid 662.2999877929688Hz/Q7.687000274658203 unchanged; additional lowmid300-800 errorlimit3.25dB. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_cohort-0369

BEGIN_TWO_ZL_NUMERIC_cohort-0367
Latest complete base ZL-WIP37 with TWO ZL. New accepted numerical continuation stereo-cascade87-cohort-0367: originalpaired control1.2838775667965816, candidate1.2830222326362453, SEM0.00010371089363511435, separatecold2[0.0011379496492391894, 0.0007530074364414663], stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/EQ76-WS16-contextual-refit01/3longincomingnotes/ARP/postFilters Side 10744.5Hz/Q1.895000100135803+2080.0Hz/Q5.117000102996826+966.1000366210938Hz/Q9.017999649047852; Stereo 775.1000366210938Hz/Q25.0+1680.0Hz/Q9.305999755859375; Left 994.0Hz/Q5.871000289916992/-1.700000762939453dB; Mid 662.2999877929688Hz/Q7.687000274658203 unchanged; additional lowmid300-800 errorlimit3.25dB. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_cohort-0367

BEGIN_TWO_ZL_NUMERIC_cohort-0363
Latest complete base ZL-WIP37 with TWO ZL. New accepted numerical continuation stereo-cascade87-cohort-0363: originalpaired control1.2833836688336056, candidate1.282654340091553, SEM3.6518167687275305e-05, separatecold2[0.0005604249776054449, 0.0006515006463312378], stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/EQ76-WS16-contextual-refit01/3longincomingnotes/ARP/postFilters Side 10744.5Hz/Q1.895000100135803+2080.0Hz/Q5.117000102996826+966.1000366210938Hz/Q9.017999649047852; Stereo 775.1000366210938Hz/Q25.0+1680.0Hz/Q9.305999755859375; Left 994.0Hz/Q5.871000289916992/-1.700000762939453dB unchanged; additional lowmid300-800 errorlimit3.35dB. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_cohort-0363

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

LATEST37 checkpoint 2026-10-28: full FL20 kit built and independently cold
ZIP-replayed. PUBLIC/ZL-WIP37/Diva_ZL37_STEREO_WIP_complete.zip,
16237773bytes, SHA256ac32374256a9a0c8fd71b2b1cafa718d92d74f4414cb0fca8ffe6d0ce78cd7a1.
Read ZL37_CONTINUATION_RU.md and FL_STUDIO_RU.md. Second ZL only changes:
new StereoAP6 1680Hz/Q9.306, existing StereoAP3 775.1Hz/Q25 and MidAP5
662.3Hz/Q7.687; SideAP0/1/2/LeftEQ4 and sourceDiva281/ARP/ADSR/three held
incoming notes/native12/base10WS52/PRIMARY36/nativeTrim34 remain identical.
NewPOST SHA2566597c11fe806b4d58243f8742eb0b358b02dbb86da63e007526025ba2f8c901f.
Q=H/POST_AP6_JOINT_REFINEMENT36,363actual proposals, each mean of THREE
separate actual DSP scores, two additional unseen inputs, then12NEWpairs:
first6gain.001491384464 SEM.000009900796, first10gain.001518074484
SEM.000012976757, both>max(.0005,3SEM); bothcoldpositive. All original
upper1.48/abs1.6/lowmid3.25 plus pairedlowmid+.02/bass+.15 andair+.02 pass.
First10air+.001130837812dB disclosed, no subjective cleaner claim.
All source/note changes were rejected in separate1275proposal/3825actualDSP
sourcePRIMARY study; source remains OscMix6.5 and old281 exact. Its12new
validation pairs worsened first6/first10 despite lowerAir; NOT adopted.
Pilot300AP6 models improved too little (first10gain.00043229<.0005), not adopted;
37 is a DISTINCT jointAP3/5/6 point and passed the unchanged threshold.
Initial53trial incomplete refinement attempt failed only a NumPybool JSON
progress writer; resumed on SHA-identical FIVE frozen inputs, oldincomplete
trials excluded. Marker and exactf32-from-retained-WAV restore helper archived.
All48newvalidation native/primary/control/candidateWAVs in lossless research
original-AP6-joint-refinement36-positive. No averaged or reference audio in synthesis.
Two actual input cold replays0/0, two independent restoredZIP full2ZL/trim
replays0/0, statesresaveexact/PDC0/impulseaddedonset0. No GUI/ASIO/perfectmatch.
Full37 ACTUALLY published3cdaef4ba24cae4f8ccd11cf6880675408e683a1,
adopted with0/0 actual new-runtime cold replay; main PID660359 started at362
with4actualZL+2actualnativeTrim. CURRENT37_CHAIN_READINESS_20261028.log proves
all12native state resaves and two fresh full chain0/0/PDC0. Owned complete37
stop was removed only after adoption. Main later accepted363/367/369/371/372
using separate6warm+2cold each, all playable FL20ZIP+24WAV archived. Latest
372 publication6e96058ce75941fd6d3e961b3b833a6be797c44f, savedcomponents stay.
DO NOT rerun full37adopter over the NEWER accepted372 PRIMARY.
Numeric acceptance is6warm+2cold, not a separately verified first10. Local Air
increments can accumulate; no claim of cumulative Airpreservation vs37 yet.
Main later stopped at its observed208MiB root reserve after a completedcohort.
Current owned stop anchored-air-primary-fit-20261028 keeps372 fixed while
H/PRIMARY_ANCHORED_AIR_MEAN3_372 fits PRIMARY against BOTH372 and full37 Air.
Controller N/ORIGINAL_PRIMARY_ANCHORED_AIR_MEAN3_372_STUDY.json, startupPID668376
is only a snapshot. Three COMMON real native inputs, two unseen,2sweeps;
trainingAir anchor37+.005, final BOTH local372+anchor37 first6AND10/cold2 and
Air+.02/lowmid gates. No source/native12/POST37/trim/MIDI changes.
Only after this job closes and any newpoint is fully validated/exported or
rejected may ownstop be removed and fresh main resumed from LATEST BEST.
Never restart37adopter or assume an old PID lives.

Other completed followups: Leftslot7 Peak/HighShelf72models failedscreen,
HighShelf actualtype3 calibrated by true impulse/enum (type2 isLowPass), not
adopted. PRIMARYcommon-three849cases reducedAir-.011 but first10gain.000458
below unchanged.0005floor, rejected. New three-source-parameter composite
(Offset-.11,PW51.92,VCFfreq144.26, synthetic-only RMSmatched) failed12newpairs
statistical/Air checks despite H2P/chunk/281/MIDI0, rejected. Alpha merge of
that separate quieter PRIMARY direction onto372 failed cumulative37Air and
localgain screens; no candidate adopted. All completed files/WAVs go toGit.
AB_FULL37_LATEST372_SHARED_INPUT is an actual2ZL/nativeTrim A/B using one
shared true nativeinput for both37and372; original0,37at4.168,372at8.336.
WorkingWAVs raw, AB-only common stereoRMS, no independentL/R normalization.
For the canonical rendering comparison use48000Hz/180BPM in FL Studio.

Storage 2026-10-28: closed defaultNative/VST3 buffers regenerated if needed;
root public loose cache verified against currentremote, old31/33 private WAV
copies and remaining12-point gradient WAV copies removed ONLY after exact
remote archive proof. Old32..35 public WAV/ZIP WORKTREE copies also evicted
withskip-worktree; all remote kits/Gitobjects/presets/projects remain. Do not
assume these oldlocal WAVs exist: restore exact remotearchive as needed.
Current36/currentpositive37 first0/reference/sourcebases/PCGUI retained.
Generic finite backup can reuse existing outerTAR only if EVERY current root
member and exact inventory SHA matches.48MiB measured staging reserve stays.
Sourcecoadapt archive safely refused staging atlowspace, then after verified
cleanup resumed unchanged and published5f6b38db8676883e067843cf048161cc4482b7df.
No quota% exposed; save completed work promptly, never claim15%observed.

HISTORICAL36 and older evidence follows; latest37 files/BEST override it.

Inspect actual Git HEAD/status, PUBLIC/README_RU.md and BEST before using a
snapshot below. Latest complete kit36 is PUBLIC/ZL-WIP36. Read
ZL36_CONTINUATION_RU.md and its FL_STUDIO_RU.md. Not a full sound match.
NEW complete36: PUBLIC/ZL-WIP36/Diva_ZL36_STEREO_WIP_complete.zip SHA256
b3d232fb7b1962703ba5ef01eb13b2b66e1265fb866e75d898e49c672ca7cd1c,16092505bytes.
Current accepted numeric353 PRIMARY plus jointly changed existing POSTAP0/1/2/3/5
frequency/Q. Modes/types/statuses/LeftEQ4, native12/sourceDiva281/ARP/ADSR/three
incoming heldnotes and last nativeTrim unchanged. NewPOST SHA256
4d6dcd88f6d5408a837c2de4e61163ff318992eb5e8e073f3c36ed1d856be31d.
Q=H/MID_SIDE_PHASE_JOINT35:387actual trials/3initial models then12NEWpairs.
First6gain.000764643820 SEM.000027397519; first10gain.000790490854 SEM.000022057791;
bothcoldpositive. Eachpair lowmiderror improves>=.2dB and uppererror>=.02dB;
final lowmid~1.04dB,upper~1.35-1.38dB, remaining errors not perfect stereo.
Airfirst10+.00119488dB/cold<=+.02. Actual new2ZL+nativeTrim0/0 and independent
restoredZIP2cold0/0, state resaves exact/PDC0/impulse0. User upgradefrom35:
load whole04_SUM or both ZL presets, keep SOURCE/MID/SIDE/nativeTrim. SUMonly
Mix100%, retained SOURCEChorus mix. Original is still only target.
Complete36 ACTUALLY published61f0968e52e8e8e1c2ee5a5804137ee6eba7298e,
adopted with0/0 actual new-runtime cold replay, then mainPID604171/cohort359
started with4actualZL+2nativeTrim. H/CURRENT36_CHAIN_READINESS_20261027.log
proves actual native12 resaves and0/0 two fresh complete chains/PDC0.
The coordination stop complete-WIP36-joint-phase-20261027 was removed AFTER
adoption. This main later stopped at its measured storage reserve after the
completed cohort. H/VERIFIED_FIVE_CLOSED_NEGATIVE_AUDIO_RELEASE_20261027.json
then released124531184 bytes of closed rejected WAV copies only after prior
lossless remote archive verification, fresh main-tree partOIDs and byte-exact
public manifests. Sources/states/current36/positivefirst0/reference remained.
Inspect H/ACTUAL_FULL36_AFTER_VERIFIED_CLEANUP_20261027_START.json and actual
controller PID/starttime for restart; never assume historical PID still lives.
Inspect BEST/controllers before any restart/adopter, never overwrite newer
accepted numeric PRIMARY with the older fixed full36 snapshot.

Current finite study H/DIVA_SYNC_TUNE2_MEAN3_COADAPT36 varies slaveTune2
23.94/23.98/24.00/24.04/24.10, MainOutput matched to SYNTHETIC baseline RMS
within.01dB. Actual source281 and12NOTE audited: only indices0/87 change;
HardSync/masterTune/ARP/ADSR and three held incoming notes stay unchanged.
Every primary94 training proposal scores THREE separate actual native/ZL/
trim renders, no averaged audio. Two separate unseen inputs for heldout;
strict newfirst6AND10/cold2/stereo/air and full supported source/FLP export
required. Two completed negatives preserved; after fixing the validation WAV
writer, interrupted third fit restarted on IDENTICAL frozen five WAV inputs;
RESUME_AFTER_EXPORT_WRITER_FIX.json records theirSHA. Current controller
N/ORIGINAL_DIVA_SYNC_TUNE2_MEAN3_COADAPT36_STUDY.json, driver
H/study_Diva_sync_Tune2_mean3_original.py, replay-code and resume log.
Do not restart a completed study or duplicate its live PID. New source points
are NOT adopted until robust validation plus supported source/project export.
One-shot watch_Diva_sync_Tune2_mean3_completed_backup.py only archives after
actual DSP job exits; a watcher alone is not continued sound matching.
Source waveform level-matched five alternatives all failed: public
original-Diva-level-matched-waveform-coadapt36. Tune2 levelcalibration is
original-Diva-sync-Tune2-level-calibration. Older35/34 snapshots below are
historical and must never overwrite current36 or a newer accepted BEST.

NEW complete35: PUBLIC/ZL-WIP35/Diva_ZL35_STEREO_WIP_complete.zip SHA256
f6231abe9c0e51fd84e566a0636ec434e1d27003fe665e50c8b0f2a32871ae9b,15999561bytes.
Only POST changed from34: new MID AllPass slot5,650Hz/Q9.6. PRIMARY34/dynamic22,
sourceDiva281/ARP/ADSR/threeheldnotes/native12base10WS52 and last nativeTrim34
unchanged. NewPOST SHA256 ea6a830fb7be608be0c9383a16ab592f5ea4238e97dbceb2ff1078f86f330910.
Q=H/MID_AP5_STEREO_ORIGINAL;48models/threeinputs then12NEWpairs. First6gain
.001951811588 SEM.000039957528; first10gain.001975495283 SEM.000025221148;
bothcoldpositive. EACHpair lowmidLRerror improved>=.25dB, about3.03->1.38dB;
upperRMS1.48/abs1.6/lowmid3.25; airfirst10+.00440366dB and bothcold<=+.02.
The small air increase is disclosed, not claimed cleaner than34. Two actual
cold complete input replays0/0 and two independent restoredZIP replays0/0;
state resaves exact, PDC0/impulse0. User upgrade from34 changes SECOND ZL only.
SumMix100% only; retain SOURCE Chorus mix. Original35FLP GUI test pending.
Before restarting inspect ZL35_FULL_PUBLICATION.json, ADOPTED_FULL35_RUNTIME_CHECK.json,
ACTUAL_FULL35_ORIGINAL_TARGET_START.json and actual BEST/controller/PIDs.
Full35 ACTUALLY published71d33ef5c52b565921681fa7aa1144df055cfc90, adopted
with0/0 actual new runtime replay, then mainPID598785/cohort353 started with
4actualZL+2actualnativeTrim. ADOPTED_FULL35_RUNTIME_CHECK.json and
ACTUAL_FULL35_ORIGINAL_TARGET_START.json record this; CURRENT35_CHAIN_READINESS_20261027.log
proves current35 native12resaves and0/0 two fresh complete cascades/PDC0.
Coordination stop complete-WIP35-MidAP5-20261027 was removed AFTER these
required adoption checks. Check latest actual controller/PIDs, not this snapshot.
Older34/33 evidence below is history; never overwrite35 with an older POST.

NEW complete34: PUBLIC/ZL-WIP34/Diva_ZL34_STEREO_WIP_complete.zip
SHA256 accc3938070c98a8115ee4cab9725a573a227db4f12dd85d19e69860ce9f0bb6,
15772661bytes. Built/restored ZIP: two actual two-ZL-before-trim and full
nativeTrim replays0/0, state resaves exact, PDC0/impulse0. PRIMARY now has
additional Side dynamic22 (94numeric parameters); Relative21/22 saved in
actual component is authoritative. Native12/base10/WS52/sourceDiva281/MIDI
unchanged, POST32 unchanged. Last nativeTrim LEFT-.020dB RIGHT0, raw
[0,12782,12800,0,0,0], stateSHA256
4a9138dc5e1f892692f01aa9efb6449b553b6c838fbb6c59507b4f13ff611354.
Q=H/AIR22_TRIM_THREE_INPUTS, first6gain .000647847844 SEM .000037890775,
first10gain .000687854215 SEM .000030538834, bothcold gains positive;
first10airchange-.025264147733dB, bothcold negative, all12upper1.48/abs1.6/
lowmid3.25/control+.02. New baseline is accepted numeric325 (not pooled33).
Do not substitute an old33/325 primary after34adoption. Inspect actual BEST.
Full34 publication/adoption/start evidence files are ZL34_FULL_PUBLICATION.json,
ADOPTED_FULL34_RUNTIME_CHECK.json, ACTUAL_FULL34_ORIGINAL_TARGET_START.json;
run/check only completed files and actual PID/starttime, not inferred success.
Complete34 was published7dc35faf47f63d17b8719325a390938d992baed9 and ACTUALLY
adopted: ADOPTED_FULL34_RUNTIME_CHECK.json gives0/0 complete runtime replay.
Actual main PID594085 started atcohort349 with4ZL+2nativeTrimhosts verified;
ACTUAL_FULL34_ORIGINAL_TARGET_START.json records it. CURRENT34_CHAIN_READINESS_20261027.log
checks native12resaves plus0/0 full current34 replay and PDC0. Old coordination
stop complete-WIP34-air22-nativeTrim-20261027 was removed AFTER that proof.
Inspect latest controller/PID/starttime; this is a snapshot. Current actual
main now searches94numeric PRIMARY parameters including dynamic22.
The readme Mix100% instruction is SUM ONLY; retain SOURCE Chorus dry/wet.

Later accepted numeric PRIMARY cohort325 has complete compatible playable ZIP:
PUBLIC/stereo-cascade87-cohort-0325/cohort-0325_complete_FL20_STEREO_WIP.zip.
Do not overwrite this newer BEST with the older full33 primary. Cohort325
paired6gain .000669109476 /SEM .000061270089; two cold gains positive;
airfirst6+.00922524dB and bothcold<=+.02. Numeric acceptance is6warm/2cold,
not the separately verified first10 required for full33. Absolute means from
separate Chorus realizations cannot rank these adjacent improvements.


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

Historical33 PRIMARY kept RelativeON in existing Side dynamicband21 plus the saved
joint refit; actual610dump/component bytes are authoritative. POST same32,
SHA256460cc43537b391236b3e8821910eede427bb6334bcce64e6e4f7be03a84e985d:
SideAP10207.6/Q2.198,2149.8/Q4.702,930/Q11.336; StereoAP782.9/Q20.561;
LeftPeak994/Q5.871/-1.70dB. Historical33 nativePOSTtrim raw[0,12769,12800,0,0,0], Left
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

Full33 was already published/adopted and ACTUALLY started. Evidence:
H/ADOPTED_FULL33_RUNTIME_CHECK.json two complete runtime cold replays0/0,
H/CURRENT_CHAIN_READINESS.json includes actual nativePOSTtrim and0/0 replay,
H/ACTUAL_FULL33_ORIGINAL_TARGET_START.json confirms mainPID550407,
cohort310 atstartup,4actualZL+2actualnativeTrimhosts. Inspect current controller
and /proc: that snapshotPID/cohort may now be stale or advanced. The historical
full32 coordination stop owner dynamic-detector-family-20261026 was removed
after33adoption; do not recreate it or rerun old adopter over newer BEST.
For a later restart inspect actual PID and intentional finite-study stop;
remove only stale own numeric pause after confirming matching process dead.
Preserve the latest BEST primary and fixed POST/native trim, not old33 primary.

Completed later studies: larger post LEFTcuts-.5/-1/-1.5/-2dB plus
PRIMARYrefits1588cases failed; actual oscillator waveform switches1985 failed;
postmatrix161 retained base; activeFX1/trueStack2 sevenfits2779 failed;
PW/PWMDepth fourfits1588 and finer PW51.85/51.87/51.89 plus same-source
finePRIMARY control1588 failed; true internalChorus replacing external six
coarse49fits294 failed. All audio/state/script archives are on ordinaryGit.
Do not re-run these exact failed points until one happens to pass.

IMPORTANT correction, proved by actual Diva renders: mainActiveFX1 is Off in
source. Changing Chrs1Wet alone while FX1Off produces BIT-IDENTICAL sourceWAV.
Earlier 'internalChorus' negative studies were OFF-FX1 Wet trials plus actual
externalmix/PRIMARY changes; they did not test audible internalChorus. All
were rejected, so no accepted kit was corrupted. ActiveFX1On/Wet15 changes
audio and cold audio/all281/MIDI/chunk replay is exact0. VoiceStack2 is
VCCVoicing index5; globalMaxVoices index4 is different. See public
original-Diva-FX1-activation-audio-audit-correction and full active/replacement
negative studies. Main/Diva remain sourceFX1Off and VoiceStack1.

New curve study H/WS_INTERLEAVED31_ORIGINAL tested31 narrow half-step
WaveShaper bumps with actual129point native DLL +2ZL+postTrim. Training gains
failed fresh stereo/noise constraints. Joint curve+posttrim27cases also failed
heldout. These are NOT adopted, and their new parameterization has NO supported
native fingerprint/export metadata yet. Do not feed them to normal exporter
or silently pretend52coordinates reproduce the modified129point state.
Research candidate only; requires supported migration/fullkit/cold/latestcontext.

Main actually restarted after verified closed-negative remote-audio and scratch
cleanup on20261027: H/ACTUAL_FULL33_AFTER_VERIFIED_CLEANUP_20261027_START.json
PID583992 atcohort332,4actualZL+2actualnativeTrim verified. Inspect /proc and
latestcontroller; PIDs/cohorts are snapshots. H/CURRENT325_CHAIN_READINESS_20261027.log
has the fresh readiness attempt. Main early training Aircap=cohortcontrol+.01,
heldouts/cold retain+.02; all quality gates unchanged. Read current main status,
not an earlier 'storage-reserve stopped' record. No fixed-count stop inserted.

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
289cases failed;25unchanged-origin setter checks were exact0. Corrected host-isolated
OFF-FX1 Wet/externalmix3latefits and4tone/drivefits failed; old colliding fragments were
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

New finite refinement H/MID_AP5_REFINEMENT35/controller ORIGINAL_MID_AP5_REFINEMENT35_STUDY.json varies only existing POST MidAP5 frequency/Q on three same fresh inputs. Original objective/first6AND10/cold2/stereo/air unchanged, extra each-pair lowmid improvement>=.05dB. Keep complete35 until any newer point passes and has full export/replay/publication. All tested candidate audio is actual plugin DSP; only record-improving feasible training WAVs retained to avoid storage exhaustion.
