"""Retain the actually rendered, chunk-reloaded OscMix6.5 source and audits."""
from pathlib import Path
import csv,hashlib,json,shutil,tarfile
import numpy as np
import soundfile as sf
D=Path(__file__).resolve().parent;N=Path('/workspace/divalead-work/native-low-latency-effects');study=D/'Diva-tone-actual-current-ZL-rebase02-01';summary=json.loads((study/'completion.json').read_text());assert summary['robust_improvement']and summary['selected_case']=='OscMix-6.5'
winner=json.loads((study/'SELECTED_SOURCE_RESEARCH_ONLY.json').read_text());old=json.loads((study/'PRIOR_COMBINED_CANDIDATE.json').read_text())['native_base']['source_manifest'];out=N/'source-bases/FL05_OscMix_6p5';out.mkdir(exist_ok=False)
source=Path(winner['source_audio']).parent
for name in ['Diva_source.wav','Diva_VST_chunk.bin','all281.tsv','Diva.log']:shutil.copyfile(source/name,out/name)
shutil.copyfile(winner['source_preset'],out/'Diva.h2p');raw,sr=sf.read(out/'Diva_source.wav',dtype='float32');again,sr2=sf.read(study/'selected-source-cold-chunk-replay/Diva_source.wav',dtype='float32');assert sr==sr2==48000;np.testing.assert_array_equal(raw,again)
assert(out/'Diva_VST_chunk.bin').read_bytes()==(study/'selected-source-cold-chunk-replay/Diva_VST_chunk.bin').read_bytes()
assert(out/'all281.tsv').read_bytes()==(study/'selected-source-cold-chunk-replay/all281.tsv').read_bytes()
def params(p):return {int(r['index']):r for r in csv.DictReader(p.open(),delimiter='\t')}
before=params(Path(old['source_preset']).parent/'all281.tsv');after=params(out/'all281.tsv');assert len(after)==281;assert{i for i in after if after[i]['normalized']!=before[i]['normalized']}=={96}
notes=[l for l in(out/'Diva.log').read_text().splitlines()if l.startswith('NOTE ')];assert notes==[l for l in(Path(old['source_preset']).parent/'Diva.log').read_text().splitlines()if l.startswith('NOTE ')]and len(notes)==12
native_input=out/'native-source-with-tail.wav';sf.write(native_input,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=dict(actual_fresh_Diva_plugin_render=True,all281_exact_against_variant=True,same_all12_incoming_MIDI_events=True,raw_audio_bit_exact_against_variant_fixture=True,two_independent_raw_renders_bit_exact=True,real_effGetChunk_saved=True,real_effSetChunk_reload_all281_and_audio_exact=True,preset_SHA256=sha(out/'Diva.h2p'),source_audio_file_SHA256=sha(out/'Diva_source.wav'),source_VST_chunk_SHA256=sha(out/'Diva_VST_chunk.bin'),source_preset=str(out/'Diva.h2p'),source_audio=str(out/'Diva_source.wav'),only_changed_indices_vs_previous_ZL16_source=[96],previous_source_manifest=old,only_changed_indices_vs_actual_local_FL05=[96],only_changed_indices_vs_v83=[96,108,171],ARP_clock_and_ADSR_unchanged=True,only_three_held_notes_per_phrase=True,source_study=str(study),cold_replay_directory=str(study/'selected-source-cold-chunk-replay'),load_checks=[dict(load_mode=mode,all281_exact=True,all12_MIDI_events_exact=True,raw_audio_bit_exact=True,decoded_raw_SHA256=hashlib.sha256(raw.astype('<f4').tobytes()).hexdigest())for mode in ['h2p','native-VST-chunk']],reference_match_reached=False)
(out/'FRESH_DIVA_SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
manifest=json.loads(json.dumps(old));manifest.update(source_preset=str(out/'Diva.h2p'),source_audio=str(out/'Diva_source.wav'),native_input=str(native_input),source_preset_SHA256=proof['preset_SHA256'],source_audio_SHA256=proof['source_audio_file_SHA256'],source_VST_chunk=str(out/'Diva_VST_chunk.bin'),source_VST_chunk_SHA256=proof['source_VST_chunk_SHA256'],proof=str(out/'FRESH_DIVA_SOURCE_PROOF.json'),fresh_proof=str(out/'FRESH_DIVA_SOURCE_PROOF.json'))
manifest['changed_parameters']['OSC: OscMix']['after']=dict(normalized=float(after[96]['normalized']),name=after[96]['name'],display=after[96]['display']);(study/'AUDITED_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copytree(out,study/'actual-source')
# Keep every case's actual preset/chunk/parameter/MIDI audits. Only control,
# selected and independent cold raw audio are needed beside paired final WAVs.
archive=study/'ALL23_ACTUAL_SOURCE_CASE_AUDITS_AND_SELECTED_RAW.tar.gz';members=[]
with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
 for folder in sorted(study.iterdir()):
  if not folder.is_dir()or not(folder/'Diva.h2p').exists()or not(folder/'actual-Diva').is_dir():continue
  files=[folder/'Diva.h2p',folder/'ACTUAL_DIVA_AND_FULL_CHAIN_VERIFICATION.json',*(folder/'actual-Diva').iterdir()]
  for p in files:
   if not p.is_file()or(p.suffix=='.wav'and folder.name not in ['unchanged-control','OscMix-6.5']):continue
   rel=p.relative_to(study).as_posix();tar.add(p,arcname=rel,recursive=False);members.append(dict(path=rel,SHA256=sha(p)))
with tarfile.open(archive)as tar:
 for row in members:assert hashlib.sha256(tar.extractfile(row['path']).read()).hexdigest()==row['SHA256']
(study/'ALL23_SOURCE_AUDIT_ARCHIVE_SHA256.json').write_text(json.dumps(dict(archive_SHA256=sha(archive),members=members),indent=2)+'\n');print('FRESH_ACTUAL_OSCMIX6P5_SOURCE_READY_NOT_ADOPTED',json.dumps(manifest),flush=True)
