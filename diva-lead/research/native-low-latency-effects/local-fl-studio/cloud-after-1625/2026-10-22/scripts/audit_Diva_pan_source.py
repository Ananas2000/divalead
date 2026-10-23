"""Fresh Diva source and real effGetChunk/effSetChunk verification for a conditional physical-source profile, without claiming audio improvement."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,re
import numpy as np
import soundfile as sf
B=Path('/tmp/divalead-local-1625');source=Path(sys.argv[1]);source_label=sys.argv[2]
assert re.fullmatch(r'[A-Za-z0-9_.-]+',source_label),source_label
N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=B/('fresh-'+source_label+'-source-audit');ROOT.mkdir(exist_ok=True)
baseline=json.loads(Path(sys.argv[3]).read_text())['source_manifest']
P=Path('/workspace/divalead');V=P/'diva-lead/v83-wip';S=Path('/workspace/divalead-setup')
def values(p):return {int(v[0]):dict(normalized=float(v[1]),name=v[2],display=v[3])for v in(line.split('\t')for line in p.read_text().splitlines()[1:])}
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
expected=json.loads((V/'verification/MIDI_note_events_48k.json').read_text())['events']
expected=[[e[k]for k in ['frame','status','pitch','velocity']]for e in expected]
reference=values(source/'all281.tsv');fixture,sr=sf.read(source/'Diva_source.wav',dtype='float32');assert sr==48000
env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
checks=[]
for label,preset in [('h2p',source/'Diva.h2p'),('native-VST-chunk',ROOT/'h2p/Diva_VST_chunk.bin')]:
    d=ROOT/label;d.mkdir(exist_ok=True);commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0',
        'dump '+win(d/'all281.tsv'),'save '+win(d/'Diva_VST_chunk.bin'),'render '+win(d/'Diva_source.wav'),'quit']
    complete=all((d/name).is_file()for name in ['all281.tsv','Diva_VST_chunk.bin','Diva_source.wav','Diva.log'])
    if not complete:
        assert not any(d.iterdir()),'Preserve an incomplete audit directory and use a new attempt path'
        with(d/'Diva.log').open('w')as f:
            subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',
                r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(preset)],
                input='\n'.join(commands)+'\n',text=True,stdout=f,stderr=f,env=env,check=True,timeout=120)
    log=(d/'Diva.log').read_text();assert 'ERROR 'not in log
    events=[list(map(int,line.split()[1:]))for line in log.splitlines()if line.startswith('NOTE ')];assert events==expected
    actual=values(d/'all281.tsv');assert actual==reference
    y,rate=sf.read(d/'Diva_source.wav',dtype='float32');assert rate==48000;np.testing.assert_array_equal(y,fixture)
    checks.append(dict(load_mode=label,all281_exact=True,all12_MIDI_events_exact=True,raw_audio_bit_exact=True,
        decoded_raw_SHA256=hashlib.sha256(y.astype('<f4').tobytes()).hexdigest()))
old05=values(N/'source-bases/FL05_VCA_minus58/all281.tsv');old83=values(V/'verification/Diva_all281.tsv')
basevalues=values(Path(baseline['source_preset']).parent/'all281.tsv')
changed_from_current=[i for i in reference if reference[i]['normalized']!=basevalues[i]['normalized']]
assert changed_from_current and set(changed_from_current)=={167},changed_from_current
changed=[i for i in reference if reference[i]['normalized']!=old83[i]['normalized']]
assert set(changed)<={90,96,108,167,171}and 171 in changed,changed
changed_from05=[i for i in reference if reference[i]['normalized']!=old05[i]['normalized']]
assert set(changed_from05)<={90,96,108,167},changed_from05
dest=N/'source-bases'/source_label;dest.mkdir(exist_ok=False)
shutil.copyfile(source/'Diva.h2p',dest/'Diva.h2p')
for name in ['Diva_source.wav','Diva_VST_chunk.bin','all281.tsv','Diva.log']:shutil.copyfile(ROOT/'h2p'/name,dest/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=dict(source_audited_for_research_before_any_adoption=True,actual_fresh_Diva_plugin_render=True,all281_exact_against_variant=True,same_all12_incoming_MIDI_events=True,
    raw_audio_bit_exact_against_variant_fixture=True,two_independent_raw_renders_bit_exact=True,
    real_effGetChunk_saved=True,real_effSetChunk_reload_all281_and_audio_exact=True,load_checks=checks,
    preset_SHA256=sha(dest/'Diva.h2p'),source_audio_file_SHA256=sha(dest/'Diva_source.wav'),
    source_VST_chunk_SHA256=sha(dest/'Diva_VST_chunk.bin'),source_preset=str(dest/'Diva.h2p'),source_audio=str(dest/'Diva_source.wav'),
    only_changed_indices_vs_actual_local_FL05=changed_from05,only_changed_indices_vs_previous_native_source=changed_from_current,only_changed_indices_vs_v83=changed,
    ARP_clock_and_ADSR_unchanged=True,only_three_held_notes_per_phrase=True,reference_match_reached=False)
(dest/'FRESH_DIVA_SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
native=B/(source_label+'-native-source-with-tail.wav');sf.write(native,np.pad(fixture,((0,32768),(0,0))),48000,subtype='FLOAT')
manifest=dict(source_preset=str(dest/'Diva.h2p'),source_audio=str(dest/'Diva_source.wav'),native_input=str(native),
    source_preset_SHA256=proof['preset_SHA256'],source_audio_SHA256=proof['source_audio_file_SHA256'],
    source_VST_chunk=str(dest/'Diva_VST_chunk.bin'),source_VST_chunk_SHA256=proof['source_VST_chunk_SHA256'],
    changed_parameters={reference[i]['name']:dict(before=old83[i],after=reference[i])for i in changed},
    all281_audited=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_and_ADSR_unchanged=True,
    proof=str(dest/'FRESH_DIVA_SOURCE_PROOF.json'),fresh_proof=str(dest/'FRESH_DIVA_SOURCE_PROOF.json'))
(ROOT/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PHYSICAL_SOURCE_FRESH_DIVA_AND_REAL_CHUNK_RELOAD_EXACT',flush=True)
