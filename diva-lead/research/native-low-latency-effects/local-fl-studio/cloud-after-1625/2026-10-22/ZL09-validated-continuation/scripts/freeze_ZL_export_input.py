"""Freeze an accepted real component; rebuild ALL metadata from actual state."""
from pathlib import Path
import csv,hashlib,json,shutil,struct,xml.etree.ElementTree as ET
import numpy as np
from win_vst3 import D,WinVST3
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--destination',required=True);parser.add_argument('--candidate');args=parser.parse_args()
SRC=D/'ZL-continuous65';OUT=Path(args.destination);OUT.mkdir(exist_ok=False)
choice=json.loads((Path(args.candidate)if args.candidate else SRC/'BEST_CANDIDATE.json').read_text());original=Path(choice['native_ZL_component_state']);blob=original.read_bytes()
completion=json.loads((original.parent/'completion.json').read_text());assert completion['robust_improvement'] and abs(choice['loss']-completion['candidate_mean'])<1e-12
component=OUT/'ZL_component.bin';component.write_bytes(blob)
xml=ET.fromstring(blob[8:8+struct.unpack_from('<I',blob,4)[0]]);v={p.attrib['id']:float(p.attrib['value'])for p in xml.find('Para')}
static=[k for k in range(24)if v['filter_status'+str(k)]==2 and v['dynamic_on'+str(k)]==0 and v['filter_type'+str(k)]==0]
aps=[k for k in range(24)if v['filter_status'+str(k)]==2 and v['filter_type'+str(k)]==9]
dynamic=[k for k in range(24)if v['filter_status'+str(k)]==2 and v['dynamic_on'+str(k)]==1]
assert static==list(range(12))and aps[:2]==[12,13]and len(aps)>=2 and dynamic==[14,15,16,17],(static,aps,dynamic)
choice.update(ZL_peaking_MidSide_x=[v['gain'+str(k)]for k in static]+np.log2([v['freq'+str(k)]for k in static]).tolist()+np.log2([v['q'+str(k)]for k in static]).tolist(),
 ZL_allpass_bands=[dict(frequency=v['freq'+str(k)],Q=v['q'+str(k)],mode=int(v['lr_mode'+str(k)]),order=int(v['order'+str(k)]))for k in aps],
 ZL_dynamic_bands=[dict(frequency=v['freq'+str(k)],Q=v['q'+str(k)],mode=int(v['lr_mode'+str(k)]),target=v['target_gain'+str(k)],threshold=v['threshold'+str(k)],attack=v['attack'+str(k)],release=v['release'+str(k)])for k in dynamic],
 ZL_output_gain_dB=v['total_output_gain'],native_ZL_component_state=str(component),source_accepted_cohort=completion['cohort'],actual_component_XML_physical_metadata_reextracted=True)
c=WinVST3(OUT.name+'-canonical-host1');other=WinVST3(OUT.name+'-canonical-host2')
try:
 c.load(component);other.load(component);c.dump(OUT/'ZL_joint_parameters.tsv');c.save(OUT/'ZL_component_resaved.bin');assert component.read_bytes()==(OUT/'ZL_component_resaved.bin').read_bytes()
 rows=list(csv.DictReader((OUT/'ZL_joint_parameters.tsv').open(),delimiter='\t'));assert len(rows)==610
 # A retained native realization from the original official-plugin audit.
 source=D/'ZL-allpass-original-reference-01/frozen-native-0.f32';expected,_=c.render(input_file=source);got,_=other.render(input_file=source);error=float(abs(expected-got).max())
 np.testing.assert_allclose(got,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);assert c.latency()==other.latency()==0
 proof=dict(two_new_hosts=True,component_state_roundtrip_byte_exact=True,component_SHA256=hashlib.sha256(blob).hexdigest(),parameter_count=610,actual_cold_instance_max_abs_error=error,actual_cold_instance_audio_bit_exact=bool(error==0),audio_rtol=float(8*np.finfo(np.float32).eps),audio_atol=1e-12,metadata_rebuilt_from_actual_component_XML=True,declared_PDC_frames=0,source_accepted_cohort=completion['cohort'],reference_match_reached=False,actual_FL_GUI_validation_pending=True)
finally:c.close();other.close()
for name,o in [('candidate-research-only.json',choice),('completion.json',completion),('CANONICAL_COMPONENT_REPLAY_PROOF.json',proof)]: (OUT/name).write_text(json.dumps(o,indent=2)+'\n')
print('ZL_CANONICAL_EXPORT_INPUT_READY',choice['loss'],completion['cohort'],json.dumps(proof),flush=True)
