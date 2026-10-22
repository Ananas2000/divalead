"""Restore the published GitHub date folder to the scripts' sessions layout.
Run from a full divalead checkout. Destination must be new; no existing files
are replaced. This copies project assets, never installed proprietary DLLs.
"""
from pathlib import Path
import argparse,json,shutil
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
dest=a.destination.resolve();assert not dest.exists(),'Choose a new destination folder'
source=ROOT/'2026-10-22'
if not source.exists():source=ROOT/'sessions/2026-10-22'
plan=json.loads((source/'UPLOAD_MANIFEST.json').read_text(encoding='utf-8'))
base='diva-lead/research/native-low-latency-effects/local-fl-studio/'
kitrel=Path('diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')
repo=next((x for x in [ROOT/'divalead',ROOT,*ROOT.parents]if(x/kitrel).is_dir()),None)
assert repo is not None,'Full repository checkout with checkpoint-WIP is required'
dest.mkdir(parents=True)
for row in plan:
    src=ROOT/row['repo'].removeprefix(base)
    if not src.is_file():src=ROOT/row['local']
    assert src.is_file(),src
    target=dest/row['local'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
shutil.copy2(source/'UPLOAD_MANIFEST.json',dest/'sessions/2026-10-22/UPLOAD_MANIFEST.json')
kit=repo/kitrel
shutil.copytree(kit,dest/'divalead'/kitrel)
inputs=dest/'sessions/2026-10-22/input';inputs.mkdir(exist_ok=True)
for name in ('Diva_NATIVE_WIP_THREE_HELD.h2p','Diva_SOURCE_FROZEN_48k.wav','Diva_original_lead_reference.wav','Diva_THREE_HELD_180BPM.mid','NATIVE_FULL_180BPM_WIP.wav'):shutil.copy2(kit/name,inputs/name)
shutil.copytree(kit/'presets',inputs/'presets')
ref=dest/'analysis-runtime/diva-lead/v55-wip/Diva_original_lead_reference.wav';ref.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(kit/'Diva_original_lead_reference.wav',ref)
for name in ('Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp','LOCAL_CONTINUATION_RU.md'):assert(dest/'sessions/2026-10-22'/name).is_file()
print(json.dumps(dict(destination=str(dest),copied_manifest_files=len(plan),ready_for_compile=True),ensure_ascii=False))
