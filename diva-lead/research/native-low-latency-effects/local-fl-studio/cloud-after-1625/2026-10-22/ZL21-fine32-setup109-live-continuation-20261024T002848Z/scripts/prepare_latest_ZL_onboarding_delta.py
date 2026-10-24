"""Prepare reviewable current-kit setup delta; does not apply cloud config."""
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup');N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
pub=json.loads((N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').read_text());code=pub['full_kit'][-2:];kit=PUBLIC/('ZL-WIP'+code)
assert kit.is_dir()
provenance=json.loads((PUBLIC/f'ZL{code}-validated-continuation/NATIVE_BASE_ARCHIVE_PROVENANCE.json').read_text());archive=PUBLIC/provenance['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==provenance['SHA256']
base=Path(provenance['native_base_export_directory']);basecode=base.name.rsplit('_',1)[1]
script=(S/'scripts/setup-current-ZL20.sh').read_text().replace("state=public/'ZL-WIP20/",f"state=public/'ZL-WIP{code}/").replace('startup-ZL20-current-context-check',f'startup-ZL{code}-current-context-check').replace('OFFICIAL_ZL20_ACTUAL',f'OFFICIAL_ZL{code}_ACTUAL').replace('FL20_NATIVE_ZL_REBASED_04-verified-base.zip',archive.name).replace('f6afff76bec8ffe3e4022b90bed9d2cf33a85c48148b8ade679e4d6a81cd904b',provenance['SHA256']).replace('native_base04_startup_restore.json',f'native_base{basecode}_startup_restore.json')
script=re.sub(r'^native_current_scripts=.+$', 'native_current_scripts='+str(PUBLIC/f'ZL{code}-validated-continuation/scripts'),script,flags=re.M)
script=script.rstrip()+'\n';path=S/f'scripts/setup-current-ZL{code}.sh';path.write_text(script);subprocess.run(['bash','-n',str(path)],check=True)
head=subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip()
start=f'''# Diva lead: current verified ZL{code}, nativebase{basecode}

Continue the user's actual sound-matching task until a convincing original-reference
match or actual resource/service limits. Never call a WIP a full sound match.
No per-trial questions. User authorizes normal Git pushes to Ananas2000/divalead main,
FL20-compatible internet plugins, and removing unnecessary older intermediates/local
duplicates recoverable from Git. Never use MistaTowa. API quota% is unavailable;
do not pretend to detect5%remaining. Back up completed useful stages progressively.

At this checkpoint repositoryHEAD={head}. Read the current repository
diva-lead/research/native-low-latency-effects/start_skill_current.md FIRST, then
the newest successfully published ZLnn_CONTINUATION_RU.md. Newer current headers
override historical snapshots. Four other Git roots under codec/codec-research/
divalead-tools are dependency build caches, not project repositories; leave them.
Use available cloud skills if exposed; otherwise the saved current instructions.
Managed cloud Linux/Wine, no attached Windows FL GUI control. No new local-FL GUI
export, subjective listening, fresh-full-machine installation or ASIO/wholeDAW0 claim.
Desired network restricted/package-manager hosts, observed policy can remainunknown.
Git uses existing platform proxy; no runtime secrets were configured. No bypasses.

PUBLIC=diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22
Latest full userkit PUBLIC/ZL-WIP{code}/Diva_ZL_{code}_WIP_complete_WIP.zip:
FLP/WAV/DivaH2P/MIDI/17FST/standardVSTpreset/proofs/FL20guide. A/B original0s,
candidate4.168s. Full export6mean={pub['original_objective_export_mean']};
independent extractedZIP/new6mean={pub['ZIP_replay_mean']}. These are unchanged
original-objective values, NOT similarity percentages or exact perceptual match.
ZIP SHA256={pub['complete_ZIP_SHA256']}.

MANDATORY nativebase={base}. Its complete source/state archive is
PUBLIC/{provenance['archive']}, SHA256={provenance['SHA256']}.
Setup restores/verifies it/source and installs fl20_curve.py and the native
exporter FROM CURRENT ZL{code}-validated-continuation/scripts after the older
embedded bootstrap. Do not use the old embedded core for current presets.
Restorer never overwrites different existing data; derived padded WAV samples
are compared bit-exact, allowing harmless WAV header timestamp differences.
This delta was tested separately; full installation of a new machine not claimed.

Only THREE incoming held notes41->37->36 perphrase, twice. Onframes
0/24000/48000/128000/152000/176000; off24000/48000/64000/152000/176000/192000;
velocity96/96/101 perphrase,48kHz. Upward motion uses Diva internal ARP up+dn2,
twooctaves,1/8,180BPM. No16short external notes. Preserve all12MIDI events andADSR.
Original P/diva-lead/v83-wip/Diva_original_lead_reference.wav is ANALYSIS/A-B ONLY,
SHA2567617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f.
Never mix reference samples into synthesis or add reference-conditioned noteautomation.

Actual source remains N/source-bases/FL05_OscMix_6p5, sourceOscMix6.5 after
fixed independent48pairs passed1.347429927->1.344884890 SEM.000404493; earlier
inconclusive12 was NOT accepted. Other280parameters/12MIDI unchanged vs6.3.
H2P and actualeffSetChunk raw/all281/chunk checks exact, freshDiva H2P/FLPchunk
wholechain proof in earlierZL17research. Againstv83 onlyOscMix5.71->6.5,
PWModDepth0->+1KeyFollow2,VCA ModDepth-68->-58. Noise0,Drift24.8,Pan-39.33,
PlateWet1.12/ARP/ADSR preserved. Source48all96WAV lossless in3SHAverifiedparts.
Original200MBblob41e9bf7d7adba68226614297644c9661181bff6d retained in Git and
protected local pre-split ref; redundant /tmp bundle was verified then evicted.

Current effects:12actual supplied native stockFX plus official free ZLEqualizer2
v1.4.1 WindowsVST3 onSUM. Old Finish12416frames retired. ZLMinimumPhase/lookahead0,
declaredPDC0/impulsefirst0, nativegraphfirst2frames; no wholeDAW/ASIO0 assertion.
ZL PE SHA2563269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d.
Native small NONZERO block-size dependence is measured; don't claim invariance.
Current topology still12staticPeak+4AllPass+6dynamicPeak+OutputGain,87physicalparams.
Use actualcomponentXML/610readbacks, NOT stale inherited arrays listing4dynamic.
Extra staticfilters in slots22/23 failed independent12 and were NOT adopted;
their proposed migration scripts are research only and uninstalled.

Preserve all nativeCurve2parent+4local+8detail coefficients and OPTIONAL supported
32fine coefficients (format smooth_fine_bumps32_v1, centers.02..64, widths.0125).
Fine basis alters existing129point nativeWaveShaper curve, never MIDI. Allzero
fine metadata preserves legacyhash/output. Optional waveshaper_native_controls
raw[Preamp,Mix,Post] bounds[64..192,0..128,0..128], defaults128/128/128 unchanged.
ActualDLL regressions proved changes stay changed, saves/resaves byteexact,
cold nativeaudio exact0, original2e-7 gate unchanged. Keep fine metadata in
fingerprint/export/replay, not only in a sidecar or x95vector. Saved nativebundle
may load ONLY when x95/allcurvelevels/controls/Chorusoverrides fingerprintmatches.
Otherwise it must not overwrite a changed trial. Canonical exported nativeaudio
comes from ACTUAL serialized nativepresets, SDK-vs-FST residual diagnostic only.

ZL20 first mixedwarm/cold zero check failednative6.26e-7/whole1.49e-6; original
failedZIP/code/captures preserved. Three fresh chains/eightdiagnosticcaptures
gave exact0; cause NOT established. Current finalizer compares original and
two extractedZIP native+ZL instances under identical fresh conditions. All
12nativebytes, native2e-7 and wholefloat32rtol8eps/atol1e-12 UNCHANGED. Hot/wet
history is separate diagnostic, never claim arbitrarynativehotcold exactness.

Research outcomes backed: source22PWM/sync REJECTED; WS19controls310 REJECTED;
source25Drift/Plate REJECTED; unusedstaticfilters1129 REJECTED; nativeEQ76cycle04
1409cases REJECTED paired12gain.000980<3SEM.001635. No re-test-until-pass.
Fine32study513cases passed independent12:1.331061557834->1.328437636044,
SEM.000751500573, actualnative12statebytes andzeroDepth0, monotonecurvevalid.
Adopt only after supportednewbase/fullFLP/actualZIP replay/normalpush; inspect
N/NATIVE_WS_FINE32_FULL_KIT_ADOPTION.json and latest actual main/base before use.

Paths P=/workspace/divalead,N=/workspace/divalead-work/native-low-latency-effects,
R=/workspace/divalead-work/three-held-continuation,B=/tmp/divalead-local-1625,
D=B/internet-plugins-20261023,W=/tmp/divalead-native-effects,S=/workspace/divalead-setup.
PY=/workspace/.venvs/divalead/bin/python -B; PYTHONPATH=D:W:B,OPENBLAS_NUM_THREADS=1,
OMP_NUM_THREADS=1,PYTHONDONTWRITEBYTECODE=1. Wine S/sysroot/usr/lib/wine/wine64,
WINEPREFIX=S/wine2 forDiva/ZL or W/wine fornative; WINEDLLPATH=S/sysroot/usr/lib/
x86_64-linux-gnu/wine,WINEDEBUG=-all,DISPLAY=:90. NativeEXEs must reside inW beside
QuickFontCache/dsp_ipp/freetype/zlib dependencies. Supplied Diva(x64).vst3 isVST2.

Before starting jobs inspect N/FL20_ZL_CONTINUOUS_CONTROLLER.json AND actual
/proc/PID/statstarttime/cmdline/hosts. BEST D/ZL-continuous65/BEST_CANDIDATE.json
and realcomponent authoritative. Do not duplicate existing main/watcher/finite jobs.
Main4actualVST3workers,3freshnativeinputs,twoheldouts,freshpaired6; gain must exceed
max(.0005,3SEM), save/resavebytes and2NEWcoldinstances rtol8eps/atol1e-12.
Directory continuous65 is historical name, now87. Ownernumericpause
external-ZL-continuous65-refinement. Legacy stockmatcher/Finishpublisher retired;
keep N/fl20-corrected-search.stop. Finite ownedstops N/zl-continuation.stop and
zl-useful-full-backup.stop; remove only matching owner after safe completed boundary.
For fine32 owner native-WS-fine32-finite-refit-20261024; read WS_FINE32_SEQUENTIAL_CONTROLLER
and ZL_NATIVE_WS_FINE32_STUDY_STATE plus realhosts if main is temporarily stopped.
Wrapper resumes main/watcher after acceptance/rejection/failure. WatcherPID alone
can be a short-lived publisher, verify exact scriptcmdline. Don't restart stalePIDs.

Objective FeaturesOriginal local_full_original_criteria_FL20_context_v1 is fixed:
.65tone+.35standard+.05abs(logRMSgain)+clip+tinyEQregularizer. Align819/fixededit.
No score/tolerance/alignment changes to fake improvement. Nativeonly can worsen
while combinednative+ZL improves; judge fresh completechain against original.
Reference video known HE-AACv2~32kbps: prior codecafterDSP tests failed and were
diagnostic only. Don't put a high-latency codec into keyboard productionchain.

Git normal scoped pushHEAD:main, noforce. R/auto-backup-Git.lock flock plus owned
auto-backup.pause; cleanup owner authorized-local-backed-copy-cleanup-20261023.
Preserve older fullkit/release treeOIDs. Split evidence>80MiB into64MiBparts;
GitHub100MiB blob cap. Retry only transientnetwork failures. aggregate SHA uses
Gitblobs for missing skipworktree files and excludes intentional stageddeletions.
Many exact oldZIP/proof/prefix/selected worktree duplicates evicted after origin
proof; restore individually with git restore --ignore-skip-worktree-bits -- path.
All publicversions/history retained, actualprivate selectedWAVs/states unaffected.
Some oldprivate auxrepeat/A-B bytes explicitly pruned and NOT claimedremotebacked.
Complete actual native diagnostics127MB losslessly13MBtar.xz in a46e033c checkpoint;
private WAV/F32/failedZIP duplicates offloaded only after archiveSHA/Gitexactness.
Restore chosenmember from recordedGitarchive; don't restoreall largefiles blindly.

Setup is a SAVED REVIEW DRAFT requiring Publish, not automatically applied.
User's ongoing actual matching work is not blocked on that UI step. Continue.
'''
start=start.rstrip()+'\n';(S/f'start-ZL{code}-current.md').write_text(start)
config=dict(install_script=script,start_skill=start,repositories=[dict(name='Ananas2000/divalead',host='github.com',commit=head,mount_path='divalead')]);(S/'proposed-latest-ZL-environment-config.json').write_text(json.dumps(config));print(json.dumps(dict(code=code,HEAD=head,native_base=str(base),native_archive_SHA256=provenance['SHA256'],bash_syntax_passed=True,install_chars=len(script),start_chars=len(start))))
