"""Remove only exact duplicate private proof archives after public Git backup."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
P=Path('/workspace/divalead')
N=Path('/workspace/divalead-work/native-low-latency-effects')
prefix='diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/'
pairs=[
    ('ZL-two-free-static-slots-current20-01','extra-static-filters-two-free-slots-after-ZL20-study01'),
    ('Diva-Drift-Plate-current-native04-ZL-01','actual-Diva-Drift-Plate-native04-study01'),
    ('Diva-PWM-sync-current-native04-ZL-01-recovered','actual-Diva-22-PWM-sync-native04-rejected-study01'),
    ('ZL-native-WS19-controls-current-ZL-01','native-WS19-controls-current-ZL-study01'),
    ('ZL-native-EQ76-after-ZL17-03','native-EQ76-current-six-dynamic-ZL-cycle03'),
    ('ZL-native-WS16-after-EQ76-03','native-WS16-current-six-dynamic-ZL-cycle03'),
    ('ZL-native-base-rebase-adoption-03','native-final-context03-current-main-revalidation'),
    ('Diva-tone-actual-current-ZL-rebase02-01','actual-Diva-tone-current-ZL-source-study'),
]
commit=subprocess.check_output(['git','-C',str(P),'rev-parse','origin/main'],text=True).strip()
rows=[]
before=shutil.disk_usage('/tmp').free
for private,public in pairs:
    file=D/private/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
    if not file.is_file():continue
    relative=prefix+public+'/'+file.name
    child=subprocess.Popen(['git','-C',str(P),'show',commit+':'+relative],stdout=subprocess.PIPE)
    remotehash=hashlib.sha256();remote_size=0
    while block:=child.stdout.read(1024*1024):remotehash.update(block);remote_size+=len(block)
    assert child.wait()==0
    with file.open('rb')as stream:privatehash=hashlib.file_digest(stream,'sha256').hexdigest()
    assert privatehash==remotehash.hexdigest()and file.stat().st_size==remote_size
    row=dict(private_path=str(file),bytes=remote_size,SHA256=privatehash,backed_public_commit=commit,backed_public_path=relative,restore_command='git -C /workspace/divalead show '+commit+':'+relative+' > '+str(file))
    (file.parent/'REMOTE_EXACT_VALIDATION_ARCHIVE_EVICTION.json').write_text(json.dumps(row,indent=2)+'\n')
    file.unlink();rows.append(row)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=rows,freed_bytes=sum(r['bytes']for r in rows),observed_tmp_free_change=shutil.disk_usage('/tmp').free-before,all_audio_bytes_retained_in_public_Git=True,all_main_selected_WAVs_presets_sources_and_metadata_untouched=True)
journal=N/'COMPLETED_PRIVATE_VALIDATION_ARCHIVE_DUPLICATE_EVICTION.json'
if journal.exists():receipt['previous']=json.loads(journal.read_text())
journal.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k not in ['files','previous']}),flush=True)
