"""Actual three-held Diva source variants, followed by actual native FL effects.

Every variant audits all 281 parameters and the same 12 incoming MIDI events.
This finite local screen is conditional on the newly validated native WaveShaper
curve and EQ. It never automatically replaces the audited Diva source.
"""
from pathlib import Path
import concurrent.futures,hashlib,json,os,re,threading,time,subprocess,sys
from contextlib import contextmanager
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W

from apply_native_candidate import apply
ROOT=Path(sys.argv[1]);os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/(ROOT.name+'-assessment'))
from fl20_objective import FeaturesOriginal
from native_features import target

ROOT.mkdir(exist_ok=False)
V=Path('/workspace/divalead/diva-lead/v83-wip');S=Path('/workspace/divalead-setup')
B=Path('/workspace/divalead-work/native-low-latency-effects/source-bases/FL05_OscMix_6p3')
preset=(B/'Diva.h2p').read_text();original,sr=sf.read(B/'Diva_source.wav',dtype='float32');assert sr==48000
expected=[[e[k] for k in ['frame','status','pitch','velocity']] for e in json.loads((V/'verification/MIDI_note_events_48k.json').read_text())['events']]
def parameters(path):
    return {int(v[0]):dict(normalized=float(v[1]),name=v[2],display=v[3]) for v in (line.split('\t') for line in path.read_text().splitlines()[1:])}
prior=parameters(B/'all281.tsv');assert len(prior)==281
index={v['name']:i for i,v in prior.items()}
def patch(values):
    active=None;used=set();lines=[]
    for line in preset.splitlines():
        if line.startswith('#cm='):active=line[4:]
        if '=' in line and (not line.startswith('#') or line.startswith('#FX1=')):
            k=line.split('=',1)[0];label=(active,k)
            if label in values:line=k+'='+str(values[label]);used.add(label)
        lines.append(line)
    assert used==set(values)
    return '\n'.join(lines)+'\n'
cases=[('baseline',{},set())]
for width in [49.9,50.5,50.9,51.3,51.7,52.1,52.5,53.,54.]:
    cases.append((f'PW-{width:g}',{('OSC','PW'):width},{90}))
for depth in [0.,.25,.5,1.5,2.,3.]:
    cases.append((f'PW-keyfollow-{depth:g}',{('OSC','PWMDpt'):depth},{108}))
for width in [50.9,51.3,52.5,53.]:
    for depth in [0.,2.]:
        cases.append((f'PW-{width:g}-keyfollow-{depth:g}',{('OSC','PW'):width,('OSC','PWMDpt'):depth},{90,108}))
for width in [51.3,52.5]:
    for mix in [6.,6.6]:
        cases.append((f'PW-{width:g}-mix-{mix:g}',{('OSC','PW'):width,('OSC','OscMix'):mix},{90,96}))
