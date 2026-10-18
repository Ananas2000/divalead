"""Freeze changed 16-note performance; test v57/HF2 processing combinations."""
from pathlib import Path
import sys,copy,json,ctypes,re,shutil,subprocess,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_architectures as m
import numpy as np,soundfile as sf
ROOT=m.ROOT/'finalists';ROOT.mkdir(exist_ok=False)
(ROOT/'scores').mkdir();m.common.WORK=ROOT
source_dir=m.ROOT/'sixteen-refinement/best-feasible'
selection=json.loads((source_dir/'selection.json').read_text())
(ROOT/'performance-selection.json').write_text(json.dumps(selection,indent=2)+'\n')
raw_path=ROOT/'raw-selected-Diva.wav';preset=ROOT/'source.h2p'
shutil.copyfile(source_dir/'source.h2p',preset)
assert preset.read_bytes()==(m.V/'Diva_Lead_v57_WIP.h2p').read_bytes()
for repeat in range(2):
    output=ROOT/('fresh-'+str(repeat)+'.wav');dump=ROOT/('fresh-'+str(repeat)+'.tsv')
    cmd=m.commands('sixteen',selection['timing'],output,dump,[96,96,101])
    (ROOT/('fresh-'+str(repeat)+'-commands.txt')).write_text(cmd)
    with (ROOT/('fresh-'+str(repeat)+'.log')).open('w') as log:
        subprocess.run([m.WINE,str(m.HOST),m.win(m.PLUGIN),m.win(preset)],input=cmd,text=True,env=m.env,stdout=log,stderr=log,check=True,timeout=90)
    audio,rate=sf.read(output,dtype='float32');expected,_=sf.read(source_dir/'raw-Diva.wav',dtype='float32')
    assert rate==48000;np.testing.assert_array_equal(audio,expected)
    assert dump.read_bytes()==(m.V/'verification/Diva_all281.tsv').read_bytes()
    log=(ROOT/('fresh-'+str(repeat)+'.log')).read_text();assert 'ERROR ' not in log
    events=[list(map(int,line.split()[1:])) for line in log.splitlines() if line.startswith('NOTE ')]
    assert len(events)==32
    published=json.loads((m.V/'verification/MIDI_note_events_48k.json').read_text())['events']
    assert all(e[:3]==[p[k] for k in ['frame','status','pitch']] for e,p in zip(events,published))
