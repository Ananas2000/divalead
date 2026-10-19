"""Evict only byte-identical historical private WAV copies already in committed Git."""
from pathlib import Path
import os,json,subprocess,hashlib,shutil,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');plan=json.loads((R/'published-audio-cache-plan.json').read_text());rows=plan['files'];assert rows and plan['current_three_held_tree_excluded']
head=rows[0]['commit'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==head
assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=REPO,text=True).split()[0]==head
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
objects=subprocess.check_output(['git','cat-file','--batch-check'],input='\n'.join(sorted({r['blob'] for r in rows}))+'\n',cwd=REPO,text=True).splitlines();assert all(len(x.split())==3 and x.split()[1]=='blob' for x in objects)
ledger=R/'published-audio-cache-eviction.json';assert not ledger.exists();before=shutil.disk_usage(R).free
record=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase='planned',all_data_retained_in_persistent_Git_and_public_worktree=True,all_files_byte_identical_to_committed_blob=True,current_three_held_and_actual_runtime_dependencies_excluded=True,source_commit=head,free_bytes_before=before,files=rows)
ledger.write_text(json.dumps(record,indent=2)+'\n');count=0
for row in rows:
 p=Path(row['path']);master=REPO/row['repository_path'];assert R not in p.parents
 assert p.read_bytes()==master.read_bytes() and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256']
 p.unlink();count+=1
record.update(phase='complete',private_cache_paths_evicted=count,free_bytes_after=shutil.disk_usage(R).free);ledger.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='files'}),flush=True)
