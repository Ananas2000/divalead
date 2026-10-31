from pathlib import Path
import json,numpy as np,soundfile as sf
from native_chain import NativeChain
U=Path(__file__).resolve().parent;R=U/'BIPOLAR_WS_IMPULSE_DELAY';R.mkdir();inp=R/'impulse.wav';y=np.zeros((32768,2),np.float32);y[4096]=[.17,.123];sf.write(inp,y,48000,subtype='FLOAT');rows=[]
for name,state in [('old_unipolar',U.parent/'native-low-latency-effects/validated-bases/FL20_NATIVE_ZL_REBASED_10/verification/SOURCE_WaveShaper.bin'),('new_bipolar_even8',U/'BIPOLAR_FINALIST1_AIR_MARGIN_REPAIR/CANDIDATE_WS_NATIVE_CANONICAL.bin')]:
 c=NativeChain(inp,'WS-delay-'+name,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
 try:
  for node in range(1,15):c.bypass(node,True)
  c.load_state(0,state);out,status=c.render();baseline=np.median(out[2048:3072],axis=0);d=abs(out-baseline).max(axis=1);onset=int(np.flatnonzero(d>1e-7)[0]);assert onset==4096;sf.write(R/(name+'.wav'),out,48000,subtype='FLOAT');dst=R/(name+'.bin');c.save_state(0,dst);assert dst.read_bytes()==state.read_bytes();rows.append(dict(name=name,first_impulse_response_frame=onset,added_samples=onset-4096,status=status,state_roundtrip_byte_exact=True,baseline_DC_subtracted_for_onset_only=baseline.tolist()))
 finally:c.close()
proof=dict(actual_native_DLL=True,isolated_WaveShaper_only=True,rows=rows,new_WS_added_delay_samples=0,whole_DAW_ASIO_not_measured=True,reference_match_reached=False);(R/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
