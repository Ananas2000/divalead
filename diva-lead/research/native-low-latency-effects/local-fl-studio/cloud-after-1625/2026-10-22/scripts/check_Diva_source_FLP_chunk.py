"""Build a source-only FLP fixture, extract its chunk, and verify in real Diva."""
from pathlib import Path
import hashlib,json,os,subprocess
import numpy as np
import soundfile as sf
from native_fst import parse,event,container
from fl20_diva_wrapper import program_chunk,replace_program_chunk
B=Path('/tmp/divalead-local-1625');ROOT=B/'FLP_OscMix6p3_source_chunk_integration';ROOT.mkdir(exist_ok=False)
N=Path('/workspace/divalead-work/native-low-latency-effects/source-bases/FL05_OscMix_6p3');S=Path('/workspace/divalead-setup')
local=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22')
original=(local/'Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.flp').read_bytes();p=parse(original)
chunk=(N/'Diva_VST_chunk.bin').read_bytes();events=[];seen=0
for ident,data in p['events']:
    if ident==213:
        if seen==0:data=replace_program_chunk(data,chunk)
        seen+=1
    events.append((ident,data))
result=container(p['format'],b''.join(event(i,b)for i,b in events),p['channels'])
dest=ROOT/'SOURCE_ONLY_TEST_NOT_LEAD_CANDIDATE.flp';dest.write_bytes(result);q=parse(result)
assert len(p['events'])==len(q['events'])
different=[n for n,(a,b)in enumerate(zip(p['events'],q['events']))if a!=b];assert len(different)==1
assert p['events'][different[0]][0]==213
vst=next(b for i,b in q['events']if i==213);extracted=program_chunk(vst);assert extracted==chunk
state=ROOT/'Diva_chunk_extracted_from_FLp.bin';state.write_bytes(extracted)
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0',
    'dump '+win(ROOT/'all281.tsv'),'render '+win(ROOT/'Diva_source.wav'),'quit']
with(ROOT/'Diva.log').open('w')as log:
    subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',
        r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(state)],
        input='\n'.join(commands)+'\n',text=True,env=env,stdout=log,stderr=log,check=True,timeout=120)
assert(ROOT/'all281.tsv').read_bytes()==(N/'all281.tsv').read_bytes()
actual,sr=sf.read(ROOT/'Diva_source.wav',dtype='float32');expected,_=sf.read(N/'Diva_source.wav',dtype='float32')
assert sr==48000;np.testing.assert_array_equal(actual,expected)
proof=dict(real_effGetChunk_bytes_embedded_in_FL20_wrapper_record53=True,
    binary_program_size_and_container_lengths_updated=True,all_other_FLp_events_byte_exact=True,
    extracted_project_program_loaded_by_actual_Diva=True,all281_dump_byte_exact=True,
    fresh_raw_audio_decoded_float32_bit_exact=True,only_three_held_notes_per_phrase=True,
    source_only_fixture_not_a_deployable_lead_candidate=True,actual_FL_GUI_export_pending=True,reference_match_reached=False,
    FLp_SHA256=hashlib.sha256(result).hexdigest(),real_VST_chunk_SHA256=hashlib.sha256(chunk).hexdigest())
(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print('SOURCE_VST_CHUNK_FLP_ACTUAL_DIVA_INTEGRATION_PASSED',flush=True)
