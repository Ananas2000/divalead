"""Record verified work and recovery boundaries without replacing history."""
from pathlib import Path
import datetime,json
W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
R=Path('/workspace/divalead-work/three-held-continuation');p=R/'start_skill_current.md'
joint=json.loads((N/'native-joint76-actual-integration-01/ACTUAL_INTEGRATION_PROOF.json').read_text())
assert joint['actual_76_coordinate_native_worker_executed']
state=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text())
best=json.loads((N/'NATIVE_BEST_CANDIDATE.json').read_text())
screen=json.loads((N/'native-Diva-sync-PW-fine-screen-01/SELECTION.json').read_text())
cross=json.loads((N/'native-cross-MS-branches-01/completion.json').read_text())
profile=json.loads((N/'native-Diva-cutoff148-profile-01/completion.json').read_text())
cleanup=json.loads((N/'COMPLETED_NATIVE_HOST_SCRATCH_CLEANUP.json').read_text())
old=p.read_text();marker='CURRENT VERIFIED NATIVE SOURCE/PW/PHASE FAMILY'
earlier=old[old.index(marker):] if marker in old else old
current='''CURRENT VERIFIED JOINT EQ CONTINUATION (2026-10-22 UTC). This section supersedes earlier current-state headers below. The user wants actual low-latency stock FL effects and THREE incoming held notes per phrase, continued matching to the ORIGINAL. Native transfer is still WORSE than v83 against the original. Neither 100% v83 transfer nor an original-reference match has been reached. Keep all numbered releases, root ZIPs and complete v83. Do not ask the user to assess each trial. No16-note transcription, no MistaTowa, no high-latency Finish fits.

The public kit remains a native95/common-phase kit:16 FST (4 mixer inserts,12 real native effects), actual Diva preset, the same THREE-held MIDI, source/full/edit WAV, A/B and FL_STUDIO_RU.md. SOURCE -> MID/SIDE -> SUM -> Master; SOURCE has WaveShaper, Chorus and the same signed Stereo Shaper phase pair. Read the actual Chorus SLOT MIX from current proof/guide; earlier8%/30% are obsolete. Incoming notes41->37->36 repeat twice at180BPM; the internal ARP makes upper movements. Source identity is EXPLICIT in NATIVE_BEST_CANDIDATE.json source_manifest, with durable raw/h2p hashes and independent actual Diva/all281/12event proof. Do not substitute old frozen-v83 audio for a PW-source candidate.

NEW ACTUAL WORK:35 actual Diva fine-sync/PW/FM/mix/filter cases were rendered through current real native effects, with3 independent full captures each and all281/12MIDI audits. Best apparent improvement was below the observed capture variability; NO source change was accepted. A new19-node experimental host tested two native EQ2/Stereo Shaper cross branches between Mid and Side. Zero cross contribution reproduced the old native graph EXACTLY at zero Chorus depth; a nonzero positive control changed audio.1397 actual fitting evaluations and6 fresh captures did NOT prove a robust win. The111-value cross family is EXPERIMENTAL/REJECTED, NOT supported by the public exporter/launcher: never feed it to native95 apply/export. A physical Diva cutoff148 source was independently re-rendered bit-exact, all281/12events checked, then given an actual4000-render EQ profile refit. Its fresh paired score did not robustly beat the incumbent, so that source was NOT adopted. These negative trials are retained to prevent repeating them as new findings.

JOINT76: search_native_joint_EQ_LBFGS.py now fits76 gain/matrix/frequency/bandwidth coordinates together, with real native DLL renders for every finite-difference derivative. No surrogate audio is used. Its bounded actual integration check passed, including two held-out real WS/Chorus/phase prefixes and six fresh whole-graph captures. It uses the same supported95-value deployable state and source_manifest. Exact experiment counts/results are in native-joint76-actual-integration-01, not a claim of perceptual completion. The controller alternates existing Chorus controls, coordinate fits,34-coordinate L-BFGS and this76-coordinate worker (generation%8==2). Candidate acceptance still requires a fresh whole-graph improvement beyond stochastic uncertainty; training prefixes are NEVER playback effects or reference-derived candidate audio.

One controller and4numeric workers only. NATIVE_JOINT76_HANDOFF.json records verified transfer of exact identities from the old controller; the idempotent launcher was checked twice. Read actual PID/starttime/cmdline and NATIVE_FINITE_BRANCH.json before inferring active computation. Four-slot finite experiments use SIGSTOP/SIGCONT on exact current numeric identities and always resume in finally. An alive controller heartbeat alone does not mean its numeric children are consuming CPU. Stop/pause controls remain native-search.stop/native-search.pause. Actual runtime and launch commands are in the earlier recovery section below; managed runtime is the15-node native95 family, NOT the rejected19-node test.

Native effect PDC0 and first impulse response2samples/48k are effect-only measurements; complete FL/interface latency and the FL GUI are not tested. All12 actual native states round-trip byte-exact and zero-Chorus-depth audio does too. Working Chorus LFO is free-running: use repeated captures, median by score, never a sample-identical modulated-audio claim. Fixed819-frame alignment/reference edit retained; only A/B is RMS normalized. Original audio is analyzed only, never used as candidate audio.

STORAGE: removed ONLY814 overwritten host-output scratch WAVs OUTSIDE completed experiment roots, recovering about2.09GB on/tmp. Every six-capture validation set inside each experiment, every release and public kit were preserved. See COMPLETED_NATIVE_HOST_SCRATCH_CLEANUP.json for exact sizes and SHA256. Old selective canonical-cache archives remain lossless/recoverable as documented below. Root volume is tight; generated heavy audio belongs on/tmp; native reserve root64MiB/tmp512MiB. Sync code/proofs to durable/workspace before handoff.

GIT: every writer must own exclusive R/auto-backup.pause, wait for idle Git coordinator phase paused_for_manual_Git_work, then hold R/auto-backup-Git.lock, verify clean local HEAD==origin/main, scope changes to native research, preserve numbered trees/root ZIP OIDs, push normally and verify remote bytes. Supplied DLL/EXE/RAR remain private. Default NativeChain behavior is unchanged; experimental cross_ms=True is only for the rejected test. Public source code is backed up, supplied dependencies are not redistributed.

RESTORE/cloud: no new runtime uploads, secrets or network rules are needed. Preserve proxy/CA/restricted package_managers settings. /tmp loss requires actual runtime restoration and real audio verification, not trusting saved PIDs. Saving a cloud draft is not applying/Publishing it. Full fresh-machine installation and FL GUI tests remain unclaimed. Earlier runtime restoration details remain below, while their source/best-score/controller-scheduling assertions are superseded by this section and current manifests.

'''
p.write_text(current+earlier)
(N/'JOINT76_CURRENT_GUIDE_STATE.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    best_loss=best['loss'],source_manifest=best['source_manifest'],controller_state=state,joint_actual_check=joint,
    source_screen=screen,cross_branch=cross,source_profile=profile,scratch_cleanup_files=cleanup['files'],
    scratch_actual_free_bytes=cleanup['actual_free_byte_increase'],reference_match_reached=False),indent=2)+'\n')
print('JOINT76_CURRENT_RECOVERY_GUIDE_SAVED',len(p.read_text()))
