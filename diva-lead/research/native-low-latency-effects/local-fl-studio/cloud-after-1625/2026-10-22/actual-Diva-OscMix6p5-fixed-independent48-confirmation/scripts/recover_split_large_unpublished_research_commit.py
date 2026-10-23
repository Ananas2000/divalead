"""Amend only the rejected unpublished commit; normal push, no remote rewrite."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
D=Path(__file__).resolve().parent;s=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='split_commit_recovery_helpers');P=s['P'];N=s['N'];R=s['R'];PUBLIC=s['PUBLIC'];git=s['git'];read=s['read'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
original_commit='f3ed5c50';bundle=Path('/tmp/divalead-unpublished-pre-split-f3ed5c50.bundle');study=D/'ZL-Diva-source-OscMix6p5-independent48-adoption-01';dest=PUBLIC/'actual-Diva-OscMix6p5-fixed-independent48-confirmation';filename='FORTYEIGHT_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve rejected unpublished commit in verified bundle, split its overlarge proof archive without losing WAV bytes, amend only unpublished commit'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');s['fetch_main']();before=git('rev-parse','HEAD');assert before.startswith(original_commit);parent=git('rev-parse','HEAD^');assert git('rev-parse','origin/main')==parent;assert bundle.is_file();subprocess.run(['git','-C',str(P),'bundle','verify',str(bundle)],check=True);assert before in git('bundle','list-heads',str(bundle));old=s['protected']()
  original=dest/filename;source=study/filename;digest=sha(source);assert sha(original)==digest
  git('rm','--',original.relative_to(P).as_posix());s['copy_or_split_evidence_file'](source,dest)
  manifest=read(dest/(filename+'.SPLIT_ARCHIVE_MANIFEST.json'));assert manifest['original_SHA256']==digest
  for name in ['watch_ZL_useful_complete_backups.py','backup_finite_ZL_study.py','confirm48_Diva_OscMix6p5_and_adopt_if_robust.py','recover_split_large_unpublished_research_commit.py']:
   p=D/name;compile(p.read_text(),name,'exec');shutil.copyfile(p,dest/'scripts'/name)
  shutil.copyfile(N/'OSCMIX6P5_FIXED_INDEPENDENT48_PREDECLARED_PLAN.json',dest/'OSCMIX6P5_FIXED_INDEPENDENT48_PREDECLARED_PLAN.json')
  p=dest/'README_RU.md';p.write_text(p.read_text()+f'''\nАрхив всех96 WAV сохранён без изменения данных в трёх частях64MiB,
каждая ниже ограничения GitHub100MiB. Список и SHA256:
`{filename}.SPLIT_ARCHIVE_MANIFEST.json`.
Соединить перечисленные части по порядку, проверить исходные размер и SHA256,
затем открыть обычным tar/gzip. Исходный SHA256: `{digest}`.
Первый push большого файла был отклонён до публикации. Только этот локальный
неопубликованный commit исправлен через amend после проверенного Gitbundle;
удалённая история не переписывалась, forcepush не применялся. Все96 WAV сохранены.
''')
  proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rejected_unpublished_commit=before,remote_parent=parent,preservation_bundle=str(bundle),preservation_bundle_SHA256=sha(bundle),all96_WAVs_retained_without_reencoding=True,original_archive_SHA256=digest,part_manifest=manifest,only_unpublished_commit_will_be_amended=True,no_force_push=True,reference_match_reached=False);(dest/'OVERSIZE_ARCHIVE_RECOVERY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p)for p in dest.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n')
  s['aggregate']();git('add','--',str(dest.relative_to(P)),str((PUBLIC/'SHA256SUMS.txt').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(path.startswith(str(dest.relative_to(P))+'/')or path==(PUBLIC/'SHA256SUMS.txt').relative_to(P).as_posix()for path in git('diff','--cached','--name-only').splitlines());git('commit','--amend','--no-edit');commit=git('rev-parse','HEAD');assert git('rev-parse','HEAD^')==parent;assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items());s['push_and_confirm'](commit)
  for part in manifest['parts']:
   p=dest/part['name'];blob=s['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix());assert hashlib.sha256(blob).hexdigest()==part['SHA256']and len(blob)==part['bytes']
  assert not git('status','--porcelain');receipt=dict(commit=commit,previous_unpublished_commit=before,remote_parent=parent,all_old_full_kit_tree_OIDs_preserved=True,all96_WAVs_byte_exact_in_3_HTTP_verified_parts=True,source_confirmation_mean=read(study/'completion.json')['candidate_mean'],reference_match_reached=False);(N/'SOURCE48_SPLIT_BACKUP_RECOVERY.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SOURCE48_SPLIT_BACKUP_RECOVERED',json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
