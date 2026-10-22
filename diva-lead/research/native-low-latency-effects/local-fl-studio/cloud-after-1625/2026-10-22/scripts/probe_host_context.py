"""Test documented FL render context against actual FL04 audio, not tune timbre.

The only changes are host warmup/quality/time notifications. Native parameter
state bytes, the incoming Diva performance, mixer and source remain fixed.
"""
from pathlib import Path
import concurrent.futures,json,os,queue,sys,threading,time
import numpy as np
import soundfile as sf
BASE=Path('/tmp/divalead-local-1625');ROOT=BASE/'host-context-screen-01';ROOT.mkdir(exist_ok=False)
KIT=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')
LOCAL=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22')
RUNTIME=BASE/'runtime';OUT=ROOT/'assessment';OUT.mkdir();(OUT/'scores').mkdir()
os.environ['DIVALEAD_SELECTION_WORK']=str(OUT);os.environ['DIVALEAD_RESEARCH_WORK']=str(OUT/'cache')
sys.path.insert(0,str(RUNTIME/'analysis-runtime/diva-lead/research/repository-selection'))
import compare_all as a
a.WORK=OUT
scales=json.loads((RUNTIME/'analysis-runtime/diva-lead/research/repository-selection/ranking_scales.json').read_text());TONE=dict(H24=.3,upper_harm=.25,ERB=.2,low_harm=.1,upper_off=.1,relative_phase=.05)
sys.path.insert(0,'/tmp/divalead-native-effects')
from native_chain import NativeChain
from native_features import Features
actual,sr=sf.read(LOCAL/'renders/FL_NATIVE_04_CALIBRATED.wav',dtype='float32');assert sr==48000
actual=np.pad(actual,((0,288000-len(actual)),(0,0)));flfeatures=Features(actual)
NAMES={0:'SOURCE_WaveShaper',3:'SOURCE_Chorus',4:'MID_EQ_A',5:'MID_EQ_B',6:'SIDE_EQ_A',7:'SIDE_EQ_B',8:'SUM_Stereo',10:'MID_Encode',11:'SIDE_Encode',12:'SIDE_Decode',13:'SOURCE_Phase_R',14:'SOURCE_Phase_L'}
pool=queue.Queue();clients=[];mutex=threading.Lock();rows=[];start=time.monotonic()
def checkpoint(c):
    for node,name in NAMES.items():c.load_state(node,KIT/'verification'/(name+'.bin'))
    for node in [1,2,9]:c.bypass(node,True)
    for k,v in enumerate([1-4923/12800,4923/12800,1,1,1]):c.gain(k,v)
def score(y,label):
    dest=OUT/(label+'.wav');edit=a.h.edit_aligned(a.h.align_with_pdc(y.astype(float),dict(alignment_frames=819),latency=0));sf.write(dest,edit,48000,subtype='FLOAT')
    r=a.score(dict(id=label,canonical_path=str(dest),aliases=[]));m=r['metrics'];f=flfeatures.residual(y)
    n=192000;aa=actual[:n].astype(float);bb=y[:n].astype(float);gain=float(np.sum(aa*bb)/np.sum(bb*bb));null=float(np.linalg.norm(aa-gain*bb)/np.linalg.norm(aa))
    return dict(score=sum(a.WEIGHTS[k]*m[k]/scales[k] for k in a.WEIGHTS),tone_score=sum(TONE[k]*m[k]/scales[k] for k in TONE),actual_FL_feature_distance=float(f@f),actual_FL_waveform_gainfit_residual=null,explicit_diagnostic_gain=gain,metrics=m)
def evaluate(case):
    warm,quality,warmtime,tempo=case;c=pool.get();label=f'w{warm}-q{quality}-t{warmtime}-e{tempo}'
    try:
        checkpoint(c);c.pending.append(f'C {warm} {quality} {warmtime} {tempo}');captures=[]
        for rep in range(3):
            y,status=c.render();r=score(y,label+f'-{rep}');r.update(native_status=status);captures.append((r,y))
        values=[r['actual_FL_feature_distance'] for r,_ in captures];idx=np.argsort(values)[1];path=ROOT/(label+'.wav');sf.write(path,captures[idx][1],48000,subtype='FLOAT')
        row=dict(context=dict(warmblocks=warm,processmode=quality,warmtime=warmtime,tempo_notifications=tempo),captures=[r for r,_ in captures],actual_FL_feature_distance_mean=float(np.mean(values)),actual_FL_feature_distance_std=float(np.std(values)),original_score_mean=float(np.mean([r['score'] for r,_ in captures])),original_tone_mean=float(np.mean([r['tone_score'] for r,_ in captures])),audio=str(path),native_parameter_changes=False,not_a_timbre_candidate=True)
        with mutex:rows.append(row);print('HOST_CONTEXT',case,row['actual_FL_feature_distance_mean'],row['original_score_mean'],row['original_tone_mean'],flush=True)
        return row
    finally:pool.put(c)
cases={(w,q,0,0) for w in [0,1,4,16,64,128,256] for q in [-1,1,2]}
cases|={(128,q,1,e) for q in [-1,2] for e in [0,1]}
try:
    for i in range(4):
        c=NativeChain(KIT/'Diva_SOURCE_FROZEN_48k.wav',f'host-context-{i}',fl_graph=True,phase_pair=True,engine_override='fl_native_host_context_diag.exe');clients.append(c);pool.put(c)
    with concurrent.futures.ThreadPoolExecutor(4) as executor:list(executor.map(evaluate,sorted(cases)))
finally:
    for c in clients:c.close()
rows.sort(key=lambda r:r['actual_FL_feature_distance_mean'])
(ROOT/'RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n')
(ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),actual_native_DLL_context_trials=True,source_parameters_and_MIDI_unchanged=True,selection_target='published actual FL04 audio; original score only diagnostic',best_context=rows[0]['context'],best_FL_distance=rows[0]['actual_FL_feature_distance_mean'],seconds=time.monotonic()-start,reference_match_reached=False),indent=2)+'\n')
print('ACTUAL_HOST_CONTEXT_DIAGNOSTICS_COMPLETE',rows[0]['context'],flush=True)
