"""Analysis-only upper-bound test for short causal stereo filters.

This is NOT an actual FL native-plugin render and is never a deployable native
candidate. Fit the synthesized v83 target on phrase1; assess phrase2 and two
different real Chorus passes before considering another native effect.
"""
from pathlib import Path
import json,os,time
import numpy as np
import soundfile as sf
from scipy.linalg import toeplitz,solve
from scipy.signal import correlate,fftconvolve
from native_chain import W
from native_cpu_slots import four_native_slots
ROOT=W/'causal-filter-capacity-analysis-01';ROOT.mkdir(exist_ok=False)
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target
features=FeaturesOriginal(target);start=time.monotonic();rows=[]
prefix=W/'chorus-20261022T072605Z-0002';inputs=[]
for phase in range(3):
    a,sr=sf.read(prefix/f'actual-WS-Chorus-prefix-{phase}.wav',dtype='float64');assert sr==48000
    inputs.append(np.c_[(a[:,0]+a[:,1])/2,(a[:,0]-a[:,1])/2])
train_frames=96000;X=inputs[0][:train_frames];Y=target[:train_frames].astype(float)
scales=np.sqrt(np.mean(X*X,axis=0));assert min(scales)>1e-7
Z=X/scales;center=train_frames-1
correlations=[[correlate(Z[:,i],Z[:,j],mode='full',method='fft') for j in range(2)] for i in range(2)]
right=[[correlate(Y[:,o],Z[:,i],mode='full',method='fft') for o in range(2)] for i in range(2)]
def fit(length,ridge):
    k=np.arange(length)
    blocks=[[toeplitz(correlations[i][j][center-k],correlations[i][j][center+k]) for j in range(2)] for i in range(2)]
    gram=np.block(blocks);assert np.max(abs(gram-gram.T))<1e-6
    gram=(gram+gram.T)/2;gram.flat[::len(gram)+1]+=ridge*np.trace(gram)/len(gram)
    rhs=np.vstack([np.column_stack([right[i][o][center+k] for o in range(2)]) for i in range(2)])
    return solve(gram,rhs,assume_a='pos').reshape(2,length,2)/scales[:,None,None]
def render(x,kernel):
    result=np.zeros((len(x),2))
    for i in range(2):
        for o in range(2):result[:,o]+=fftconvolve(x[:,i],kernel[i,:,o],mode='full')[:len(x)]
    return result
with four_native_slots(ROOT):
    # Known identity control independently validates correlation lag direction.
    saved=right
    identity_target=np.c_[X[:,0]+X[:,1],X[:,0]-X[:,1]]
    right=[[correlate(identity_target[:,o],Z[:,i],mode='full',method='fft') for o in range(2)] for i in range(2)]
    kernel=fit(32,1e-7);reconstructed=render(inputs[0],kernel);source_lr=np.c_[inputs[0][:,0]+inputs[0][:,1],inputs[0][:,0]-inputs[0][:,1]]
    identity_relative_RMS=float(np.sqrt(np.mean((reconstructed-source_lr)**2)/np.mean(source_lr**2)))
    assert identity_relative_RMS<.005,identity_relative_RMS
    right=saved
    for length in [32,128,512,1024]:
        for ridge in [.01,.001,.0001]:
            kernel=fit(length,ridge);captures=[]
            for phase in range(3):
                y=render(inputs[phase],kernel);r=features.residual(y[:len(target)]);loss=float(r@r)
                test=slice(128000,192000);train=slice(0,64000)
                captures.append(dict(phase=phase,loss=loss,assessment=features.local.last,
                    phrase1_relative_RMS_to_v83=float(np.sqrt(np.mean((y[train]-target[train])**2)/np.mean(target[train]**2))),
                    phrase2_relative_RMS_to_v83=float(np.sqrt(np.mean((y[test]-target[test])**2)/np.mean(target[test]**2))),
                    peak=float(abs(y).max())))
            row=dict(taps=length,causal_support_ms=1000*length/48000,ridge=ridge,
                mean_loss=float(np.mean([r['loss'] for r in captures])),captures=captures,
                IR_max_abs=float(abs(kernel).max()),analysis_only_NOT_actual_native_DLL_audio=True,
                training_target_is_synthesized_v83_not_original_audio=True,trained_on_first_phrase_only=True,
                two_heldout_actual_Chorus_passes=True,no_added_alignment_or_PDC=True,
                original_reference_match_reached=False,not_a_deployable_candidate=True)
            rows.append(row);np.savez_compressed(ROOT/f'taps-{length}-ridge-{ridge:g}.npz',kernel_MStoLR=kernel)
            print('CAUSAL_CAPACITY_ONLY',length,ridge,row['mean_loss'],flush=True)
    rows.sort(key=lambda row:row['mean_loss'])
    (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'completion.json').write_text(json.dumps(dict(analysis_only_NOT_native_DSP=True,
        identity_relative_RMS=identity_relative_RMS,cases=len(rows),best=rows[0],seconds=time.monotonic()-start,
        no_plugin_latency_or_FL_compatibility_claimed=True,reference_match_reached=False),indent=2)+'\n')
print('CAUSAL_FILTER_CAPACITY_ANALYSIS_COMPLETE',rows[0]['mean_loss'],flush=True)
