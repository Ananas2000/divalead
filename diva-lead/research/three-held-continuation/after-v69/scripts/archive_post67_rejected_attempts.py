"""Losslessly preserve completed fresh quality rejections, without validation claims."""
from pathlib import Path
import hashlib,json,re,tarfile
R=Path(__file__).resolve().parent;T=Path('/tmp/divalead-post67-rejected-completed')
assert not T.exists();T.mkdir()
files={};cases=[]
for v in sorted(R.glob('pw5190-verified-live-*')):
    match=re.fullmatch(r'pw5190-verified-live-(main|phase|balance)-(\d+)-(hf|gain|fine55|phase18|balance42|power69)',v.name)
    if not match or (v/'validation.json').exists():continue
    role,index,kind=match.groups()
    if int(index)<(31 if role=='phase' else 2):continue
    run=R/('pw5190-live-'+role)/('round-'+index+'-'+kind);decision=run/'decision.json'
    if not decision.exists():continue
    d=json.loads(decision.read_text())
    if d.get('full_proof_completed') is not False:continue
    assert d['accepted'] is False and d['arbitrary_cases_NOT_claimed'] is True
    for p in sorted(v.rglob('*')):
        if p.is_file() and not p.is_symlink() and p.suffix not in {'.so','.dll','.exe','.pyc','.tmp','.lock'}:
            files[v.name+'/'+str(p.relative_to(v))]=p
    for name in ['decision.json','fit.log','validation.log']:
        p=run/name
        if p.exists():files[v.name+'/numeric-decision/'+name]=p
    cases.append(dict(candidate=v.name,accepted=False,full_proof_completed=False,arbitrary_cases_NOT_claimed=True))
archive=T/'POST67_REJECTED_COMPLETED.tar.gz';digests={}
with tarfile.open(archive,'w:gz',compresslevel=6,dereference=True) as tar:
    for name,p in files.items():
        digests[name]=hashlib.sha256(p.read_bytes()).hexdigest();tar.add(p,arcname=name,recursive=False)
with tarfile.open(archive,'r:gz') as tar:
    for name,digest in digests.items():assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==digest
report=dict(archive=archive.name,archive_bytes=archive.stat().st_size,archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    rejected_cases=cases,all_restored_member_SHA_verified=True,members_SHA256=digests,no_private_Diva_binary=True,match_reached=False)
(T/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
(R/'post67-rejected-archive-result.json').write_text(json.dumps(report,indent=2)+'\n')
print('COMPLETED_REJECTED_ATTEMPTS_ARCHIVED',len(cases),archive.stat().st_size,flush=True)
