"""Fresh real Diva execution from H2P and actual FLP-extracted effGetChunk.
Then real native+VST3 rendering from the freshly generated source.
No GUI FL Studio export is claimed.
"""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,zipfile
import numpy as np
import soundfile as sf
from native_chain import NativeChain
from native_fst import parse
from fl20_curve import apply_candidate
from fl20_diva_wrapper import program_chunk
from fl20_vst3_state import component_from_wrapper
from win_vst3 import D,S,WinVST3,win
ROOT=D/'ZL09-fresh-Diva-to-final-render-01';ROOT.mkdir(exist_ok=False);B=D.parent
with zipfile.ZipFile(B/'Diva_ZL_09_WIP_complete_WIP.zip')as z:assert z.testzip()is None;z.extractall(ROOT/'kit')
kit=ROOT/'kit/FL20_ZL_09_WIP';v=kit/'verification';choice=json.loads((v/'candidate.json').read_text());seed=choice['native_base'];manifest=seed['source_manifest']
states=[b for i,b in parse((kit/'Diva_ZL_09_WIP.flp').read_bytes())['events']if i==213];chunk=program_chunk(states[0]);assert chunk==Path(manifest['source_VST_chunk']).read_bytes();(ROOT/'FLP_EXTRACTED_DIVA_CHUNK.bin').write_bytes(chunk)
comp=component_from_wrapper(states[-1],8);assert comp==(v/'ZL_component.bin').read_bytes();(ROOT/'FLP_EXTRACTED_ZL_COMPONENT.bin').write_bytes(comp)
env=dict(os.environ,WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
checks=[]
for label,state in [('h2p',Path(manifest['source_preset'])),('FLP_chunk',ROOT/'FLP_EXTRACTED_DIVA_CHUNK.bin')]:
 out=ROOT/label;out.mkdir();commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(out/'all281.tsv'),'save '+win(out/'Diva_VST_chunk.bin'),'render '+win(out/'Diva_source.wav'),'quit']
 with(out/'Diva.log').open('w')as log:subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(state)],input='\n'.join(commands)+'\n',text=True,stdout=log,stderr=log,env=env,check=True,timeout=120)
 assert(out/'all281.tsv').read_bytes()==(Path(manifest['source_preset']).parent/'all281.tsv').read_bytes();assert(out/'Diva_VST_chunk.bin').read_bytes()==chunk
 actual,sr=sf.read(out/'Diva_source.wav',dtype='float32');old,sr0=sf.read(manifest['source_audio'],dtype='float32');assert sr==sr0==48000;np.testing.assert_array_equal(actual,old)
 events=[line for line in(out/'Diva.log').read_text().splitlines()if line.startswith('NOTE ')];expected=[line for line in(Path(manifest['source_preset']).parent/'Diva.log').read_text().splitlines()if line.startswith('NOTE ')];assert events==expected and len(events)==12
 checks.append(dict(load=label,all281_byte_exact=True,all12_MIDI_events_exact=True,raw_audio_decoded_float32_bit_exact=True,effGetChunk_byte_exact=True))
padded=ROOT/'FRESH_DIVA_NATIVE_INPUT_WITH_TAIL.wav';sf.write(padded,np.pad(actual,((0,32768),(0,0))),48000,subtype='FLOAT')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();c=NativeChain(padded,'ZL09-fresh-actual-Diva-chain',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');z=WinVST3('ZL09-fresh-actual-Diva-final-VST3')
try:
 apply_candidate(c,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
 for row in json.loads((v/'NATIVE_BASE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest']:c.load_state(row['node'],kit/row['state'])
 z.load(ROOT/'FLP_EXTRACTED_ZL_COMPONENT.bin');raw,status=c.render();out,zstatus=z.render(raw);res=features.residual(out[:288000]);loss=float(res@res)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025;assert z.latency()==0
 sf.write(ROOT/'FRESH_DIVA_THROUGH_ACTUAL_NATIVE_AND_ZL09_WIP.wav',out,48000,subtype='FLOAT')
finally:c.close();z.close()
control=json.loads((v/'ZIP_ACTUAL_REPLAY_PROOF.json').read_text())['six_fresh_whole_chain_mean'];assert abs(loss-control)<.01
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),fresh_actual_Diva_executions=checks,only_three_incoming_held_notes_per_phrase=True,full_actual_native_plus_ZL_render_from_fresh_Diva_source=True,original_reference_criterion_loss=loss,prior_ZIP_replay_mean=control,native_status=status,ZL_status=zstatus,ZL_declared_PDC_frames=0,actual_FL_GUI_export_pending=True,reference_match_reached=False,assessment=features.local.last)
(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print('FRESH_ACTUAL_DIVA_H2P_FLP_CHUNK_AND_FULL_CHAIN_PASS',loss,flush=True)
