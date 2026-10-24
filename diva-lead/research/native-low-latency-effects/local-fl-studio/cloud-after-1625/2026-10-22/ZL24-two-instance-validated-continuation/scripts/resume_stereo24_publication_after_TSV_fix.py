"""Finish staged full-kit publication after lossless empty-field TSV formatting."""
from pathlib import Path
import csv,datetime,fcntl,gzip,hashlib,io,json,os,runpy,shutil,zipfile
A=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo24_scoped_publication_resume')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];ROOT=A/'FL20_ZL24_STEREO_WIP';archive=A/'Diva_ZL24_STEREO_WIP_complete.zip';dest=PUBLIC/'ZL-WIP24';research=PUBLIC/'ZL24-two-instance-validated-continuation';pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='losslessly format two empty final TSV cells and finish owned staged stereo24 publication'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);before=git('rev-parse','HEAD');assert before=='033d396107a1682b0bff1639d8c35e355383affd';assert git('ls-remote','origin','refs/heads/main').split()[0]==before
  assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);proof=[]
  for name in ['PRIMARY_610_PARAMETERS.tsv','POST_610_PARAMETERS.tsv']:
   p=ROOT/'verification'/name;raw=p.read_bytes();text=raw.decode();normalized='\n'.join(line+'""'if line.endswith('\t')else line for line in text.splitlines())+'\n'
   old=list(csv.reader(io.StringIO(text),delimiter='\t'));new=list(csv.reader(io.StringIO(normalized),delimiter='\t'));assert old==new and len(old)==611
   (p.parent/(name+'.raw.gz')).write_bytes(gzip.compress(raw,mtime=0));p.write_text(normalized);proof.append(dict(file=name,all610_parameter_cells_identical=True,raw_original_SHA256=hashlib.sha256(raw).hexdigest(),original_raw_dump_preserved_as_gzip=True))
  (ROOT/'verification/TSV_EMPTY_FINAL_FIELD_FORMAT_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
  (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for p in sorted(ROOT.rglob('*')):
    if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
  with zipfile.ZipFile(archive)as z:
   assert z.testzip()is None
   for p in ROOT.rglob('*'):
    if p.is_file():assert z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix())==p.read_bytes()
  build=read(A/'ZL24_FINAL_BUILD_COMPLETION.json');build.update(ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),ZIP_bytes=archive.stat().st_size,TSV_empty_field_formatting_is_lossless=True,raw_actual_dumps_also_preserved=True);(A/'ZL24_FINAL_BUILD_COMPLETION.json').write_text(json.dumps(build,indent=2)+'\n')
  shutil.copytree(ROOT,dest,dirs_exist_ok=True);shutil.copyfile(archive,dest/archive.name);shutil.copyfile(A/'ZL24_FINAL_BUILD_COMPLETION.json',research/'ZL24_FINAL_BUILD_COMPLETION.json');shutil.copyfile(Path(__file__),research/'scripts'/Path(__file__).name)
  packs=set((P/'.git/objects/pack').glob('*.promisor'));h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete ZL24 stereo WIP with two real zero-PDC ZL instances and extracted ZIP replay');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert set((P/'.git/objects/pack').glob('*.promisor'))==packs
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.mp3',dest/'FL_STUDIO_RU.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP24',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='06',requires_two_ZL_instances=True,original_objective_export_mean=build['mean_new_native_original_objective_with_regularizer'],ZIP_replay_fixed_native_input_max_abs_errors=[0.,0.],ZIP_replay_is_two_cold_instances_not_six_new_native_renders=True,HTTP_checks=checks,old_full_kit_and_PC_GUI_tree_OIDs_preserved=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (A/'ZL24_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
