"""Fresh Diva trials: three held notes with ARP/LFO versus the v57 16-note MIDI.
The published Finish v57 is frozen for every screening render. Scores are not
perceived similarity. Any accepted changed source still needs its own NEW proof.
"""
from pathlib import Path
import os, sys, json, copy, ctypes, subprocess, re, hashlib, shutil, time
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np
import soundfile as sf
B=Path('/workspace/divalead-work')
REPO=Path('/workspace/divalead')
P=REPO/'diva-lead/research/repository-selection'
V=REPO/'diva-lead/v57-wip'
ROOT=Path(__file__).resolve().parent
SETUP=Path('/workspace/divalead-setup')
sys.path.insert(0,str(P))
import compare_all as common
common.WORK=ROOT
(ROOT/'scores').mkdir(exist_ok=True)
env=os.environ.copy()
env.update(WINEPREFIX=str(SETUP/'wine2'),WINEDLLPATH=str(SETUP/'sysroot/usr/lib/x86_64-linux-gnu/wine'),WINEDEBUG='-all',XDG_CACHE_HOME=str(SETUP/'cache'))
WINE=str(SETUP/'sysroot/usr/lib/wine/wine64')
HOST=B/'current-source-history-probe/diva_performance_history.exe'
PLUGIN=Path('/workspace/attachments/6a76beaa-924d-4f2e-8491-512d9b487af2/Diva(x64).vst3')
NATIVE=B/'fl-v57-build/native_finish.so'
LIB=ctypes.CDLL(str(NATIVE))
LIB.native_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]
TIMING=json.loads((V/'render_timing_180BPM.json').read_text())
PRESET=(V/'Diva_Lead_v57_WIP.h2p').read_bytes()
SCALES=json.loads((P/'ranking.json').read_text())['normalizing_errors']
CAP=.5555931508910259
history=[]
cache={}
best={}

def win(path):return 'Z:'+str(path).replace('/','\\')
def write(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)

def patch(fields):
    data=PRESET
    for key,value in fields.items():
        module,name=key.split(':')
        start=data.index(('#cm='+module+'\n').encode())+len('#cm='+module+'\n')
        end=data.find(b'#cm=',start)
        if end<0:end=len(data)
        section,n=re.subn(rb'(?m)^'+re.escape(name.encode())+rb'=[^\r\n\x00]*',(name+'='+format(value,'.2f')).encode(),data[start:end])
        assert n==1,key
        data=data[:start]+section+data[end:]
    return data

def commands(family,timing,output,dump,roots):
    if family=='sixteen':
        lines=['pattern 8 0 8','timing {} {}'.format(timing['host_swing'],timing['host_default_gate'])]
        for command,values in [('stepvel',timing['velocities']),('stepgrid',timing['offsets']+timing['gates']),('secondvel',timing['second_velocities']),('secondgrid',timing['second_offsets']+timing['second_gates'])]:
            lines.append(command+' '+' '.join(map(str,values)))
    else:lines=['pattern 3 0 8','velocities '+' '.join(map(str,roots))]
    return '\n'.join(lines+['warmblocks 128','preludes 0','dump '+win(dump),'render '+win(output),'quit'])+'\n'

def evaluate(family,fields=None,timing=None,roots=(96,96,101),label=''):
    fields={} if fields is None else fields
    timing=copy.deepcopy(TIMING if timing is None else timing)
    key=json.dumps([family,fields,timing,roots],sort_keys=True)
    if key in cache:return cache[key]
    index=len(history)
    case=ROOT/('trial-'+format(index,'04d'));case.mkdir(exist_ok=False)
    preset=case/'source.h2p';preset.write_bytes(patch(fields))
    output=ROOT/'current-source.wav';dump=case/'all281.tsv'
    cmd=commands(family,timing,output,dump,roots)
    (case/'commands.txt').write_text(cmd)
    with (case/'Diva.log').open('w') as log:
        subprocess.run([WINE,str(HOST),win(PLUGIN),win(preset)],input=cmd,text=True,env=env,stdout=log,stderr=log,check=True,timeout=90)
    log=(case/'Diva.log').read_text();assert 'ERROR ' not in log
    notes=[list(map(int,line.split()[1:])) for line in log.splitlines() if line.startswith('NOTE ')]
    note_ons=[x for x in notes if x[1]==144]
    assert len(note_ons)==(16 if family=='sixteen' else 6)
    (case/'events.json').write_text(json.dumps(notes,indent=2)+'\n')
    dry,sr=sf.read(output,dtype='float32');assert sr==48000 and dry.shape==(288000,2) and np.isfinite(dry).all()
    actual=np.zeros_like(dry);assert LIB.native_render(dry.ctypes.data,actual.ctypes.data,len(dry),48000)
    edit=common.h.edit_aligned(common.h.align_with_pdc(actual.astype('float64'),TIMING,latency=12416))
    editfile=ROOT/'current-edit.wav';sf.write(editfile,edit,48000,subtype='FLOAT')
    measured=common.score(dict(id='arch'+format(index,'04d'),canonical_path=str(editfile),aliases=[]))
    metrics=measured['metrics'];score=sum(common.WEIGHTS[k]*metrics[k]/SCALES[k] for k in common.WEIGHTS)
    peaks=[]
    for step in range(8):
        z=dry[round((step/6+.055)*48000):round((step/6+.145)*48000)]
        power=np.mean(abs(np.fft.rfft(z*np.hanning(len(z))[:,None],65536,axis=0))**2,axis=1)
        freq=np.fft.rfftfreq(65536,1/48000);mask=(freq>50)&(freq<200)
        peaks.append(float(freq[mask][np.argmax(power[mask])]))
    row=dict(index=index,family=family,label=label,fields=fields,timing=timing,root_velocities=list(roots),score=score,metrics=metrics,crest_RMS_dB=measured['diagnostics']['crest_RMS_db'],pitch_peaks_first_phrase_Hz=peaks,note_on_count=len(note_ons),raw_SHA256=hashlib.sha256(dry.tobytes()).hexdigest(),frozen_Finish='published v57',match_reached=False,case=str(case),actual_Diva_render=True,full_changed_source_proof_pending=True)
    if index==0:
        assert family=='sixteen' and not fields and timing==TIMING
        np.testing.assert_array_equal(dry,sf.read(V/'Diva_SOURCE_FROZEN_48k.wav',dtype='float32')[0])
        np.testing.assert_allclose(actual,sf.read(V/'verification/Selected_WITH_PDC.wav',dtype='float32')[0],rtol=0,atol=2e-7)
        expected=json.loads((V/'verification/selected_validation.json').read_text())['score']
        assert abs(score-expected)<2e-7,(score,expected)
        row['published_source_and_Finish_baseline_checked']=True
    history.append(row);cache[key]=row;write(case/'result.json',row);write(ROOT/'history.json',history)
    print('TRIAL',index,family,label,'score',round(score,9),'crest',round(row['crest_RMS_dB'],6),'peaks',[round(x,1) for x in peaks],flush=True)
    if family not in best or score<best[family]['score']:
        best[family]=row
        dest=ROOT/('best-'+family);dest.mkdir(exist_ok=True)
        shutil.copyfile(preset,dest/'source.h2p');shutil.copyfile(dump,dest/'all281.tsv')
        sf.write(dest/'raw-Diva.wav',dry,48000,subtype='FLOAT');sf.write(dest/'processed-v57-WITH_PDC.wav',actual,48000,subtype='FLOAT');sf.write(dest/'REFERENCE_EDIT_WIP.wav',edit,48000,subtype='FLOAT')
        write(dest/'selection.json',row);write(ROOT/'best-by-family.json',best)
    return row

