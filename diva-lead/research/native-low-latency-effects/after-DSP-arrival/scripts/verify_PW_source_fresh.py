from pathlib import Path
import datetime,hashlib,json,os,subprocess
import numpy as np
import soundfile as sf
from native_chain import W
from native_cpu_slots import four_native_slots
ROOT=W/'PW-keyfollow-fresh-Diva-proof';ROOT.mkdir(exist_ok=False)
N=Path('/workspace/divalead-work/native-low-latency-effects');V=Path('/workspace/divalead/diva-lead/v83-wip');S=Path('/workspace/divalead-setup');source=N/'source-bases/PW-keyfollow-depth-1'
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
expected=[[e[k] for k in ['frame','status','pitch','velocity']] for e in json.loads((V/'verification/MIDI_note_events_48k.json').read_text())['events']]
with four_native_slots(ROOT):
 env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
 dump=ROOT/'all281.tsv';raw=ROOT/'Diva_source.wav';commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(dump),'render '+win(raw),'quit']
 with (ROOT/'Diva.log').open('w') as f:subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(source/'Diva.h2p')],input='\n'.join(commands)+'\n',text=True,env=env,stdout=f,stderr=f,check=True,timeout=120)
 text=(ROOT/'Diva.log').read_text();events=[list(map(int,s.split()[1:])) for s in text.splitlines() if s.startswith('NOTE ')];assert events==expected
 assert dump.read_bytes()==(source/'all281.tsv').read_bytes();actual,rate=sf.read(raw,dtype='float32');prior,oldrate=sf.read(source/'Diva_source.wav',dtype='float32');assert rate==oldrate==48000;np.testing.assert_array_equal(actual,prior)
 rows=(source/'all281.tsv').read_text().splitlines()[1:];original=(V/'verification/Diva_all281.tsv').read_text().splitlines()[1:];changes=[i for i,(a,b) in enumerate(zip(rows,original)) if a!=b];assert len(rows)==281 and changes==[108],changes
 proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_fresh_Diva_plugin_render=True,preset=str(source/'Diva.h2p'),preset_SHA256=hashlib.sha256((source/'Diva.h2p').read_bytes()).hexdigest(),source_audio=str(source/'Diva_source.wav'),source_audio_file_SHA256=hashlib.sha256((source/'Diva_source.wav').read_bytes()).hexdigest(),decoded_float32_SHA256=hashlib.sha256(actual.astype('<f4').tobytes()).hexdigest(),raw_audio_bit_exact_against_variant_fixture=True,all281_exact_against_variant=True,only_changed_parameter_vs_v83=108,changed_control='OSC: PWModDepth',value='+1.00',same_all12_incoming_MIDI_events=True,only_three_held_notes_per_phrase=True,frames=len(actual),sample_rate=rate,reference_match_reached=False)
 (source/'FRESH_DIVA_SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(ROOT/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print('FRESH_DIVA_PW_KEYFOLLOW_ALL281_12EVENTS_AND_RAW_BITEXACT_PASS')
