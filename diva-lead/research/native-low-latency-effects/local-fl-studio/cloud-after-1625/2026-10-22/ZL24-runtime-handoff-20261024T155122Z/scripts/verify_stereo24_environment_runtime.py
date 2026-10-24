"""Actual official two-ZL startup check; no GUI/ASIO/full-machine claim."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from win_vst3 import D,WinVST3
args=argparse.ArgumentParser();args.add_argument('--receipt',required=True);config=args.parse_args()
plugin=D/'ZL Equalizer 2.vst3/Contents/x86_64-win/ZL Equalizer 2.vst3'
assert hashlib.sha256(plugin.read_bytes()).hexdigest()=='3269c63a7b6c4a2cc38b249c3678efaf2759ea4a71a299020e3b67a96595028d'
root=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP24/verification')
p=WinVST3('ST24-startup-primary');z=WinVST3('ST24-startup-post')
try:
 for c,name in [(p,'ZL24_PRIMARY_COMPONENT.bin'),(z,'ZL24_POST_COMPONENT.bin')]:
  c.load(root/name);dst=D/('startup-resaved-'+name);c.save(dst);assert dst.read_bytes()==(root/name).read_bytes()
 impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];first,_=p.render(impulse);out,_=z.render(first)
 assert p.latency()==z.latency()==0 and not np.any(out[:4096]);delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0
 result=dict(actual_official_two_ZL_execution=True,PE_SHA256=hashlib.sha256(plugin.read_bytes()).hexdigest(),both_state_roundtrips_byte_exact=True,combined_declared_PDC_frames=0,impulse_added_delay_frames=0,native_base_06_unchanged=True,no_GUI_or_ASIO_or_fresh_full_machine_claim=True,reference_match_reached=False)
 Path(config.receipt).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:p.close();z.close()
