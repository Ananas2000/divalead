"""Archive recoverable old rejected training logs before removing only their root-cache copies."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
V=Path(__file__).resolve().parent;A=V.parent/'pc-stereo-20261024/stereo-continuous87';O=V.parent/'stereo-refinement-20261025';R=Path('/tmp/divalead-old-rejected-numeric401-550-gz-20261104');R.mkdir();rows=[]
for n in range(401,551):
 d=A/f'cohort-{n:04}';p=d/'training-results.json.gz';c=d/'completion.json'
 if not(p.is_file()and(d/'heldout.json').is_file()):continue
 if c.exists()and json.loads(c.read_text()).get('robust_improvement')is not False:continue
 out=R/d.name;out.mkdir();shutil.copyfile(p,out/p.name)
 for name in ['heldout.json','completion.json']:
  if(d/name).is_file():shutil.copyfile(d/name,out/name)
 blob=p.read_bytes();rows.append(dict(original=str(p),archive_member=d.name+'/'+p.name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
assert rows and sum(r['bytes']for r in rows)>32*2**20
(R/'CLOSED_REJECTED_GZ_PROVENANCE.json').write_text(json.dumps(dict(all_selected_training_runs_have_completed_heldout_rows=True,all_accepted_cohorts_excluded=True,only_original_large_training_gz_caches_will_be_released_after_verified_publication=True,rows=rows),indent=2)+'\n');shutil.copyfile(Path(__file__),R/Path(__file__).name)
label='old-rejected-numeric401-550-training-gz-cache-20261104'
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(O/'backup_complete_finite_study.py'),'--root',str(R),'--label',label,'--note','Closed rejected cohorts401..550: exact training GZ plus heldout/negative summaries; all accepted cohorts excluded; root duplicate caches released only after archive memberSHA and remote Git verification'],check=True)
receipt=json.loads((O/(label+'_PUBLICATION.json')).read_text());assert receipt['all_retained_study_files_and_WAVs_remote_Git_verified'];members=json.loads((Path('/workspace/divalead')/receipt['public_path']/'ARCHIVE_MEMBER_SHA256.json').read_text());lookup={r['name']:r for r in members}
for row in rows:
 assert lookup[row['archive_member']]['SHA256']==row['SHA256'];assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest()==row['SHA256']
(V/'OLD_REJECTED_NUMERIC_GZ_401_550_RELEASE_PLAN.json').write_text(json.dumps(dict(publication=receipt,rows=rows),indent=2)+'\n');before=shutil.disk_usage('/workspace').free
for row in rows:Path(row['original']).unlink()
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),publication_commit=receipt['commit'],public_path=receipt['public_path'],rows=rows,actual_root_bytes_released=shutil.disk_usage('/workspace').free-before,all_summary_state_source_and_all_accepted_cohorts_kept=True,only_exact_remotely_backed_closed_rejected_training_gz_cache_released=True);(V/'OLD_REJECTED_NUMERIC_GZ_401_550_CACHE_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