features=FeaturesOriginal(target);local=threading.local();clients=[];mutex=threading.Lock();rows=[];start=time.monotonic()
env=os.environ.copy();env.update(WINEPREFIX=str(S/'wine2'),WINEDLLPATH=str(S/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(S/'cache'))
def win(p):return 'Z:'+str(p.resolve()).replace('/','\\')
def evaluate(case,reps=3):
    label,values,allowed=case;d=ROOT/label;d.mkdir();p=d/'Diva.h2p';p.write_text(patch(values))
    output=d/'Diva_source.wav';dump=d/'all281.tsv';log=d/'Diva.log'
    commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0','dump '+win(dump),'save '+win(d/'Diva_VST_chunk.bin'),'render '+win(output),'quit']
    with log.open('w') as f:
        subprocess.run([str(S/'sysroot/usr/lib/wine/wine64'),'/workspace/divalead-work/current-source-history-probe/diva_performance_history.exe',r'Z:\workspace\attachments\6a76beaa-924d-4f2e-8491-512d9b487af2\Diva(x64).vst3',win(p)],input='\n'.join(commands)+'\n',text=True,env=env,stdout=f,stderr=f,check=True,timeout=120)
    text=log.read_text();assert 'ERROR ' not in text
    got=[list(map(int,v.split()[1:])) for v in text.splitlines() if v.startswith('NOTE ')]
    assert got==expected
    actual=parameters(dump);changed={i for i in prior if actual[i]['normalized']!=prior[i]['normalized']}
    assert changed==allowed,(label,changed,allowed)
    source,rate=sf.read(output,dtype='float32');assert rate==48000 and source.shape==original.shape
    if label in ['baseline','fresh-control']:np.testing.assert_array_equal(source,original)
    padded=d/'source-with-tail.wav';sf.write(padded,np.pad(source,((0,32768),(0,0))),rate,subtype='FLOAT')
    if not hasattr(local,'client'):
        c=NativeChain(W/'native-frozen-source-with-tail.wav',f'Diva-PW-harmonic-local-{threading.get_ident()}',fl_graph=True,phase_pair=len(x)==95,engine_override='fl_native_fl20_host.exe');local.client=c
        with mutex:clients.append(c)
    c=local.client;c.load_input(padded);fitted=x.copy();apply_full(c,fitted)
    # Global gain adjustment is performed by the actual two EQs in each branch.
    raw,_=c.render();features.residual(raw[:len(target)]);gain=features.local.last['diagnostics']['global_RMS_gain_for_AB']
    fitted[28:30]=np.clip(fitted[28:30]+10*np.log10(gain),-18,18);apply_full(c,fitted)
    captures=[]
    for rep in range(reps):
        y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(fitted[:28]**2))*.00000025
        captures.append(dict(loss=loss,assessment=features.local.last,audio=y,status=status))
    captures.sort(key=lambda row:row['loss']);median=captures[len(captures)//2];loss=float(np.mean([r['loss'] for r in captures]));std=float(np.std([r['loss'] for r in captures]));y=median['audio'];status=median['status']
    row=dict(case=label,loss=loss,realization_standard_deviation=std,x=fitted.tolist(),realization_losses=[r['loss'] for r in captures],source_preset=str(p),source_audio=str(output),source_preset_SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),source_VST_chunk_SHA256=hashlib.sha256((d/'Diva_VST_chunk.bin').read_bytes()).hexdigest(),actual_raw_SHA256=hashlib.sha256(source.astype('<f4').tobytes()).hexdigest(),changed_parameters={actual[i]['name']:dict(before=prior[i],after=actual[i]) for i in sorted(changed)},all281_audited=True,only_requested_source_parameters_changed=True,all12_MIDI_events_exact=True,only_three_held_notes=True,ARP_clock_and_envelopes_unchanged=True,original_reference_assessment=median['assessment'],native_status=status,strict_waveform_match=False,original_reference_match_reached=False,not_automatically_accepted=True,seconds=time.monotonic()-start)
    with mutex:
        rows.append(row);(d/'verification.json').write_text(json.dumps(row,indent=2)+'\n');sf.write(d/'native-with-tail.wav',y,48000,subtype='FLOAT')
        print('SOURCE_NATIVE_CASE',label,loss,features.local.last['tone_score'],flush=True)
    return row

def apply_full(c,v):
    apply(c,v)
    for i,value in overrides.items():c.set(3,int(i),int(value))

@contextmanager
def corrected_slots():
    N=Path('/workspace/divalead-work/native-low-latency-effects');pause=N/'fl20-corrected-search.pause'
    owner=dict(owner='finite-corrected-source-harmonic-screen',root=str(ROOT),reason='Conditional wider PW and KeyFollow screen: H6/H11/H13 residuals after corrected-context EQ76 profiling')
    with pause.open('x')as f:json.dump(owner,f)
    try:
        deadline=time.monotonic()+1200
        while True:
            state=json.loads((N/'FL20_CORRECTED_SEARCH_CONTROLLER.json').read_text())
            if state['phase']=='paused_by_control_or_actual_disk_reserve':break
            assert time.monotonic()<deadline;time.sleep(5)
        yield dict(best_candidate=str(N/'FL20-corrected/BEST_CANDIDATE.json'))
    finally:
        if pause.exists()and json.loads(pause.read_text()).get('owner')==owner['owner']:pause.unlink()

