from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,urllib.request,fcntl
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
prefix=(D/'publish_ZL05_kit.py').read_text().split("assert read(PAUSE)['owner']==OWNER")[0]
exec(compile(prefix,'ZL05-publisher-definitions','exec'),globals())
assert read(PAUSE)['owner']==OWNER
with(R/'auto-backup-Git.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before;old=protected()
 dest=PUBLIC/'ZL-WIP05';research=PUBLIC/'ZL05-export-and-storage-cleanup';scripts=research/'scripts';canonical=research/'canonical-export-input'
 raw=canonical/'ZL_joint_parameters.tsv';blob=gzip.compress(raw.read_bytes(),mtime=0);assert gzip.decompress(blob)==raw.read_bytes();(canonical/(raw.name+'.gz')).write_bytes(blob);raw.unlink()
 shutil.copyfile(D/'publish_ZL05_kit.py',scripts/'publish_ZL05_kit.py');shutil.copyfile(D/'finish_ZL05_publication.py',scripts/'finish_ZL05_publication.py')
 aggregate_hashes();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
 assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
 git('commit','-m','Save verified ZL05 full FL20 kit and restorable remote-backed local storage cleanup');commit=git('rev-parse','HEAD')
 assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
 subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
 checks=[]
 for rel in [f'ZL-WIP05/{LABEL}_complete_WIP.zip','ZL-WIP05/AB_REFERENCE_ZL05_WIP.mp3','ZL-WIP05/FL_STUDIO_RU.md','ZL05_CONTINUATION_RU.md']:
  p=PUBLIC/rel;url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix()
  with urllib.request.urlopen(url,timeout=40)as r:b=r.read()
  assert b==p.read_bytes();checks.append(dict(path=rel,bytes=len(b),HTTP_byte_exact=True))
 receipt=dict(commit=commit,previous_HEAD=before,full_kit='ZL-WIP05',all_old_full_kit_and_numbered_release_tree_OIDs_preserved=True,HTTP_checks=checks,complete_ZIP_SHA256=hashlib.sha256((B/(LABEL+'_complete_WIP.zip')).read_bytes()).hexdigest(),reference_match_reached=False)
 (N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
