"""Real Windows FL20 native states -> real installed ZL VST3, original criteria."""
from pathlib import Path
import os,sys,json,hashlib,csv,math,time
ROOT=Path(__file__).resolve().parent.parent
S=ROOT/'sessions/2026-10-24';U=S/'ZL23_upstream/FL20_ZL_23_WIP';V=U/'verification'
sys.path[:0]=[str(ROOT/'tools/native-host'),str(ROOT/'tools')]
import numpy as np,soundfile as sf
from local_native_chain import NativeChain
from win_vst3_20261024 import WinVST3
from assess_20261024 import assess
R=S/'renders';R.mkdir(exist_ok=True)
PRIVATE=S/'ZL23_CONFIRMED_INPUT.bin' # Short path: C fopen has MAX_PATH limitations.
NODES={0:'SOURCE_WaveShaper',3:'SOURCE_Chorus',4:'MID_EQ_A',5:'MID_EQ_B',6:'SIDE_EQ_A',7:'SIDE_EQ_B',8:'SUM_Stereo',10:'MID_Encode',11:'SIDE_Encode',12:'SIDE_Decode',13:'SOURCE_Phase_R',14:'SOURCE_Phase_L'}
def native(index):
    path=R/f'FL20_NATIVE_PREFIX_{index:02}.wav'
    if path.exists():return sf.read(path,dtype='float32',always_2d=True)[0]
    c=NativeChain(V/'NATIVE_SOURCE_WITH_TAIL.wav',path.stem,host_executable='fl_native_fl20_host_20261024.exe',session=S)
    try:
        for node,name in NODES.items():c.load_state(node,V/(name+'.bin'))
        for node in (1,2,9):c.bypass(node)
        # Actual FLP source Chorus slot mix, raw5593/12800 (not rounded x).
        c.gain(0,1-5593/12800);c.gain(1,5593/12800)
        for k in (2,3,4):c.gain(k,1)
        y,status=c.render();print(status,flush=True);return y
    finally:c.close()
def evaluate(z,x,label):
    y,status=z.render(x,R);path=R/(label+'.wav');sf.write(path,y,48000,subtype='FLOAT')
    a=assess(path);gain=a['diagnostics']['global_RMS_gain_for_AB']
    loss=.65*a['tone_score']+.35*a['standard_score']+.05*abs(math.log(gain))+20*max(0,a['peak']-.95)**2
    # Native EQ regularizer is identical in these paired ZL-only comparisons.
    return dict(label=label,loss=loss,tone=a['tone_score'],standard=a['standard_score'],peak=a['peak'],status=status)
def main():
    rows=[];z=WinVST3('oct24')
    try:
        print(z.ready,flush=True)
        for i in range(5):
            x=native(i)
            for name,component in [('public',V/'ZL_component.bin'),('confirmed',PRIVATE)]:
                z.load(component);row=evaluate(z,x,f'ZL23_{name}_{i:02}');rows.append(row);print(json.dumps(row),flush=True)
            (S/'ZL23_LOCAL_BASELINE_PAIRS.json').write_text(json.dumps(rows,indent=2))
        z.load(PRIVATE);z.dump(S/'ZL23_CONFIRMED_ALL610.tsv');z.save(S/'ZL23_CONFIRMED_RESAVED.bin')
    finally:
        z.close();(S/'ZL23_WINDOWS_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
    diffs=[rows[i]['loss']-rows[i+1]['loss']for i in range(0,len(rows),2)]
    report=dict(paired_improvements=diffs,mean=float(np.mean(diffs)),sem=float(np.std(diffs,ddof=1)/np.sqrt(len(diffs))),minimum_required=max(.0005,3*float(np.std(diffs,ddof=1)/np.sqrt(len(diffs)))),candidate_not_yet_promoted=True)
    (S/'ZL23_LOCAL_BASELINE_SUMMARY.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
