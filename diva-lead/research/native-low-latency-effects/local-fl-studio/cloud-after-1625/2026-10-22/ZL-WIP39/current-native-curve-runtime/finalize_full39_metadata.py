from pathlib import Path
import hashlib,json,shutil,struct,xml.etree.ElementTree as ET,zipfile
U=Path(__file__).resolve().parent;result=json.loads((U/'ZL39_BUILD_COMPLETION.json').read_text());root=Path(result['root']);v=root/'verification';p=v/'candidate.json';d=json.loads(p.read_text());b=(v/'ZL39_POST_COMPONENT.bin').read_bytes();values={p.attrib['id']:float(p.attrib['value'])for p in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')}
for mode,key in [(0,'post_Stereo_AllPasses'),(3,'post_Mid_AllPasses'),(4,'post_Side_AllPasses')]:d[key]=[dict(frequency=values['freq'+str(k)],Q=values['q'+str(k)],slot=k)for k in range(24)if values['filter_status'+str(k)]==2 and values['filter_type'+str(k)]==9 and values['lr_mode'+str(k)]==mode]
for mode,key in [(1,'post_Left_EQ'),(2,'post_Right_EQ')]:d[key]=[dict(frequency=values['freq'+str(k)],Q=values['q'+str(k)],gain_dB=values['gain'+str(k)],slot=k)for k in range(24)if values['filter_status'+str(k)]==2 and values['filter_type'+str(k)]==0 and values['lr_mode'+str(k)]==mode]
p.write_text(json.dumps(d,indent=2)+'\n');shutil.copyfile(U/'BUILD39_FLOAT_REPLAY_DIAGNOSIS.json',v/'BUILD39_FLOAT_REPLAY_DIAGNOSIS.json');shutil.copyfile(Path(__file__),root/'current-native-curve-runtime'/Path(__file__).name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(root/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(root).as_posix()+'\n'for p in sorted(root.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
archive=Path(result['ZIP'])
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(root.rglob('*')):
  if p.is_file():z.write(p,root.name+'/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in root.rglob('*'):
  if p.is_file():assert z.read(root.name+'/'+p.relative_to(root).as_posix())==p.read_bytes()
result.update(ZIP_bytes=archive.stat().st_size,ZIP_SHA256=sha(archive),metadata_reextracted_from_actual_POST=True,audio_and_all_cold_replayed_plugin_states_unchanged_after_metadata_only_finalization=True);(U/'ZL39_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
