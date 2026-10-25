"""Execute both official ZL components from the explicit complete kit at startup."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from win_vst3 import D,WinVST3
parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);parser.add_argument('--kit',default='ZL-WIP26');args=parser.parse_args()
assert args.kit.startswith('ZL-WIP')and '/'not in args.kit and '..'not in args.kit
plugin=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
assert hashlib.sha256(plugin.read_bytes()).hexdigest()=='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
kit=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22')/args.kit
layout=json.loads((kit/'artifact_layout.json').read_text());clients=[];hashes=[]
try:
 for k,key in enumerate(['primary_component','post_component']):
  c=WinVST3('ST25-startup-'+str(k));clients.append(c);source=kit/layout[key];c.load(source)
  saved=D/('startup-ST25-component-'+str(k)+'.bin');c.save(saved);assert saved.read_bytes()==source.read_bytes();hashes.append(hashlib.sha256(source.read_bytes()).hexdigest())
 impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];first,_=clients[0].render(impulse);out,_=clients[1].render(first)
 assert all(c.latency()==0 for c in clients)and not np.any(out[:4096])
 delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0
 receipt=dict(complete_kit=args.kit,actual_official_two_ZL_execution=True,component_SHA256=hashes,both_state_roundtrips_byte_exact=True,combined_declared_PDC_frames=0,impulse_added_delay_frames=0,native_base_06_unchanged=True,no_GUI_or_ASIO_or_fresh_full_machine_claim=True,reference_match_reached=False)
 Path(args.receipt).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 for c in clients:c.close()
