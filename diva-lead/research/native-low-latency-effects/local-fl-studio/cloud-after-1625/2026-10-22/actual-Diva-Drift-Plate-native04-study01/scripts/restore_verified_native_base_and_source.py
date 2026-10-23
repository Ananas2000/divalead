"""Idempotent native-base/source delta restore; never overwrite different data."""
from pathlib import Path
import argparse,gzip,hashlib,io,json,os,stat,zipfile
import numpy as np
import soundfile as sf
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--parent',required=True);p.add_argument('--restore-source',action='store_true');p.add_argument('--receipt',required=True);a=p.parse_args()
archive=Path(a.archive);assert hashlib.sha256(archive.read_bytes()).hexdigest()==a.expected_sha256
parent=Path(a.parent).resolve();parent.mkdir(parents=True,exist_ok=True);checked=[];created=[]
def put(path,blob):
 path=Path(path)
 if path.exists():assert path.is_file()and path.read_bytes()==blob,('Preserve different existing file',str(path))
 else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob);created.append(str(path))
 checked.append(dict(path=str(path),bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None;top=set()
 for info in z.infolist():
  rel=Path(info.filename);assert not rel.is_absolute()and '..'not in rel.parts;assert not stat.S_ISLNK(info.external_attr>>16);top.add(rel.parts[0]);target=parent/rel
  assert target.resolve().is_relative_to(parent)
  if not info.is_dir():put(target,z.read(info))
 assert len(top)==1;base=parent/top.pop()
candidate=json.loads((base/'verification/candidate.json').read_text());source=candidate['source_manifest']
if a.restore_source:
 put(source['source_preset'],(base/'Diva_NATIVE_WIP_THREE_HELD.h2p').read_bytes());put(source['source_audio'],(base/'Diva_SOURCE_FROZEN_48k.wav').read_bytes());put(source['source_VST_chunk'],(base/'verification/Diva_VST_chunk.bin').read_bytes())
 for field,digest in [('source_preset','source_preset_SHA256'),('source_audio','source_audio_SHA256'),('source_VST_chunk','source_VST_chunk_SHA256')]:assert hashlib.sha256(Path(source[field]).read_bytes()).hexdigest()==source[digest]
 source_dir=Path(source['source_preset']).parent
 for name in ['all281.tsv','Diva.log']:put(source_dir/name,gzip.decompress((base/'verification'/(name+'.gz')).read_bytes()))
 report=json.loads((base/'verification/NATIVE_PRESET_VERIFICATION.json').read_text());fresh=report['fresh_Diva_proof'];put(source['fresh_proof'],(json.dumps(fresh,indent=2)+'\n').encode())
 raw,sr=sf.read(source['source_audio'],dtype='float32',always_2d=True);assert sr==48000;padded=np.pad(raw,((0,32768),(0,0)));input_path=Path(source['native_input'])
 if input_path.exists():
  # This derived WAV has no stored file-byte hash. Different WAV PEAK/header
  # timestamps are harmless; retain the existing file and check actual samples.
  existing,rate=sf.read(input_path,dtype='float32',always_2d=True);assert rate==sr;np.testing.assert_array_equal(existing,padded);checked.append(dict(path=str(input_path),existing_file_preserved=True,decoded_float32_bit_exact=True,SHA256=hashlib.sha256(input_path.read_bytes()).hexdigest()))
 else:
  buffer=io.BytesIO();sf.write(buffer,padded,sr,format='WAV',subtype='FLOAT');put(input_path,buffer.getvalue());check,rate=sf.read(input_path,dtype='float32',always_2d=True);assert rate==sr;np.testing.assert_array_equal(check,padded)
receipt=dict(native_base=str(base),archive_SHA256=a.expected_sha256,all_archive_files_CRC_and_bytes_verified=True,source_restored_or_exact_existing=a.restore_source,created_files=created,checked_files=checked,does_not_claim_fresh_task_or_FL_GUI_validation=True,reference_match_reached=False)
Path(a.receipt).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(native_base=str(base),checked_files=len(checked),created_files=len(created),source_restored_or_exact_existing=a.restore_source,archive_SHA256=a.expected_sha256)),flush=True)
