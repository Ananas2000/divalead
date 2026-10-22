"""Independently reproduce local FL04/05 Diva states with the same held-note MIDI."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625');ROOT=BASE/'fresh-Diva04-05';ROOT.mkdir(exist_ok=False)
KIT=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')
LOCAL=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22')
S=Path('/workspace/divalead-setup');N=Path('/workspace/divalead-work/native-low-latency-effects');V=Path('/workspace/divalead/diva-lead/v83-wip')
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
def params(p):
    rows=[line.split('\t') for line in p.read_text().splitlines()[1:]]
    return {int(v[0]):dict(normalized=float(v[1]),name=v[2],display=v[3]) for v in rows}
expected=[[e[k] for k in ['frame','status','pitch','velocity']]for e in json.loads((V/'verification/MIDI_note_events_48k.json').read_text())['events']]
env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
rows=[]
for label,preset in [('FL04',KIT/'Diva_NATIVE_WIP_THREE_HELD.h2p'),('FL05a',LOCAL/'Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.h2p'),('FL05b',LOCAL/'Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.h2p')]:
    d=ROOT/label;d.mkdir();shutil.copyfile(preset,d/'Diva.h2p');commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(d/'all281.tsv'),'render '+win(d/'Diva_source.wav'),'quit']
    with (d/'Diva.log').open('w') as log:
        subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(d/'Diva.h2p')],input='\n'.join(commands)+'\n',text=True,env=env,stdout=log,stderr=log,check=True,timeout=120)
    log=(d/'Diva.log').read_text();assert 'ERROR ' not in log
    events=[list(map(int,line.split()[1:]))for line in log.splitlines()if line.startswith('NOTE ')];assert events==expected
    values=params(d/'all281.tsv');assert len(values)==281;y,sr=sf.read(d/'Diva_source.wav',dtype='float32');assert sr==48000 and y.shape==(288000,2)
    row=dict(label=label,all281=values,preset_SHA256=hashlib.sha256((d/'Diva.h2p').read_bytes()).hexdigest(),source_audio_file_SHA256=hashlib.sha256((d/'Diva_source.wav').read_bytes()).hexdigest(),decoded_audio_SHA256=hashlib.sha256(y.astype('<f4').tobytes()).hexdigest(),all12_MIDI_events_exact=True);rows.append(row)
    if label=='FL04':np.testing.assert_array_equal(y,sf.read(KIT/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32')[0])
    elif label=='FL05b':np.testing.assert_array_equal(y,sf.read(ROOT/'FL05a/Diva_source.wav',dtype='float32')[0])
    print('ACTUAL_DIVA_SOURCE_AUDIT',label,row['decoded_audio_SHA256'],flush=True)
old=rows[0]['all281'];new=rows[1]['all281'];changed=[i for i in old if old[i]['normalized']!=new[i]['normalized']];assert changed==[171],changed
assert rows[1]['all281']==rows[2]['all281'];published=params(LOCAL/'DIVA_FLP05_VERIFIED_ALL281.tsv');assert all(new[i]['normalized']==published[i]['normalized'] for i in new)
out=N/'source-bases/FL05_VCA_minus58';out.mkdir(exist_ok=False)
for name in ['Diva.h2p','Diva_source.wav','all281.tsv','Diva.log']:shutil.copyfile(ROOT/'FL05a'/name,out/name)
baseline83=params(V/'verification/Diva_all281.tsv');changed83=[i for i in baseline83 if baseline83[i]['normalized']!=new[i]['normalized']];assert changed83==[108,171],changed83
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_fresh_Diva_plugin_render=True,all281_exact_against_variant=True,same_all12_incoming_MIDI_events=True,raw_audio_bit_exact_against_variant_fixture=True,two_independent_FL05_raw_renders_bit_exact=True,FL04_raw_bit_exact_against_delivered_fixture=True,preset_SHA256=rows[1]['preset_SHA256'],source_audio_file_SHA256=rows[1]['source_audio_file_SHA256'],source_preset=str(out/'Diva.h2p'),source_audio=str(out/'Diva_source.wav'),only_changed_indices_vs_FL04=[171],only_changed_indices_vs_v83=changed83,ARP_clock_and_ADSR_unchanged=True,VCA_modulation_depth_changed_to_minus58=True,not_a_timbre_improvement_claim=True,reference_match_reached=False)
(out/'FRESH_DIVA_SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(ROOT/'PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
raw,_=sf.read(out/'Diva_source.wav',dtype='float32');padded=BASE/'FL05-native-source-with-tail.wav';sf.write(padded,np.pad(raw,((0,32768),(0,0))),48000,subtype='FLOAT')
manifest=dict(source_preset=str(out/'Diva.h2p'),source_audio=str(out/'Diva_source.wav'),native_input=str(padded),source_preset_SHA256=proof['preset_SHA256'],source_audio_SHA256=proof['source_audio_file_SHA256'],changed_parameters={new[i]['name']:dict(before=baseline83[i],after=new[i])for i in changed83},all281_audited=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_and_ADSR_unchanged=True,proof=str(out/'FRESH_DIVA_SOURCE_PROOF.json'),fresh_proof=str(out/'FRESH_DIVA_SOURCE_PROOF.json'))
(ROOT/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('LOCAL05_SOURCE_REPRODUCED_AND_DURABLE',flush=True)
