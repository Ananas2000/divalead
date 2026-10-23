"""Render the actual Diva with only Plate2 Wet changed; retain all281/MIDI/chunk."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
import numpy as np
import soundfile as sf
control=Path(sys.argv[1]);out=Path(sys.argv[2]);wet=float(sys.argv[3]);out.mkdir(exist_ok=False)
base=json.loads(control.read_text())['source_manifest'];source=Path(base['source_preset']).parent
text=(source/'Diva.h2p').read_text();lines=[];active=None;changed=0
for line in text.splitlines():
    if line.startswith('#cm='):active=line[4:]
    if active=='Plate2'and line.startswith('Wet='):line='Wet='+str(wet);changed+=1
    lines.append(line)
assert changed==1
preset=out/'Diva.h2p';preset.write_text('\n'.join(lines)+'\n')
S=Path('/workspace/divalead-setup');P=Path('/workspace/divalead')
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
cmd=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(out/'all281.tsv'),'save '+win(out/'Diva_VST_chunk.bin'),'render '+win(out/'Diva_source.wav'),'quit']
env=dict(os.environ,WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',DISPLAY=':90',XDG_CACHE_HOME=str(S/'cache'))
with(out/'Diva.log').open('w')as f:
    subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(preset)],input='\n'.join(cmd)+'\n',text=True,env=env,stdout=f,stderr=f,check=True,timeout=120)
def values(p):return {int(v[0]):dict(normalized=float(v[1]),name=v[2],display=v[3])for v in(line.split('\t')for line in p.read_text().splitlines()[1:])}
old=values(source/'all281.tsv');new=values(out/'all281.tsv');assert len(old)==len(new)==281
indices=[i for i in old if old[i]['normalized']!=new[i]['normalized']];assert indices==[235],indices
expected=json.loads((P/'diva-lead/v83-wip/verification/MIDI_note_events_48k.json').read_text())['events'];expected=[[e[k]for k in ['frame','status','pitch','velocity']]for e in expected]
log=(out/'Diva.log').read_text();events=[list(map(int,line.split()[1:]))for line in log.splitlines()if line.startswith('NOTE ')];assert events==expected and 'ERROR 'not in log
y,sr=sf.read(out/'Diva_source.wav',dtype='float32');assert sr==48000 and y.shape==(288000,2)and np.isfinite(y).all()
proof=dict(actual_Diva_execution=True,only_changed_parameter_index=235,changed_parameter=new[235],
 all281_audited=True,all12_incoming_MIDI_events_exact=True,only_three_held_notes_per_phrase=True,
 ARP_clock_and_envelopes_unchanged=True,raw_float32_SHA256=hashlib.sha256(y.astype('<f4').tobytes()).hexdigest(),
 actual_effGetChunk_saved=True,baseline_source_preset_SHA256=base['source_preset_SHA256'],fixture_only_no_native_improvement_claim=True,reference_match_reached=False)
(out/'FIXTURE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
