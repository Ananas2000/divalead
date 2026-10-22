"""Reproduce authored local-to-cloud diagnostics with actual supplied DLLs.

No optimization. Original reference audio is confined to the analysis module.
All native state bytes are loaded from the exact checkpoint used by FL04.
"""
from pathlib import Path
import hashlib,json,os,sys,shutil,struct,time
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625');ROOT=BASE/'reproduction';ROOT.mkdir(exist_ok=False)
LOCAL=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22')
KIT=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')
RUNTIME=BASE/'runtime';OUT=ROOT/'assessment';OUT.mkdir();(OUT/'scores').mkdir()
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(RUNTIME/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((RUNTIME/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text())
TONE=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
sys.path.insert(0,'/tmp/divalead-native-effects')
from native_chain import NativeChain
NAMES={0:'SOURCE_WaveShaper',3:'SOURCE_Chorus',4:'MID_EQ_A',5:'MID_EQ_B',6:'SIDE_EQ_A',7:'SIDE_EQ_B',8:'SUM_Stereo',10:'MID_Encode',11:'SIDE_Encode',12:'SIDE_Decode',13:'SOURCE_Phase_R',14:'SOURCE_Phase_L'}
def checkpoint(c):
    for node,name in NAMES.items():c.load_state(node,KIT/'verification'/(name+'.bin'))
    for node in [1,2,9]:c.bypass(node,True)
    for k,v in enumerate([1-4923/12800,4923/12800,1,1,1]):c.gain(k,v)
def score(path):
    y,sr=sf.read(path,dtype='float64',always_2d=True);assert sr==48000
    edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0))
    dest=OUT/(path.stem+'-edit.wav');sf.write(dest,edit,sr,subtype='FLOAT')
    row=a.score(dict(id=path.stem,canonical_path=str(dest),aliases=[]));m=row['metrics']
    row.update(score=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS),tone_score=sum(TONE[k]*m[k]/scales[k] for k in TONE),source_file=str(path),file_SHA256=hashlib.sha256(path.read_bytes()).hexdigest())
    return row
start=time.monotonic();allrows=[]
for name in ['DIAG_FL_NO_CHORUS','DIAG_OFFLINE_NO_CHORUS','DIAG_CHORUS_NATIVE_RELOAD']:
    row=score(BASE/'diagnostics/renders'/(name+'.wav'));allrows.append(row);print('PUBLISHED_REPLAY',name,row['score'],row['tone_score'],flush=True)
for name in ['FL_NATIVE_04_CALIBRATED','FL_NATIVE_05_MODDEPTH']:
    row=score(LOCAL/'renders'/(name+'.wav'));allrows.append(row);print('PUBLISHED_REPLAY',name,row['score'],row['tone_score'],flush=True)
c=NativeChain(KIT/'Diva_SOURCE_FROZEN_48k.wav','local1625-fresh-repro',fl_graph=True,phase_pair=True)
try:
    checkpoint(c);state_checks=[]
    for node,name in NAMES.items():
        dest=ROOT/(name+'.bin');c.save_state(node,dest);assert dest.read_bytes()==(KIT/'verification'/(name+'.bin')).read_bytes();state_checks.append(name)
    for rep in range(6):
        y,status=c.render();path=ROOT/f'FRESH_WINE_CHORUS_ON_{rep}.wav';sf.write(path,y,48000,subtype='FLOAT');row=score(path);row['native_status']=status;allrows.append(row)
        print('ACTUAL_NATIVE_FRESH',rep,row['score'],row['tone_score'],flush=True)
    c.gain(0,1);c.gain(1,0);c.bypass(3,True);y,status=c.render();path=ROOT/'FRESH_WINE_NO_CHORUS.wav';sf.write(path,y,48000,subtype='FLOAT');row=score(path);allrows.append(row)
    provided,sr=sf.read(BASE/'diagnostics/renders/DIAG_OFFLINE_NO_CHORUS.wav',dtype='float32');assert y.shape==provided.shape
    delta=y.astype(float)-provided.astype(float)
    null=dict(decoded_float32_bit_exact=bool(np.array_equal(y,provided)),max_abs_error=float(abs(delta).max()),null_RMS=float(np.sqrt(np.mean(delta*delta))),no_gain_or_time_fit_used=True)
    print('ACTUAL_NO_CHORUS',row['score'],row['tone_score'],null,flush=True)
finally:c.close()
(ROOT/'RESULTS.json').write_text(json.dumps(dict(all12_state_bytes_exact=state_checks,old_search_stopped=True,results=allrows,Windows_vs_Wine_offline_no_Chorus_null=null,actual_native_DLL_render=True,actual_FL_files_replayed_not_new_GUI_exports=True,reference_used_only_for_analysis=True,seconds=time.monotonic()-start,reference_match_reached=False),indent=2)+'\n')
print('LOCAL_1625_BASELINE_REPRODUCED',flush=True)
