"""Finalize integration metadata only; all already replayed DSP bytes stay fixed."""
from pathlib import Path
import hashlib,json,shutil,struct,xml.etree.ElementTree as ET,zipfile
V=Path(__file__).resolve().parent;result=json.loads((V/'ZL40_BUILD_COMPLETION.json').read_text());root=Path(result['root']);v=root/'verification';p=v/'candidate.json';d=json.loads(p.read_text());old_components={name:hashlib.sha256((v/name).read_bytes()).hexdigest() for name in ['SOURCE_WaveShaper.bin','ZL40_PRIMARY_COMPONENT.bin','ZL40_POST_COMPONENT.bin','POST_NATIVE_STEREO_TRIM.bin']}
d['post_native_trim'].update(requested_left_dB=-.04,requested_right_dB=0,left_raw=12764,right_raw=12800)
b=(v/'ZL40_POST_COMPONENT.bin').read_bytes();values={p.attrib['id']:float(p.attrib['value']) for p in ET.fromstring(b[8:8+struct.unpack_from('<I',b,4)[0]]).find('Para')}
for mode,key in [(0,'post_Stereo_AllPasses'),(3,'post_Mid_AllPasses'),(4,'post_Side_AllPasses')]:d[key]=[dict(frequency=values['freq'+str(k)],Q=values['q'+str(k)],slot=k)for k in range(24)if values['filter_status'+str(k)]==2 and values['filter_type'+str(k)]==9 and values['lr_mode'+str(k)]==mode]
for mode,key in [(1,'post_Left_EQ'),(2,'post_Right_EQ')]:d[key]=[dict(frequency=values['freq'+str(k)],Q=values['q'+str(k)],gain_dB=values['gain'+str(k)],slot=k)for k in range(24)if values['filter_status'+str(k)]==2 and values['filter_type'+str(k)]==0 and values['lr_mode'+str(k)]==mode]
p.write_text(json.dumps(d,indent=2)+'\n');shutil.copyfile(V/'ACTUAL_DIVA_SOURCE_RECHECK.json',v/'ACTUAL_DIVA_SOURCE_RECHECK.json')
for name in ['finalize_full40_metadata.py','build_complete_original_wip40.py']:shutil.copyfile(V/name,root/'current-native-curve-runtime'/name)
assert old_components=={name:hashlib.sha256((v/name).read_bytes()).hexdigest()for name in old_components}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(root/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(root).as_posix()+'\n'for p in sorted(root.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
archive=Path(result['ZIP'])
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in sorted(root.rglob('*')):
  if p.is_file():z.write(p,root.name+'/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in root.rglob('*'):
  if p.is_file():assert z.read(root.name+'/'+p.relative_to(root).as_posix())==p.read_bytes()
result.update(ZIP_bytes=archive.stat().st_size,ZIP_SHA256=sha(archive),metadata_finalization_changed_DSP=False,actual_Diva_recheck_added=True);(V/'ZL40_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