shutil.copyfile(ROOT/'fresh-0.wav',raw_path)
m.write(ROOT/'MIDI-events.json',events)
print('FRESH_CHANGED_MIDI_DIVA_TWICE_EXACT_ALL281_UNCHANGED_TIMING_PITCH_UNCHANGED',flush=True)
hf_proof=json.loads((m.B/'guarded-hf-continuation/BEST_ACTUAL.json').read_text())
hf_report=json.loads(Path(hf_proof['validation']).read_text())
hf_cfg=json.loads(Path(hf_report['core_model']).read_text())
v57_cfg=json.loads((m.V/'analysis/spectral_model.json').read_text())
assert all(hf_cfg[k]==v for k,v in v57_cfg.items() if k!='hf_matrix_parameters')
m.write(ROOT/'HF-selection-proof.json',hf_proof)
compiler=str(m.SETUP/'sysroot/usr/bin/x86_64-w64-mingw32-gcc-posix')
records=[]
for label,cfg in [('v57',v57_cfg),('hf2',hf_cfg)]:
    case=ROOT/label;case.mkdir();analysis=case/'analysis';shutil.copytree(m.V/'analysis',analysis)
    code=analysis/'lead_finish.c';text=code.read_text();assert text.count('0x444c3537')==1
    code.write_text(text.replace('0x444c3537','0x444c3538').replace('v57 WIP','v58 WIP'))
    m.write(analysis/'spectral_model.json',cfg)
    candidate=json.loads((analysis/'selected_candidate.json').read_text());candidate['spectral_model']=cfg
    candidate['settings']=selection['timing'];candidate['stage']='v58 WIP changed MIDI dynamics, fresh source proof'
    candidate['source_render_history']['target_MIDI_events_unchanged']=False
    for key in ['hf_matrix_parameters']:candidate[key]=cfg[key]
    m.write(analysis/'selected_candidate.json',candidate)
    header=analysis/'spectral_ms_settings.h';text=header.read_text();values=np.asarray(cfg['hf_matrix_parameters']).reshape(10,10)
    array='{'+','.join('{'+','.join(format(float(x),'.17g') for x in row)+'}' for row in values)+'}'
    text,n=re.subn(r'SMS_HF_PARAMETERS\[10\]\[10\]=\{.*?\};','SMS_HF_PARAMETERS[10][10]='+array+';',text,flags=re.S);assert n==1
    header.write_text(text)
    native=case/'native_finish.so';subprocess.run(['gcc','-O3','-shared','-fPIC','-o',str(native),str(analysis/'native_finish.c'),'-lm'],check=True,timeout=120)
    lib=ctypes.CDLL(str(native));lib.native_render.argtypes=m.LIB.native_render.argtypes
    source=np.ascontiguousarray(sf.read(raw_path,dtype='float32')[0]);out=np.zeros_like(source)
    assert lib.native_render(source.ctypes.data,out.ctypes.data,len(source),48000)
    sf.write(case/'native-WITH_PDC.wav',out,48000,subtype='FLOAT')
    edit=m.common.h.edit_aligned(m.common.h.align_with_pdc(out.astype('float64'),m.TIMING,latency=12416))
    edit_path=case/'REFERENCE_EDIT_WIP.wav';sf.write(edit_path,edit,48000,subtype='FLOAT')
    measured=m.common.score(dict(id=label,canonical_path=str(edit_path),aliases=[]))
    score=sum(m.common.WEIGHTS[k]*measured['metrics'][k]/m.SCALES[k] for k in m.common.WEIGHTS)
    from search_global_guards import ORIGINAL53_LIMITS
    original=json.loads((m.P/'ranking.json').read_text())['results'][0]['metrics']
    feasible=bool(measured['diagnostics']['crest_RMS_db']<=m.CAP and all(measured['metrics'][k]<=original[k]*v for k,v in ORIGINAL53_LIMITS.items()))
    row=dict(label=label,analysis=str(analysis),score=score,metrics=measured['metrics'],crest_RMS_dB=measured['diagnostics']['crest_RMS_db'],fixed_original11_and_crest_passed=feasible,match_reached=False)
    records.append(row);m.write(case/'measurements.json',row);print('COMBINATION',json.dumps(row),flush=True)
selected=min([r for r in records if r['fixed_original11_and_crest_passed']],key=lambda r:r['score'])
m.write(ROOT/'selected.json',selected)
case=Path(selected['analysis']).parent
dll=case/'Diva_Lead_Finish_v58_WIP_x64.dll'
subprocess.run([compiler,'-O3','-shared','-static-libgcc','-Wl,--no-insert-timestamp','-o',str(dll),str(case/'analysis/lead_finish.c'),'-lm'],check=True,timeout=120)
with (case/'Windows.log').open('w') as log:
    subprocess.run([m.WINE,str(m.B/'fl-v57-build/fx_render_host.exe'),m.win(dll),m.win(raw_path),m.win(case/'actual-Windows.wav'),'512'],env=m.env,stdout=log,stderr=log,check=True,timeout=150)
actual=sf.read(case/'actual-Windows.wav',dtype='float32')[0]
native=sf.read(case/'native-WITH_PDC.wav',dtype='float32')[0]
np.testing.assert_allclose(actual,native,rtol=0,atol=2e-7)
selected['Windows_native_max_error']=float(np.max(abs(actual-native)))
m.write(ROOT/'selected.json',selected)
print('SELECTED_WINDOWS_NATIVE_PASS',selected['score'],selected['Windows_native_max_error'],flush=True)
