"""Actual installed Diva + actual native FL chain; original-reference screening.

Only the fixed three-held-note protocol is used. Every candidate gets a fresh
Diva instance, dump of all parameters, and a saved native h2p state.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import subprocess,json,time,threading,queue,concurrent.futures,sys
import numpy as np,soundfile as sf
from local_native_chain import NativeChain,SESSION,ROOT,W
OUT=SESSION/'diva-source-screen';OUT.mkdir(exist_ok=True);(OUT/'scores').mkdir(exist_ok=True)
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(ROOT/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((ROOT/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());tone_weights=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
start=time.monotonic();pool=queue.Queue();clients=[];lock=threading.Lock();results=[]
def rel(p):return os.path.relpath(p,ROOT)
for k in range(4):
    c=NativeChain(SESSION/'renders/DIVA_FRESH_DIRECT.wav',f'DIVA_SCREEN_{k}');c.checkpoint();c.label=f'worker-{k}';clients.append(c);pool.put(c)
base=SESSION/'input/Diva_NATIVE_WIP_THREE_HELD.h2p'
trials=[('baseline',{})]
for tag,index,values in[
 ('pan',167,[(v+100)/200 for v in(-50,-39.33,-30,-20,-10,0,10)]),
 ('cutoff',148,[(v-30)/120 for v in(137,140,142,144.16,146,148,150)]),
 ('resonance',149,[v/100 for v in(0,6,12.13,18,25)]),
 ('pulsewidth',90,[v/100 for v in(45,48,50,51.91,54,57,60)]),
 ('mix',96,[v/100 for v in(0,2.5,5.71,8,12,20)]),
 ('moddepth',171,[(v+100)/200 for v in(-78,-73,-68,-63,-58)]),
 ('drift',134,[v/200 for v in(0,10,24.8,35,50)]),
 ('finetune',15,[(v+100)/200 for v in(-3,-1,0,1.02,2,3,5)]),
 ('attack',33,[v/100 for v in(14,17,20,23,26)]),
 ('release',36,[v/100 for v in(2,4,6,8)]),
 ('reverbwet',235,[v/100 for v in(0,.5,1.12,2)])]:
    trials += [(f'{tag}-{j}',{index:value})for j,value in enumerate(values)]
def evaluate(trial):
    tag,changes=trial;c=pool.get()
    try:
        raw=OUT/(c.label+'-raw.wav');preset=OUT/(tag+'.h2p');dump=OUT/(tag+'-all281.tsv');log=OUT/(tag+'.log')
        commands=['pattern 3 0 8','velocities 96 96 101','warmblocks 128','preludes 0']+[f'set {i} {v:.9g}'for i,v in changes.items()]+['render '+rel(raw),'dump '+rel(dump),'save '+rel(preset),'quit']
        p=subprocess.run([str(W/'diva_source_render_host.exe'),r'C:\Program Files\VstPlugins\Diva(x64).dll',rel(base)],cwd=ROOT,input='\n'.join(commands)+'\n',text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,timeout=60);log.write_text(p.stdout,encoding='utf-8');assert p.returncode==0,p.stdout
        notes=[line for line in p.stdout.splitlines()if line.startswith('NOTE ')];assert len(notes)==12
        rows=dump.read_text().splitlines()[1:];assert len(rows)==281
        for i,v in changes.items():assert abs(float(rows[i].split('\t')[1])-v)<1e-6
        c.load_input(raw);y,status=c.render();edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype('float64'),dict(alignment_frames=819),latency=0));dest=OUT/(c.label+'-edit.wav');sf.write(dest,edit,48000,subtype='FLOAT')
        score=a.score(dict(id=c.label,canonical_path=str(dest),aliases=[]));m=score['metrics'];standard=sum(a.WEIGHTS[k]*m[k]/scales[k]for k in a.WEIGHTS);tone=sum(tone_weights[k]*m[k]/scales[k]for k in tone_weights);gain=score['diagnostics']['global_RMS_gain_for_AB'];peak=float(abs(y).max());loss=.65*tone+.35*standard+.05*abs(np.log(gain))+20*max(0,peak-.95)**2
        row=dict(tag=tag,changes=changes,loss=loss,score=standard,tone_score=tone,peak=peak,metrics=m,gain_for_AB=gain,seconds=time.monotonic()-start,native_status=status,all281_dumped=True,MIDI_note_events=12,match_reached=False)
        (OUT/(tag+'.json')).write_text(json.dumps(row,indent=2));sf.write(OUT/(tag+'.wav'),y,48000,subtype='FLOAT')
        with lock:
            results.append(row);(OUT/'ranking.json').write_text(json.dumps(sorted(results,key=lambda r:r['loss']),indent=2));print('SOURCE_TRIAL',json.dumps({k:row[k]for k in('tag','loss','score','tone_score','seconds')}),flush=True)
        return row
    finally:pool.put(c)
try:
    with concurrent.futures.ThreadPoolExecutor(4)as executor:list(executor.map(evaluate,trials))
finally:
    for c in clients:c.close()
print('COMPLETE',len(results),time.monotonic()-start,flush=True)
