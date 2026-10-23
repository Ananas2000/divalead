"""Restore a corrected FL05/native WIP from Git assets into a NEW workspace.

Requires the existing prepared native-DLL runtime separately. Never overwrites
active hosts, user projects or existing research result folders.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,shutil,subprocess,zipfile
import numpy as np
import soundfile as sf
p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True)
p.add_argument('--repository',type=Path,default=Path('/workspace/divalead'))
p.add_argument('--checkpoint');args=p.parse_args()
dest=args.destination.resolve();assert not dest.exists(),'Use a new folder; never overwrite an active runtime'
repo=args.repository.resolve();base=repo/'diva-lead/research/native-low-latency-effects'
research=base/'local-fl-studio/cloud-after-1625/2026-10-22'
if args.checkpoint is None:
    available=[d for d in research.glob('WIP[0-9][0-9]')if d.is_dir()and list(d.glob('*_complete_WIP.zip'))]
    assert available,'No complete supported WIP found'
    args.checkpoint=max(available,key=lambda d:int(d.name[3:])).name
public=research/args.checkpoint
zipfiles=list(public.glob('*_complete_WIP.zip'));assert len(zipfiles)==1;archive=zipfiles[0]
expected={line.split('  ',1)[1]:line.split('  ',1)[0]for line in(research/'SHA256SUMS.txt').read_text().splitlines()}
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected[archive.relative_to(research).as_posix()]
dest.mkdir(parents=True);source=dest/'source05';source.mkdir()
with zipfile.ZipFile(archive)as z:
    assert z.testzip()is None
    members=z.namelist();prefixes={n.split('/')[0]for n in members};assert len(prefixes)==1;prefix=prefixes.pop()+'/'
    assert all(not Path(n).is_absolute()and'..'not in Path(n).parts for n in members)
    candidate=json.loads(z.read(prefix+'verification/candidate.json'));original_proof=json.loads(z.read(prefix+'verification/NATIVE_PRESET_VERIFICATION.json'))
    recorded=dest/'checkpoint-exported-native-full.wav';recorded.write_bytes(z.read(prefix+'NATIVE_FULL_180BPM_WIP.wav'))
    candidate['recorded_audio']=str(recorded)
    assert candidate['source_manifest']and not candidate.get('source_post_EQ')
    for name,out in [('Diva_NATIVE_WIP_THREE_HELD.h2p','Diva.h2p'),('Diva_SOURCE_FROZEN_48k.wav','Diva_source.wav')]:
        (source/out).write_bytes(z.read(prefix+name))
    # WIP06 predates embedding the raw audit files. Its physical all281
    # parameters are also checked in the actual local FL05 TSV in the repo.
    audit_locations={}
    for name in ['all281.tsv','Diva.log']:
        member=prefix+'verification/'+name+'.gz'
        if member in members:
            (source/name).write_bytes(gzip.decompress(z.read(member)));audit_locations[name]='ZIP'
        elif name=='all281.tsv':
            src=base/'local-fl-studio/2026-10-22/DIVA_FLP05_VERIFIED_ALL281.tsv'
            shutil.copyfile(src,source/name);audit_locations[name]='Actual local FL05 raw TSV in full checkout'
        else:audit_locations[name]='Not embedded in WIP06; no new render log fabricated'
    midi_member=prefix+'verification/MIDI_note_events_48k.json'
    (dest/'MIDI_note_events_48k.json').write_bytes(z.read(midi_member)if midi_member in members else(repo/'diva-lead/v83-wip/verification/MIDI_note_events_48k.json').read_bytes())
manifest=candidate['source_manifest'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if manifest.get('source_VST_chunk'):
    with zipfile.ZipFile(archive)as z:data=z.read(prefix+'verification/Diva_VST_chunk.bin')
    chunk=source/'Diva_VST_chunk.bin';chunk.write_bytes(data)
    assert sha(chunk)==manifest['source_VST_chunk_SHA256']
    manifest=dict(manifest,source_VST_chunk=str(chunk))
assert sha(source/'Diva.h2p')==manifest['source_preset_SHA256']
assert sha(source/'Diva_source.wav')==manifest['source_audio_SHA256']
assert len((source/'all281.tsv').read_text().splitlines())==282
raw,sr=sf.read(source/'Diva_source.wav',dtype='float32');assert sr==48000 and raw.shape==(288000,2)
native_input=dest/'FL05-native-source-with-tail.wav';sf.write(native_input,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT')
fresh=dict(original_proof['fresh_Diva_proof'],source_preset=str(source/'Diva.h2p'),source_audio=str(source/'Diva_source.wav'),
    source_audio_restored_byte_exact=True,new_Diva_execution_not_claimed_by_restoration=True)
proof=source/'FRESH_DIVA_SOURCE_PROOF.json';proof.write_text(json.dumps(fresh,indent=2)+'\n')
candidate['source_manifest']=dict(manifest,source_preset=str(source/'Diva.h2p'),source_audio=str(source/'Diva_source.wav'),
    native_input=str(native_input),proof=str(proof),fresh_proof=str(proof))
(dest/'restored-candidate.json').write_text(json.dumps(candidate,indent=2)+'\n')
subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(base/'local-fl-studio/tools/restore_checkpoint.py'),
    '--destination',str(dest/'runtime')],check=True)
for path in (research/'scripts').glob('*'):
    if path.is_file()and path.suffix in['.py','.c']:shutil.copyfile(path,dest/path.name)
report=dict(source_checkpoint=args.checkpoint,ZIP_SHA256=sha(archive),source_h2p_and_raw_WAV_file_bytes_exact=True,recorded_audio_rebased_to_byte_exact_exported_checkpoint_WAV=True,recorded_audio_SHA256=sha(recorded),
    native_input_rebuilt=True,actual_VST_program_restored=bool(manifest.get('source_VST_chunk')),all281_raw_TSV_preserved=True,audit_locations=audit_locations,all12_MIDI_events_preserved=True,
    local_analysis_runtime_restored_with_fixed_reference_path=True,existing_DSP_hosts_not_modified=True,
    from_scratch_machine_install_not_claimed=True,reference_match_reached=False)
(dest/'RESTORATION_PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
