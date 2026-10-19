"""Retain8 real quality probes and the rejected initial gain attempt losslessly."""
from pathlib import Path
import hashlib,io,json,tarfile
ROOT=Path(__file__).resolve().parent;DEST=Path('/tmp/divalead-pw-diagnostics-archive');DEST.mkdir(exist_ok=False)
sources=[(Path('/tmp/divalead-pw5190-accuracy'),'accuracy'),
         (ROOT/'source-pw5190-accuracy-control','accuracy-control'),
         (ROOT/'pw5190-verified-gain-0001','rejected-gain-actual'),
         (ROOT/'pw5190-gain-research','rejected-gain-numeric-run'),
         (Path('/tmp/divalead-pw5190-gains'),'rejected-gain-numeric-scratch')]
assert json.loads((sources[0][0]/'completed.json').read_text())['trials']==8
decision=json.loads((ROOT/'pw5190-gain-research/decision.json').read_text())
assert not decision['accepted'] and not decision['full_proof_completed']
assert not (ROOT/'pw5190-verified-gain-0001/validation.json').exists()
files=[]
for folder,prefix in sources:
    for path in sorted(folder.rglob('*')):
        if path.is_file() and not path.is_symlink() and path.suffix not in {'.so','.dll','.exe','.pyc','.tmp','.lock'} and '__pycache__' not in path.parts:
            files.append((path,prefix+'/'+str(path.relative_to(folder))))
for name in ['probe_pw5190_accuracy.py','run_pw5190_accuracy_probe.py','fit_pw5190_gains.py',
             'run_pw5190_gain_research.py','three_gain_interior_projection.py','repair_pw5190_gain_all_guards.py']:
    files.append((ROOT/name,'scripts/'+name))
archive=DEST/'PW_accuracy_and_REJECTED_initial_gain.tar.gz'
members={};seen={};logical=unique=0
with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
    for path,name in files:
        assert name not in members
        content=path.read_bytes();digest=hashlib.sha256(content).hexdigest();logical+=len(content)
        members[name]=dict(SHA256=digest,bytes=len(content))
        info=tarfile.TarInfo(name);info.mtime=0
        key=(len(content),digest)
        if key in seen:
            info.type=tarfile.LNKTYPE;info.linkname=seen[key];tar.addfile(info)
        else:
            info.size=len(content);tar.addfile(info,io.BytesIO(content));seen[key]=name;unique+=len(content)
with tarfile.open(archive) as tar:
    assert set(tar.getnames())==set(members)
    for member in tar:
        assert hashlib.sha256(tar.extractfile(member).read()).hexdigest()==members[member.name]['SHA256']
assert archive.stat().st_size<50_000_000
report=dict(actual_accuracy_source_renders=8,accuracy_improvement_accepted=False,
    initial_gain_rejected=True,initial_gain_full_arbitrary_cases_NOT_claimed=True,
    rejected_guard_excess=dict(envelope_absolute=2.254831044101735e-11),
    stronger_all_guard_projection_is_a_SEPARATE_proved_candidate='pw5190-verified-gain-interior-0001',
    all_members_SHA_verified=True,all_original_bytes_and_paths_restorable=True,
    file=archive.name,archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),archive_bytes=archive.stat().st_size,
    logical_uncompressed_bytes=logical,unique_uncompressed_bytes=unique,members=members,match_reached=False)
(DEST/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='members'}),flush=True)
