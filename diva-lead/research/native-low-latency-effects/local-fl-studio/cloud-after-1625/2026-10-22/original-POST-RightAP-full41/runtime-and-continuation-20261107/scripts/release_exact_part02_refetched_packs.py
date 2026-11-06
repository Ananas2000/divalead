from pathlib import Path
import datetime,json,shutil,subprocess
J=Path(__file__).resolve().parent;P=Path('/workspace/divalead');O=J.parent/'stereo-refinement-20261025';label='original-native12-POST-RightAP12800-Q25-current620-NEW12-passed-20261107-part02of06';receipt=json.loads((O/(label+'_PUBLICATION.json')).read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified']and receipt['resumed_after_environment_reconnect'];dest=P/receipt['public_path'];m=json.loads(next(dest.glob('*.ARCHIVE_MANIFEST.json')).read_text());known={r['OID']:r for r in m['parts']};assert len(known)==3
rows=[]
for name in ['pack-1df3f32b304430a525954b9fa449cee50b3cf434','pack-96898cfcbcf5e0c7ee3e4ae4d16aff0252c652bc','pack-9b82d3f9b09951a114337edbdc786c94f71fb3a3']:
 assert name!='pack-41e9bf7d7adba68226614297644c9661181bff6d';base=P/'.git/objects/pack'/name;pack=base.with_suffix('.pack');idx=base.with_suffix('.idx');assert pack.exists()and idx.exists()and base.with_suffix('.promisor').exists();out=subprocess.check_output(['git','verify-pack','-v',str(idx)],text=True);entries=[x.split()for x in out.splitlines()if len(x.split())>=5 and len(x.split()[0])==40 and x.split()[1]in['blob','tree','commit','tag']];assert entries and all(x[1]=='blob'and x[0]in known for x in entries);rows.append(dict(pack=str(pack),entries=entries,archive_OIDs_already_exact_HTTP_and_Git_verified=True,bytes=pack.stat().st_size))
assert {x[0]for row in rows for x in row['entries']}==set(known)
(J/'EXACT_PART02_REFETCHED_PACK_RELEASE_PLAN.json').write_text(json.dumps(dict(receipt=receipt,rows=rows),indent=2)+'\n');before=shutil.disk_usage('/workspace').free
for row in rows:
 base=Path(row['pack']).with_suffix('')
 for suffix in ['.pack','.idx','.promisor']:base.with_suffix(suffix).unlink()
subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL)
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,actual_root_bytes_released=shutil.disk_usage('/workspace').free-before,only_three_new_single_verified_archive_blob_promisor_caches_removed=True,protected_unknown_private_and_structural_packs_preserved=True,Git_connectivity_passed_without_lazy_fetch=True);(J/'EXACT_PART02_REFETCHED_PACK_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
