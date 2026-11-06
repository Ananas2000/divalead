"""Archive a closed immutable study in bounded subsets; verify all before release.

Each part uses the existing archiver and its unchanged48MiB staging guard.
Symlink inputs avoid duplicating audio and are archived as exact regular bytes.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--label',required=True);p.add_argument('--note',required=True);p.add_argument('--retain-original-audio',action='store_true');p.add_argument('--resume-verified-parts',action='store_true');args=p.parse_args()
J=Path(__file__).resolve().parent;R=Path(args.root);O=J.parent/'stereo-refinement-20261025';P=Path('/workspace/divalead')
completion=json.loads((R/'completion.json').read_text());assert completion['not_adopted'] is True;assert not completion['robust_improvement']or args.retain_original_audio,'Positive pending-export study must retain original audio'
files=[f for f in sorted(R.rglob('*'))if f.is_file()and f.suffix not in ['.f32','.dll','.exe']]
inventory=[dict(name=f.relative_to(R).as_posix(),bytes=f.stat().st_size,SHA256=hashlib.sha256(f.read_bytes()).hexdigest())for f in files]
assert inventory;groups=[];group=[];size=0
for row in inventory:
    if row['bytes']>96*2**20:
        if group:groups.append(group);group=[];size=0
        assert shutil.disk_usage('/workspace').free>row['bytes']+48*2**20,'Existing large member plus original48MiB guard must fit; preserve source'
        groups.append([row]);continue
    if group and size+row['bytes']>96*2**20:groups.append(group);group=[];size=0
    group.append(row);size+=row['bytes']
if group:groups.append(group)
base=Path('/tmp')/(args.label+'-immutable-split-inputs');base.mkdir(exist_ok=args.resume_verified_parts);plan=dict(original_closed_root=str(R),original_inventory=inventory,parts=len(groups),target_input_subset_bytes=96*2**20,existing_larger_single_members_get_own_part_with_original48MiB_guard=True,all_results_rejected=not completion['robust_improvement'],quality_passed_but_not_adopted=completion['robust_improvement'],reference_match_reached=False)
if(base/'COMPLETE_ORIGINAL_INVENTORY.json').exists():assert json.loads((base/'COMPLETE_ORIGINAL_INVENTORY.json').read_text())==plan
else:(base/'COMPLETE_ORIGINAL_INVENTORY.json').write_text(json.dumps(plan,indent=2)+'\n')
receipts=[]
for k,group in enumerate(groups,1):
    label=args.label+f'-part{k:02d}of{len(groups):02d}'
    receipt_path=O/(label+'_PUBLICATION.json')
    if args.resume_verified_parts and receipt_path.exists():
        receipt=json.loads(receipt_path.read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified'];members=json.loads((P/receipt['public_path']/'ARCHIVE_MEMBER_SHA256.json').read_text());lookup={r['name']:r for r in members}
        for row in group:assert lookup[row['name']]['SHA256']==row['SHA256']and lookup[row['name']]['bytes']==row['bytes']
        receipts.append(dict(part=k,commit=receipt['commit'],public_path=receipt['public_path'],original_members=group));continue
    part=base/f'part-{k:02d}';part.mkdir()
    for row in group:
        source=R/row['name'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['SHA256'];dest=part/row['name'];dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(source.absolute())
    shutil.copyfile(base/'COMPLETE_ORIGINAL_INVENTORY.json',part/'COMPLETE_ORIGINAL_INVENTORY.json')
    (part/'THIS_PART_ORIGINAL_MEMBERS.json').write_text(json.dumps(group,indent=2)+'\n')
    label=args.label+f'-part{k:02d}of{len(groups):02d}'
    subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(O/'backup_complete_finite_study.py'),'--root',str(part),'--label',label,'--note',args.note+f' Closed study split{k}/{len(groups)}. COMPLETE_ORIGINAL_INVENTORY.json lists whole original study; THIS_PART_ORIGINAL_MEMBERS.json identifies this subset. Reassemble all parts into one directory preserving relative paths. No new sound accepted.'],check=True)
    receipt=json.loads((O/(label+'_PUBLICATION.json')).read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified']
    members=json.loads((P/receipt['public_path']/'ARCHIVE_MEMBER_SHA256.json').read_text());lookup={r['name']:r for r in members}
    for row in group:assert lookup[row['name']]['SHA256']==row['SHA256']and lookup[row['name']]['bytes']==row['bytes']
    receipts.append(dict(part=k,commit=receipt['commit'],public_path=receipt['public_path'],original_members=group))
    (J/(args.label+'_PARTIAL_REMOTE_PROOF.json')).write_text(json.dumps(dict(plan=plan,verified_parts=receipts),indent=2)+'\n')
# All original bytes are checked again BEFORE removing any source cache copy.
for row in inventory:assert hashlib.sha256((R/row['name']).read_bytes()).hexdigest()==row['SHA256']
released=[]
for row in inventory:
    f=R/row['name']
    if not args.retain_original_audio and(f.suffix=='.wav'or f.name.endswith('.tar.gz')):f.unlink();released.append(row)
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_closed_root=str(R),all_original_members_remote_verified=True,all_parts=receipts,released_only_verified_closed_audio_caches=released,source_native_states_and_metadata_kept=True,not_adopted=True,reference_match_reached=False)
(J/(args.label+'_COMPLETE_PUBLICATION.json')).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(parts=len(groups),original_members=len(inventory),original_root=str(R),all_original_members_remote_verified=True,not_adopted=True,reference_match_reached=False)),flush=True)
