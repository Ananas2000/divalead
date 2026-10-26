"""Keep old complete kits in Git; release verified redundant checkout ZIPs."""
from pathlib import Path
import hashlib,json,runpy,subprocess
H=Path(__file__).resolve().parent;h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='old_zip_cache_only');P,PUBLIC=h['P'],h['PUBLIC'];git=h['git'];assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','origin/main');assert git('rev-parse','HEAD')==commit;rows=[]
for k in range(24,32):
 p=PUBLIC/f'ZL-WIP{k}'/f'Diva_ZL{k}_STEREO_WIP_complete.zip'
 if not p.exists():continue
 rel=p.relative_to(P).as_posix();b=p.read_bytes();oid=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert git('rev-parse','HEAD:'+rel)==oid and git('rev-parse',':'+rel)==oid;assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+rel)==b
 git('update-index','--skip-worktree','--',rel);p.unlink();rows.append(dict(path=rel,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest(),Git_blob_OID=oid,remote_commit=commit,HTTP_byte_exact=True,index_and_remote_kit_retained=True))
assert not git('status','--porcelain');result=dict(files=rows,bytes=sum(r['bytes']for r in rows),only_verified_old_public_checkout_ZIP_copies_removed=True,current32_and_sourcebases_and_all_presets_WAVs_history_PC_tree_private_refs_preserved=True,restore='git show HEAD:path > destination, or download exact recorded commit URL; clear skip-worktree for that path before normal checkout if needed');(H/'VERIFIED_OLD_LOCAL_KIT_ZIP_CACHE_RELEASE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='files'}),flush=True)
