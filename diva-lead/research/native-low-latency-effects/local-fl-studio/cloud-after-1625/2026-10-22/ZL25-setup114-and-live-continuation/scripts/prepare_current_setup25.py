"""Preserve setup113; add the actually executed two-component WIP25 smoke."""
from pathlib import Path
import json,subprocess
H=Path(__file__).resolve().parent;S=Path('/workspace/divalead-setup');P=Path('/workspace/divalead')
draft=json.loads((H/'BACKEND_DRAFT_BEFORE_WIP25.json').read_text());assert draft['revision']==113
public='diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
delta='''

# WIP25: current complete kit retains BOTH official ZL instances and THREE
# Side AllPass bands in POST. Older startup fixtures above are historical
# readiness checks, not the production chain or an auto-start matching job.
PYTHONPATH="$zl_runtime" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 "$zl_python" \\
 /workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL25-runtime-handoff-20261025/scripts/verify_current_stereo_environment_runtime.py \\
 --kit ZL-WIP25 --receipt /workspace/divalead-setup/STEREO25_ENV_STARTUP_PROOF.json
'''
script=draft['install_script']+delta;path=S/'scripts/setup-current-STEREO25.sh';path.write_text(script);subprocess.run(['bash','-n',str(path)],check=True)
header='''# Current complete WIP25: three held notes, fixed three-band POST, two ZL instances

Read repository start_skill_current.md FIRST; its newest headers override older
snapshots appended below. Current complete kit PUBLIC/ZL-WIP25/
Diva_ZL25_STEREO_WIP_complete.zip SHA256
82bbb71f01d3eaab39ba13b6f3f222ce3be143cebdd4a74820d271d246fe216e.
PUBLIC=diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22.
Read PUBLIC/ZL25_CONTINUATION_RU.md and
PUBLIC/ZL25-runtime-handoff-20261025/README_RU.md for current recovery scripts.

Topology REQUIRED: native12/base06/fine32 -> PRIMARY -> POST ZL. Primary at
fullkit25 is accepted stereo-cohort15, POST Side AllPass10000Hz/Q2 +2200Hz/Q4
+895.8Hz/Q13.84. Three bands inside SECOND ZL, not three ZL instances.
Post SHA256 51dd979271b5fbfda5cffbd8cb71796009a5b3cc305289bbf9c472c672a7a96e.
The current matcher freezes POST from adopted BEST, never hardcoded old24.
Both MinimumPhase/lookahead0/AutoGainOFF. Actual complete ZIP and two cold
runtime replay exact0/0; actual generic startup component roundtrips/PDC0/
impulse0 passed. These are not GUI/ASIO/wholeDAW or fresh-machine claims.
New25 FLP is serialized/parsed/ZIP-replayed but Windows GUI opening pending.

Fresh6gain.001388351833 SEM.000015055695 > unchangedthreshold.0005,
cold2+.001292979650/+.001385139518. NativeDLL renders on preserved actual
Diva source, not new Diva synth instances or new GUI exports. All30studyWAV
remote lossless in lowmid-Side-phase-after-cohort15-20261025.300–800Hz left
bias improved~4.8to4.2dB vsoriginal~1dB, so residuals remain. FullmatchFALSE.
Preserve sourceDiva281/ARP/ADSR/three incoming held notes41-37-36 per phrase
twice/native06/fine32/routes. No MistaTowa or referenceaudio in synthesis.

A=/workspace/divalead-work/pc-stereo-20261024,
N=/workspace/divalead-work/native-low-latency-effects,
D=/tmp/divalead-local-1625/internet-plugins-20261023,
B=/tmp/divalead-local-1625,W=/tmp/divalead-native-effects.
Current A/continue_stereo_ZL_matching.py, N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json
and A/stereo-continuous87/BEST_CANDIDATE.json are authoritative. Check actual
PID/starttime/cmdline/four real VST3 hosts; snapshots do not prove a live job.
2workers*2ZL, PRIMARY87params, POST immutable per run. Originalobjective/
819alignment/weights/fresh6 max(.0005,3SEM)/cold2positive/strictcoldtolerances
unchanged. EXTRA upperstereo RMS<=1.5dB/max|LR|<=1.6dB over2–5/5–10/10–14kHz;
also lowmid300–800LRerror<=3.35dB to preserve new repair. Autoacceptedstages
publishALL24WAV plus full playable FLP/FST/WAV/h2p/MIDI ZIP. Publisher now
uses full_public_kit_directory and artifact_layout.json, keeps both effects.

Old single-stage matcher/watcher stay retired via N/zl-continuation.stop and
zl-useful-full-backup.stop owner two-ZL-stereo24-retired-single-stage. Newstop
N/zl-stereo-continuation.stop,newpause zl-stereo-numerical.pause. Do not remove
another owner's pause. Check livejob before any restart. To restore absent A
scripts copy five public runtime scripts, preserve different existing files.
Restore absent BEST from CURRENT_BEST_AT_HANDOFF.json only after paths/state
checks; do not overwrite newer accepted work. All archived fullkits/PCGUI
must survive. User wants continued independent work, no per-trial questions.

Old verified public audio worktree caches may be absent via skip-worktree;
public Git history/fullkits remain. Structural promisor packs preserve refs,
old blobcache holes expected. Fetch individual needed files, never bulk
two-treegitdiff/ls-tree--long. Privateoriginalsource48 and its archive ref
must survive. Root208MiB/tmp128MiB storage guards. APIquota% unavailable,
back completed useful stages immediately. No new complete fresh-machine
bootstrap execution is claimed; only syntax/full local smoke delta checked.

'''
start=header+draft['start_skill'];(S/'start-current-STEREO25.md').write_text(start)
proposal=dict(install_script=script,start_skill=start)
(S/'proposed-STEREO25-environment-config.json').write_text(json.dumps(proposal,indent=2)+'\n')
(H/'SETUP25_PREPARATION.json').write_text(json.dumps(dict(base_draft_revision=113,full_install_preserved_as_prefix=True,script=str(path),shell_syntax_passed=True,new_generic_startup_actually_executed=True,all_existing_network_secrets_environment_preserved=True,full_machine_rebootstrap_not_claimed=True),indent=2)+'\n')
print('Full setup syntax passed; preparation complete; not yet saved.')
