"""Create lossless listening AB, complete kit and all research checkpoint files."""
from pathlib import Path
import json,zipfile,hashlib,shutil,math
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent.parent;S=R/'sessions/2026-10-24'
OUT=R/'divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';OUT.mkdir(parents=True,exist_ok=True)
ref,sr=sf.read(S/'ZL23_upstream/FL20_ZL_23_WIP/Diva_original_lead_reference.wav',always_2d=True);assert sr==48000
labels=['original','FL26_public_ZL23','FL26_confirmed_ZL23']
clips=[ref]+[sf.read(S/'assessment'/(k+'_REFERENCE_EDIT.wav'),always_2d=True)[0]for k in('FL26_ZL23_BASELINE','Diva_ZL23_BEST_FL26')]
assert all(x.shape==ref.shape for x in clips)
rms=lambda x:float(np.sqrt(np.mean(x*x)))
gains=[rms(ref)/rms(x)for x in clips];peak=max(float(abs(x*g).max())for x,g in zip(clips,gains));safety=min(1.,.98/peak)
parts=[]
for i,(x,g)in enumerate(zip(clips,gains)):
    if i:parts.append(np.zeros((24000,2)))
    parts.append(x*g*safety)
sf.write(S/'AB_ORIGINAL_FL26_ZL23.flac',np.concatenate(parts),48000,subtype='PCM_24')
(S/'AB_LEVELS_20261024.json').write_text(json.dumps(dict(order=labels,starts_seconds=[i*(len(ref)/48000+.5)for i in range(3)],per_clip_RMS_gains=gains,common_peak_safety_gain=safety,only_AB_gain_matched=True,original_candidate_WAVs_untouched=True),indent=2))
metrics=[]
for name in('FL26_ZL23_BASELINE','Diva_ZL23_BEST_FL26','NATIVE_FULL_180BPM_WIP'):
    q=json.loads((S/'assessment'/(name+'.json')).read_text());q['original_objective_without_constant_EQ_reg']=.65*q['tone_score']+.35*q['standard_score']+.05*abs(math.log(q['diagnostics']['global_RMS_gain_for_AB']))+20*max(0,q['peak']-.95)**2;metrics.append(q)
(S/'FINAL_GUI_METRICS.json').write_text(json.dumps(metrics,indent=2))
q=json.loads((S/'GUI_SCREEN_ONLY_PROPOSAL.json').read_text());q.update(rejected=True,reason='All 16 static probes were worse than the accepted component, including this proposal. Do not load as best.');(S/'GUI_SCREEN_ONLY_PROPOSAL.json').write_text(json.dumps(q,indent=2))
selected=['CONTINUE_RU.md','Diva_ZL23_BEST_FL26.flp','Diva_ZL23_BEST_FL26.h2p','Diva_ZL23_BEST_FL26.wav','Diva_ZL23_CONFIRMED_LOCAL.flp','SUM_ZL23_CONFIRMED_LOCAL.fst','AB_ORIGINAL_FL26_ZL23.flac','AB_LEVELS_20261024.json','BEST_FLP_VERIFICATION.json','ZL23_CONFIRMED_INPUT.bin','ZL23_CONFIRMED_ALL610.tsv','FINAL_GUI_METRICS.json']
def archive(name,paths):
    p=OUT/name;manifest=[]
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for f in sorted(set(paths)):
            assert f.is_relative_to(R) and f.suffix.lower()!='.dll'
            arc='local-fl-matching/'+f.relative_to(R).as_posix();z.write(f,arc)
            manifest.append(dict(path=arc,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    with zipfile.ZipFile(p)as z:assert z.testzip()is None
    (OUT/(name+'.manifest.json')).write_text(json.dumps(manifest,indent=2))
    return dict(file=name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),files=len(manifest))
play=[S/n for n in selected]+[f for f in(S/'ZL23_upstream').rglob('*')if f.is_file()]
reports=[f for f in S.rglob('*')if f.is_file()and 'ZL23_upstream'not in f.parts and 'cache'not in f.parts and f.suffix.lower()not in('.wav','.flac','.f32')]
reports += [S/n for n in('FL26_PRE_ZL_00.wav','FL26_PRE_ZL_01.wav','FL26_ZL23_BASELINE.wav')]
names=['assess_20261024.py','build_zl23_confirmed_20261024.py','experiment_20261024.py','search_zl_gui_20261024.py','screen_dynamic_20261024.py','prepare_20261024.py','cloud_native_fst.py','verify_best_20261024.py','pack_20261024.py']
reports += [R/'tools'/n for n in names]
native=['win_vst3_20261024.py','local_native_chain.py','vst3_effect_host_20261024.c','vst3_effect_host_20261024.exe','fl_native_fl20_host_20261024.c','fl_native_fl20_host_20261024.exe','fl_native_probe.c','diva_source_render_host.c','diva_source_render_host.exe']
reports += [R/'tools/native-host'/n for n in native]
reports += [f for f in(R/'analysis-runtime').rglob('*')if f.is_file()and '__pycache__'not in f.parts]
static=[f for f in(S/'renders').glob('*.wav')if f.name.startswith(('GUI_SCREEN_','GUI_PREFIX_'))]
dynamic=[f for f in(S/'renders').glob('*.wav')if f.name.startswith('DYNAMIC_')]
packages=[archive('Diva_ZL23_LOCAL_COMPLETE.zip',play),archive('LOCAL_RESEARCH_TOOLS_AND_REPORTS.zip',reports),archive('STATIC_TRIALS_AUDIO.zip',static),archive('DYNAMIC_TRIALS_AUDIO.zip',dynamic)]
(OUT/'PACKAGES.json').write_text(json.dumps(packages,indent=2))
shutil.copyfile(S/'CONTINUE_RU.md',OUT/'README_RU.md')
for n in('BEST_FLP_VERIFICATION.json','FINAL_GUI_METRICS.json','DYNAMIC_SCREEN.json','GUI_SINGLE_PREFIX_SCREEN.json','GUI_PREFIX_BASELINES.json','AB_LEVELS_20261024.json'):
    shutil.copyfile(S/n,OUT/n)
for n in('Diva_ZL23_BEST_FL26.flp','Diva_ZL23_BEST_FL26.h2p','Diva_ZL23_BEST_FL26.wav','AB_ORIGINAL_FL26_ZL23.flac'):
    shutil.copyfile(S/n,OUT/n)
for n in names:shutil.copyfile(R/'tools'/n,OUT/n)
print(json.dumps(packages,indent=2))
