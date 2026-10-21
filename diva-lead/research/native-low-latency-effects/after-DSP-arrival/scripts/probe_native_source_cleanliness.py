"""Actual three-held Diva source variants, followed by actual native FL effects.

Every variant audits all 281 parameters and the same 12 incoming MIDI events.
This is a finite experiment, never an automatic replacement of the v83 source.
"""
from pathlib import Path
import concurrent.futures,hashlib,json,os,re,threading,time,subprocess
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from native_cpu_slots import four_native_slots
from apply_native_candidate import apply
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(W/'source-cleanliness-isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target

ROOT=W/'native-source-cleanliness';ROOT.mkdir(exist_ok=False)
V=Path('/workspace/divalead/diva-lead/v83-wip');S=Path('/workspace/divalead-setup')
preset=(V/'Diva_Lead_v83_WIP.h2p').read_text();original,sr=sf.read(V/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32');assert sr==48000
expected=[[e[k] for k in ['frame','status','pitch','velocity']] for e in json.loads((V/'verification/MIDI_note_events_48k.json').read_text())['events']]
def parameters(path):
    return {int(v[0]):dict(normalized=float(v[1]),name=v[2],display=v[3]) for v in (line.split('\t') for line in path.read_text().splitlines()[1:])}
prior=parameters(V/'verification/Diva_all281.tsv');assert len(prior)==281
index={v['name']:i for i,v in prior.items()}
def patch(values):
    active=None;used=set();lines=[]
    for line in preset.splitlines():
        if line.startswith('#cm='):active=line[4:]
        if '=' in line and not line.startswith('#'):
            k=line.split('=',1)[0];label=(active,k)
            if label in values:line=k+'='+str(values[label]);used.add(label)
        lines.append(line)
    assert used==set(values)
    return '\n'.join(lines)+'\n'
cases=[('baseline',{},set()),('divine',{('OPT','Acc'):3},{18}),('fast',{('OPT','Acc'):1},{18})]
for f in [0.,.3,.7,1.5,2.]:cases.append((f'wet-{f:g}',{('Plate2','Wet'):f},{235}))
for f in [50.,80.,95.]:cases.append((f'damp-{f:g}',{('Plate2','Damp'):f},{231}))
for f in [138.,145.5,150.]:cases.append((f'cutoff-{f:g}',{('VCF1','Freq'):f},{148}))
for f in [4.,8.,18.]:cases.append((f'resonance-{f:g}',{('VCF1','Res'):f},{149}))
for f in [49.5,50.5,53.5]:cases.append((f'PW-{f:g}',{('OSC','PW'):f},{90}))
for f in [0.,3.,10.]:cases.append((f'mix-{f:g}',{('OSC','OscMix'):f},{96}))
cases.append(('divine-dry',{('OPT','Acc'):3,('Plate2','Wet'):0.},{18,235}))
features=FeaturesOriginal(target);local=threading.local();clients=[];mutex=threading.Lock();rows=[];start=time.monotonic()
env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(S/'cache'))
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
def evaluate(case):
    label,values,allowed=case;d=ROOT/label;d.mkdir();p=d/'Diva.h2p';p.write_text(patch(values))
    output=d/'Diva_source.wav';dump=d/'all281.tsv';log=d/'Diva.log'
    commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(dump),'render '+win(output),'quit']
    with log.open('w') as f:
        subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(p)],input='\n'.join(commands)+'\n',text=True,env=env,stdout=f,stderr=f,check=True,timeout=120)
    text=log.read_text();assert 'ERROR ' not in text
    got=[list(map(int,v.split()[1:])) for v in text.splitlines() if v.startswith('NOTE ')]
    assert got==expected
    actual=parameters(dump);changed={i for i in prior if actual[i]['normalized']!=prior[i]['normalized']}
    assert changed==allowed,(label,changed,allowed)
    source,rate=sf.read(output,dtype='float32');assert rate==48000 and source.shape==original.shape
    if label=='baseline':np.testing.assert_array_equal(source,original)
    padded=d/'source-with-tail.wav';sf.write(padded,np.pad(source,((0,32768),(0,0))),rate,subtype='FLOAT')
    if not hasattr(local,'client'):
        c=NativeChain(W/'native-frozen-source-with-tail.wav',f'source-cleanliness-{threading.get_ident()}',fl_graph=True,engine_override='fl_native_source_variants_host.exe');local.client=c
        with mutex:clients.append(c)
    c=local.client;c.load_input(padded);apply(c,x);y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025
    row=dict(case=label,loss=loss,source_preset=str(p),source_audio=str(output),actual_raw_SHA256=hashlib.sha256(source.astype('<f4').tobytes()).hexdigest(),changed_parameters={actual[i]['name']:dict(before=prior[i],after=actual[i]) for i in sorted(changed)},all281_audited=True,only_requested_source_parameters_changed=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_and_envelopes_unchanged=True,original_reference_assessment=features.local.last,native_status=status,strict_waveform_match=False,original_reference_match_reached=False,not_automatically_accepted=True,seconds=time.monotonic()-start)
    with mutex:
        rows.append(row);(d/'verification.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(d/'native-with-tail.wav',y,48000,subtype='FLOAT')
        print('SOURCE_NATIVE_CASE',label,loss,features.local.last['tone_score'],flush=True)
    return row

with four_native_slots(ROOT) as parent:
    base=json.loads((Path(parent['search_root'])/'best.json').read_text());x=np.array(base['x']);assert len(x)==86
    (ROOT/'frozen-native-effects.json').write_text(json.dumps(base,indent=2)+'\n')
    try:
        baseline=evaluate(cases[0])
        with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,cases[1:]))
    finally:
        for c in clients:c.close()
rows.sort(key=lambda v:v['loss']);(ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),elapsed_seconds=time.monotonic()-start,baseline_loss=baseline['loss'],best_case=rows[0]['case'],best_loss=rows[0]['loss'],all_actual_Diva_and_native_FX=True,match_reached=False),indent=2)+'\n')
print('ACTUAL_DIVA_NATIVE_CLEANLINESS_COMPLETE',rows[0]['case'],rows[0]['loss'],flush=True)