with corrected_slots() as parent:
    base=json.loads(Path(parent['best_candidate']).read_text());x=np.array(base['x']);overrides=base.get('chorus_overrides',{});assert len(x)==95 and not base.get('source_post_EQ')
    assert hashlib.sha256((B/'Diva.h2p').read_bytes()).hexdigest()==base['source_manifest']['source_preset_SHA256']
    (ROOT/'frozen-native-effects.json').write_text(json.dumps(base,indent=2)+'\n')
    try:
        baseline=evaluate(cases[0])
        # Keep only the four currently useful native clients, not an idle fifth.
        for c in clients:c.close()
        clients.clear();del local.client
        with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,cases[1:]))
        for c in clients:c.close()
        clients.clear()
        best=min(rows,key=lambda r:r['loss']);case=next(v for v in cases if v[0]==best['case'])
        selected=evaluate(('fresh-selected',case[1],case[2]),6)
        assert selected['actual_raw_SHA256']==best['actual_raw_SHA256'],'Independent selected Diva raw differed'
        selected['fresh_Diva_source_bit_exact_against_selected_case']=True
        control=evaluate(('fresh-control',{},set()),6)
        se=float(np.hypot(selected['realization_standard_deviation'],control['realization_standard_deviation'])/np.sqrt(6))
        selected.update(robust_improvement=bool(case[2])and bool(control['loss']-selected['loss']>max(.003,3*se)),seed_fresh_mean_loss=control['loss'],fresh_mean_standard_error=se,
            full_fresh_native_realizations=6,source_Diva_independently_rerendered=True,actual_FL_validation_pending=True,
            new_source_not_adopted_or_exported=True,chorus_overrides=overrides,host_context='Chorus_excluded_from_silent_warmup',
            objective_version='local_full_original_criteria_FL20_context_v1',new_basis_for_conditional_source_screen='Signed residuals after source6.3 and new EQ76/Chorus controls: relative H6+3.7dB/H11+5.1dB/H13-4.3dB suggest testing pulse-width cancellation at the physical source')
        (ROOT/'PROVISIONAL_SELECTED.json').write_text(json.dumps(selected,indent=2)+'\n')
        (ROOT/'FRESH_CONTROL.json').write_text(json.dumps(control,indent=2)+'\n')
        if selected['robust_improvement']:
            # Keep the same owned CPU pause through real Diva chunk reload and
            # an independent complete native6+6 pair. This still does not adopt.
            for c in clients:c.close()
            clients.clear()
            audit=ROOT.parent/'fresh-FL05_PW_Harmonic03-source-audit'
            for script,args,logname in [
                ('audit_selected_harmonic_source.py',[ROOT,'FL05_PW_Harmonic03'],'source-audit.log'),
                ('pair_audited_harmonic_source.py',[ROOT,audit/'source_manifest.json',ROOT.parent/'paired-harmonic-current-FX-03'],'source-pair.log')]:
                with(ROOT/logname).open('w')as f:
                    subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(ROOT.parent/script),*map(str,args)],env=os.environ.copy(),stdout=f,stderr=f,check=True)

    finally:
        for c in clients:c.close()
rows.sort(key=lambda v:v['loss']);(ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),elapsed_seconds=time.monotonic()-start,baseline_loss=baseline['loss'],best_case=rows[0]['case'],best_loss=rows[0]['loss'],all_actual_Diva_and_native_FX=True,match_reached=False,new_source_not_adopted=True,provisional_robust=selected['robust_improvement']),indent=2)+'\n')
print('ACTUAL_DIVA_NATIVE_HARMONIC_SCREEN_COMPLETE',rows[0]['case'],rows[0]['loss'],flush=True)