if __name__=='__main__':
    baseline=evaluate('sixteen',label='exact v57 control')
    arp={'ARP:OnOff':1,'ARP:Dir':4,'ARP:Oct':2,'ARP:CDiv':0,'ARP:Rstrt':0,'ARP:Order':0,'CLK:Mult':100,'CLK:Base':2,'CLK:Swing':0}
    control=evaluate('three-arp',arp,label='held three; internal up+dn2, eighth clock')
    for direction in [1,2,3,4]:
        for order in [0,1]:
            f=dict(arp,**{'ARP:Dir':direction,'ARP:Order':order})
            evaluate('three-arp',f,label='ARP direction/order '+str((direction,order)))
    current=best['three-arp']
    for field,values in [('ENV1:Vel',[0,50,80]),('VCA1:ModDpt',[-94,-91,-87,-84,-80,-76]),('ENV1:Atk',[0,1.5,5,8,12]),('ENV1:Dec',[6,8,13,16]),('CLK:Swing',[.5,1,2]),('OSC:Mix',[4,7])]:
        if field=='OSC:Mix':continue
        fields=copy.deepcopy(current['fields']);choices=[current]
        for value in values:
            f=dict(fields);f[field]=value
            choices.append(evaluate('three-arp',f,roots=current['root_velocities'],label=field+'='+str(value)))
        current=min(choices,key=lambda r:r['score'])
    # Internal LFO pitch alternatives retain exactly three incoming notes.
    for wave in [0,1,4,5]:
        for phase in [0,16.67,33.33]:
            f={'LFO2:Sync':10,'LFO2:Trig':1,'LFO2:Wave':wave,'LFO2:Phse':phase,'LFO2:Polar':1,'LFO2:Dly':0,'LFO2:Rate':0,'LFO2:DMS1':0,'LFO2:DMD1':0,'OSC:TM1Src':17,'OSC:TM1Dpt':12,'OSC:TM2Src':17,'OSC:TM2Dpt':12}
            evaluate('three-lfo',f,label='unipolar LFO2 1/4dot '+str((wave,phase)))
    current=baseline
    for scale in [1.0,.5]:
        for field,delta in [('all_gates',.006),('high_velocities',2),('low_velocities',1),('ENV1:Atk',.4),('ENV1:Dec',.5)]:
            origin=copy.deepcopy(current)
            choices=[current]
            for sign in [-1,1]:
                fields=copy.deepcopy(origin['fields']);timing=copy.deepcopy(origin['timing'])
                if field=='all_gates':
                    for k in ['gates','second_gates']:timing[k]=[min(1.05,max(.8,x+sign*delta*scale)) for x in timing[k]]
                elif field.endswith('_velocities'):
                    indices=[2,5] if field.startswith('high') else [0,1,3,4,6,7]
                    for k in ['velocities','second_velocities']:
                        for i in indices:timing[k][i]=max(1,min(127,timing[k][i]+int(sign*max(1,round(delta*scale)))))
                else:
                    defaults={'ENV1:Atk':2.95,'ENV1:Dec':10.75}
                    fields[field]=round(fields.get(field,defaults[field])+sign*delta*scale,2)
                choices.append(evaluate('sixteen',fields,timing,label=field+' '+str(sign*delta*scale)))
            # Avoid treating a weighted gain with a larger crest error as accepted.
            feasible=[r for r in choices if r['crest_RMS_dB']<=CAP]
            current=min(feasible or [current],key=lambda r:r['score'])
    write(ROOT/'completed.json',dict(trials=len(history),baseline=baseline,best_by_family=best,match_reached=False))
    print('COMPLETED',len(history),{k:r['score'] for k,r in best.items()},flush=True)
